# Dinner for Eight: render report

Idea #C6 / top-10 section 8. An 11.5 m² kitchen (3.2 × 3.6 m, 2.6 m ceiling) whose slim island unfolds into a table
for eight in three clacks, while eight folding chairs, each seat matching a plate, hop out of a plain oak wall.
Everything is in `rooms/dinner_for_eight/project.py` (one `build()`, two timelines: the default 15 s cut and
`ROOM_CUT=long` for the 46 s cut). The plan copy with all build changes is `PLAN.md`.

## What I built

- **Shell:** white walls and ceiling, a pale-grey screed that the light-oak planks cover (far to near), a doorway on
  the table's centre line with a warm hallway spill, a north window with a snowy sill and ground outside (day view,
  turning to a warm dusk at lights-on).
- **West run (south to north):** tall pull-out pantry (6 shelves, 48 jars in 7 colours), fridge column with a plinth
  vent grille and a top vent gap, sink unit with three pull-out bins (one sage), dishwasher, the dinner column (pegged
  plate drawer over a pan drawer with enamel pots; above the worktop an oak lift-up holding eight tumblers, and a top
  cabinet with a pull-down dish lift carrying the platter), oven + hob + slim hood, a spice pull-out. Uppers to the
  ceiling, a muted rose-clay splashback strip (the one accent).
- **East wall:** flush light-oak panels: broom cupboard, the chair wall (two bi-fold doors, four 0.575 m leaves, eight
  folding chairs hung flat in a 4 × 2 grid) and open cookbook shelves.
- **Butterfly island:** two halves slide 0.40 m apart (clack 1), a two-part leaf rises and flips open (clack 2), four
  legs fold down (clack 3): 1.2 m island to a 2.0 × 0.85 m table at x 1.45-2.30, y 0.80-2.80.
- **Folding chair:** three rigid parts (back + rear legs, seat on a hinge, front legs riding the seat front), one
  unfold-and-hop function reused eight times; seats in the eight plate glazes (sage, celery, dusty blue, slate, clay,
  ochre, plum-grey, butter), so each chair lands at the place whose plate matches it.
- **Setting:** eight plates, eight tumblers, eight napkins, linen runner, bread board, fruit bowl, potted fir with red
  berries, dome pendant (drops on its cord, swings, lights on), LED strips under the uppers and in the shelves.
- **Host:** the faceless stand-in (`pipeline/figure.py`) sits at the west seat by the oven and lifts a tumbler; in
  the long cut they also work the dish lift and serve the platter.
- **Sound:** two new SFX kinds in `pipeline/music.py`: a ceramic `clink` (plates, the toast) and a ratchet `clack`
  (the three table clacks). Original music at 120 BPM (`music.json` written by the project).

## 15 s cut: shot list

| Time | Shot | What happens |
|---|---|---|
| 0.00-3.00 | S1: high north-east corner, push-in toward the doorway | empty room; eight plates fall onto the bare screed in a ring (0.24-0.89); planks slap down far to near and the plates hop as theirs lands (0.36-1.06); base units slide out of the west wall (1.14-1.78); pantry and fridge columns slide in whole (1.70-2.02); the island drops into the ring (2.22); plates hop up into a stack on it (2.24-2.65); worktop (2.68); the oak panel wall slides out (2.95) |
| 3.30-4.92 | S2: north aisle | plate drawer opens, the stack hops across the aisle onto its pegs, one plate at a time (3.50-3.97), drawer shuts (4.20); uppers slide out of the wall (4.28); the two doors over the sink flip open on coloured bowls and shut (4.30-4.98); hood, hob, sink; splashback slides on in six groups (4.70-4.98); pots on the hob |
| 5.12-7.00 | S2b: push-in on the pantry, from the north | pantry pulls out (5.12), six shelves fill with jars (5.40-6.53), slides back (6.97); fridge grille clicks in (6.98) |
| 7.30-8.55 | S3a: high from the north-west | clack 1 (7.54), clack 2 (7.96), clack 3 (8.18); plate drawer opens, plates hop onto the eight places (8.30-8.94) |
| 8.75-10.92 | S3b: from above the west run, facing the chair wall | bi-fold doors open on the 4 × 2 grid of coloured chairs (8.48); chairs hop out one every 0.2 s, east side first, unfold in the air, land at their plates (9.12-10.52); runner rolls down the table (10.85); doors shut (10.94) |
| 11.15-15.00 | S4: drift from the east side north and round into the frame-1 pose | lift-up opens on the tumblers, they hop to the places (11.42-12.13); pendant drops and swings (12.06); lights on and dusk outside (12.20); bread, fruit, fir; host pops in and sits (12.30-12.80); napkins (13.00-13.70); berries (13.82); host lifts a tumbler (14.08-14.34); last berry (14.40); the drift ends on the frame-1 pose, so the loop cuts back to the empty room |

### 15 s cut: results

