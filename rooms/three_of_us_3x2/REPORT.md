# Three of Us in 3 × 2 m (C1) — render report

**Status:** 15 s cut done — `out/three_of_us_3x2_15s.mp4` (music), `out/three_of_us_3x2_15s_sfx_only.mp4`, `out/three_of_us_3x2_still.jpg`. Long cut: timeline written; preview, gates and render next.

## What I built

`rooms/three_of_us_3x2/project.py` — one project, `ROOM_CUT=15` (default) or `ROOM_CUT=long`, sharing `build()`.

A 2.0 × 3.0 m bedroom, 2.9 m ceiling, neutral white shell, light birch, celery accent:
- **Bed deck** wall to wall at 1.20 m (y 1.5-3.0) on two pale-grey posts, barred guard rail, 10 cm landing, a standard
  double mattress (1.90 × 1.35 m), sage duvet, two pillows, a muted mustard throw.
- **Crib on castors** (0.56 × 0.92 m, birch slats, sky-blue sheet) that parks under the deck by day and rolls out beside
  the stair at night; a crib drawer (long cut); an open crib-bay shelf behind it filled with colour-coded packs and an LED.
- **4-step drawer stair** (0.24 m rises, 0.25 m treads), celery riser-drawer fronts, drawers up to 0.95 m long (step 4
  comes 0.75 m out), pale-grey handrail, LED under every tread.
- **Baby pull-out** (1.22 m travel) under the deck: low birch front, end-on rail of tiny outfits, two bins.
- **Wardrobe** (3 × 0.5 m bays, birch fronts, top cabinets from 2.05 m): bay C, the parents', is sparse (three dark
  garments); bays A and B, the baby's, fill with tiny outfits, stacks and baskets; changing flap folding down into a
  0.5 × 0.9 m top with a mat; nappy drawer; toe-kick step drawer and lift-up top flap (long cut).
- **Bridge cabinet** over the door with lift-up flaps (rolled duvet, suitcase, box in the long cut).
- **Niche** in the north wall beside the window: night light, books (monitor and phone in the long cut).
- **Two faceless stand-in parents** (`pipeline/figure.py`), matte warm grey and soft blue.
- Evening: lavender-peach window, daylight and fills kept at 85-90 %, staggered lights (reading light, tread LEDs bottom
  to top, crib-bay shelf LED, night light).

No on-screen text, no logos, no readable props (blank book spines, unlabelled packs, a blank monitor glow).

## 15 s cut — shot list

| Time | Shot | What happens |
|---|---|---|
| 0.0-3.2 s | hall, crane up + push in | crib flies in from the lens and lands (0.26 s); planks slap far to near; posts; **deck slams in wall to wall (0.82 s)**; crib-bay shelf fills with packs; crib rolls into its bay (1.75 s); guard rail, mattress, duvet, pillows, throw, night light, books, reading light |
| 3.5-7.0 s | high from the hall over the stair, slide + pan right | stair blocks drop bottom to top; handrail; four riser drawers slide out toward the lens and fill in turn (jumpers, sheets, sleep sacks, towels), step 4's long drawer; the baby pull-out glides out, tiny outfits tick onto its rail, it glides back |
| 7.3-10.7 s | west cut-away, full-height wardrobe, crane up + push in | bridge cabinet lands; wardrobe carcass slides out of the wall; **wow: the parents' bay opens first (bwomp) on three dark garments, then the baby's two bays burst open and fill (pip-pip-pip)**; changing flap folds down, mat; nappy drawer fills and shuts; doors close in the swing |
| 11.0-12.95 s | low on the crib and stair, truck left | dusk; crib rolls out beside the stair; parent 2 pops in on the deck, parent 1 on step 2; reading light, tread LEDs bottom to top |
| 13.25-15.0 s | hall wide, crane up into the frame-1 pose | shelf LED, night light; parent 1's hand rocks the crib; parent 2 lies back, duvet settles; loops to frame 1 |

## Process and review gates

