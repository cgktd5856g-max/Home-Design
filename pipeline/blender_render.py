#!/usr/bin/env python3
"""Render a roomkit project with Blender Cycles (photoreal). Same pieces, timeline, camera and light slots as the
code renderer, plus production shading: wood grain, tiles with grout, baked marble / floor / window view, glass,
bevelled edges, a sun through the window, motion blur and OpenImageDenoise.

usage: <python with bpy> blender_render.py <project.py> <outdir> [options]
  --size WxH        render size (default 720x1280)        --samples N   max samples per pixel (default 64)
  --test t1,t2,..   stills at those times -> <outdir>/test_<t>.png + test_sheet.jpg (look development)
  --frames a:b      render only frames a..b (1-based, inclusive); default: the whole clip
  --blend           also save <outdir>/scene.blend
  --fps N           frame rate of the render (default: the project's FPS)
  --adaptive X      adaptive-sampling noise threshold (default 0.02)   --bounces M,D,G   max, diffuse, glossy (default 6,3,3)
  --nobevel         skip the bevel shader (faster)
The project's BLENDER dict tunes the look (exposure, look, sun, glass, bevel, separate, fill_lights, wood_scale,
bake_rect, bake_px). Frames go to <outdir>/frames/f_0001.png ...; finished frames are skipped on a re-run.
"""
import importlib.util
import math
import os
import shutil
import sys
import time

import numpy as np
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import textures


NO_BEVEL = False
P_fps_override = [None]


def opt(args, name, default=None):
    return args[args.index(name) + 1] if name in args else default


def load_project(path):
    spec = importlib.util.spec_from_file_location('project', path)
    P = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(P)
    return P


def set_in(node, names, value):
    for n in ([names] if isinstance(names, str) else names):
        if n in node.inputs:
            node.inputs[n].default_value = value
            return True
    return False


def ior_from_f0(f0):
    s = math.sqrt(max(min(f0, 0.5), 1e-4))
    return (1 + s) / (1 - s)


