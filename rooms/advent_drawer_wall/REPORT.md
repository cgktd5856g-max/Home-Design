# The Advent Stair: report

## What was built
An 8 m² kids' room (2.6 x 3.1 m, 2.8 m ceiling) that builds itself while snow falls past the window:
- **Loft bed** on the north wall, deck at 1.38 m. It has oak posts, a slat rail with fairy lights, a matte gold
  duvet, a green throw, a headboard cubby and a slim tree on the landing.
- **Den** under the loft: a desk with a drawer, a chair, a cubby with four fabric bins, a two-shelf book wall in a
  sweep of colour, a lamp and an LED strip.
- **The Advent Stair** on the east wall: six steps (0.23 m rises) with 24 light-oak drawers, 21 in the stepped side
  face and 3 in the top risers.
  - Each drawer's tray slides out, its front drops into an oak ledge, and a small toy hops onto it: a car,
    baubles, a duck, a candy cane, blocks, a bell, a rocket, a mitten, a teddy, gifts, a yo-yo, a mini tree, a sock,
    a drum, a sweet, a train, a wooden star, a top, a bunny and a gingerbread-style house. The top drawer holds the
    star.
  - An oak guard runs on the open side of the top treads.
- **The person moment**: a faceless child steps up, opens the top drawer, and the star flies to the tree as the
  lights come on.
- **Music**: an original cue (`music_advent.py`): 120 BPM in F major, synthesized sleigh bells and a glockenspiel.
  The cascade plays a rising F major scale, one note per drawer, and the close ripple plays it back down.
- **No on-screen text**: nothing on the drawers, blank book spines, no logos or IP.

The concept moved from a 4 x 6 drawer wall to the Advent Stair on 23 Nov, following the coordinator's update
(`production/sessions/advent_drawer_wall_update1.md`). The C5 plan and the top-10 document were folded in.

## Files
- `out/advent_drawer_wall_15s.mp4`: music version (YouTube Shorts). 1080x1920, 25 fps, 15.0 s, H.264 + AAC.
- `out/advent_drawer_wall_15s_sfx_only.mp4`: landing sounds and the drawer scale only (TikTok / Reels with a
  trending sound).
- `out/advent_drawer_wall_still.jpg`: the hero frame, all 24 drawers open (9.3 s).
- `rooms/advent_drawer_wall/project.py`, `music_advent.py`, `PLAN.md`, `progress/` (probe stills, preview metrics,
  Blender test sheet).

## 15 s cut: shot list
| Time | Station | What happens |
|---|---|---|
| 0.00-2.90 | High doorway corner, craning down | Frame 1: the empty white room, snow at the window, a sunbeam. The planks slap down (0.04-0.27 s) and the **loft deck slams in at 0.28 s**. Then the posts, then the six stair blocks (0.62-0.97 s). **The tease**: one drawer drops its front, a duck hops out with a glint, and it shuts (1.0-1.8 s). Then the rail, the stair guard, the mattress, the duvet, the pillow, the throw, the tree, the fairy lights and the cubby books. |
| 3.15-5.20 | The den, a lateral drift | Desk, chair, cubby, four bins, desk drawer (opens, fills, shuts), lamp, shelves, the book sweep, rug. |
| 5.42-8.55 | Low push up the stair | **The cascade**: 24 drawers open bottom to top, 0.12 s apart, each on the next note of the scale (5.70-8.46 s). |
| 8.75-10.75 | All open, pushing in | All 24 are held open for 1.5 s with a sparkle chime, then a descending close ripple 0.02 s apart (9.96-10.63 s) and one thud. |
| 11.00-12.75 | The child and the tree | The child pops onto tread 3 and steps up. Bend-and-reach; the top drawer opens (11.70 s) and the star flies to the tree (11.92-12.16 s). **Lights on** at 12.20 s: the tree, the star, the fairy lights, the den strip, the lamp and the downlights. |
| 13.02-15.00 | Final wide | A pouf and slippers land; the camera drifts into the exact frame-1 pose while snow keeps falling (loop join). |

