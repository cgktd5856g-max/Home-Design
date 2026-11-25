# Not One Handle in Sight: report

Idea #7 (C11) from `research/top10_ideas.md`. A 9.6 m² bedroom (3.0 × 3.2 m) of flush, handle-free white push-latch
panels with a walk-in closet behind the west wall. White shell, light oak, olive bedding as the one accent; the colour
comes from filled storage (dusty teal, berry, sand, sky, blush and charcoal clothes, books, bags, a sky-blue suitcase).
No on-screen text, no logos, original music (music.py, 120 BPM, new chord loop).

## Deliverables

| File | What |
|---|---|
| `out/not_one_handle_15s.mp4` | 15 s cut, 1080x1920, 25 fps, music (YouTube Shorts) |
| `out/not_one_handle_15s_sfx_only.mp4` | the same with sound effects only (TikTok / Instagram, add a trending sound) |
| `out/not_one_handle_still.jpg` | final wide at 14.5 s (the loop pose, finished room) |
| `rooms/not_one_handle/project.py` | the room; `ROOM_CUT=long` selects the 44 s long cut (built, not rendered yet) |
| `rooms/not_one_handle/PLAN.md` | the plan, with the production changes listed at the top |

## 15 s shot list

| Time | Shot | What happens |
|---|---|---|
| 0.0-3.0 | high south-east corner, push-in | bare grey slab with a sun patch; planks land from 0.0; the closet platform and bulkhead slide out of the west wall (0.04-0.22); the panel domino (aisle face first, 0.30-1.34); door A springs open on the lit, packed rail (0.78-1.30, the teaser); headboard shelf, bed platform, mattress, olive duvet, pillows, bench, jute runner, oak ledge with books, print and plant (1.2-2.8) |
| 3.3-7.0 | aisle, close on the bedside panel, sliding back | the flap flips down into a lit ledge (3.3); lamp, books, phone (3.6-4.3); both bed drawers slide out (4.7 / 4.85); suitcase, rolled duvet, three vacuum bags drop in (5.1-5.9); drawers shut (6.3 / 6.45) |
| 7.3-9.2 | from the south-east, through door A | door A swings away from the lens and the closet light snaps on (7.15-7.45); the camera glides through the centre of the doorway and turns to the rails; the bottom rail fills one garment at a time (8.45-9.3) |
| 9.2-11.0 | hard cut: the dollhouse view from above the bed | the aisle face and closet ceiling are hidden; the whole lit walk-in; boxes slide onto the top shelf, shoes drop; the figure reaches up for a jacket |
| 11.0-13.0 | hard cut: overhead, turning | open wave (toe-kicks, bed drawers, bench lid, door A, the desk folds down, 11.0-11.3); the six shut in one ripple round the room with rising latch ticks (11.75-12.5); cove LEDs on round the room (12.55); a toe-kick pops back open (12.85) |
| 13.0-15.0 | descent into the frame-1 pose | a throw drops on the bed (13.3); the drawer clicks shut (14.0); the camera eases into the exact frame-1 pose, so the video loops |

## Measured (research/hh_metrics.py on the final)

| Metric | Result | Hits' range |
|---|---|---|
| motion (median change per 0.2 s) | 11.6 | 7.5+ |
| share of clear changes | 0.64 | 0.39+ |
| longest still | 1.0 s | 1.8 s or less |
| camera movement | 8.29 | 1.8+ |
| first clear movement | 0.2 s | 0.4 s or less |
| brightness | 173 | 138-178 |
| saturation | 0.23 | 0.17-0.38 |
| warmth | 37.3 | 22-57 |

Every 15 s target is in range (length applies to the long cut only). Every second of the final is at brightness 150 or
above. `qa.py`: 1080x1920, h264, 25 fps, AAC, 15.0 s. Its sound-sync list flags several landings in the ripple and the
drawer gag as up to 0.4 s off; those are detector merges of sounds 0.1-0.15 s apart, as HANDOFF section 9 explains.
music.py places every sound exactly at its landing time.