# ------------------------------------------------------------------------------------------- materials
class Materials:
    def __init__(self, rk, BL):
        self.rk, self.BL = rk, BL
        self.names = {i: n for n, i in rk.MATIDX.items()}
        self.bounds = {}
        for parts in rk.INST.values():
            for Pt, _, m in parts:
                lo, hi = Pt.reshape(-1, 3).min(0), Pt.reshape(-1, 3).max(0)
                if m in self.bounds:
                    a, b = self.bounds[m]
                    self.bounds[m] = (np.minimum(a, lo), np.maximum(b, hi))
                else:
                    self.bounds[m] = (lo, hi)
        self.mats = [self.build(self.names[i], rk.MATS[i], i) for i in range(len(rk.MATS))]

    # -- helpers
    def coords(self, nt):
        tc = nt.nodes.new('ShaderNodeTexCoord')
        return tc.outputs['Object']

    def uv_from_plane(self, nt, vec, au, av, rect):
        N, L = nt.nodes, nt.links
        sep = N.new('ShaderNodeSeparateXYZ'); L.new(vec, sep.inputs[0])
        comb = N.new('ShaderNodeCombineXYZ')
        for k, (ax, a0, a1) in enumerate(((au, rect[0], rect[1]), (av, rect[2], rect[3]))):
            mr = N.new('ShaderNodeMapRange'); mr.clamp = False
            mr.inputs['From Min'].default_value = a0; mr.inputs['From Max'].default_value = a1
            L.new(sep.outputs['XYZ'[ax]], mr.inputs['Value'])
            L.new(mr.outputs['Result'], comb.inputs[k])
        return comb.outputs['Vector']

    def baked_image(self, name, tex, rec, midx):
        lo, hi = self.bounds[midx]
        ext = hi - lo
        order = np.argsort(-ext)
        au, av, fx = int(order[0]), int(order[1]), int(order[2])
        rect = self.BL.get('bake_rect', {}).get(name, (lo[au], hi[au], lo[av], hi[av]))
        px = self.BL.get('bake_px', {}).get(name, 0.002)
        res = (max(16, int((rect[1] - rect[0]) / px)), max(16, int((rect[3] - rect[2]) / px)))
        t0 = time.time()
        rgb, mask = textures.bake(tex, rec, rect, (au, av), (fx, float((lo[fx] + hi[fx]) / 2)), res)
        img = bpy.data.images.new(f'bake_{name}', res[0], res[1], alpha=True, float_buffer=True)
        for cs in ('Linear Rec.709', 'Linear', 'Non-Color'):
            try:
                img.colorspace_settings.name = cs
                break
            except Exception:
                pass
        img.alpha_mode = 'CHANNEL_PACKED'
        a = np.ones(rgb.shape[:2], np.float32) if mask is None else 1.0 - mask.astype(np.float32)
        img.pixels.foreach_set(np.dstack([rgb.astype(np.float32), a]).ravel())
        img.pack()
        print(f'  baked {name}: {res[0]}x{res[1]} in {time.time() - t0:.1f}s', flush=True)
        return img, au, av, rect

    # -- one material
    def build(self, name, rec, midx):
        BL = self.BL
        tex = int(rec[0])
        col, col2, col3 = tuple(map(float, rec[1:4])), tuple(map(float, rec[4:7])), tuple(map(float, rec[20:23]))
        rough, f0, metal = float(rec[7]), float(rec[8]), rec[9] > 0.5
        emis = np.array(rec[10:13], float)
        p = [float(v) for v in rec[13:19]]
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        nt = m.node_tree
        N, L = nt.nodes, nt.links
        out = next(n for n in N if n.type == 'OUTPUT_MATERIAL')
        bsdf = next(n for n in N if n.type == 'BSDF_PRINCIPLED')
        normal_in = None                         # socket that wants the final normal (for bevel chaining)

        # emission-only materials (LEDs, screens, window view)
        if (max(col) < 1e-6 and emis.max() > 0) or tex in (8, 9):
            em = N.new('ShaderNodeEmission')
            k = float(emis.max())
            em.inputs['Color'].default_value = (*(emis / k), 1.0)
            em.inputs['Strength'].default_value = k
            if tex == 9:
                img, au, av, rect = self.baked_image(name, tex, rec, midx)
                it = N.new('ShaderNodeTexImage'); it.image = img; it.extension = 'EXTEND'
                L.new(self.uv_from_plane(nt, self.coords(nt), au, av, rect), it.inputs['Vector'])
                L.new(it.outputs['Color'], em.inputs['Color'])
            L.new(em.outputs['Emission'], out.inputs['Surface'])
            N.remove(bsdf)
            return m

        set_in(bsdf, 'Base Color', (*col, 1.0))
        set_in(bsdf, 'Roughness', rough)
        set_in(bsdf, 'Metallic', 1.0 if metal else 0.0)
        if f0 > 0:
            set_in(bsdf, 'IOR', ior_from_f0(f0))
        else:
            set_in(bsdf, ['Specular IOR Level', 'Specular'], 0.25)
        vec = self.coords(nt)

        if tex == 2:                                                        # wood grain along an axis
            ax, seed = int(p[0]), p[1]
            across, along = BL.get('wood_scale', (55.0, 1.6))
            mp = N.new('ShaderNodeMapping')
            sc = [across] * 3; sc[ax] = along
            mp.inputs['Scale'].default_value = sc
            mp.inputs['Location'].default_value = (seed * 1.37, seed * 2.11, seed * 0.73)
            L.new(vec, mp.inputs['Vector'])
            nz = N.new('ShaderNodeTexNoise')
            set_in(nz, 'Scale', 1.0); set_in(nz, 'Detail', 12.0); set_in(nz, 'Roughness', 0.62); set_in(nz, 'Distortion', 0.35)
            L.new(mp.outputs['Vector'], nz.inputs['Vector'])
            cr = N.new('ShaderNodeValToRGB')
            e0, e1 = cr.color_ramp.elements[0], cr.color_ramp.elements[1]
            e0.position, e1.position = 0.32, 0.70
            e0.color = (*[c * 0.74 for c in col], 1.0); e1.color = (*[min(1.0, c * 1.13) for c in col], 1.0)
            L.new(nz.outputs['Fac'], cr.inputs['Fac'])
            mp2 = N.new('ShaderNodeMapping')
            sc2 = [across * 7] * 3; sc2[ax] = along * 3
            mp2.inputs['Scale'].default_value = sc2
            L.new(vec, mp2.inputs['Vector'])
            nz2 = N.new('ShaderNodeTexNoise'); set_in(nz2, 'Scale', 1.0); set_in(nz2, 'Detail', 3.0)
            L.new(mp2.outputs['Vector'], nz2.inputs['Vector'])
            mix = N.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
            mix.inputs['Factor'].default_value = 0.18
            L.new(cr.outputs['Color'], mix.inputs[6]); L.new(nz2.outputs['Color'], mix.inputs[7])
            L.new(mix.outputs[2], bsdf.inputs['Base Color'])
            set_in(bsdf, 'Roughness', 0.42)
            set_in(bsdf, ['Specular IOR Level', 'Specular'], 0.45)
        elif tex == 3:                                                      # speckle
            nz = N.new('ShaderNodeTexNoise'); set_in(nz, 'Scale', 380.0); set_in(nz, 'Detail', 2.0)
            L.new(vec, nz.inputs['Vector'])
            mr = N.new('ShaderNodeMapRange')
            mr.inputs['To Min'].default_value = 1 - p[0] * 1.5; mr.inputs['To Max'].default_value = 1 + p[0] * 1.5
            L.new(nz.outputs['Fac'], mr.inputs['Value'])
            vm = N.new('ShaderNodeVectorMath'); vm.operation = 'SCALE'; vm.inputs[0].default_value = col
            L.new(mr.outputs['Result'], vm.inputs['Scale'])
            L.new(vm.outputs['Vector'], bsdf.inputs['Base Color'])
        elif tex == 4:                                                      # blind: horizontal slat lines + back-light glow
            sep = N.new('ShaderNodeSeparateXYZ'); L.new(vec, sep.inputs[0])
            dv = N.new('ShaderNodeMath'); dv.operation = 'DIVIDE'; dv.inputs[1].default_value = p[0]
            L.new(sep.outputs['Z'], dv.inputs[0])
            fr = N.new('ShaderNodeMath'); fr.operation = 'FRACT'; L.new(dv.outputs[0], fr.inputs[0])
            cr = N.new('ShaderNodeValToRGB')
            cr.color_ramp.elements[0].position = 0.0; cr.color_ramp.elements[0].color = (0.62, 0.62, 0.62, 1)
            cr.color_ramp.elements[1].position = 0.14; cr.color_ramp.elements[1].color = (1, 1, 1, 1)
            e2 = cr.color_ramp.elements.new(1.0); e2.color = (0.90, 0.90, 0.90, 1)
            L.new(fr.outputs[0], cr.inputs['Fac'])
            mul = N.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = 1.0
            mul.inputs[6].default_value = (*col, 1.0); L.new(cr.outputs['Color'], mul.inputs[7])
            L.new(mul.outputs[2], bsdf.inputs['Base Color'])
            if emis.max() > 0:
                k = float(emis.max())
                L.new(cr.outputs['Color'], bsdf.inputs['Emission Color'])
                set_in(bsdf, 'Emission Strength', k)
            emis = np.zeros(3)
            set_in(bsdf, 'Roughness', 0.85)
        elif tex == 7:                                                      # stripes
            sep = N.new('ShaderNodeSeparateXYZ'); L.new(vec, sep.inputs[0])
            dv = N.new('ShaderNodeMath'); dv.operation = 'DIVIDE'; dv.inputs[1].default_value = p[1]
            L.new(sep.outputs['XYZ'[int(p[0])]], dv.inputs[0])
            fr = N.new('ShaderNodeMath'); fr.operation = 'FRACT'; L.new(dv.outputs[0], fr.inputs[0])
            lt = N.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'; lt.inputs[1].default_value = 0.5
            L.new(fr.outputs[0], lt.inputs[0])
            mix = N.new('ShaderNodeMix'); mix.data_type = 'RGBA'
            mix.inputs[6].default_value = (*col2, 1.0); mix.inputs[7].default_value = (*col, 1.0)
            L.new(lt.outputs[0], mix.inputs['Factor'])
            L.new(mix.outputs[2], bsdf.inputs['Base Color'])
            set_in(bsdf, 'Roughness', 0.95); set_in(bsdf, ['Sheen Weight', 'Sheen'], 0.5)
        elif tex in (11, 13):                                               # baked marble / cement floor
            img, au, av, rect = self.baked_image(name, tex, rec, midx)
            it = N.new('ShaderNodeTexImage'); it.image = img; it.extension = 'EXTEND'; it.interpolation = 'Cubic'
            L.new(self.uv_from_plane(nt, vec, au, av, rect), it.inputs['Vector'])
            L.new(it.outputs['Color'], bsdf.inputs['Base Color'])
            if tex == 13:
                bump = N.new('ShaderNodeBump'); set_in(bump, 'Strength', 0.6); set_in(bump, 'Distance', 0.0012)
                L.new(it.outputs['Alpha'], bump.inputs['Height'])
                L.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
                normal_in = bump.inputs['Normal']
        elif tex == 12:                                                     # tiles with grout
            tu, tv, gw, ax = p[0], p[1], p[2], int(p[3])
            sep = N.new('ShaderNodeSeparateXYZ'); L.new(vec, sep.inputs[0])
            comb = N.new('ShaderNodeCombineXYZ')
            u, v = (('Y', 'Z'), ('X', 'Z'), ('X', 'Y'))[ax]
            L.new(sep.outputs[u], comb.inputs[0]); L.new(sep.outputs[v], comb.inputs[1])
            br = N.new('ShaderNodeTexBrick'); br.offset = p[4]; br.squash = 1.0
            br.inputs['Color1'].default_value = (*[c * 0.985 for c in col], 1.0)
            br.inputs['Color2'].default_value = (*[min(1.0, c * 1.015) for c in col], 1.0)
            br.inputs['Mortar'].default_value = (*col2, 1.0)
            set_in(br, 'Scale', 1.0); set_in(br, 'Mortar Size', gw * 0.5); set_in(br, 'Mortar Smooth', 0.25)
            set_in(br, 'Brick Width', tu); set_in(br, 'Row Height', tv); set_in(br, 'Bias', 0.0)
            L.new(comb.outputs[0], br.inputs['Vector'])
            L.new(br.outputs['Color'], bsdf.inputs['Base Color'])
            bump = N.new('ShaderNodeBump'); bump.invert = True; set_in(bump, 'Strength', 0.7); set_in(bump, 'Distance', 0.0015)
            L.new(br.outputs['Fac'], bump.inputs['Height'])
            L.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
            normal_in = bump.inputs['Normal']
        elif tex == 14:                                                     # brushed metal
            ax = int(p[0])
            mp = N.new('ShaderNodeMapping'); sc = [900.0] * 3; sc[ax] = 6.0
            mp.inputs['Scale'].default_value = sc
            L.new(vec, mp.inputs['Vector'])
            nz = N.new('ShaderNodeTexNoise'); set_in(nz, 'Scale', 1.0); set_in(nz, 'Detail', 2.0)
            L.new(mp.outputs['Vector'], nz.inputs['Vector'])
            mr = N.new('ShaderNodeMapRange')
            mr.inputs['To Min'].default_value = max(0.05, rough - 0.08); mr.inputs['To Max'].default_value = rough + 0.08
            L.new(nz.outputs['Fac'], mr.inputs['Value']); L.new(mr.outputs['Result'], bsdf.inputs['Roughness'])
        elif tex == 15:                                                     # quartz with flecks
            nz = N.new('ShaderNodeTexNoise'); set_in(nz, 'Scale', p[0] * 0.55); set_in(nz, 'Detail', 2.0)
            L.new(vec, nz.inputs['Vector'])
            cr = N.new('ShaderNodeValToRGB'); cr.color_ramp.interpolation = 'CONSTANT'
            cr.color_ramp.elements[0].color = (*col, 1.0)
            cr.color_ramp.elements[1].position = 0.70; cr.color_ramp.elements[1].color = (*col2, 1.0)
            L.new(nz.outputs['Fac'], cr.inputs['Fac'])
            L.new(cr.outputs['Color'], bsdf.inputs['Base Color'])

        if emis.max() > 0:
            k = float(emis.max())
            set_in(bsdf, 'Emission Color', (*(emis / k), 1.0))
            set_in(bsdf, 'Emission Strength', k)
        if name in BL.get('glass', []):
            set_in(bsdf, ['Transmission Weight', 'Transmission'], 1.0)
            set_in(bsdf, 'Roughness', 0.03); set_in(bsdf, 'IOR', 1.47)
            set_in(bsdf, 'Base Color', (0.95, 0.97, 0.96, 1.0))
        r_bev = None if NO_BEVEL else BL.get('bevel', {}).get(name)
        if r_bev:
            bv = N.new('ShaderNodeBevel'); bv.samples = 6
            set_in(bv, 'Radius', r_bev)
            if normal_in is not None:
                L.new(bv.outputs['Normal'], normal_in)
            else:
                L.new(bv.outputs['Normal'], bsdf.inputs['Normal'])
        return m


