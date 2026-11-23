# The Bed on the Ceiling: report

Idea #5 (C9) of the top-10 slate. A 9 m² (3.0 × 3.0 m) bedroom with a sofa and a desk; a made double bed docks on the
ceiling in second 1 and later glides 2.06 m down onto the sofa on four 65 mm steel posts.

## Deliverables

| File | What |
|---|---|
| `out/bed_on_the_ceiling_15s.mp4` | 15 s cut, 1080x1920, 25 fps, original music + sounds (YouTube Shorts) |
| `out/bed_on_the_ceiling_15s_sfx_only.mp4` | same, sound effects only (TikTok / Instagram, add a trending sound) |
| `out/bed_on_the_ceiling_still.jpg` | wide at 10.6 s: the bed down on the sofa, posts, rail, book tower |
| long cut | not rendered yet (see Status) |

## What was built (`project.py`)

- **Shell**: 3.0 × 3.0 × 2.85 m, neutral white (242, 241, 238), light-oak planks, north window with a linen roller
  blind, door at the east end of the south wall, peg hooks with a coat and a tote.
- **Bed bay (west)**: blue-grey sofa (seat box, two lidded cushions, three 6 cm wall pads), two floor-to-ceiling book
  towers with a mustard → ochre → sage → slate gradient (one empty cubby for the long cut), four steel posts with floor
  and ceiling plates and belt slots, a ceiling rail with an LED strip, a plain motor box, a crank socket and one plain
  unlabelled button at 1.1 m.
- **The bed**: oak underside with four downlights, made bedding (`cloth()` duvet, terracotta throw, pillows), two straps,
  a safety-sensor strip, a 0.7 m front drawer. One rigid track: rise 0.60–1.20 s, park, smootherstep descent
  7.95–10.15 s (long cut: down 27.6–30.0, back up 44.7–47.0), stopping 2 cm above the sofa.
- **North**: light-oak desk with a three-drawer pedestal, laptop, lamp, mug, plant, chair; bedside alcove with the
  ottoman; fold-out nightstand on the NW tower (lamp, phone, mug).
- **East**: 1.4 m wardrobe: long hanging over a shoe pull-out; tee drawers, an upright fold-down ironing board and folded
  stacks; oak and mirror sliding fronts with steel pulls.
- **Stand-in** (`pipeline/figure.py`, light grey): pops in, presses the post button, steps back clear of the bed and
  looks up during the descent, then sits on the bed edge.
- **Sound** (`pipeline/music.py`, new kinds): `clunk` (dock), `deep` (landing), `tink` (posts), `riffle` (books),
  `bip` (button), `boing` (pillow bounce), `hum` (motor; the music dips about 4.5 dB under it). Music at 118 BPM.
- `pipeline/mkvideo_png.py`: `--grade` takes an optional third value, a brightness gamma.

## 15 s shot list

| Time | Station | What happens |
|---|---|---|
| 0.0–3.08 | S1 SE corner, push-in, tilt follows the bed | empty room with a sunbeam; planks land 0.02–0.46; made bed pops on the floor at 0.6 and docks on the ceiling at 1.2 (clunk); rail 1.4; four posts fly in whole 1.4–1.8 (tinks); towers 2.1; motor 2.15; books 2.1–2.5; sofa 2.55, pads 2.7, cushions 2.85, pillows 3.0, ottoman 3.0 |
| 3.3–7.08 | S2 from under the bed, east then north | wardrobe 3.3; pegs, coat, tote 3.5–3.8; garments 3.7–4.0; tee drawer opens 4.15, fills, shuts 4.8; folded stacks; oak and mirror fronts 4.96 / 5.1; desk 5.25; pedestal 5.45; drawer opens 5.6, fills, shuts 6.2; chair 6.35; laptop, lamp, mug, plant 6.55–6.94 |
| 7.3–10.78 | S3 the ride, SE three-quarter view, lowering with the bed | stand-in pops in 7.3, presses the button 7.65 (bip), steps back; downlights 7.85; **the bed descends 7.95–10.15** (hum), lands with the deepest thud; straps unclip 10.25; pillows bounce 10.35 (boing) |
| 11.0–15.0 | S4 low by the bed drawer, pull back and rise to the frame-1 pose | stand-in sits on the bed edge; bed drawer out 11.15 (pyjamas, book, eye mask), shut 11.6; nightstand flips out 11.6; lamp, phone, mug 11.8–12.05; cloud dims the sun 14% at 12.0; rail LED 12.2, shelf LEDs 12.5, nightstand lamp 12.8, desk lamp 13.1, phone glow 13.4; drift eases into the frame-1 pose (loop) |

10 storage moments in the plan; the 15 s cut shows 7 (book towers, wardrobe hanging, tee drawer + stacks, desk
pedestal, bed drawer, fold-out nightstand, mirror front). The sofa lids, ottoman and ironing board are long-cut moments.

## Metrics (`research/hh_metrics.py`)