## Render

- Blender Cycles, 720x1280, 16 samples, adaptive 0.04, bounces 4,2,2, no bevel; encoded to 1080x1920 with
  `--grade 1.35,0.03`.
- Render time: about 3.9 h of machine time for 375 frames (25-40 s a frame). That includes 106 frames rendered twice:
  97 with a black floor from Cycles persistent data, plus 8 opening frames with a stray door sliver.
- The rail close-up inside the closet (8.0-9.2 s) and the overhead wave (11-12.5 s) rendered dim (down to 86). A
  smoothed per-frame gamma lift (minimum gamma 0.56, 121 frames) brings every frame to about 150 or above before the
  grade. No frame was re-rendered for this.

## Reviews

- Review gate 1 (three fresh reviewers on the low-res preview): 5, 6 and 5 out of 10. Fixed from their notes:
  - the teaser moved into the frame centre;
  - a door swinging into the lens was refilmed from the other side;
  - dead white stretches were cut;
  - the dollhouse was reframed so the rails aren't seen end-on;
  - the overhead was framed tighter, and the floor plant left out of it;
  - colour lands earlier;
  - the end eases into the frame-1 pose;
  - nothing smears across hard cuts.

  Not done: the reviewers disagreed on the teaser and on the dollhouse width, and the plan won. Hair and faces on the
  figure were not added (house style).
- Review gate 2 (one reviewer on the Blender stills): 5/10. Fixed:
  - garments are now shaped meshes on oak hangers, not slabs;
  - storage colours muted to dusty tones;
  - greyer olive;
  - paler oak;
  - rail support rods.

  Still weak: folded stacks read as soft rounded bars rather than fabric. No reviewer saw the final video.

## What I'd improve

- Folded clothes need fold lines and a knit texture; the faceless figure reads as a mannequin (deliberate).
- The rail close-up is dim at render time; a brighter rail light (or a wider pull-back) would avoid the post lift.
- The lights-on beat is hard to see from the overhead camera; the coves only read during the descent.

## Long cut

Built in the same project (`ROOM_CUT=long`, 44 s, 7 zones: toe-kicks, ledge, bed drawers, bench, desk, the
flap-and-shelf rack, the walk-in, the dollhouse, the person walking in through door A and out through the mirror, the
overhead finale). Code-renderer probes and four Blender test stills are checked. Still to do: a low-res preview with
`hh_metrics.py`, then the detached render (about 1,100 frames, roughly 8-11 h at 25-35 s a frame).

## Lessons for next time

- A solid carcass box behind a fold-down desk hides the recess contents: build carcasses as walls around every opening
  (cost one test round).
- Cycles persistent data blacked out the floor from the moment a light switched on until another one did (frames
  102-193 of 375): set `BLENDER['persistent'] = False` for every final render.
- The hinge helper showed a squashed sliver before the piece landed: hide every piece until its landing starts (8
  frames re-rendered).
- Hard cuts in a gliding-camera video smear in both renderers: keep the camera pose constant up to the cut and open
  the shutter at the frame (`pipeline/blender_render.py` change on this branch).
- Close-ups inside an enclosed closet render dark (brightness 86-103) even with an area light: give the closet two
  lights (ceiling and under the hat shelf) at twice the room's LED radiance, or pull back.
- A door hinged on the far side swings straight into a camera facing it: film a swinging door from the hinge side's
  opposite diagonal so the leaf moves away from the lens.
- Garments on a rail seen end-on read as one slab, and slab garments look like cardboard: use the shaped garment mesh
  in this project (`garment()`) and film rails at an angle.
- The ffmpeg `fps=2` filter samples frames slightly late, so a contact sheet showed a reviewer the wrong frame 1: build
  review sheets with `select='eq(n,...)'` at exact frame numbers.