# ------------------------------------------------------------------------------------------- meshes
def make_mesh(name, Pt, Nt, Mi, mats):
    Pt, Nt = Pt.astype(np.float64).copy(), Nt.astype(np.float64).copy()
    g = np.cross(Pt[:, 1] - Pt[:, 0], Pt[:, 2] - Pt[:, 0])
    flip = np.einsum('ij,ij->i', g, Nt.sum(axis=1)) < 0      # make winding agree with the shading normals
    Pt[flip] = Pt[flip][:, [0, 2, 1]]; Nt[flip] = Nt[flip][:, [0, 2, 1]]
    V = Pt.reshape(-1, 3)
    key = np.round(V * 1e5).astype(np.int64)
    _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    inv = np.asarray(inv).reshape(-1)
    verts = V[first]
    faces = inv.reshape(-1, 3)
    ok = (faces[:, 0] != faces[:, 1]) & (faces[:, 1] != faces[:, 2]) & (faces[:, 0] != faces[:, 2])
    faces, Nl, Mi = faces[ok], Nt[ok].reshape(-1, 3), Mi[ok]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts.tolist(), [], faces.tolist())
    used = sorted(set(Mi.tolist()))
    for k in used:
        me.materials.append(mats[k])
    remap = {k: i for i, k in enumerate(used)}
    me.polygons.foreach_set('material_index', [remap[k] for k in Mi.tolist()])
    me.polygons.foreach_set('use_smooth', [True] * len(faces))
    me.update()
    Nl = Nl / (np.linalg.norm(Nl, axis=1, keepdims=True) + 1e-12)
    try:
        me.normals_split_custom_set(Nl.tolist())
    except Exception as e:                       # flat shading still looks right for boxes
        print('  custom normals unavailable:', e)
    return me


