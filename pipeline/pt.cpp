// pt.cpp - small CPU path tracer for the room-build clip (triangles + BVH, NEE, GGX, G-buffers for denoising)
// usage: pt scene.bin frames.bin outprefix f0 f1 W H NAA NL
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <cstring>
#include <cstdint>
#include <vector>
#include <string>
#include <algorithm>
#include <omp.h>
#include <immintrin.h>

static const float PI = 3.14159265358979f;
static const float EPS = 2e-4f;

struct V3 {
  float x, y, z;
  V3() : x(0), y(0), z(0) {}
  V3(float a) : x(a), y(a), z(a) {}
  V3(float a, float b, float c) : x(a), y(b), z(c) {}
  float operator[](int i) const { return (&x)[i]; }
  float& operator[](int i) { return (&x)[i]; }
};
static inline V3 operator+(V3 a, V3 b) { return V3(a.x + b.x, a.y + b.y, a.z + b.z); }
static inline V3 operator-(V3 a, V3 b) { return V3(a.x - b.x, a.y - b.y, a.z - b.z); }
static inline V3 operator-(V3 a) { return V3(-a.x, -a.y, -a.z); }
static inline V3 operator*(V3 a, V3 b) { return V3(a.x * b.x, a.y * b.y, a.z * b.z); }
static inline V3 operator*(V3 a, float s) { return V3(a.x * s, a.y * s, a.z * s); }
static inline V3 operator*(float s, V3 a) { return V3(a.x * s, a.y * s, a.z * s); }
static inline V3 operator/(V3 a, float s) { float i = 1.0f / s; return V3(a.x * i, a.y * i, a.z * i); }
static inline V3& operator+=(V3& a, V3 b) { a.x += b.x; a.y += b.y; a.z += b.z; return a; }
static inline float dot(V3 a, V3 b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
static inline V3 cross(V3 a, V3 b) { return V3(a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x); }
static inline float len(V3 a) { return sqrtf(dot(a, a)); }
static inline V3 norm(V3 a) { float l = len(a); return l > 0 ? a / l : V3(0, 0, 1); }
static inline float lum(V3 a) { return 0.2126f * a.x + 0.7152f * a.y + 0.0722f * a.z; }
static inline float clampf(float v, float a, float b) { return v < a ? a : (v > b ? b : v); }

static inline uint32_t pcg_hash(uint32_t v) {
  uint32_t s = v * 747796405u + 2891336453u;
  uint32_t w = ((s >> ((s >> 28u) + 4u)) ^ s) * 277803737u;
  return (w >> 22u) ^ w;
}
struct RNG {
  uint32_t s;
  inline float next() { s = pcg_hash(s); return (s >> 8) * (1.0f / 16777216.0f); }
};
static inline float hashf(int x, int y, int z) {
  uint32_t h = (uint32_t)x * 73856093u ^ (uint32_t)y * 19349663u ^ (uint32_t)z * 83492791u;
  h = pcg_hash(h);
  return (h >> 8) * (1.0f / 16777216.0f);
}
static inline float vnoise(V3 p) {
  float fx = floorf(p.x), fy = floorf(p.y), fz = floorf(p.z);
  int ix = (int)fx, iy = (int)fy, iz = (int)fz;
  float tx = p.x - fx, ty = p.y - fy, tz = p.z - fz;
  tx = tx * tx * (3 - 2 * tx); ty = ty * ty * (3 - 2 * ty); tz = tz * tz * (3 - 2 * tz);
  float c000 = hashf(ix, iy, iz), c100 = hashf(ix + 1, iy, iz), c010 = hashf(ix, iy + 1, iz), c110 = hashf(ix + 1, iy + 1, iz);
  float c001 = hashf(ix, iy, iz + 1), c101 = hashf(ix + 1, iy, iz + 1), c011 = hashf(ix, iy + 1, iz + 1), c111 = hashf(ix + 1, iy + 1, iz + 1);
  float a = c000 + (c100 - c000) * tx, b = c010 + (c110 - c010) * tx, c = c001 + (c101 - c001) * tx, d = c011 + (c111 - c011) * tx;
  float e = a + (b - a) * ty, f = c + (d - c) * ty;
  return e + (f - e) * tz;
}
static inline float fbm(V3 p, int oct) {
  float a = 0.5f, s = 0, n = 0;
  for (int i = 0; i < oct; i++) { s += a * vnoise(p); n += a; p = p * 2.03f; a *= 0.5f; }
  return s / n;
}

// ------------------------------------------------------------------------------------------------ scene
struct SrcTri { float p[9]; float n[9]; int mat; };
struct Inst { std::vector<SrcTri> tris; };
struct Tri { V3 v0, e1, e2; V3 n0, n1, n2; int inst; int mat; };
struct Light { int type; int always; V3 c, eu, ev, L, axis, n; float spotExp, area, radius; };
struct Node { float bmin[3]; int leftFirst; float bmax[3]; int count; };

static const int MATF = 24;
static std::vector<float> mats;
static std::vector<Inst> insts;
static std::vector<Tri> tris;
static std::vector<float> minv;   // per instance 12 floats (inverse affine)
static std::vector<Light> lights;
static std::vector<Node> nodes;
static std::vector<int> tidx;
static std::vector<float> tbb;    // per tri: min xyz, max xyz, centroid xyz

static void buildBVH() {
  int n = (int)tris.size();
  tidx.resize(n); tbb.resize((size_t)n * 9);
  for (int i = 0; i < n; i++) {
    tidx[i] = i;
    V3 a = tris[i].v0, b = a + tris[i].e1, c = a + tris[i].e2;
    for (int k = 0; k < 3; k++) {
      float mn = std::min(a[k], std::min(b[k], c[k])), mx = std::max(a[k], std::max(b[k], c[k]));
      tbb[(size_t)i * 9 + k] = mn; tbb[(size_t)i * 9 + 3 + k] = mx; tbb[(size_t)i * 9 + 6 + k] = (mn + mx) * 0.5f;
    }
  }
  nodes.clear(); nodes.reserve((size_t)n * 2 + 8);
  Node root; root.leftFirst = 0; root.count = n; nodes.push_back(root);
  std::vector<int> stack; stack.push_back(0);
  while (!stack.empty()) {
    int ni = stack.back(); stack.pop_back();
    int first = nodes[ni].leftFirst, cnt = nodes[ni].count;
    float bmin[3] = {1e30f, 1e30f, 1e30f}, bmax[3] = {-1e30f, -1e30f, -1e30f}, cmin[3] = {1e30f, 1e30f, 1e30f}, cmax[3] = {-1e30f, -1e30f, -1e30f};
    for (int i = first; i < first + cnt; i++) {
      const float* b = &tbb[(size_t)tidx[i] * 9];
      for (int k = 0; k < 3; k++) {
        bmin[k] = std::min(bmin[k], b[k]); bmax[k] = std::max(bmax[k], b[3 + k]);
        cmin[k] = std::min(cmin[k], b[6 + k]); cmax[k] = std::max(cmax[k], b[6 + k]);
      }
    }
    for (int k = 0; k < 3; k++) { nodes[ni].bmin[k] = bmin[k]; nodes[ni].bmax[k] = bmax[k]; }
    if (cnt <= 3) continue;
    const int NB = 12;
    float bestCost = 1e30f; int bestAxis = -1, bestBin = 0;
    for (int ax = 0; ax < 3; ax++) {
      float ext = cmax[ax] - cmin[ax];
      if (ext < 1e-7f) continue;
      float bmn[NB][3], bmx[NB][3]; int bc[NB];
      for (int b = 0; b < NB; b++) { bc[b] = 0; for (int k = 0; k < 3; k++) { bmn[b][k] = 1e30f; bmx[b][k] = -1e30f; } }
      float sc = NB / ext;
      for (int i = first; i < first + cnt; i++) {
        const float* b = &tbb[(size_t)tidx[i] * 9];
        int bi = std::min(NB - 1, (int)((b[6 + ax] - cmin[ax]) * sc));
        bc[bi]++;
        for (int k = 0; k < 3; k++) { bmn[bi][k] = std::min(bmn[bi][k], b[k]); bmx[bi][k] = std::max(bmx[bi][k], b[3 + k]); }
      }
      float la[NB], ra[NB]; int lc[NB], rc[NB];
      float mn[3] = {1e30f, 1e30f, 1e30f}, mx[3] = {-1e30f, -1e30f, -1e30f}; int c = 0;
      for (int b = 0; b < NB - 1; b++) {
        c += bc[b];
        for (int k = 0; k < 3; k++) { mn[k] = std::min(mn[k], bmn[b][k]); mx[k] = std::max(mx[k], bmx[b][k]); }
        float dx = mx[0] - mn[0], dy = mx[1] - mn[1], dz = mx[2] - mn[2];
        la[b] = c ? (dx * dy + dy * dz + dz * dx) : 0; lc[b] = c;
      }
      for (int k = 0; k < 3; k++) { mn[k] = 1e30f; mx[k] = -1e30f; } c = 0;
      for (int b = NB - 1; b > 0; b--) {
        c += bc[b];
        for (int k = 0; k < 3; k++) { mn[k] = std::min(mn[k], bmn[b][k]); mx[k] = std::max(mx[k], bmx[b][k]); }
        float dx = mx[0] - mn[0], dy = mx[1] - mn[1], dz = mx[2] - mn[2];
        ra[b - 1] = c ? (dx * dy + dy * dz + dz * dx) : 0; rc[b - 1] = c;
      }
      for (int b = 0; b < NB - 1; b++) {
        if (lc[b] == 0 || rc[b] == 0) continue;
        float cost = la[b] * lc[b] + ra[b] * rc[b];
        if (cost < bestCost) { bestCost = cost; bestAxis = ax; bestBin = b; }
      }
    }
    if (bestAxis < 0) continue;
    float dx = bmax[0] - bmin[0], dy = bmax[1] - bmin[1], dz = bmax[2] - bmin[2];
    float parentCost = (dx * dy + dy * dz + dz * dx) * cnt;
    if (bestCost >= parentCost && cnt <= 8) continue;
    float sc = NB / (cmax[bestAxis] - cmin[bestAxis]);
    int i = first, j = first + cnt - 1;
    while (i <= j) {
      int bi = std::min(NB - 1, (int)((tbb[(size_t)tidx[i] * 9 + 6 + bestAxis] - cmin[bestAxis]) * sc));
      if (bi <= bestBin) i++; else { std::swap(tidx[i], tidx[j]); j--; }
    }
    int lcnt = i - first;
    if (lcnt == 0 || lcnt == cnt) continue;
    int li = (int)nodes.size();
    Node a, b; a.leftFirst = first; a.count = lcnt; b.leftFirst = i; b.count = cnt - lcnt;
    nodes.push_back(a); nodes.push_back(b);
    nodes[ni].leftFirst = li; nodes[ni].count = 0;
    stack.push_back(li); stack.push_back(li + 1);
  }
}

struct Hit { float t, u, v; int tri; };

static inline bool triHit(const Tri& t, const V3& o, const V3& d, float& tt, float& uu, float& vv) {
  V3 p = cross(d, t.e2);
  float det = dot(t.e1, p);
  if (fabsf(det) < 1e-14f) return false;
  float inv = 1.0f / det;
  V3 s = o - t.v0;
  float u = dot(s, p) * inv;
  if (u < 0 || u > 1) return false;
  V3 q = cross(s, t.e1);
  float v = dot(d, q) * inv;
  if (v < 0 || u + v > 1) return false;
  float x = dot(t.e2, q) * inv;
  if (x > 1e-5f && x < tt) { tt = x; uu = u; vv = v; return true; }
  return false;
}
static inline bool slab(const Node& n, const V3& o, const V3& inv, float tmax, float& tn) {
  float t1 = (n.bmin[0] - o.x) * inv.x, t2 = (n.bmax[0] - o.x) * inv.x;
  float tmin = std::min(t1, t2), tmx = std::max(t1, t2);
  t1 = (n.bmin[1] - o.y) * inv.y; t2 = (n.bmax[1] - o.y) * inv.y;
  tmin = std::max(tmin, std::min(t1, t2)); tmx = std::min(tmx, std::max(t1, t2));
  t1 = (n.bmin[2] - o.z) * inv.z; t2 = (n.bmax[2] - o.z) * inv.z;
  tmin = std::max(tmin, std::min(t1, t2)); tmx = std::min(tmx, std::max(t1, t2));
  tn = tmin;
  return tmx >= std::max(tmin, 0.0f) && tmin < tmax;
}
static bool intersect(const V3& o, const V3& d, Hit& h) {
  V3 inv(1.0f / d.x, 1.0f / d.y, 1.0f / d.z);
  int stack[64], sp = 0, ni = 0;
  h.t = 1e30f; h.tri = -1;
  float tn;
  if (!slab(nodes[0], o, inv, h.t, tn)) return false;
  while (true) {
    const Node& n = nodes[ni];
    if (n.count > 0) {
      for (int i = n.leftFirst; i < n.leftFirst + n.count; i++) {
        int ti = tidx[i];
        if (triHit(tris[ti], o, d, h.t, h.u, h.v)) h.tri = ti;
      }
      if (sp == 0) break;
      ni = stack[--sp];
    } else {
      int a = n.leftFirst, b = a + 1;
      float ta, tb;
      bool ha = slab(nodes[a], o, inv, h.t, ta), hb = slab(nodes[b], o, inv, h.t, tb);
      if (ha && hb) { if (ta > tb) std::swap(a, b); stack[sp++] = b; ni = a; }
      else if (ha) ni = a;
      else if (hb) ni = b;
      else { if (sp == 0) break; ni = stack[--sp]; }
    }
  }
  return h.tri >= 0;
}
static bool occluded(const V3& o, const V3& d, float tmax) {
  V3 inv(1.0f / d.x, 1.0f / d.y, 1.0f / d.z);
  int stack[64], sp = 0, ni = 0;
  float tn, u, v;
  if (!slab(nodes[0], o, inv, tmax, tn)) return false;
  while (true) {
    const Node& n = nodes[ni];
    if (n.count > 0) {
      for (int i = n.leftFirst; i < n.leftFirst + n.count; i++) {
        float tt = tmax;
        if (triHit(tris[tidx[i]], o, d, tt, u, v)) return true;
      }
      if (sp == 0) break;
      ni = stack[--sp];
    } else {
      int a = n.leftFirst, b = a + 1;
      float ta, tb;
      bool ha = slab(nodes[a], o, inv, tmax, ta), hb = slab(nodes[b], o, inv, tmax, tb);
      if (ha && hb) { stack[sp++] = b; ni = a; }
      else if (ha) ni = a;
      else if (hb) ni = b;
      else { if (sp == 0) break; ni = stack[--sp]; }
    }
  }
  return false;
}

// ------------------------------------------------------------------------------------------------ materials
struct Surf { V3 P, Ng, N, alb, emis; float rough, f0; bool metal, glossy; int inst; };

static void evalMat(const float* m, const V3& po, V3& alb, V3& emis, float& rough) {
  int tex = (int)m[0];
  V3 c(m[1], m[2], m[3]), c2(m[4], m[5], m[6]);
  emis = V3(m[10], m[11], m[12]);
  rough = m[7];
  switch (tex) {
    default: alb = c; break;
    case 1: {  // floor planks along y
      float pw = m[13], pl = m[14];
      float fx = po.x / pw; int ix = (int)floorf(fx); float rx = fx - ix;
      float off = hashf(ix, 7, 1) * pl;
      float fy = (po.y + off) / pl; int iy = (int)floorf(fy); float ry = fy - iy;
      float tone = hashf(ix, iy, 3), tone2 = hashf(ix, iy, 11);
      float g = fbm(V3(po.x * 42.f + tone * 50.f, po.y * 2.4f + tone2 * 20.f, tone * 9.f), 4);
      float g2 = vnoise(V3(po.x * 190.f, po.y * 11.f, tone * 10.f));
      float k = 0.74f + 0.40f * tone + 0.30f * (g - 0.5f) + 0.10f * (g2 - 0.5f);
      V3 base = c * (1 - tone2 * 0.5f) + c2 * (tone2 * 0.5f);
      alb = base * k;
      float gap = std::min(std::min(rx, 1 - rx) * pw, std::min(ry, 1 - ry) * pl);
      if (gap < 0.0016f) alb = alb * (0.40f + 0.60f * gap / 0.0016f);
      rough = clampf(m[7] + 0.16f * (g - 0.5f), 0.08f, 1.0f);
    } break;
    case 2: {  // wood board, grain along axis
      int ax = (int)m[13]; float seed = m[14];
      float along = po[ax], a1 = po[(ax + 1) % 3], a2 = po[(ax + 2) % 3];
      float g = fbm(V3(a1 * 48.f + seed * 17.f, a2 * 48.f + seed * 31.f, along * 2.6f), 4);
      float g2 = vnoise(V3(a1 * 230.f, a2 * 230.f, along * 9.f + seed));
      alb = c * (0.90f + 0.24f * (g - 0.5f) + 0.07f * (g2 - 0.5f));
    } break;
    case 3: {  // wallpaper speckle
      float a = m[13];
      float n1 = vnoise(po * 380.f), n2 = fbm(po * 9.f, 3);
      alb = c * (1 + a * (n1 - 0.5f) * 2 + 0.05f * (n2 - 0.5f) * 2);
    } break;
    case 4: {  // roman blind: horizontal folds, weave
      float period = m[13];
      float fz = po.z / period; float rz = fz - floorf(fz);
      float fold = (rz < 0.10f) ? 0.66f + 0.34f * (rz / 0.10f) : 1.0f - 0.10f * rz;
      float w = vnoise(V3(po.x * 520.f, po.z * 520.f, 0));
      float w2 = fbm(V3(po.x * 6.f, po.z * 30.f, 3.f), 2);
      float k = fold * (0.92f + 0.12f * w + 0.08f * (w2 - 0.5f));
      alb = c * k; emis = emis * k;
    } break;
    case 5: {  // knit ribs
      int ax = (int)m[13]; float per = m[14];
      float f = po[ax] / per; float r = f - floorf(f);
      float rib = 0.78f + 0.22f * sinf(r * PI);
      float n = vnoise(po * 330.f);
      alb = c * (rib * (0.90f + 0.18f * n));
    } break;
    case 6: {  // boucle
      float n = vnoise(po * 210.f), n2 = vnoise(po * 80.f + V3(7, 3, 1));
      alb = c * (0.78f + 0.24f * n + 0.10f * n2);
    } break;
    case 7: {  // stripes
      int ax = (int)m[13]; float per = m[14];
      float f = po[ax] / per; float r = f - floorf(f);
      alb = (r < 0.5f) ? c : c2;
      alb = alb * (0.90f + 0.18f * vnoise(po * 300.f));
    } break;
    case 8: {  // monitor screen (emissive, own design)
      float u = (po.x - m[13]) / m[14], v = (po.z - m[15]) / m[16];
      V3 bg = V3(0.05f, 0.03f, 0.16f) * (1 - v) + V3(0.16f, 0.05f, 0.30f) * v;
      float d1 = (u - 0.66f) * (u - 0.66f) * 3.0f + (v - 0.56f) * (v - 0.56f);
      float d2 = (u - 0.28f) * (u - 0.28f) * 3.0f + (v - 0.40f) * (v - 0.40f);
      V3 col = bg + V3(1.0f, 0.35f, 0.85f) * expf(-d1 / 0.035f) + V3(0.25f, 0.55f, 1.0f) * 0.8f * expf(-d2 / 0.05f);
      if (v < 0.07f) col = col * 0.5f + V3(0.10f, 0.10f, 0.14f);
      alb = V3(0.01f);
      emis = col * m[10];
    } break;
    case 9: {  // window backdrop: hazy sky, skyline, trees (p: horizon height, horizontal axis 0 = x / 1 = y)
      float x = m[14] > 0.5f ? po.y : po.x, z = po.z, hz = m[13];
      float t = clampf((z - hz) / 2.2f, 0.f, 1.f);
      V3 sky = V3(1.0f, 1.0f, 1.0f) * (1 - t) + V3(0.66f, 0.78f, 1.0f) * t;
      V3 col = sky;
      float bw = 0.11f; int bi = (int)floorf(x / bw);
      float bh = 0.06f + 0.34f * powf(hashf(bi, 5, 2), 2.2f) + 0.10f * vnoise(V3(x * 0.8f, 1.f, 2.f));
      if (z < hz + bh) col = V3(0.58f, 0.65f, 0.76f) * 0.9f + sky * 0.1f;
      int bi2 = (int)floorf((x + 0.05f) / 0.19f);
      float bh2 = 0.02f + 0.20f * hashf(bi2, 9, 4);
      if (z < hz + bh2) col = V3(0.44f, 0.51f, 0.62f) * 0.92f + sky * 0.08f;
      float th = hz - 0.02f + 0.30f * fbm(V3(x * 2.3f, 3.f, 1.f), 3) + 0.05f * vnoise(V3(x * 22.f, 0.f, 5.f));
      if (z < th) { float s = 0.75f + 0.5f * vnoise(V3(x * 30.f, z * 30.f, 2.f)); col = V3(0.20f, 0.29f, 0.21f) * s * 0.9f + sky * 0.1f; }
      alb = V3(0.0f);
      emis = col * m[10];
    } break;
    case 10: {  // keyboard keys grid on top
      float fx = po.x / m[13], fy = po.y / m[13];
      float rx = fx - floorf(fx), ry = fy - floorf(fy);
      float k = (rx < 0.12f || ry < 0.12f) ? 0.35f : 1.0f;
      alb = c * k;
    } break;
    case 16: {  // night backdrop: deep blue sky, dark skyline with lit windows (p: horizon height, horizontal axis)
      float x = m[14] > 0.5f ? po.y : po.x, z = po.z, hz = m[13];
      float t = clampf((z - hz) / 2.5f, 0.f, 1.f);
      V3 sky = V3(0.10f, 0.12f, 0.24f) * (1 - t) + V3(0.025f, 0.035f, 0.09f) * t;
      sky = sky + V3(0.20f, 0.11f, 0.05f) * expf(-fmaxf(z - hz, 0.f) / 0.35f) * 0.6f;
      V3 col = sky;
      float bw = 0.16f; int bi = (int)floorf(x / bw);
      float bh = 0.10f + 0.55f * powf(hashf(bi, 3, 7), 1.8f) + 0.08f * vnoise(V3(x * 0.6f, 4.f, 1.f));
      if (z < hz + bh) {
        col = V3(0.012f, 0.014f, 0.024f);
        float wx = x / 0.022f, wz = (z - hz) / 0.03f;
        int ix = (int)floorf(wx), iz = (int)floorf(wz);
        float rx = wx - ix, rz = wz - iz;
        if (rx > 0.25f && rx < 0.75f && rz > 0.3f && rz < 0.75f && hashf(ix, iz, bi) > 0.72f)
          col = V3(1.0f, 0.72f, 0.38f) * (0.6f + 0.6f * hashf(ix, iz, 5));
      }
      int bi2 = (int)floorf((x + 0.07f) / 0.26f);
      float bh2 = 0.03f + 0.22f * hashf(bi2, 11, 2);
      if (z < hz + bh2) col = V3(0.006f, 0.007f, 0.012f);
      alb = V3(0.0f);
      emis = col * m[10];
    } break;
    case 11: {  // marble: col base, col2 bold flowing veins (p: scale, vein width, seed, vein strength)
      float sc = m[13], vw = m[14], seed = m[15], vd = m[16];
      V3 q = po * sc + V3(seed * 3.1f, seed * 1.7f, seed * 2.3f);
      float w1 = fbm(q * 0.8f, 5), w2 = fbm(q * 2.4f + V3(5.2f, 1.3f, 2.8f), 4);
      float t = q.x * 0.6f + q.y * 0.55f + q.z * 0.8f + 2.8f * w1 + 0.7f * w2;
      float v = fabsf(sinf(t * 1.7f));
      float thick = vw * (0.25f + 1.0f * fbm(q * 0.45f + V3(11.f, 3.f, 6.f), 3));
      float ev = clampf(1.0f - v / thick, 0.f, 1.f);
      float vein = clampf(ev * ev * (3 - 2 * ev) * 1.5f, 0.f, 1.f);
      float t2 = (q.y * 0.9f - q.x * 0.4f - q.z * 0.5f) * 1.3f + 2.2f * fbm(q * 1.5f + V3(9.1f, 4.4f, 7.7f), 4);
      float v2 = fabsf(sinf(t2 * 2.6f));
      float vein2 = powf(clampf(1.0f - v2 / (vw * 0.22f), 0.f, 1.f), 1.2f) * 0.55f;
      float cloud = fbm(q * 0.7f + V3(2.f, 8.f, 1.f), 3);
      V3 base = c * (0.95f + 0.07f * (cloud - 0.5f));
      float k = clampf(std::max(vein, vein2) * vd, 0.f, 1.f);
      alb = base * (1 - k) + c2 * k;
    } break;
    case 12: {  // tiles with grout: col tile, col2 grout (p: tile u, tile v, grout width, plane normal axis 0/1/2, row offset)
      float tu = m[13], tv = m[14], gw = m[15]; int ax = (int)m[16]; float roff = m[17];
      float u, v;
      if (ax == 0) { u = po.y; v = po.z; } else if (ax == 1) { u = po.x; v = po.z; } else { u = po.x; v = po.y; }
      float fv = v / tv; int iv = (int)floorf(fv); float rv = fv - iv;
      float fu = u / tu + roff * (float)(iv & 1); int iu = (int)floorf(fu); float ru = fu - iu;
      float tone = hashf(iu, iv, 21);
      alb = c * (0.975f + 0.04f * tone + 0.02f * (vnoise(po * 140.f) - 0.5f));
      float dg = std::min(std::min(ru, 1 - ru) * tu, std::min(rv, 1 - rv) * tv);
      if (dg < gw * 0.5f) alb = c2;
      else if (dg < gw * 0.5f + 0.003f) alb = alb * (0.92f + 0.08f * (dg - gw * 0.5f) / 0.003f);
    } break;
    case 13: {  // cement floor tile: col base, col2 / col3 four-petal flowers at tile corners, col3 diamonds at edge midpoints
      // p: tile size, flower radius, grout width, diamond half-diagonal
      float ts = m[13], fr = m[14], gw = m[15], dm = m[16];
      V3 c3(m[20], m[21], m[22]);
      float fx = po.x / ts, fy = po.y / ts;
      float ix = floorf(fx), iy = floorf(fy);
      float rx = fx - ix, ry = fy - iy;
      float tone = hashf((int)ix, (int)iy, 31);
      alb = c * (0.975f + 0.035f * tone + 0.03f * (fbm(po * 25.f, 2) - 0.5f));
      float gx = std::min(rx, 1 - rx) * ts, gy = std::min(ry, 1 - ry) * ts;
      if (std::min(gx, gy) < gw * 0.5f) alb = c * 0.84f;
      float cxn = floorf(fx + 0.5f), cyn = floorf(fy + 0.5f);
      float dx = po.x - cxn * ts, dy = po.y - cyn * ts;
      float r = sqrtf(dx * dx + dy * dy), th = atan2f(dy, dx);
      float pet = fabsf(cosf(2.0f * th));
      float rr = fr * (0.20f + 0.80f * powf(pet, 0.6f));
      bool a = ((((int)cxn) + ((int)cyn)) & 1) == 0;
      if (r < rr) {
        alb = (a ? c2 : c3) * (0.92f + 0.12f * vnoise(po * 160.f));
        if (r < fr * 0.15f) alb = alb * 0.78f;
      }
      float d1 = fabsf(po.x - (ix + 0.5f) * ts) + fabsf(po.y - cyn * ts);
      float d2 = fabsf(po.x - cxn * ts) + fabsf(po.y - (iy + 0.5f) * ts);
      if (std::min(d1, d2) < dm) alb = c3 * (0.95f + 0.1f * vnoise(po * 160.f));
    } break;
    case 14: {  // brushed metal (p: brushing axis)
      int ax = (int)m[13];
      float along = po[ax], a1 = po[(ax + 1) % 3], a2 = po[(ax + 2) % 3];
      float n = vnoise(V3(a1 * 900.f, a2 * 900.f, along * 6.f));
      alb = c * (0.92f + 0.10f * n);
    } break;
    case 15: {  // quartz: col base with sparse col2 flecks (p: fleck scale, fleck threshold)
      float sc = m[13], thr = m[14];
      float n = vnoise(po * sc), n2 = vnoise(po * (sc * 0.37f) + V3(3, 7, 1));
      alb = c * (0.92f + 0.16f * fbm(po * 30.f, 2));
      float k = clampf((n * 0.7f + n2 * 0.3f - thr) / (1 - thr), 0.f, 1.f);
      alb = alb * (1 - k) + c2 * k;
    } break;
  }
}

static inline void shade(const Hit& h, const V3& o, const V3& d, Surf& s) {
  const Tri& t = tris[h.tri];
  s.P = o + d * h.t;
  V3 ng = norm(cross(t.e1, t.e2));
  V3 ns = norm(t.n0 * (1 - h.u - h.v) + t.n1 * h.u + t.n2 * h.v);
  if (dot(ng, ns) < 0) ng = -ng;
  if (dot(ng, d) > 0) { ng = -ng; ns = -ns; }
  s.Ng = ng; s.N = ns; s.inst = t.inst;
  const float* mi = &minv[(size_t)t.inst * 12];
  V3 po(mi[0] * s.P.x + mi[1] * s.P.y + mi[2] * s.P.z + mi[3], mi[4] * s.P.x + mi[5] * s.P.y + mi[6] * s.P.z + mi[7],
        mi[8] * s.P.x + mi[9] * s.P.y + mi[10] * s.P.z + mi[11]);
  const float* m = &mats[(size_t)t.mat * MATF];
  evalMat(m, po, s.alb, s.emis, s.rough);
  s.f0 = m[8]; s.metal = m[9] > 0.5f; s.glossy = ((int)m[19] & 1) != 0;
}

// ------------------------------------------------------------------------------------------------ lights
static inline void basis(const V3& n, V3& t, V3& b) {
  if (fabsf(n.z) < 0.999f) t = norm(cross(V3(0, 0, 1), n)); else t = V3(1, 0, 0);
  b = cross(n, t);
}
static V3 sampleLight(const Light& l, const V3& P, const V3& Ng, const V3& N, RNG& g) {
  if (l.type == 0) {
    float a = g.next(), b = g.next();
    V3 x = l.c + l.eu * a + l.ev * b;
    V3 w = x - P; float d2 = dot(w, w); float d = sqrtf(d2); w = w / d;
    float cs = dot(N, w); if (cs <= 0 || dot(Ng, w) <= 0) return V3(0);
    float cl = -dot(l.n, w); if (cl <= 0) return V3(0);
    float prof = 1;
    if (l.spotExp > 0) { float ca = -dot(l.axis, w); if (ca <= 0) return V3(0); prof = powf(ca, l.spotExp); }
    if (occluded(P + Ng * EPS, w, d - 2 * EPS)) return V3(0);
    return l.L * (prof * cs * cl * l.area / (std::max(d2, 1e-4f) * PI));
  } else {
    V3 wc = l.c - P; float dc2 = dot(wc, wc);
    float r2 = l.radius * l.radius;
    if (dc2 <= r2 * 1.02f) return V3(0);
    float dc = sqrtf(dc2); wc = wc / dc;
    float cosmax = sqrtf(std::max(0.0f, 1 - r2 / dc2));
    float u1 = g.next(), u2 = g.next();
    float ct = 1 - u1 * (1 - cosmax), st = sqrtf(std::max(0.0f, 1 - ct * ct)), ph = 2 * PI * u2;
    V3 t, b; basis(wc, t, b);
    V3 w = norm(t * (st * cosf(ph)) + b * (st * sinf(ph)) + wc * ct);
    float cs = dot(N, w); if (cs <= 0 || dot(Ng, w) <= 0) return V3(0);
    float disc = r2 - dc2 * st * st;
    float d = dc * ct - sqrtf(std::max(0.0f, disc));
    if (occluded(P + Ng * EPS, w, d - 2 * EPS)) return V3(0);
    float pdf = 1.0f / (2 * PI * (1 - cosmax));
    return l.L * (cs / (pdf * PI));
  }
}
static V3 direct(const V3& P, const V3& Ng, const V3& N, RNG& g) {
  V3 sum(0);
  float w[32]; float wsum = 0; int nl = (int)lights.size();
  for (int i = 0; i < nl; i++) {
    const Light& l = lights[i];
    w[i] = 0;
    if (l.always) { sum += sampleLight(l, P, Ng, N, g); continue; }
    V3 c = l.type == 0 ? l.c + (l.eu + l.ev) * 0.5f : l.c;
    V3 v = c - P; float d2 = dot(v, v); float d = sqrtf(d2); V3 dir = v / d;
    if (dot(N, dir) < -0.3f) continue;
    float prof = 1;
    if (l.type == 0) {
      float cl = -dot(l.n, dir); if (cl <= 0.0f) continue;
      if (l.spotExp > 0) { float ca = -dot(l.axis, dir); if (ca <= 0) continue; prof = powf(ca, l.spotExp); }
      prof *= cl;
    }
    w[i] = lum(l.L) * l.area * prof / std::max(d2, l.area) + 1e-6f;
    wsum += w[i];
  }
  if (wsum > 0) {
    float r = g.next() * wsum; int pick = -1;
    for (int i = 0; i < nl; i++) { if (w[i] <= 0) continue; pick = i; if (r < w[i]) break; r -= w[i]; }
    if (pick >= 0) sum += sampleLight(lights[pick], P, Ng, N, g) * (wsum / w[pick]);
  }
  return sum;
}

// ------------------------------------------------------------------------------------------------ BSDF helpers
static inline V3 cosSample(const V3& n, RNG& g) {
  float u1 = g.next(), u2 = g.next();
  float r = sqrtf(u1), ph = 2 * PI * u2;
  V3 t, b; basis(n, t, b);
  return norm(t * (r * cosf(ph)) + b * (r * sinf(ph)) + n * sqrtf(std::max(0.0f, 1 - u1)));
}
static inline float G1(float nx, float a2) { return 2 * nx / (nx + sqrtf(a2 + (1 - a2) * nx * nx)); }
// sample GGX reflection; returns false if below the surface. weight = BRDF*cos/pdf
static inline bool ggxSample(const Surf& s, const V3& wo, RNG& g, V3& wi, V3& weight) {
  float a = std::max(0.02f, s.rough * s.rough), a2 = a * a;
  float u1 = g.next(), u2 = g.next();
  float ct = sqrtf((1 - u1) / (1 + (a2 - 1) * u1)), st = sqrtf(std::max(0.0f, 1 - ct * ct)), ph = 2 * PI * u2;
  V3 t, b; basis(s.N, t, b);
  V3 h = norm(t * (st * cosf(ph)) + b * (st * sinf(ph)) + s.N * ct);
  float voh = dot(wo, h); if (voh <= 0) return false;
  wi = h * (2 * voh) - wo;
  float nol = dot(s.N, wi), nov = std::max(1e-4f, dot(s.N, wo));
  if (nol <= 0 || dot(s.Ng, wi) <= 0) return false;
  float f5 = powf(1 - voh, 5);
  V3 F = s.metal ? s.alb + (V3(1) - s.alb) * f5 : V3(s.f0 + (1 - s.f0) * f5);
  float G = G1(nol, a2) * G1(nov, a2);
  weight = F * (G * voh / (nov * std::max(1e-4f, ct)));
  return true;
}

static int MAXD = 4;
static float AMB = 0.10f;

// radiance arriving along a ray
static V3 Li(V3 o, V3 d, RNG& g, bool countEmis, int depth) {
  V3 L(0), T(1);
  for (;; depth++) {
    Hit h;
    if (!intersect(o, d, h)) break;
    Surf s; shade(h, o, d, s);
    if (countEmis) L += T * s.emis;
    if (depth >= MAXD) { L += T * s.alb * AMB; break; }
    V3 wo = -d;
    float nov = std::max(1e-4f, dot(s.N, wo));
    float F = 0, pS = 0;
    if (s.metal) pS = 1;
    else if (s.f0 > 0) { F = s.f0 + (1 - s.f0) * powf(1 - nov, 5); pS = clampf(F * 2.0f, 0.10f, 0.6f); }
    V3 wi;
    if (pS > 0 && g.next() < pS) {
      V3 wgt;
      if (!ggxSample(s, wo, g, wi, wgt)) break;
      T = T * wgt * (1.0f / pS);
      countEmis = true;
    } else {
      V3 kd = s.alb * ((1 - F) / (1 - pS));
      L += T * kd * direct(s.P, s.Ng, s.N, g);
      wi = cosSample(s.N, g);
      if (dot(wi, s.Ng) <= 0) break;
      T = T * kd;
      countEmis = false;
    }
    if (depth >= 2) {
      float q = std::min(0.95f, std::max(T.x, std::max(T.y, T.z)));
      if (q <= 0 || g.next() > q) break;
      T = T / q;
    }
    o = s.P + s.Ng * EPS; d = wi;
  }
  return L;
}
static inline V3 clampLum(V3 c, float mx) {
  if (!(c.x == c.x) || !(c.y == c.y) || !(c.z == c.z)) return V3(0);
  float l = lum(c);
  return l > mx ? c * (mx / l) : c;
}
static inline uint16_t f2h(float f) {
  if (!(f == f)) f = 0;
  f = clampf(f, -60000.f, 60000.f);
  return (uint16_t)_cvtss_sh(f, _MM_FROUND_TO_NEAREST_INT | _MM_FROUND_NO_EXC);
}

int main(int argc, char** argv) {
  if (argc < 10) { fprintf(stderr, "usage: pt scene frames outprefix f0 f1 W H NAA NL [clampInd clampSpec]\n"); return 1; }
  const char* sceneFile = argv[1]; const char* frameFile = argv[2]; std::string outp = argv[3];
  int f0 = atoi(argv[4]), f1 = atoi(argv[5]), W = atoi(argv[6]), H = atoi(argv[7]), NAA = atoi(argv[8]), NL = atoi(argv[9]);
  float CLI = argc > 10 ? atof(argv[10]) : 6.0f, CLS = argc > 11 ? atof(argv[11]) : 12.0f;
  FILE* f = fopen(sceneFile, "rb");
  if (!f) { fprintf(stderr, "no scene\n"); return 1; }
  int magic, nMat, nInst;
  if (fread(&magic, 4, 1, f) != 1 || fread(&nMat, 4, 1, f) != 1 || fread(&nInst, 4, 1, f) != 1) return 1;
  mats.resize((size_t)nMat * MATF);
  if (fread(mats.data(), 4, mats.size(), f) != mats.size()) return 1;
  insts.resize(nInst);
  size_t total = 0;
  for (int i = 0; i < nInst; i++) {
    int n; if (fread(&n, 4, 1, f) != 1) return 1;
    insts[i].tris.resize(n);
    if (n && fread(insts[i].tris.data(), sizeof(SrcTri), n, f) != (size_t)n) return 1;
    total += n;
  }
  fclose(f);
  fprintf(stderr, "scene: %d mats, %d insts, %zu tris\n", nMat, nInst, total);
  FILE* ff = fopen(frameFile, "rb");
  if (!ff) { fprintf(stderr, "no frames\n"); return 1; }
  int nFrames; if (fread(&nFrames, 4, 1, ff) != 1) return 1;
  size_t NP = (size_t)W * H;
  std::vector<uint8_t> bAlb(NP * 3); std::vector<int8_t> bNrm(NP * 3); std::vector<float> bDep(NP); std::vector<uint16_t> bId(NP);
  std::vector<uint16_t> bE(NP * 3), bIrr(NP * 3), bSpec(NP * 3);
  std::vector<float> xf((size_t)nInst * 13);
  minv.resize((size_t)nInst * 12);
  std::vector<char> instMoving(nInst, 0);
  for (int fr = 0; fr < nFrames; fr++) {
    float cam[12];
    if (fread(cam, 4, 12, ff) != 12) break;
    if (fread(xf.data(), 4, xf.size(), ff) != xf.size()) break;
    int nL; if (fread(&nL, 4, 1, ff) != 1) break;
    std::vector<float> lraw((size_t)nL * 20);
    if (nL && fread(lraw.data(), 4, lraw.size(), ff) != lraw.size()) break;
    if (fr < f0) continue;
    if (fr >= f1) break;
    double t0 = omp_get_wtime();
    // world triangles
    tris.clear();
    for (int i = 0; i < nInst; i++) {
      const float* m = &xf[(size_t)i * 13];
      float a = m[0], b = m[1], c = m[2], d = m[4], e = m[5], ff2 = m[6], gg = m[8], hh = m[9], ii = m[10];
      float det = a * (e * ii - ff2 * hh) - b * (d * ii - ff2 * gg) + c * (d * hh - e * gg);
      float id = fabsf(det) > 1e-20f ? 1.0f / det : 0;
      float inv[9] = {(e * ii - ff2 * hh) * id, (c * hh - b * ii) * id, (b * ff2 - c * e) * id,
                      (ff2 * gg - d * ii) * id, (a * ii - c * gg) * id, (c * d - a * ff2) * id,
                      (d * hh - e * gg) * id, (b * gg - a * hh) * id, (a * e - b * d) * id};
      float* mi = &minv[(size_t)i * 12];
      for (int r = 0; r < 3; r++) {
        mi[r * 4 + 0] = inv[r * 3]; mi[r * 4 + 1] = inv[r * 3 + 1]; mi[r * 4 + 2] = inv[r * 3 + 2];
        mi[r * 4 + 3] = -(inv[r * 3] * m[3] + inv[r * 3 + 1] * m[7] + inv[r * 3 + 2] * m[11]);
      }
      instMoving[i] = m[12] > 1.5f;
      if (m[12] < 0.5f || id == 0) continue;
      for (const SrcTri& s : insts[i].tris) {
        V3 p[3], n[3];
        for (int k = 0; k < 3; k++) {
          float x = s.p[k * 3], y = s.p[k * 3 + 1], z = s.p[k * 3 + 2];
          p[k] = V3(m[0] * x + m[1] * y + m[2] * z + m[3], m[4] * x + m[5] * y + m[6] * z + m[7], m[8] * x + m[9] * y + m[10] * z + m[11]);
          float nx = s.n[k * 3], ny = s.n[k * 3 + 1], nz = s.n[k * 3 + 2];
          n[k] = norm(V3(inv[0] * nx + inv[3] * ny + inv[6] * nz, inv[1] * nx + inv[4] * ny + inv[7] * nz, inv[2] * nx + inv[5] * ny + inv[8] * nz));
        }
        Tri t; t.v0 = p[0]; t.e1 = p[1] - p[0]; t.e2 = p[2] - p[0]; t.n0 = n[0]; t.n1 = n[1]; t.n2 = n[2]; t.inst = i; t.mat = s.mat;
        if (len(cross(t.e1, t.e2)) < 1e-12f) continue;
        tris.push_back(t);
      }
    }
    buildBVH();
    lights.clear();
    for (int i = 0; i < nL && i < 32; i++) {
      const float* r = &lraw[(size_t)i * 20];
      Light l; l.type = (int)r[0]; l.c = V3(r[1], r[2], r[3]); l.eu = V3(r[4], r[5], r[6]); l.ev = V3(r[7], r[8], r[9]);
      l.L = V3(r[10], r[11], r[12]); l.axis = norm(V3(r[13], r[14], r[15])); l.spotExp = r[16]; l.always = (int)r[17];
      if (l.type == 0) { V3 cr = cross(l.eu, l.ev); l.area = len(cr); l.n = norm(cr); l.radius = 0; }
      else { l.radius = r[4]; l.area = PI * l.radius * l.radius; l.n = V3(0, 0, 1); }
      lights.push_back(l);
    }
    V3 cpos(cam[0], cam[1], cam[2]), ctgt(cam[3], cam[4], cam[5]), cup(cam[6], cam[7], cam[8]);
    float vfov = cam[9] * PI / 180.0f;
    V3 fw = norm(ctgt - cpos), rt = norm(cross(fw, cup)), up = cross(rt, fw);
    float th = tanf(vfov * 0.5f), asp = (float)W / H;
    double t1 = omp_get_wtime();
#pragma omp parallel for schedule(dynamic, 4)
    for (int y = 0; y < H; y++) {
      for (int x = 0; x < W; x++) {
        size_t pi = (size_t)y * W + x;
        RNG g; g.s = pcg_hash((uint32_t)pi * 9781u + (uint32_t)fr * 6271u + 17u); g.next();
        V3 A(0), E(0), IRR(0), SPEC(0);
        V3 gn(0, 0, 0); float gd = 0; int gid = 32767; bool mv = false;
        for (int s = 0; s < NAA; s++) {
          float jx = 0.5f, jy = 0.5f;
          if (s > 0) { jx = g.next(); jy = g.next(); }
          float sx = ((x + jx) / W * 2 - 1) * th * asp, sy = (1 - (y + jy) / H * 2) * th;
          V3 d = norm(fw + rt * sx + up * sy);
          Hit h;
          if (!intersect(cpos, d, h)) continue;
          Surf sf; shade(h, cpos, d, sf);
          if (s == 0) { gn = sf.Ng; gd = h.t; gid = sf.inst; }
          if (instMoving[sf.inst]) mv = true;
          E += sf.emis;
          if (!sf.metal) A += sf.alb;
          if (s >= NL) continue;
          V3 wo = -d;
          float nov = std::max(1e-4f, dot(sf.N, wo));
          float F = (sf.f0 > 0 && !sf.metal) ? sf.f0 + (1 - sf.f0) * powf(1 - nov, 5) : 0;
          if (!sf.metal) {
            V3 dl = direct(sf.P, sf.Ng, sf.N, g);
            V3 wi = cosSample(sf.N, g);
            V3 ind(0);
            if (dot(wi, sf.Ng) > 0) ind = clampLum(Li(sf.P + sf.Ng * EPS, wi, g, false, 1), CLI);
            IRR += (clampLum(dl, CLI * 8) + ind) * (1 - F);
          }
          if (sf.metal || (sf.glossy && sf.f0 > 0)) {
            V3 wi, wgt;
            if (ggxSample(sf, wo, g, wi, wgt)) SPEC += clampLum(wgt * Li(sf.P + sf.Ng * EPS, wi, g, true, 1), CLS);
          }
        }
        float ia = 1.0f / NAA, il = 1.0f / std::max(1, std::min(NL, NAA));
        A = A * ia; E = E * ia; IRR = IRR * il; SPEC = SPEC * il;
        for (int k = 0; k < 3; k++) {
          bAlb[pi * 3 + k] = (uint8_t)clampf(sqrtf(std::max(0.0f, A[k])) * 255.0f + 0.5f, 0, 255);
          bNrm[pi * 3 + k] = (int8_t)clampf(gn[k] * 127.0f, -127, 127);
          bE[pi * 3 + k] = f2h(E[k]); bIrr[pi * 3 + k] = f2h(IRR[k]); bSpec[pi * 3 + k] = f2h(SPEC[k]);
        }
        bDep[pi] = gd; bId[pi] = (uint16_t)(gid | (mv ? 0x8000 : 0));
      }
    }
    char name[512]; snprintf(name, sizeof(name), "%s_%04d.bin", outp.c_str(), fr);
    std::string tmp = std::string(name) + ".tmp";
    FILE* fo = fopen(tmp.c_str(), "wb");
    int hdr[2] = {W, H};
    fwrite(hdr, 4, 2, fo);
    fwrite(bAlb.data(), 1, bAlb.size(), fo); fwrite(bNrm.data(), 1, bNrm.size(), fo); fwrite(bDep.data(), 4, bDep.size(), fo);
    fwrite(bId.data(), 2, bId.size(), fo); fwrite(bE.data(), 2, bE.size(), fo); fwrite(bIrr.data(), 2, bIrr.size(), fo); fwrite(bSpec.data(), 2, bSpec.size(), fo);
    fclose(fo);
    rename(tmp.c_str(), name);
    fprintf(stderr, "frame %d: %zu tris, bvh %.2fs, render %.1fs\n", fr, tris.size(), t1 - t0, omp_get_wtime() - t1);
  }
  fclose(ff);
  return 0;
}