## hh_metrics on the final 15 s cut
| Metric | Value | Target | |
|---|---|---|---|
| dmed (motion) | 7.7 | 7.5+ | ok |
| s10 (share of clear changes) | 0.45 | 0.39+ | ok |
| calm (longest still) | 0.4 s | 1.8 s or less | ok |
| camera | 5.22 | 1.8+ | ok |
| fb (first movement) | 0.2 s | 0.4 s or less | ok |
| lum (brightness) | 164 | 138-178 | ok |
| sat (saturation) | 0.27 | 0.17-0.38 | ok |
| warm (warmth) | 44.0 | 22-57 | ok |
| len | 15.0 s | 34-46 s (long cut only) | n/a |

`qa.py`: 1080x1920 H.264 yuv420p at 25 fps, AAC 44.1 kHz stereo, 15.0 s. The landing sounds are placed at the exact
event times by `music.py`. `qa.py`'s onset detector merges the dense cascade ticks (8 a second), so its offsets
there are detector limits, not sync errors. The isolated landings sit within about 10 ms.

## Render
- Blender Cycles, 720x1280, 16 spp, adaptive 0.04, bounces 4,2,2, no bevel. 375 frames at about 40 s each.
- Total about 3.3 h of render time: 1 h 56 min for frames 1-200 and 2 h for 201-375 after a worker restart killed
  the process, plus about 45 min re-rendering 65 frames (see below).
- Encoded with `mkvideo_png.py --grade 1.35,0.03`.

## Review gates
- **Gate 1** (the preview, 3 rounds): scored 6, 6.5 and 6. The fixes applied:
  - a tighter, level cascade camera;
  - frame 1 with the whole window and a stronger sunbeam;
  - the deck landing by 0.28 s;
  - a bigger tease;
  - the stand-in in a coloured top;
  - oak ledges for contrast;
  - late landings in the final wide.

  Some of the reviewers' points were artifacts of the washed-out code-renderer preview, for example that the loop
  pose didn't match frame 1; the camera poses were checked directly.
- **Gate 2** (Blender stills): scored 6. The fixes applied:
  - 3x brighter fairy and tree bulbs;
  - a paler subfloor and a softer sun;
  - re-framing the child;
  - removing the black squares at the window corners and on the stair risers (coplanar faces).

## What I'd improve
- The reviewers never scored above 6.5; the brief asked for 8. The main remaining critiques:
  - the den beat (3-5 s) is quick, and the desk drawer and book sweep are small on a phone;
  - the child shot is busy;
  - the window view is a flat card.
- The den chair is motion-blurred where the camera glides close past it.
- The faceless mannequin reads as a mannequin. A dressed stand-in would be warmer.
- `qa.py`'s sync check can't resolve the cascade ticks; a per-event check against the known event times would be
  better.

## Lessons for next time
- **Hook**: measure `fb` on a preview graded to the final look. The raw code-renderer preview is washed out and
  hides real motion, and floor planks landing on a pale subfloor barely register. Land something big (the deck) by
  0.3 s.
- **Black-frame glitch**: Cycles sometimes renders a frame with large black patches (a bad sample spread by the
  denoiser). After every render, scan the frames for pixels under 12 over more than 2% of the frame. Re-render the
  bad frames with a slightly different sample count, which changes the sampling pattern; a plain re-render can
  repeat it.
- **Worker restart**: a session-worker restart kills detached Blender processes too. Keep a background waiter armed
  (an until-loop that exits when the process disappears), check the frame count on every wake-up and resume with
  the same command.
- **Coplanar faces** (a drawer front flush with a solid block, overlapping window-frame boxes) render as black
  squares in Cycles but look fine in the code renderer. Leave a gap or recess of a few millimetres.

## Long cut
Status: the 44 s timeline (`ROOM_CUT=long`, 15 stations following the C5 schedule) is written and probed. The top-10
colour rules (matte ochre duvet, gold only on the star) are applied to it. It renders next, to ship by 2 Dec.