def look_at_matrix(pos, fwd, up_hint=(0, 0, 1)):
    f = np.array(fwd, float); f /= np.linalg.norm(f)
    r = np.cross(f, up_hint)
    if np.linalg.norm(r) < 1e-6:
        r = np.cross(f, (0, 1, 0))
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    M = np.eye(4)
    M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = r, u, -f, pos
    return M


def camera_matrix(c):
    y, p = math.radians(c['yaw']), math.radians(c['pitch'])
    d = (math.sin(y) * math.cos(p), math.cos(y) * math.cos(p), math.sin(p))
    return look_at_matrix(c['pos'], d)


def key_transform(obj, Ms, vis, nfr, insert_vis=True):
    """Keyframe obj only where it moves (and where its visibility flips)."""
    vis = np.asarray(vis, bool)
    if vis.any():
        idx = np.flatnonzero(vis)
        Ms = Ms.copy()
        Ms[:idx[0]] = Ms[idx[0]]                 # no jump from the hidden pose (keeps motion blur clean)
        Ms[idx[-1] + 1:] = Ms[idx[-1]]
    static = np.allclose(Ms, Ms[0], atol=1e-7)
    if static:
        obj.matrix_world = Matrix(Ms[0].tolist())
    else:
        q_prev = None
        for f in range(nfr):
            if f == 0 or f == nfr - 1 or not np.allclose(Ms[f], Ms[f - 1], atol=1e-7) or not np.allclose(Ms[f], Ms[f + 1], atol=1e-7):
                loc, rot, sca = Matrix(Ms[f].tolist()).decompose()
                if q_prev is not None and q_prev.dot(rot) < 0:
                    rot.negate()
                q_prev = rot.copy()
                obj.location, obj.rotation_quaternion, obj.scale = loc, rot, sca
                for path in ('location', 'rotation_quaternion', 'scale'):
                    obj.keyframe_insert(path, frame=f + 1)
    if insert_vis and not vis.all():
        for f in range(nfr):
            if f == 0 or vis[f] != vis[f - 1]:
                obj.hide_render = not bool(vis[f])
                obj.keyframe_insert('hide_render', frame=f + 1)


