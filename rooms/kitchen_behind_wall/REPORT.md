# The Kitchen Behind the Wall (#10, C14): report

## What was built
`rooms/kitchen_behind_wall/project.py`: a 14 m² studio (4.0 × 3.5 m, 2.7 m ceiling). It has a white storage bed with three birch drawers on the west wall and a wall of four birch bi-fold panels (0.64 × 2.45 m) on the north wall. The panels fold into a 20 cm pocket. Behind them a kitchen builds: a pale sage stack-bond tile, oak base units, a pale-grey worktop, sink, hob, white uppers, a hood with its duct, an oak jar shelf, a two-door cupboard and kidney shelves in the blind corner. The east wall has a tall birch return with a larder (five inner drawers) and a fridge (fixed door, slatted grilles). In the wow, oak lids drop over the hob and sink, the sink cover slides out 25 cm as a knee ledge, the stool glides over from the bed, and a faceless grey-denim stand-in steps in and sits down. No on-screen text and no logos; the music and sounds are original (`pipeline/music.py`, 120 BPM). One project file serves both cuts: `ROOM_CUT=long` selects the 46 s cut.

Deliverables: `out/kitchen_behind_wall_15s.mp4`, `out/kitchen_behind_wall_15s_sfx_only.mp4` and `out/kitchen_behind_wall_still.jpg`, all 1080x1920 at 25 fps, graded `--grade 1.35,0.03`. The long cut is coded but not yet rendered.

## 15 s shot list
| Time | Shot | What happens |
|---|---|---|
| 0.0-3.0 | S1, doorway push-in | Closed birch wall; folds from 0.04 s (four clacks, 0.10-0.30), stack into the pocket (0.54); sage tiles slap in right to left (0.30-1.0); base units slide in (0.9-1.6); worktop, sink, hob, fruit, tap, soap |
| 3.3-7.0 | S2, slide east along the run | Uppers fly in, open corner shelves, hood, duct, jar shelf, jars and mugs ripple in; the two-door cupboard opens on plates and blue bowls and shuts; the corner door opens, two kidney shelves glide out, enamel pots land, they glide back |
| 7.3-8.36 | S3, larder | The door swings to 115°, five drawers cascade out and fill with coloured jars and tins, then close |
| 8.56-10.75 | S3B, desk, three-quarter (the wow) | Hob lid and sink cover drop on, the ledge slides out, the stool glides over from the bed, laptop and lamp land, the stand-in steps in and sits (10.18), a mug lands, the head turns to the window |
| 11.0-13.6 | S4, lit run, slide with a height change | Stool and ledge go back; under-cupboard LEDs, jar-shelf LED, lamp and hood light switch on (daylight eases to 85%); herb pot, tea tin, board, mugs, kettle, herbs and vase land |
| 13.9-15.0 | S5, closing wide | The stack slides out and the panels unfold shut (four falling clacks); the inside lights go off; the last frame matches frame 1, so the video loops |

## Measurements (final, `research/hh_metrics.py`)
motion 10.1 · clear changes 0.53 · longest still 0.4 s · camera 7.14 · first clear movement 0.2 s · brightness 154 · saturation 0.27 · warmth 42.4. All in the hits' range; only length is off (34-46 s, which applies to the long cut). Brightness per second before the grade: 142-171. No frame has black patches. Sound sync from `qa.py`: within ±10 ms, apart from detector merges of close sounds (for example mugs2, +196 ms).

## Review gates
- **Gate 1 (preview):** 6.5, then 7, then 6.5. I stopped at the 3-round cap. Fixes applied: a mid-tone stand-in, a new three-quarter desk angle with a sit-down, larder framing, landings during the lit section, a split final wide and a faster fold.
- **Gate 2 (Blender stills):** 6. Fixes applied: the niche fill light was pointing up into the bulkhead and is now turned the right way; carcass and drawer panels had coplanar overlapping faces that rendered black edges and now butt between the sides; the hood chimney is one clean box; jars are colour-filled with varied lids; the sage is greyer and the pots matte.

## Render
Blender 5.3 Cycles, 720x1280, 16 spp, adaptive 0.04, bounces 4,2,2, `--nobevel`: about 31-40 s a frame, roughly 4.5 h in all over three runs. A container restart killed the first run. In the first pass, frames 147-213 came out with the tall birch door solid black: this is the Cycles persistent-data bug. I re-rendered those frames with `BLENDER['persistent'] = False`.

## What I'd improve
- There is no real knee space under the desk: the knees sit under the 25 cm ledge in front of drawer fronts.
- The stand-in has mannequin slab feet.
- The lights-on is subtle in daylight (rules cap the daylight dip at 85%).
- The corner open shelves are partly hidden by the tall return.

## Lessons for next time
- Check every `rect_light`'s `cross(eu, ev)` sign when you add it. The niche fill faced +z for a whole preview cycle and blew out the bulkhead in Blender.
- Never let panels overlap with shared outer faces (a full-width bottom between full-height sides): Cycles draws black edge lines. Butt the panels between the sides with a 0.5 mm gap.
- Contact sheets made with ffmpeg's `fps=2` can show a mid-motion frame as "0.0 s". Make reviewer sheets with `select='not(mod(n,12))'` so tile 0 is frame 0.
- Set `persistent=False` from the start of any final render longer than about 100 frames (67 bad frames here).
- A Bash waiter can't outlive 2 h. Re-arm it, and after any container restart check `pgrep` and restart the render script.

## Long cut (46.0 s, 1,150 frames)
`out/kitchen_behind_wall_long.mp4` and `_long_sfx_only.mp4`, graded `--grade 1.35,0.03`. Rendered with no preview and no review gates: the owner asked to save credits, so `.render/kitchen_behind_wall/autopipe.sh` rendered, scanned, encoded and pushed it on its own. The render took about 13.3 h at about 42 s a frame. The scan found 0 bad frames.

**Metrics:** brightness 153, saturation 0.25, warmth 38.2, camera 3.79 and length 46.0 are in range. **Off:** motion 5.7 (target 7.5+), clear changes 0.22 (target 0.39+), longest still 3.8 s (target 1.8 or less), first clear movement 3.4 s (target 0.4 or less).

The long cut was never tuned on a preview the way the 15 s cut was. Its first shot builds slowly, with tiles every 0.11 s and base units at 1.2-2.0 s, and several stations hold close on a single mechanism. To bring it into range, apply the 15 s fixes: a faster first push-in and fold, shorter and closer holds in A1, A7 and A8, and more landings in the bed and over-bed beats. Preview at 216x384 and check `hh_metrics.py` before re-rendering.
