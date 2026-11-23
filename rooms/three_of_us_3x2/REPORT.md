# Three of Us in 3 × 2 m (C1) — render report

**Status:** 15 s cut rendering in Blender (draft report; numbers below are filled in as each stage finishes).

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

## Final (to fill in)

- Render time, hh_metrics on the final, qa.py result.

## What I'd improve

- First clear movement is 0.8 s in the measurement (target 0.4 s): frame 1 is mostly white wall around the crib, so
  0.2 s steps change little until the deck lands.
- The faceless mannequins still read as mannequins; reviewers found them a little cold.
- Long cut: the plan's "parent 1 pulls the skinny rail out" is not staged — the parents' rail now runs parallel to the
  front so the bay reads sparse, and the shrug carries the joke on its own.
