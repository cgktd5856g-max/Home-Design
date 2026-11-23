# Same Bed, Better Room (idea #2 / C4): report

## What I built
A 3.0 × 3.1 m (9.3 m²) bedroom for a couple, built entirely from code in `project.py` and rendered in Blender Cycles.
- **Opening (overhead, circling):** the room starts empty, then the usual layout lands: bed dead centre, wardrobe at its foot, desk wedged at the bed's corner. The wardrobe doors bonk the bed and the chair knocks it.
- **The shuffle:** the same pieces slide like tiles into a better plan.
  - The bed slides into the east corner. It slides; it never turns.
  - The wardrobe moves to the west wall and turns a quarter in open floor.
  - The desk turns inside the door, runs up the new 0.95 m aisle and lands under the window.
- **The platform:** one rigid oak lift rises under the same bed to 1.0 m, and the bed's legs fold up. It has:
  - three stair blocks with side-pull drawers (knitwear and shoes);
  - a deep drawer (suitcase and spare duvet);
  - a 1.4 m pull-out shirt rail, the wow;
  - a headboard ledge.
- **Wardrobe:** an oak top cupboard takes it to the ceiling, and the doors open wide with no bonk. Its two drawers fill in the long cut.
- **Ending:** lights-on, then the camera rises to the exact frame-1 pose, so every loop is a before-and-after.

The long cut adds a faceless stand-in who walks in, opens the wardrobe, stretches in the aisle and pulls the rail out.

**Look:** white shell, light oak, a white duvet, one grey-blue accent (pillow and throw), and colour from the filled storage. There is no text anywhere.

## Deliverables
- `out/same_bed_better_room_15s.mp4`: 15.0 s, 1080x1920, 25 fps, original music at 120 BPM.
- `out/same_bed_better_room_15s_sfx_only.mp4`: the same video with sound effects only, for adding a trending sound.
- `out/same_bed_better_room_still.jpg`: the final overhead wide of the finished room (the loop frame).
- The long cut is in progress; see the bottom of this file.

## 15 s shot list
| Time (s) | Shot | What happens |
|---|---|---|
| 0.0-4.5 | Overhead orbit, 68° down, 48° lens, 6°/s, slow push-in | The empty room. At 0.3 s the bed drops in from 3.2 m with a thud. At 0.6 s the wardrobe lands. At 0.9 s its doors swing and bonk the bed foot at 64°. At 1.05 s the desk and chair land, and at 1.18 s the chair knocks the bed. The shuffle runs 1.3-4.4 s with a wooden clack on every move, plus a scrape for the bed's slide. At 4.75 s the window shelf lands. |
| 4.5-7.0 | Drop to a low glide, then a descent through the door; the lens widens to 85° | At 5.1-5.9 s the platform lifts the bed to 1.0 m. At 5.98, 6.18 and 6.38 s the steps land, with rising thunks. At 6.5-7.1 s the stair drawers pop out full of knitwear and shoes, then close. |
| 7.22-8.75 | Straight on to the wardrobe, tilting down | 7.26-7.5 s: the oak top cupboard slides on. 7.62 s: the doors swing wide with a two-note chime where the bonk used to be. 7.84-8.02 s: both sets of clothes fly onto the bar. 8.42 s: the doors close. |
| 8.97-10.95 | Low (1.0 m) at the south end of the aisle, 56° lens | **Wow:** the 1.4 m rail glides out of the platform side with 12 shirts (8.95-9.45 s), holds, and glides back (10.55-10.88 s). |
| 11.15-12.4 | Wide from the door corner, pushing in | The ledge fills with books, a plant and a lamp; the window-shelf books and boxes, desk lamp, notebook and plant land. At 12.18 s the lights cascade on (LED under the platform lip, stair LEDs, ledge lamp, desk lamp) and daylight eases to 86%. |
| 12.4-15.0 | Rise out of the room back to the frame-1 pose | The chair rolls out (12.85 s) and the deep drawer slides out with a suitcase (13.35-14.2 s), then both return. The camera arrives at the exact frame-1 position and speed at 15.0 s. |

