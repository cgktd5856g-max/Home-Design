# Handoff: making viral room-build videos from code

Written 23 Nov 2026 for the next agent picking up this project. Read this whole file first. Then read
`research/HANDOFF.md` and `research/report.md` for the evidence behind the creative rules.

---

## 1. What this project is

**The goal:** original vertical "room-build" videos for TikTok, Instagram Reels and YouTube Shorts, in the style of
the viral account **@havenhaus_1 (Haven Haus)**.

**The format:**
- The video opens on an empty room, then every piece of furniture flies in and lands on its own, with a sound on
  each landing.
- Storage is the star: drawers open, fill and close; beds lift; doors slam shut.
- It ends on a held, beautiful wide shot.

**How it is made:** entirely from code. Python describes the room, and **Blender (Cycles)** renders it
photo-realistically. No design apps (no Coohom or Kujiale), no AI video generators and no paid software. It all runs
on a 4-core cloud machine with no GPU.

**What Haven Haus actually does:** it mostly **reposts** videos from Chinese Douyin designers. Watermarks seen:
`@设计师温倪`, `@设计师阳阳`. Those designers most likely use Kujiale/Coohom's "growth animation". Under the 2026
platform rules (Instagram, TikTok, YouTube), repost accounts lose reach and originals win. That is our edge.

### The owner's standing preferences (follow these)
- **No on-screen text** in the videos, ever: no captions, labels or end cards. Post captions are fine.
- **Quality first.** "Spend forever if needed" for a really good video, but report time estimates up front.
- **Updates as you go:** a still early, a low-res preview, progress screenshots during long renders, then the final.
- **Free tools by default.** A paid GPU (for example the Higgsfield connector) only with explicit approval and a
  price quote.
- Original music and sounds only. Never copy anyone's assets, audio, text or watermarks.
- Packed smart storage and a different layout every video. Clean and bright, never dark or grainy (a night
  finale is fine).
- Theme ideas are welcome, but no copyrighted characters or logos.

---

## 2. The repository

```
HANDOFF.md            this file
README.md             quick start
RESEARCH.md           first research pass (how Haven Haus sources videos, tools, platform rules)
research/             deep research by a separate agent: report.md, next_videos.md (20 ranked ideas),
                      videos.csv (298 Haven Haus Shorts), deep_analysis.csv (59 measured), hh_metrics.py,
                      youtube_inventory.py, sources.md, HANDOFF.md, agent_research_prompt.md
pipeline/
  roomkit.py          scene description: materials, primitives (box, rbox, lathe, tube, ellipsoid, grid_tris), lights
  animkit.py          timeline: drop / slide / fly / grow / from_camera / custom + landing events -> frames.json
  camkit.py           camera: gliding HOLDS joined by fast swings -> camera(t) (hold_camera)
  figure.py           stand-in people (adult / child mannequins), posable and animatable
  pt.cpp, dn.cpp      code renderer (CPU path tracer + denoiser): fast previews and probe stills
  run.py              driver for the code renderer: probe | preview | final
  post.py, mkvideo.py, rawio.py   grading + encoding for the code renderer
  music.py            original synth music + one sound per landing event -> music.wav, sfx_only.wav
  qa.py               format check, frame sheets, sound-sync report
  analyze_reference.py  break down a reference video (cuts, camera, BPM)
  textures.py         bakes procedural textures to images for Blender (marble, floor tiles, planks, sky, night)
  blender_render.py   Blender bridge: loads a room project into Blender Cycles and renders PNG frames
  mkvideo_png.py      PNG frames -> 1080x1920 MP4: landing punch, sharpening, colour grade, music
rooms/
  kitchen/project.py  8 m² L-kitchen, with a pull-out pantry finale
  bedroom/project.py  11 m² bedroom: bed nook, lift-up bed, desk, sliding wardrobe, day-to-night finale
out/                  finished videos and stills (committed)
.render/              work folders and rendered frames (git-ignored; survives container restarts, /tmp may not)
```

---

## 3. The pipeline at a glance

```
rooms/<room>/project.py
   build()     every piece in its final position, as named meshes with materials
   timeline()  how each piece moves (and when), plus landing events (sounds + camera punch)
   camera(t)   camera pose at any time (glides inside shots, fast swings between them)
   lights()    a fixed list of light "slots" (off = zero brightness)
   BLENDER     look settings for Blender (exposure, translucent materials, bake sizes...)
        |
        +--> code renderer (pt.cpp): probe stills and the low-res preview with music   [minutes]
        |
        +--> blender_render.py -> PNG frames (Cycles, 720x1280)                        [hours]
                 -> mkvideo_png.py: punch + sharpen + grade + music -> 1080x1920 MP4
   music.py builds music.wav / sfx_only.wav from frames.json (written by the project export)
```