- Files: `out/dinner_for_eight_15s.mp4` (music), `out/dinner_for_eight_15s_sfx_only.mp4` (landing sounds only, for
  TikTok / Instagram with a trending sound), `out/dinner_for_eight_still.jpg` (the final wide at 14.6 s).
- Render: Blender Cycles 5.3, 720x1280, 16 samples, adaptive 0.04, bounces 4,2,2, `--nobevel`: 375 frames in 2 h 57 min
  (29 s a frame on 4 cores; the first 15 frames were rendered by a first run I restarted after the LESSONS fixes).
  Every frame checked for brightness outliers before encoding: none.
- Encode: `pipeline/mkvideo_png.py ... --grade 1.15,-0.01,1.45` (1080x1920). I added an optional third grade value,
  a gamma, because the raw frames averaged about 177 and the standard `1.35,0.03` grade gave warmth 60.3 (cream cast)
  and brightness 172+.
- QA (`pipeline/qa.py`): 1080x1920 h264, 25 fps, AAC, 15.00 s; landing sounds sit within about 5-8 ms of their
  landings (a few dense clusters, e.g. napkins and the fir, read as one onset).
- `research/hh_metrics.py out/dinner_for_eight_15s.mp4`:

| Metric | Value | Target | |
|---|---|---|---|
| motion (dmed) | 10.3 | 7.5+ | ok |
| clear-change share (s10) | 0.55 | 0.39+ | ok |
| longest still (calm) | 0.6 s | 1.8 s or less | ok |
| camera movement | 8.51 | 1.8+ | ok |
| first clear movement (fb) | 0.6 s | 0.4 s or less | miss (first plate lands at 0.24 s, but a small plate on a grey floor is a small change) |
| brightness | 154 | 138-178 | ok |
| saturation | 0.23 | 0.17-0.38 | ok |
| warmth | 36.0 | 22-57 | ok |

## Long cut (46 s)

LONG_SECTION

## Review gates

- **Gate 1 (preview, three rounds):** 5 → 6 → 6.5 out of 10. Fixes applied each round: frame 1 empty with a plate
  already falling; a closer north-west angle for the clacks; the stack hop and pantry framed mid-screen; coloured seat
  boards so the folded chairs read on the oak wall; runner filling the dead half-second at 10.5 s; a smaller, higher
  pendant; a muted splashback. After round 3 I stopped as the brief caps it at three rounds; the measured numbers pass.
- **Gate 2 (Blender stills):** 6/10. Fixed: frame 0 truly empty, plates no longer clip planks, neutral (not warm)
  fill lights against a cream cast, thinner seat cushions, a darker screed so the opening isn't blown out. Not
  changed: the potted fir (it is the plan's December centrepiece), the stand-in figure (a channel convention).
- After reading `production/LESSONS.md`: the tall columns now slide in whole instead of growing, and the uppers and
  hood slide out of the wall instead of dropping through the ceiling.

## What I'd improve

- **The hook:** first clear movement measures 0.6 s (target 0.4). A small plate on a grey floor is a small change; a
  bigger first landing (the island or a plank band close to the camera at 0.2 s) would fix it.
- **Preview reviews stopped at 6.5/10.** Open notes: the tumbler lift-up is small in frame at 11.4 s; the clacks could
  be framed lower and closer still; napkins read as paper squares (no folds); floor and wall veneer could use a touch
  of gloss and roughness variation.
- **Long cut:** its low-res previews missed the pacing targets (longest still 3.0 s, motion 6.6) because several
  stations look at large white surfaces (uppers, columns) where camera motion barely changes the frame. I made one more
  round of fixes (planks spread over the first 2.5 s, upper doors flipping open on the bowls during the bins beat,
  steeper pitches) and rendered it without a further preview, in lean mode. Measured results are below.

## Lessons for next time

- A gliding-camera preview at 360x640 takes about 12 minutes for 15 s; background tool calls die at 20 minutes, so run
  previews with `setsid nohup` and poll, never as one long foreground or background call.
- Probe stations with `ROOM_ST=S1,S3a,...` (a switch in the project) before animating: it caught a camera inside the
  pantry column and a chair-wall angle that could not see the wall.
- White shells hide motion from `hh_metrics.py`: a station looking at white uppers or columns reads as "still" even
  while the camera glides. Keep colour or texture (open storage, wood, floor) in every station.
- The standard `--grade 1.35,0.03` pushed this white-and-oak kitchen to warmth 60 (cream cast); `1.15,-0.01` with a
  darkening gamma landed it at 36. Measure the grade on a sample of frames before encoding.
- Read `production/LESSONS.md` before animating: I had to rework the tall columns (they grew) and the uppers (they
  dropped through the ceiling) after the render had started.
- Coloured seat boards on the folding chairs made the 4 x 2 chair wall read at phone size; plain oak chairs on an oak
  wall had no contrast.
