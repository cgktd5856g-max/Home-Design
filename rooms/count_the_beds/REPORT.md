# Count the Beds: render report

Idea #9 (C7) from `research/top10_ideas.md`. A 10.2 m² (3.4 × 3.0 m) kids' room for two that sleeps five: a podium
with a hollow, a steel raised bed over a low bed, a fold-out futon under the landing lid, a double on castors that
rolls out of the podium and pops up to chair height, a stair along the south wall, top cabinets over the west wall,
a fold-down desk for two, coat hooks and a night step. Neutral white shell, light oak, pale-grey steel, one slate
accent; colour from clothes, books, pencil pots, bags and the rug. No on-screen text.

Files: `project.py` (room, 15 s timeline, camera, lights, Blender look), `long_cut.py` (the 46 s cut, `ROOM_CUT=long`),
`PLAN.md` (copy of the plan), `progress/` (checkpoints). Pipeline change: `pipeline/music.py` gained the event kinds
`pluck` (a pitched note, for the five rising "count" notes C5 D5 E5 G5 A5), `bell` (original two-note doorbell),
`rumble` (the double rolling) and `clank` (steel).

## 15 s cut: shot list

| Time | Shot | What happens |
|---|---|---|
| 0.0-2.9 | doorway dolly in (eased: fast start = the loop's speed) | doorbell; a slate rug unrolls; the slate suitcase skids in past the lens (lands 0.34), white case 0.52, backpack + sleeping bag 0.70; podium slaps down in three sections (0.95-1.25); low mattress; steel ledger clank, corner post, raised deck, mattress; under-deck shelf and book ledge fill; four stair blocks rise west to east; duvets; reading light 1 + note C, light 2 + note D, pillows |
| 3.2-5.05 | west wall: linen + wardrobe | coat hooks + two kids' jackets and a tote; the top cabinet run lands; linen doors open, stacks of folded duvets by colour, slam; wardrobe doors open, pull-down rail swings down with clear-coloured kids' clothes, lifts, doors slam |
| 5.35-7.0 | desk + guest cabinet | niche appears, desk flap drops, pigeonholes fill with books in a ripple, pencil pots; guest flap lifts, the three bags fly up into it, flap slams; desk folds flush |
| 7.3-8.6 | futon | landing lid lifts, folded futon rises, slides onto its place, lid shuts, the futon unfolds north in three clacks; light 3 + note E, slate pillow |
| 8.85-10.75 | the wow, low at the lens | latch click; the double rolls 1.2 m out of the podium toward the lens (rumble), the LED in the hollow glows; legs clack down and it rises to 50 cm with an overshoot; the oat throw flies on and opens on its hinge; lights 4 and 5 + notes G and A, pillows; the night step slides out |
| 11.05-15.0 | final: from the hallway back into the frame-1 pose (38° sweep) | grandma (slate) and grandpa (grey, feet on the night step) pop in on the double's foot end; cane; window turns to a peach dusk; the five reading lights swell with an echo of the five notes; ends on the exact frame-1 pose (loops) |

Storage moments in the 15 s cut: coat hooks, linen cabinet, wardrobe pull-down rail, desk + pigeonholes, guest cabinet
swallowing the bags, futon from the landing box, the double from the podium, the night step (8).

## Results (15 s cut)

Deliverables: `out/count_the_beds_15s.mp4` (music), `out/count_the_beds_15s_sfx_only.mp4`, `out/count_the_beds_still.jpg`
(the final wide at 12.0 s). 1080x1920, 25 fps, 375 frames, graded `--grade 1.5,0.05`.

`research/hh_metrics.py` on the final:

| Metric | Value | Target |
|---|---|---|
| motion (median change per 0.2 s) | 9.7 | 7.5+ |
| share of clear changes | 0.49 | 0.39+ |
| longest still | 0.2 s | 1.8 s or less |
| camera movement | 6.77 | 1.8+ |
| first clear movement | 0.2 s | 0.4 s or less |
| brightness | 167 | 138-178 |
| saturation | 0.22 | 0.17-0.38 |
| warmth | 32.1 | 22-57 |
| length | 15.0 | 34-46 (long cut only) |

Every target passes except length, which applies only to the long cut. Per-second brightness of the raw frames is
145-187, so the dusk end stays above 140. No frame has black patches (pixels under 12 over 2% of the frame: 0 of 375).
`qa.py` sound sync: the landing sounds sit within a few ms of their landings. A few onsets are flagged, such as the dusk
swish (+191 ms); that is the detector, since swishes ramp up to the landing.

Render: Blender Cycles 720x1280, 16 samples, adaptive 0.04, bounces 4,2,2, no bevel. About 30 s a frame alone and
45-65 s while a preview shared the CPU. Two container restarts cost resumes; total about 4.5 h of wall time.

Review gates: gate 1 (preview) scored 6, 6.5 and 6.5 over the three allowed rounds, so it never reached 8. The fixes
from every round went in before the final render:
- frame 1 shows the window;
- all three bags land in frame;
- the cabinet lands as the swing settles;
- a calmer solid rug;
- a bigger, overshooting pop-up;
- the grandparents seated off to the right, slate and mid-grey, with grandpa's feet on the night step;
- one glide from the hallway into the exact frame-1 pose.

Gate 2 (Blender stills) scored 6. Its fixes went in too:
- the black seams at coplanar faces (desk niche, rail posts);
- a missing futon-box lid;
- cream items made grey or blue;
- brighter exposure and sky.

### What I'd still improve
- The grandparents remain the biggest thing in the last 3.5 s. A wider final framing or smaller figures would let all
  five beds read more clearly.
- The lights-on payoff is subtle: five warm pools and a peach window, but no big contrast change.
- Duvets are rigid cloth shapes and the clothes read as flat boards; real soft goods would look more premium.
- At the strong grade the walls lean slightly warm in the dusk frames (warmth 32 overall, still inside the band).
- The long cut is not rendered yet. Its first preview missed the motion targets (motion 4.2, a still of 2.6 s), and its
  cameras have been reworked since but not re-measured.

## Lessons for next time
- Coplanar faces (a 1 mm back panel flush with the wall, rail ends flush with a post) render black in Cycles but fine
  in the code renderer. Overlap them by a few mm or leave a gap.
- When replacing a block of `build()` code with a script, diff the piece list afterwards: a whole piece (the landing
  lid) silently disappeared and was only caught two reviews later.
- Running a preview next to the Blender render roughly doubled the render time (30 s to 60 s a frame); don't.
- A slow final glide (0.5 m over 4 s) costs a lot of motion and clear-change share. Sweep 30-40 degrees of yaw in
  every hold instead.
- Seated figures at the foot of a bed 1.2 m from the doorway fill the loop frame. Place them off-centre before the
  first review.
- `mkvideo_png.py --grade 1.5,0.05` brought a neutral white Blender room (saturation 0.12, warmth 10 raw) into the
  hits' band.