---

## 4. Setup in a fresh cloud session

```bash
pip install numpy scipy opencv-python-headless          # g++ (OpenMP) and ffmpeg are already installed
uv venv /root/bpyenv && uv pip install --python /root/bpyenv/bin/python bpy==5.3.0 numpy   # Blender 5.3 as a Python module
/root/bpyenv/bin/python -c "import bpy; print(bpy.app.version_string)"
```
- download.blender.org is blocked by the network policy, but PyPI works.
- bpy 5.3 matches this machine's Python 3.13.
- Caption fonts are in `/usr/share/fonts/opentype/inter/`. They are unused, because there is no text in the videos.

---

## 5. Making a video, step by step (the bedroom as the example)

```bash
P=rooms/bedroom/project.py; W=/home/user/Home-Design/.render/bed

# 1) Stills of the finished room from each camera station (fast, code renderer)
ROOM_REST=1 python3 pipeline/run.py $P $W/rest probe 0.5,1.5,2.5,3.5,4.5,5.5
ROOM_REST=1 ROOM_NIGHT=1 python3 pipeline/run.py $P $W/rest probe 5.5          # night version

# 2) Check busy moments of the animation (collisions, framing, pops)
python3 pipeline/run.py $P $W/anim probe 0.5,4.3,4.9,10.2,16.8,23.3,30.5 --size 360x640

# 3) Low-res preview with music, for pacing (about 8-10 min); also writes frames.json, music.wav, sfx_only.wav in $W/work
python3 pipeline/run.py $P $W/work preview --out $W/bedroom_preview.mp4

# 4) Blender look test on a few moments (about 12 s per still at 540x960)
/root/bpyenv/bin/python pipeline/blender_render.py $P $W/bl_test --size 540x960 --samples 16 --adaptive 0.04 \
    --bounces 4,2,2 --nobevel --test 4.9,16.8,28.0,30.5

# 5) Final Blender render, detached so it survives the 2-hour tool limit (resumable: finished frames are skipped)
(setsid nohup /root/bpyenv/bin/python pipeline/blender_render.py $P $W/bl_final --fps 25 --size 720x1280 \
    --samples 16 --adaptive 0.04 --bounces 4,2,2 --nobevel > $W/bl_final.log 2>&1 < /dev/null &)
grep -E "^frame|Traceback|^done in" $W/bl_final.log | tail -n 2        # progress + ETA

# 6) Encode: music version + sound-effects-only version, colour graded into the hits' band
python3 pipeline/mkvideo_png.py $W/bl_final/frames 25 $W/work/frames.json out/bedroom_build.mp4 1080 1920 \
    $W/work/music.wav --grade 1.35,0.03
python3 pipeline/mkvideo_png.py $W/bl_final/frames 25 $W/work/frames.json out/bedroom_build_sfx_only.mp4 1080 1920 \
    $W/work/sfx_only.wav --grade 1.35,0.03

# 7) Quality checks
python3 pipeline/qa.py $W/work out/bedroom_build.mp4          # format, frame sheets, sound sync (keep within 50 ms)
python3 research/hh_metrics.py out/bedroom_build.mp4          # motion / stillness / camera / colour against the hits
```

**Timing on this 4-core machine:**

| Step | Time |
|---|---|
| Code-renderer probe | about 2 s per still |
| Code-renderer preview | about 0.5 s per frame record |
| Blender at 720x1280, 16 spp | about 17-26 s per frame (a 33 s video at 25 fps is about 4-5 h) |
| Encode | about 2 min |