## hh_metrics (final 15 s, music version, graded 1.35,0.03)
| Metric | Value | Target | |
|---|---|---|---|
| motion | 8.8 | 7.5+ | ok |
| share of clear changes | 0.49 | 0.39+ | ok |
| longest still | 1.2 s | ≤1.8 s | ok |
| camera movement | 7.17 | 1.8+ | ok |
| first clear movement | 0.2 s | ≤0.4 s | ok |
| brightness | 173 | 138-178 | ok |
| saturation | 0.19 | 0.17-0.38 | ok |
| warmth | 30.2 | 22-57 | ok |

All targets are met. The "len" target applies only to the long cut.

## QA (`pipeline/qa.py`)
- **Format:** 1080x1920, h264, 25 fps, AAC 44.1 kHz stereo, 15.000 s.
- **Sound sync:** every hard landing (thud, clack, bonk) is within 10 ms. A few soft sounds report larger offsets because the onset detector picks a nearby louder hit (for example a drawer swish 85-285 ms before a clack). Both are written from the same event list, so I believe these are detection misses, not desync.

## Render
Blender Cycles, 720x1280, 16 samples, adaptive 0.04, bounces 4/2/2, no bevel, upscaled to 1080x1920 in the encode.
- The final run took 7,396 s for its last 170 frames. 375 frames in total took about 3.3 hours of wall time. That includes a restart and long stretches sharing the CPU with the long-cut preview, so it was about 45-60 s per frame, against about 18 s alone.
- The process died once when the session's worker restarted, and resumed cleanly from frame 206.
- I stopped and resumed it once on purpose at frame 46, to apply the final plan's changes (whole-piece landings, rigid lift). Those changes don't affect frames before 5 s.

## Review gates
- **Gate 1 (preview, three rounds):** 5.5, then 6, then 6.5. It never reached 8 within the allowed three rounds. What changed between rounds:
  - Frame 1: tighter framing and a pale surround.
  - The wow moved from a high window-end view, where the rail's oak face hid the shirts, to a low view down the rail, and is held longer. The shirts are modelled with shoulders, sleeves and hangers.
  - The yellow duvet was muted, then made white.
  - The stair drawers were filled fuller.
  - The tail got two more landings.

  The last round's fixes (rail held longer, tail landings, colour) went in without another review.
- **Gate 2 (Blender stills):** scored 6. What I changed:
  - garments as real shirts, angled on the wardrobe bar;
  - a coloured shirt at the front of the rail;
  - a white duvet;
  - shoes on the wardrobe shelf;
  - mustard dropped;
  - brighter exposure and world fill;
  - a window view in the low shots.

  I didn't fix the black seam at the platform corner, or the drawer stacks that still read a little like soap bars.

## Honest notes and what I'd improve
- **Duvet:** the plan's ochre duvet was changed to white after three reviewers read it as mustard or cream. Warmth now comes from the oak and the terracotta and rust storage.
- **Top cupboard:** the final plan has it "drop onto the wardrobe". Under a 2.7 m ceiling a drop would pass through the ceiling, so it slides on whole from the aisle with a small hop.
- **Wardrobe moment:** the wardrobe station is close (the platform is 0.95 m away), so the closed doors fill the frame for about 0.5 s around 7.2 s and 8.5 s. That was reviewers' main remaining complaint.
- **Lights-on:** it is a modest payoff in daylight: the lamps glow, but the room doesn't change much.
- **Motion blur:** the swing between stations shows heavy motion blur for 2-3 frames. It reads as a whip.
- **With more time:** a slightly wider wardrobe shot (would need a cutaway), crisper stair-drawer contents, and a rug or runner for warmth on the floor.

## Long cut
Status: built (`ROOM_CUT=long`, 45 s), but not rendered yet. The code-renderer preview is in progress. Its Blender render (1,125 frames) follows, then encode and push of `out/same_bed_better_room_long.mp4` and `_sfx_only`.