- Probe stills from every station, then animation probes; fixed: speckle from the north-window sun (always-sampled now),
  black edges on frame 0, doors visible before the wardrobe landed, the handrail crossing the wardrobe shot (hidden in that
  hold), the niche hidden behind the wardrobe (moved to the north wall), the stair shot moved to the hall side.
- **Review gate 1** (fresh reviewer, contact sheet + metrics + plan + checklist): 5/10 → 6.5 → 6.5 in three rounds (the
  maximum). Fixes applied each round: sparse parents' bay opening first, crib flying in large at frame 1, pull-out with a
  low front, closer framing of every beat, studio enclosure (no black voids in swings), doors closing in the swing, closer
  hall camera so the room fills the frame. **It did not reach 8/10**; the last round's framing fixes are applied but were
  not re-scored.
- **Review gate 2** (Blender stills): 6/10; fixed hook haze (softer sun, plank order), matte mannequins, muted throw,
  neutral-warm LEDs, under-deck fill, window-frame and crib overlap artefacts, plank seam at the wall.

## Preview metrics (code renderer, 15 s cut)

```
dmed 8.8 ok | s10 0.36 OFF (target 0.39) | calm 0.8 s ok | camera 4.84 ok | fb 0.8 s OFF (target 0.4)
lum 166 ok | sat 0.24 ok | warm 35.4 ok
```

## Final 15 s cut

- Blender Cycles, 720x1280, 16 spp, adaptive 0.04, bounces 4/2/2, no bevel; 375 frames at about 25 s each =
  **2 h 24 min** of render (8,632 s for 345 frames after a restart, plus 30 frames before the container slept).
- Encoded to 1080x1920 with `--grade 1.35,0.03`. Frame brightness check: no black or outlier frames (one flag in a
  camera swing, a false positive).
- `qa.py`: 1080x1920 h264 25 fps, AAC 44.1 kHz stereo, 15.0 s. Landing sounds land within about 10 ms of their pieces
  wherever the onset detector can separate them (dense clusters and chimes with long tails merge in its readout).
- `hh_metrics.py` on the final:

```
dmed 8.6 ok | s10 0.36 OFF (0.39) | calm 0.6 s ok | camera 5.72 ok | fb 0.6 s OFF (0.4)
lum 142 ok | sat 0.30 ok | warm 42.5 ok        (len n/a for a 15 s cut)
```

Two misses (the brief aims for at most one): the share of clearly changing steps (0.36) and first clear movement
(0.6 s). Colour lands mid-band: no cream cast, saturation from the filled storage.

## What I'd improve

- First clear movement is 0.8 s in the measurement (target 0.4 s): frame 1 is mostly white wall around the crib, so
  0.2 s steps change little until the deck lands.
- The faceless mannequins still read as mannequins; reviewers found them a little cold.
- A few thin black seams show on the wardrobe's end panel in the last 2 s (overlapping carcass boxes, like the ones I
  fixed on the window frame and crib).
- The share of clearly changing 0.2 s steps (0.36) is just under target: the wardrobe-fill stretch (8.6-10.4 s) changes
  in small, many-piece steps; a faster camera there or bigger single landings would lift it.

## Lessons for next time

- Overlapping boxes (frame members, rails over posts) render black dots or seams in Cycles: build members that butt, never overlap.
- A small, very bright light that most points can't see (a north-window sun under a deck) speckles the code renderer: mark it always-sampled.
- Hidden walls leave black void in swings and odd angles: put a white studio box around the set from the start.
- Choose each station by which way the moving fronts face (drawers facing south need a camera from the south), before modelling.
- Long detached renders die when the session idles: keep a background until-loop waiter armed for the whole render.
- Faces of hanging garments seen end-on read as one slab; to read "sparse", hang few short garments parallel to the front.
- Long cut: the plan's "parent 1 pulls the skinny rail out" is not staged — the parents' rail now runs parallel to the
  front so the bay reads sparse, and the shrug carries the joke on its own.