- In Blender, frames where nothing moves are copied instead of rendered. With a gliding camera every frame is unique.
- A GPU would make Blender about 20-50 times faster (needs the owner's approval: it costs money).

---

## 6. Writing a new room (copy `rooms/bedroom/project.py`)

**Units and axes:** metres; x = east, y = north, z = up. The room spans x 0..W, y 0..D, z 0..H.

**Pieces**
- Build every piece where it finally rests, with `add('<piece>', geometry, '<material>')`.
- Everything that moves on its own needs its own piece name. The static shell is `room`.

**Materials:** `mat(name, tex=…, col=srgb(...), col2=..., col3=..., rough, f0, metal, emis, p=(…))`. Texture types:

| tex | What |
|---|---|
| 0 | solid colour |
| 1 | floor planks |
| 2 | wood board (`wood_mats` + `wood()` pick the grain direction) |
| 3 | speckle |
| 4 | blind folds |
| 5 | knit |
| 6 | boucle |
| 7 | stripes |
| 9 | day window view (p[1] = 1 for an east/west window) |
| 10 | keyboard |
| 11 | marble |
| 12 | tiles with grout |
| 13 | cement flower tiles |
| 14 | brushed metal |
| 15 | quartz |
| 16 | night skyline |

Blender maps all of them. Textures 1, 11, 13, 9 and 16 are baked to images (`pipeline/textures.py`); the others
become node setups.

**Helpers in the bedroom file**

| Helper | Makes |
|---|---|
| `cloth()` | a draped duvet or throw with wrinkles and soft skirts |
| `pillow()` | a puffy pillow with pinched seams |
| `garment()` | a hanging clothes piece |
| `stack()` | folded clothes |
| `plant()` | a potted plant |
| `disc()` | a flat round piece |

**Lights: always a fixed list of slots.** A light that is off returns zero brightness, so the light keeps the same
index on every frame. Blender keyframes lights by index, so they must never be added or removed mid-video.
- Rectangle lights shine toward `cross(eu, ev)`. Check the sign, or the light faces outward and the room goes black.
- Use `spot_rect` for spots and `sphere_light` for bulbs.
- **The sun** is a small far-away rectangle placed **between the window and the window-view backdrop**. The backdrop
  plane would otherwise block it in the code renderer.

**The `BLENDER` dict**

| Key | What it sets |
|---|---|
| `exposure` | exposure (AgX "Medium High Contrast" look) |
| `translucent` | `{material: amount}` for sheer curtains |
| `separate` | materials that become camera-only objects (the window views, so they don't block light) |
| `fill_lights` | slot indices hidden from reflections |
| `bake_rect` / `bake_px` | area and pixel size for baked textures |
| `glass` | glass materials |
| `bevel` | bevel the edges (slow; we render with `--nobevel`) |

**Timeline helpers** (`animkit.Timeline`), plus the extras in the bedroom file:
- `drop`, `slide`, `fly`, `grow(axis, pivot)`, `from_camera`, and `custom(name, fn)` where `fn(t)` returns
  `(4x4 matrix, visible)`.
- `door_z` makes a door pop in already open and slam shut. It hinges on z (side doors) or x (lift-up flaps).
- `drawer_fn` makes a drawer open, hold and close, optionally riding on a parent piece.
- `appear(name, t_on, t_off)` switches a piece on or off.
- Contents ride inside a drawer with `drop(..., parent=drawer_fn)`.
- Every helper registers a landing event. Event kinds are `thud`, `tick`, `swish` and `chime`; they drive the sounds
  and the camera punch.

**Camera:** `HOLDS = [(t0, t1, (start_pose, end_pose)), …]`, then `camera = hold_camera(HOLDS, VFOV, rest=REST)`
(`pipeline/camkit.py`).
- Each shot **glides** from its start pose to its end pose. The hits' camera never stands still.
- Fast eased swings (about 0.3 s) join the shots; the last move is a whip.
- `vfov` 85, eye height about 1.3-1.5 m.

**Probe modes:** `ROOM_REST=1` shows the finished room, with the camera stepping through the stations at
t = 0.5, 1.5, …; add `ROOM_NIGHT=1` for the night version.

**Stand-in people** (`pipeline/figure.py`): a friendly, faceless mannequin in adult (1.68 m, light grey) or child
(1.15 m, soft peach) size, built from roomkit primitives. Each body segment is its own piece (`mom_torso`,
`mom_thigh_l`, …), so poses animate as rigid per-piece transforms in both renderers.
- In `build()`: `mom = fg.figure('mom', 'adult', pose='stand', at=(x, y, yaw))`. `at` puts the pelvis over (x, y),
  facing `yaw` (the camera convention: 0 = facing +y). The feet land on `floor` (default 0; 0.016 on the bedroom rug),
  or the figure sits on a surface with `seat=z`.
- In `timeline()`: `mom.animate(tl, pose=…, at=…, seat=…, visible=…, pop=t)`. Each argument is a constant or a
  function of t. `pop` scales the figure in from its feet, with a tick sound.
- Poses are dicts of joint angles in degrees: `spine`, `neck`, `hip_l/r`, `knee_l/r`, `ankle_l/r`, `sh_l/r`,
  `sh_l/r_out`, `elbow_l/r`, and a few more (see the module docstring).
  - Presets in `fg.POSES`: `stand`, `sit`, `sit_desk`, `reach_up`, `reach_both`, `step_up`, `crouch`, `wave`, plus
    `fg.walk_pose(phase)`.
  - Combine them with `fg.lerp_pose(a, b, u)`, `fg.mirror(p)` (swap left and right) and
    `fg.track([(t, pose), …])` (eased pose keyframes).
- `fg.walk([(t, (x, y, yaw)), …], fig)` returns `(pose_fn, at_fn)`. The legs cycle with the distance walked, and
  the figure stops at each key.
- `fig.sit_pose(seat_z)` solves a sitting pose for any seat height: feet flat on the floor when the legs reach,
  otherwise dangling, as for a child on a bed.
- Contacts are approximate: place the figure clear of furniture and check with a probe still.
- A step-up foot rises about 0.2 m for an adult and 0.13 m for a child.

---

## 7. The creative formula (from the research; see research/report.md)

1. **A whole room transforms.** 27 of 29 hits do this; flops show one cabinet.
2. **Frame 1 is the empty room** (with a sunbeam), and something moves by 0.3 s.
3. **A landing every 0.3-0.6 s.** 6-12 storage reveals: drawers fill, beds lift, wardrobes fill, doors slam,
   pull-outs.
4. **The camera glides inside every shot.** No moment holds still for more than about 1.5 s. Targets in
   `hh_metrics.py`: motion 7.5+, camera movement 1.8+, longest still 1.8 s or less.
5. **Length:** hits are 34-53 s full-room tours (median 39 s). Under 30 s none passed 1M.
6. **Colour band:** a white or pale shell, light wood and one accent (sage, terracotta, blue), with colour coming
   from filled storage. Targets: saturation 0.17-0.38, warmth 22-57, brightness 138-178. No orange cast, no dark
   wood. The final grade `--grade 1.35,0.03` lands there.
7. **Payoff:** lights on, or a day-to-night lights cascade, then a held wide that loops.
8. **Sound:** a sound on every landing over original music at about 115-128 BPM.
9. **Room priority:**
   - bedrooms run at 1.51× the account's normal views, kids' rooms 1.35×, wardrobes 1.05×, kitchens 1.0× (but
     one kitchen hit 19.3M);
   - a size in the caption ("8 m²", "11 m²") gives about 1.34×;
   - "two kids, one room" gives 1.36×.
10. **Comments are debates.** Clever but contestable storage drives replies. Ask for room requests with
    dimensions, and answer with videos (TikTok's "reply with video").

**Next ideas:** `research/next_videos.md` ranks 20. The top is "Three kids, one 9 m² room", then a 7 m² bedroom
with a loft and walk-in closet.

---

## 8. Lessons learned (save yourself the time)

**Camera and staging**
- **Lift-up beds:** a camera at the foot can't see into the storage, because the lifted base blocks it. Show the
  lift from the side, and hinge the base at the head at mattress-top level so the foot rises.
- The rug at the bed foot is out of frame from the hero camera, so stage it from another shot.

**Rendering**
- **Winding and normals:** shapes made from grids can render black in Cycles. The bridge flips triangle winding to
  match the shading normals; keep that.
- **Window views:** list their materials in `separate`. Otherwise they cast shadows and light the room in Blender.
- The code renderer's mirror and transparency are rough; judge materials in Blender stills, not probes.

**Long renders**
- Run them **detached** (`setsid nohup … &`). Background tools stop after 2 hours, and container restarts kill
  processes.
- The render resumes where it stopped; check frames with `cv2.imread` and delete unreadable ones.
- Keep work in `.render/`, not `/tmp`.
- Blender logs contain a harmless "CUEW … Error" line. Watch for `Traceback` instead of "Error".

**Permissions and network**
- The auto-mode safety check blocks `yt-dlp` and also blocks the agent editing its own permission settings. The
  owner must add allow rules themselves (repository `.claude/settings.json`, `"Bash(yt-dlp *)"`).
- `www.youtube.com` and `i.ytimg.com` are already allowed in the "Home Decor" environment.

**Git**
- A research agent also pushes to `claude/viral-video-research-vq8gmc`. If a push is rejected, run
  `git fetch origin <branch> && git merge --no-edit FETCH_HEAD`, then push. Never force-push.
- Don't commit `.render/` or preview videos (both are git-ignored). Commit final videos in `out/`.

**Design**
- Soft goods: use `cloth()` and `pillow()`. Plain boxes look like foam.

---

## 9. Current status (23 Nov 2026)

| Item | State |
|---|---|
| Kitchen v1 (code renderer) | done: `out/kitchen_build.mp4` (+ `_sfx_only`) |
| Kitchen v2 (Blender, pull-out pantry finale) | done: `out/kitchen_build_v2.mp4` (+ `_sfx_only`), 15.5 s |
| Bedroom (Blender, 32.7 s, 818 frames) | done: `out/bedroom_build.mp4` (+ `_sfx_only`), 1080x1920, 25 fps, graded `--grade 1.35,0.03`. Render took about 4.5 h on 4 CPU cores, plus one resume after a container restart |
| Research | done (see `research/`) |

**Bedroom QA (`research/hh_metrics.py`)**

| Metric | Bedroom | Hits | |
|---|---|---|---|
| brightness / saturation / warmth | 148 / 0.27 / 37.5 | 138-178 / 0.17-0.38 / 22-57 | in range |
| camera movement | 2.95 | 2.9 (flops 1.0) | in range |
| median motion per 0.2 s | 4.0 | 8.4 (flops 5.1) | **low** |
| longest still stretch | 2.8 s (the night hold at the end) | 1.4 s (flops 2.6) | **long** |
| first clear movement | 1.0 s | 0.4 s or less | **late** |

- Sound sync is exact by construction: music.py places each sound at the event's landing time, and frame f is
  rendered and encoded at t = f/25. `qa.py` flags 18 of 90 thuds and ticks as more than 50 ms off. Those are
  detector misses, not timing errors: the detector merges sounds closer than about 80 ms (the flute run, the shelves
  and books) and skips quiet lone ticks below its 97th-percentile threshold.
- **Lesson for the next video:** pace it faster. Aim for more pieces per second, hard movement in the first 0.4 s
  (a big piece landing close to the camera, not floor planks at the bottom edge), and holds no longer than about
  1.5 s, including the payoff at the end. The kitchen v2 measured low on motion too.

**To re-render a room,** run section 5 step 5. It skips frames already on disk, so a stopped render resumes.

**Bedroom shot list (32.7 s)**

| Time | Shot | What happens |
|---|---|---|
| 0-3.6 s | hero | empty room with a sunbeam; floor planks land far to near; wardrobe towers rise; bridge cabinet; the fluted sage headboard ripples in; the bed frame builds board by board; base and mattress drop |
| 3.9-7.3 s | across the bed | the base lifts on its hinge; suitcase, boxes and vacuum bags drop in; it closes; duvet, four pillows, throw |
| 7.6-12.4 s | west tower | nightstand drawer opens and fills; phone on the wireless charger (glow); sconce; tower wardrobe pops open, fills with clothes, slams; overhead flaps lift, fill and close |
| 12.7-18.2 s | desk | desk, drawer cabinet, shelves, books, laptop, lamp, mug, plant; drawer moment; chair rolls in; laptop opens; curtain track and sheer curtains |
| 18.5-26.5 s | wardrobe | rug unrolls; wardrobe slides out; drawers; clothes slide onto rails; folded stacks, shoes, boxes; LEDs on; a drawer of tees; the pull-down rail lowers and rises; oak and mirror sliding doors; the mirror door slides open and shut |
| 27.1-32.7 s | final | vase, candle, second sconce; night falls (sky swap); lights cascade (LED strip grazing the flutes, sconces, niches, downlights, desk lamp); slow push-in hold |

---

## 10. Posting notes (for the owner)

- **Caption:** size + problem + a debatable question. For example: "11 m² bedroom, zero wasted space 🤯 Would you
  sleep under the bridge cabinet? Comment your room size 👇". Use 3-5 hashtags (#bedroomdesign #smallbedroom
  #storageideas #interiordesign).
- **TikTok and Instagram:** post the `_sfx_only` file and add a trending sound. **YouTube Shorts:** post the music
  version.
- **Pin a comment** asking for room requests with dimensions, and answer them with "reply with video".
- **Post 3-5 originals a week.** Never re-post old clips; that is what is sinking Haven Haus in 2026.
- **Don't present renders as real client homes.** "Designed" is fine.