def light_params(rec):
    """roomkit light record -> (kind, matrix, size_x, size_y, power, color, radius)."""
    typ = int(rec[0])
    Lc = np.array(rec[10:13], float)
    k = float(Lc.max())
    color = tuple(Lc / k) if k > 0 else (1.0, 1.0, 1.0)
    if typ == 1:
        c, r = np.array(rec[1:4]), float(rec[4])
        return 'POINT', look_at_matrix(c, (0, 0, -1)), 0, 0, 4 * math.pi ** 2 * r * r * k, color, r
    c, eu, ev = np.array(rec[1:4]), np.array(rec[4:7]), np.array(rec[7:10])
    spot = float(rec[16])
    n = np.cross(eu, ev); n /= (np.linalg.norm(n) + 1e-12)
    a, b = np.linalg.norm(eu), np.linalg.norm(ev)
    center = c + (eu + ev) / 2
    if spot > 0:
        axis = np.array(rec[13:16], float)
        return 'SPOT', look_at_matrix(center, axis), 0, 0, 4 * math.pi * k * a * b, color, 0.03
    M = np.eye(4)
    M[:3, 0] = ev / (b + 1e-12); M[:3, 1] = eu / (a + 1e-12); M[:3, 2] = -n; M[:3, 3] = center
    return 'AREA', M, b, a, math.pi * a * b * k, color, 0