| | dmed | s10 | calm | camera | fb | lum | sat | warm |
|---|---|---|---|---|---|---|---|---|
| target | ≥7.5 | ≥0.39 | ≤1.8 | ≥1.8 | ≤0.4 | 138–178 | 0.17–0.38 | 22–57 |
| preview (round 3) | 12.1 | 0.59 | 0.2 | 7.95 | 0.2 | 173 | 0.22 | 33.3 |
| **final 15 s** | **12.7** | **0.59** | **0.4** | **10.88** | **0.2** | **150** | **0.25** | **36.3** |

All eight pass (length is the long-cut test). Grade: `--grade 1.22,0.025,1.18` (the default 1.35,0.03 gave brightness
138, on the edge of the band). `qa.py`: 1080x1920 h264 25 fps, AAC, 15.000 s. Sound sync: almost every landing
within ±25 ms; a few report 50–300 ms where quiet sounds sit inside a cluster (the four post tinks, the book riffles,
the shelf-LED tick next to the rail chime); music.py places every sound at its event time, so these are
onset-detector misses, not drift. Every one of the 375 frames was checked for brightness outliers: none (the one
flag, frame 81, is the swing across the white wall).

## Review gates (fresh reviewer subagents)

- **Gate 1** (preview contact sheet): 6/10 in all three rounds. Fixed after each: first movement (0.8 → 0.2 s: darker
  subfloor, planks from higher and earlier), the opening tilt follows the rising bed, the ride re-framed so the bed,
  the closing gap and the sofa share the frame, the pedestal moved to the west end of the desk (see below), a real
  pull-back ending into the frame-1 pose, shorter swings, lights-on staggered to 13.4 s, mid-distance bed drawer.
  Not adopted: removing the terracotta throw / mustard pillow (both are in the plan; the throw was toned down and
  narrowed).
- **Gate 2** (Blender stills): 6/10. Fixed: the stand-in's hips hung off the bed corner (now seated on the mattress,
  feet on the floor), dark strap buckles → pale straps, black crank knob → steel, motor-box slats removed (read as a
  barcode), darkest garment → light grey, a black item in the desk drawer → cream, the wardrobe side out of the final
  frame.
- The brief asked for 8+; both gates stayed at 6 after the allowed rounds. The reviewers' remaining points are taste
  (one accent vs. the plan's palette; the frame-1 empty room is plain until the bed rises at 0.6 s; the stand-in is
  large in the last 3 s). Honest assessment: the hook (made bed rising and docking in second 1) and the ride read
  clearly; the weakest part is the last 2 s, which is a slow drift with the seated stand-in at the right edge.

## Changes from the plan

- **Desk pedestal at the west end** of the desk, not the east: at the east end its drawer would open into the
  wardrobe (only 15 cm between the wardrobe's north end at y 2.30 and the desk front at y 2.45). The chair tucks at the
  east end; the knee space and window are unchanged.
- Final top-10 version applied (coordinator): neutral white shell, posts / towers / rail land whole (no growing), a 14%
  cloud dip (cap 15%), one plain button with no icons.
- Camera poses tuned from the plan's starting poses after probes (the plan's S3 start sat inside the wardrobe's side).
- The stand-in steps back to x 1.86–2.04 (≥ 0.38 m east of the bed's front edge) and is never under or on the bed
  while it moves.

## Render

- 375 frames at 720x1280, Cycles 16 spp, adaptive 0.04, bounces 4,2,2, no bevel: 12,480 s (3 h 28 min), 29–34 s per
  frame (slower while probes ran alongside). The detached process survived a container restart.

## What I'd improve

- Frame 1 is a plain white corner until the planks land; a stronger sunbeam or a wider first pose would hook harder.
- The seated stand-in fills the right edge of the final 3 s; a sit spot further from the camera or a recline pose.
- Garments are simple tubes; real fabric folds would look more premium in the wardrobe close-up.
- Motion blur makes the 1.0 s rise soft; a slightly slower rise (0.6 → 1.3 s) would read sharper.

## Lessons for next time

- Check the plan's dimensions for drawer clearance before modelling: the east-end pedestal drawer would have opened into
  the wardrobe, which cost a layout change after two review rounds.
- `hh_metrics` "first movement" needs a mean change over 10 on the 45x80 grid at 0.2–0.4 s: planks of a similar
  brightness to the subfloor never register, so make the subfloor clearly darker than the floor and land the planks
  big and early.
- A camera tilted down for frame 1 loses a rising object off the top; tie the opening pitch to the object's height.
- Probe every station at its start AND end pose: a pose that sits inside a carcass or 0.4 m from a post looks fine in
  the plan's numbers.
- `figure.sit_pose` places the pelvis at `at`; for a bed edge put `at` 0.1 m inside the mattress, not on the edge.
- Don't run probes alongside the Blender render: it went from 29 to 34 s per frame.
- Background waiters stop at 2 h; re-arm them, and check the render process after any container restart.
- The default grade 1.35,0.03 put this neutral-white room at brightness 138 (edge of band); a gamma of 1.18 fixed it.

## Status

- 15 s cut: done and pushed.
- Long cut (49.5 s, `ROOM_CUT=long`): timeline and 15 stations written and probed (books, sofa lids, ottoman, desk scene,
  pillows hopping into the cubby, the ride, bed drawer, nightstand, wardrobe, ironing board, shoe pull-out, the bed going
  back up, lights). Next: low-res preview + metrics, both review gates, then about 10–12 h of Blender rendering.
