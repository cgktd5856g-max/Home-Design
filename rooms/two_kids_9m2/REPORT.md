# Two kids, one room: "Tape Line, Turning Wall" — report

## What was built

A 12.2 m² kids' room (3.6 × 3.4 × 2.7 m) for two siblings, built entirely from code (`project.py`) and rendered in
Blender Cycles. A two-tone tape line (celery | blue) zips down the middle of the empty room and the two halves build
at the same time. A loaded double-sided wardrobe (1.5 × 0.5 × 2.2 m, on casters, with a steel pivot post and a curved
floor track) swings 90° off the far wall onto the tape and telescopes a slatted oak end panel. One playroom becomes
two bedrooms, and at the end it swings back so the last frame matches frame 1.

- **West, child A (celery):** loft bed at 1.6 m with a slatted rail and ladder; a book wall facing the door; an
  under-loft desk with a drawer, lamp and stool.
- **East, child B (soft blue):** mid-sleeper at 0.9 m with four stair drawers; a den under it (sliding door, LED,
  cushions, picture books); a small desk and shelf outside the swing arc.
- **Wardrobe:** face A has oak doors over folded shelves, two drawers, coloured bins and a hatch. Face B is a blue
  cubby grid, reachable only once the wardrobe has swung; 12 bins fill it.
- **Arc check (top view):** swept radius 1.27 m. Nearest clearances are B's bed corner at 1.43 m, B's desk at 1.38 m
  and the floor lamp at 1.58 m. No figure is inside the arc while it moves.

Concept history: this session started on the brief's "slatted partition, 9 m²" design (kept as
`project_slatted_v1.py`, preview only). Mid-session the coordinator switched the slot to the judged winner C2, and I
reconciled it with `production/plans/C2.md`.

## 15 s cut — shot list (`out/two_kids_9m2_15s.mp4`, `_sfx_only.mp4`, `out/two_kids_9m2_still.jpg`)

| Time | Shot | What happens |
|---|---|---|
| 0.0-2.45 | doorway, dolly up the tape (88° lens) | empty pale room with a sunbeam; the tape zips; oak planks slap down in mirrored pairs; loft deck ⟷ mid-sleeper (double thud); pivot post + track clank; the wardrobe slams on; ladder ⟷ stair columns; rails; **28° tease nudge** and clunk back; mattresses |
| 2.7-3.7 | A's side | duvets, pillows; the book wall fills left to right; reading lights; the two rugs |
| 3.72-7.0 | B's side, low and close | stair-drawer wave (open bottom → top, fill, close top → bottom); the den door slides open, LED, cushions in, shut |
| 7.04-9.0 | A's entry corner, 1.9 m | face A doors open on loaded shelves + a drawer fills, then close; **the swing 7.95-8.92** (whoosh → latch clunk) |
| 9.04-9.95 | daylight payoff wide on the tape | wardrobe on the line, A left, B right; the end panel telescopes out |
| 10.15-11.3 | from B's bed | 12 bins + books cascade into face B's cubbies |
| 11.55-12.35 | night, A's side | dusk; A's reading light, loft LED, desk lamp; child A on the loft |
| 12.55-15.0 | night, B's side → frame-1 pose | child B on the mid-sleeper; B's lamp, downlights; panel retracts; **the wardrobe swings back**; a plush lands on the rug; the end pose equals frame 1 |

## Metrics (`research/hh_metrics.py`, final 15 s)

| metric | value | target |
|---|---|---|
| motion (dmed) | 9.3 | 7.5+ |
| share of clear changes | 0.47 | 0.39+ |
| longest still | 0.4 s | ≤ 1.8 s |
| camera | 6.31 | 1.8+ |
| first movement | 0.4 s | ≤ 0.4 s |
| brightness | 151 | 138-178 |
| saturation | 0.24 | 0.17-0.38 |
| warmth | 34.4 | 22-57 |

All eight are in the hits' band. `pipeline/qa.py`: 1080×1920 H.264 25 fps, AAC 44.1 kHz, 15.0 s. Landings are within
±10 ms of their sounds through the build. In the night section the long, overlapping chimes merge into fewer
detected onsets; I checked the waveform by hand and the sounds are at the right times.

Review gates: gate 1 (preview) passed at 8.5/10 after three rounds; gate 2 (Blender stills) ended at 7.5/10 with its
remaining fixes applied (flat fabric bins, cooler night downlights).

## Render time

About 24 s per frame alone at 720×1280, 16 spp; 45-58 s when sharing the CPU with a preview. Two container restarts
killed the detached render (at frames 103 and 107). The 15 s cut took about 5 h of wall time instead of the 2.5 h
it needed. 125 frames were re-rendered afterwards (see below).

## Fixes after the first encode

- A black notch at the loft corner (the book wall had no top panel, so there was a hole under the deck corner): a top
  panel was added and the 125 frames that show that corner were re-rendered.
- One fully motion-blurred in-between frame at 3.72 s (the "cut" between two shots left a frame mid-swing): the next
  shot now starts on that frame.

## What I'd improve

- Frame 1 is clean but soft: a pale empty room with a sunbeam and the tape. A stronger hook (the tease swing in frame
  earlier, or a lower, closer start on the tape) could test better.
- The night section is staged around two static seated mannequins. A climb into bed would make the person moment
  stronger (it is in the long cut's hatch handover instead).
- The 15 s cut swings back at the end (the wow plays twice); C2's plan ended split and lit. Worth A/B-ing.

## Lessons for next time

- **Container restarts kill detached renders.** Keep a waiter running (Bash in the background, an until-loop) for
  the whole render, re-arm it before it times out, and check the frame count, not just the log.
- **Never run a preview alongside the final render.** It halved Blender's speed (24 → 46 s per frame).
- **A concept switch mid-session cost about 3 hours.** Read the coordinator's branch for plan updates before
  modelling, and wait for the plan doc when it is announced as imminent.
- **Pivot geometry:** put the pivot at the centre of the wardrobe's depth so it lands centred on the tape. Check the
  swept radius against every corner in top view first; it is 1.27 m for a 1.5 m unit, not √(L² + D²).
- **"Hard cuts" need a gap no longer than one frame.** Two holds 0.04 s apart at 25 fps leave one in-between frame
  mid-swing, which renders as a full-frame smear.
- **Close every box.** An open-topped carcass under a deck shows as a black hole in Cycles. Probe the corners at full
  resolution before the final.
- **Long holds need bigger camera moves.** The long cut's stations reused the 15 s deltas over 3-4 s and failed the
  motion targets; scale the move to the hold length.