# ------------------------------------------------------------------------------------------- main
def main():
    argv = sys.argv[1:]
    project, outdir = os.path.abspath(argv[0]), os.path.abspath(argv[1])
    args = argv[2:]
    os.makedirs(outdir, exist_ok=True)
    W, H = (int(v) for v in opt(args, '--size', '720x1280').split('x'))
    samples = int(opt(args, '--samples', '64'))
    global NO_BEVEL
    NO_BEVEL = '--nobevel' in args
    if opt(args, '--fps'):
        P_fps_override[0] = int(opt(args, '--fps'))
    t_start = time.time()

    bpy.ops.wm.read_factory_settings(use_empty=True)
    P = load_project(project)
    P.build()
    rk = P.rk
    BL = getattr(P, 'BLENDER', {})
    tl = P.timeline()
    fps = P_fps_override[0] or P.FPS
    tl.fps = fps
    nfr = int(round(P.DUR * fps))
    print(f'project: {len(rk.ORDER)} pieces, {len(rk.MATS)} materials, {nfr} frames', flush=True)

    sc = bpy.context.scene
    sc.render.fps = fps
    sc.frame_start, sc.frame_end = 1, nfr
    bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'

    mats = Materials(rk, BL).mats
    sep_names = set(BL.get('separate', []))
    sep_ids = {rk.MATIDX[n] for n in sep_names if n in rk.MATIDX}

    # per-frame states
    states = [tl.state(f / fps) for f in range(nfr)]
    lrecs = [P.lights(m4, vis) for (m4, vis) in states]

    coll = sc.collection
    for name in rk.ORDER:
        parts = rk.INST[name]
        Pt = np.concatenate([q[0] for q in parts]); Nt = np.concatenate([q[1] for q in parts])
        Mi = np.concatenate([np.full(len(q[0]), q[2]) for q in parts])
        groups = [(name, ~np.isin(Mi, list(sep_ids)))] + [(f'{name}__{n}', Mi == rk.MATIDX[n]) for n in sep_names if n in rk.MATIDX]
        Ms = np.array([s[0][name] for s in states])
        vis = np.array([s[1][name] > 0 for s in states])
        for oname, sel in groups:
            if not sel.any():
                continue
            me = make_mesh(oname, Pt[sel], Nt[sel], Mi[sel], mats)
            obj = bpy.data.objects.new(oname, me)
            coll.objects.link(obj)
            obj.rotation_mode = 'QUATERNION'
            if oname != name:                    # separated emitter (window view): camera + reflections only
                obj.visible_diffuse = False; obj.visible_shadow = False
                obj.visible_transmission = False; obj.visible_volume_scatter = False
            key_transform(obj, Ms, vis, nfr)
    print(f'meshes + animation: {time.time() - t_start:.1f}s', flush=True)

    # camera
    cam = bpy.data.cameras.new('cam')
    cam.sensor_fit = 'VERTICAL'
    cam.angle_y = math.radians(P.camera(0).get('vfov', 85.0))
    cam.clip_start, cam.clip_end = 0.02, 80.0
    cobj = bpy.data.objects.new('cam', cam); coll.objects.link(cobj); sc.camera = cobj
    cobj.rotation_mode = 'QUATERNION'
    key_transform(cobj, np.array([camera_matrix(P.camera(f / fps)) for f in range(nfr)]), np.ones(nfr, bool), nfr, insert_vis=False)

    # lights (one Blender light per slot)
    fill = set(BL.get('fill_lights', []))
    for i in range(len(lrecs[0])):
        prm = [light_params(lr[i]) for lr in lrecs]
        kind = prm[0][0]
        ld = bpy.data.lights.new(f'light{i}', kind)
        lo = bpy.data.objects.new(f'light{i}', ld); coll.objects.link(lo)
        lo.rotation_mode = 'QUATERNION'
        lo.visible_camera = False
        if i in fill:
            lo.visible_glossy = False
        if kind == 'AREA':
            ld.shape = 'RECTANGLE'
        if kind == 'SPOT':
            ld.spot_size = math.radians(120); ld.spot_blend = 0.8
        if kind in ('SPOT', 'POINT'):
            ld.shadow_soft_size = prm[0][6]
        key_transform(lo, np.array([q[1] for q in prm]), np.ones(nfr, bool), nfr, insert_vis=False)
        last = None
        for f in range(nfr):
            vals = (round(prm[f][2], 5), round(prm[f][3], 5), round(prm[f][4], 4), prm[f][5])
            nxt = None if f == nfr - 1 else (round(prm[f + 1][2], 5), round(prm[f + 1][3], 5), round(prm[f + 1][4], 4), prm[f + 1][5])
            if vals != last or vals != nxt or f == nfr - 1:
                if kind == 'AREA':
                    ld.size, ld.size_y = max(vals[0], 1e-4), max(vals[1], 1e-4)
                    ld.keyframe_insert('size', frame=f + 1); ld.keyframe_insert('size_y', frame=f + 1)
                ld.energy = vals[2]; ld.color = vals[3]
                ld.keyframe_insert('energy', frame=f + 1); ld.keyframe_insert('color', frame=f + 1)
            last = vals
    sun = BL.get('sun')
    if sun:
        sd = bpy.data.lights.new('sun', 'SUN')
        sd.energy = sun['strength']; sd.color = sun['color']; sd.angle = math.radians(sun.get('angle', 1.0))
        so = bpy.data.objects.new('sun', sd); coll.objects.link(so)
        so.matrix_world = Matrix(look_at_matrix((0, 0, 0), sun['dir']).tolist())

    # world, render settings, colour
    world = bpy.data.worlds.new('world'); sc.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs['Color'].default_value = (0.05, 0.05, 0.05, 1); bg.inputs['Strength'].default_value = 1.0
    sc.render.engine = 'CYCLES'
    cy = sc.cycles
    cy.device = 'CPU'
    cy.samples = samples
    cy.use_adaptive_sampling = True; cy.adaptive_threshold = float(opt(args, '--adaptive', '0.02'))
    cy.use_denoising = True
    try:
        cy.denoiser = 'OPENIMAGEDENOISE'; cy.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    except Exception:
        pass
    mb, db, gb = (int(v) for v in opt(args, '--bounces', '6,3,3').split(','))
    cy.max_bounces = mb; cy.diffuse_bounces = db; cy.glossy_bounces = gb; cy.transmission_bounces = 4; cy.transparent_max_bounces = 8
    cy.sample_clamp_indirect = 6.0
    cy.caustics_reflective = False; cy.caustics_refractive = False; cy.blur_glossy = 1.0
    sc.render.use_persistent_data = True
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = W, H, 100
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.5
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_depth = '8'
    vs = sc.view_settings
    vs.view_transform = 'AgX'
    for lk in (BL.get('look', 'AgX - Medium High Contrast'), 'AgX - Medium High Contrast', 'Medium High Contrast', 'None'):
        try:
            vs.look = lk
            break
        except Exception:
            pass
    vs.exposure = BL.get('exposure', 0.0)
    print(f'scene ready: {time.time() - t_start:.1f}s (look {vs.look})', flush=True)
    if '--blend' in args:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(outdir, 'scene.blend'))

    tests = opt(args, '--test')
    if tests:
        paths = []
        for t in (float(v) for v in tests.split(',')):
            sc.frame_set(min(nfr, int(round(t * fps)) + 1))
            sc.render.filepath = os.path.join(outdir, f'test_{t:.2f}.png')
            t0 = time.time()
            bpy.ops.render.render(write_still=True)
            print(f'test {t:.2f}s rendered in {time.time() - t0:.1f}s', flush=True)
            paths.append(sc.render.filepath)
        try:
            import cv2
            ims = [cv2.imread(pth) for pth in paths]
            cv2.imwrite(os.path.join(outdir, 'test_sheet.jpg'), np.hstack(ims), [cv2.IMWRITE_JPEG_QUALITY, 90])
        except Exception as e:
            print('sheet skipped:', e)
        return
    fr = opt(args, '--frames')
    a, b = (int(v) for v in fr.split(':')) if fr else (1, nfr)
    fdir = os.path.join(outdir, 'frames')
    os.makedirs(fdir, exist_ok=True)
    # a frame whose pieces, camera and lights match its neighbours renders identically: copy it instead
    sigs = []
    for f in range(nfr):
        m4, vis = states[f]
        c = P.camera(f / fps)
        parts = [np.concatenate([m4[k].ravel(), [float(vis[k] > 0)]]) for k in rk.ORDER]
        parts += [np.array([*c['pos'], c['yaw'], c['pitch']], float)] + [np.asarray(L, float).ravel() for L in lrecs[f]]
        sigs.append(np.round(np.concatenate(parts), 6))
    dup = [2 <= i < nfr - 1 and all(np.array_equal(sigs[i], sigs[g]) for g in (i - 2, i - 1, i + 1)) for i in range(nfr)]
    todo = [f for f in range(a, b + 1) if not os.path.exists(os.path.join(fdir, f'f_{f:04d}.png'))]
    left = sum(1 for f in todo if not dup[f - 1])
    print(f'rendering {len(todo)} frames ({left} unique, the rest copied)', flush=True)
    t0, n_done = time.time(), 0
    for f in todo:
        path = os.path.join(fdir, f'f_{f:04d}.png')
        prev = os.path.join(fdir, f'f_{f - 1:04d}.png')
        if dup[f - 1] and os.path.exists(prev):
            shutil.copyfile(prev, path)
            continue
        sc.frame_set(f)
        sc.render.filepath = path
        tf = time.time()
        bpy.ops.render.render(write_still=True)
        n_done += 1; left -= 1
        avg = (time.time() - t0) / n_done
        print(f'frame {f}/{nfr} {time.time() - tf:.1f}s  avg {avg:.1f}s  eta {left * avg / 60:.0f} min', flush=True)
    print(f'done in {time.time() - t_start:.0f}s', flush=True)


if __name__ == '__main__':
    main()
