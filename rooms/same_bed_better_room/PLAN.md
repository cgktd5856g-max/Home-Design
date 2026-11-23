<!-- id: C4 | reviewer_score: 6 | verdict: ok -->
<!-- one_line: Overhead tile-puzzle fix of a real bad bedroom layout for a couple (bed dead centre, wardrobe doors bonking its foot) into a corner bed on one 1 m storage platform with a 1.4 m pull-out shirt rail; a Dec-Jan "fix this layout" test, not a top bet. -->

## Same Bed, Better Room

**Pitch**: Seen from above, an empty 9.3 m² bedroom fills in about a second with the layout most people have. The bed sits dead centre, the wardrobe at its foot bonks it every time the doors open, and the desk is wedged at the bed's corner. Then the same pieces slide like a tile puzzle into a better plan, and the bed rises on one storage platform. The room is for a couple: two pillows, two sets of clothes. The last frame uses the first frame's camera, so every loop is a before-and-after.

**Post caption** (in the post, never on screen): "Send this to whoever gets the wall side. Same 3 × 3.1 m bedroom (9.3 m²), same bed, same wardrobe, same desk. With the bed in the middle, the wardrobe doors hit the end of the bed and the desk chair can't pull out. Move the bed to the corner and raise it 1 m: the wardrobe goes full height, the desk gets the window, and a 1.4 m shirt rail slides out from under the bed. The big addition is one platform; the full list is pinned. Middle or corner? Save this before you move your bed."
- Pinned comment:
  - before and after plans with dimensions, including the room door hinged on its west jamb;
  - what stayed (bed, mattress, wardrobe, desk, chair) and what was added (one platform with stairs, a deep drawer, the pull-out rail and a headboard ledge; a top cupboard on the wardrobe; one shelf over the window);
  - "The rail and the wardrobe doors are used one at a time.";
  - "Changing the sheets: the mattress slides 30 cm toward the aisle.";
  - "In real life the bed's legs come off and the frame sits in a recess in the deck.";
  - "Modelled and rendered from code."

**Why it should work**
- [measured, videos.csv] Bed placement is a strong but crowded title family.
  - 15 bed-placement or tatami titles: era-adjusted 0.43 to 17.54, median 1.74, 13 of 15 above 1.00. With the two "raise the bed" titles: 17 titles, median 2.53.
  - Two are below the norm: "Small Bedroom? Flip the Bed, Double the Space!" (0.43) and the newest, "If your bedroom layout isn't enough, try changing the direction of your bed." (0.82, est. 16 Nov 2026).
  - The closest match shows a normal layout first, then rebuilds it: "The small bedroom felt twice as spacious after the bed wasn't placed in the middle!" (Aug 2026), 536,285 views, era-adjusted 16.75, 49 s, motion 7.5, longest still 1.2 s, camera 4.26.
- [measured] It is a whole bedroom that ends on a raised bed:
  - bedrooms run at 1.51 times normal;
  - 28 of 29 hits build or transform a whole room, against 12 of 30 flops;
  - every 2026 hit was a bedroom or kids' room with a raised or loft bed. "Be bold! Raise the bed by 90 centimeters in a small bedroom!" got 343,222 views (era-adjusted 10.39).
- [measured, weak] Problem-first openings are thin evidence. 3 of the 59 open on a problem: 2 hits and 1 flop (50,604 views).
  - The hits are the 1,590,288-view kitchen with red X marks (6.47) and the 982,327-view "bathroom door facing the bed" bedroom (6.42).
  - That bedroom has the lowest motion (3.9) and camera score (0.77) of any hit, so copy its opening, not its camera.
  - The only overhead plan-view opening among the 59 was a hit (695,010 views, 4.54), but it measured grey and cool (saturation 0.13, warmth 16.1). So the made-up ochre bed lands at 0.3 s.
- [fact, search snapshots: indicative] The debate works outside the channel, but the peak is old.
  - HomeCraft's "Who still puts the bed in the middle of a small bedroom?" is its best post (351.8K likes, 759 comments), from Apr 2024. Its other snapshot posts got 260-924 likes, and there is no figure for its 1 Jun 2026 "Stop centering the bed".
  - An architect fixing a viewer's tiny bedroom layout passed 2.1M views.
  - The trends file names "two kids, one room" as the topic still breaking out. Treat this video as the Dec-Jan "fix this layout" test.
- [fact, trends file] Sends come from premises that name a household (siblings, a couple) and from captions like "Send this to whoever gets the top bunk". [inference] Two pillows, two sets of clothes and "who gets the wall side" turn a layout debate into a send.
- [fact] YouTube counts every replay as a view. [inference] Ending on the frame-1 camera makes each replay a before-and-after.
- [measured] No text is needed. Comments are practicality debates in many languages, and viewers notice playful sound ("the Scooby-Doo sound effects", 214 likes), so a bonk can show the problem. [inference] "Be Bold — Stop Putting the Bed in the Center of a Small Bedroom!" ran at only 1.015, the 3rd weakest of the 15, so the puzzle motion has to carry the video, not the slogan.

**The room**
- **Size and shape**: 9.3 m², 3.0 m east-west × 3.1 m north-south, 2.7 m ceiling, 0.12 m walls. Room coordinates: x runs east from the west wall (0-3.0 m), y runs north from the door wall (0-3.1 m).
  - **The pieces**: a double bed with a 1.5 × 2.1 m frame and a 1.4 × 2.0 × 0.2 m mattress; a 1.0 × 0.55 m wardrobe, 2.0 m tall, with two 0.5 m doors; a 0.8 × 0.5 m desk and a low-back chair that tucks fully under it.
  - **South (door) wall**: 0.8 m door at the west end (x 0.15-0.95), hinged on the west jamb and opening inward. Its swing (x 0.15-0.95, y 0-0.8) stays clear of everything.
  - **North (window) wall**: 1.2 m window at the west end (x 0.15-1.35, sill 0.85 m, top 2.25 m). After: the desk centred under it (x 0.35-1.15, y 2.6-3.1) and a shelf above at 2.35 m.
  - **East side (after)**:
    - the platform bed: x 1.5-3.0, y 1.0-3.1, deck at 1.0 m. The frame sits in a recess, so the mattress lies on the deck and its top is at 1.2 m;
    - a headboard ledge, part of the platform, along the north wall over the bed head;
    - stairs at its foot: x 1.5-2.25, treads y 0.25-1.0, steps at 0.25, 0.5 and 0.75 m. Their drawers pull out west;
    - a deep drawer in the platform's south face beside the stairs: x 2.3-3.0, pulling out 0.8 m;
    - the pull-out rail unit inside the platform's west side: 1.4 m long (y 1.05-2.45), sliding out 0.55 m.
  - **West wall (after)**: the old wardrobe at y 1.0-2.0, raised to 2.7 m with an oak top cupboard.
  - **Result**: a clear aisle 0.95 m wide (wardrobe front at x 0.55 to the platform at x 1.5), running 1.55 m from the wardrobe's south end to the tucked chair. 1.5 m of sitting headroom above the mattress. The climb is 0.25 m from the top step to the deck, then 0.2 m onto the mattress.
  - **Clearances in the finished room** (worked out from these sizes; re-check in the collision test):
    - wardrobe doors at 90° reach x 1.05 and stay 0.55 m from the chair;
    - the open rail reaches x 0.95 and stops 10 cm short of the chair;
    - the open rail and an open wardrobe door would overlap, so they are used one at a time (pinned);
    - stair drawers reach about x 1.0, clear of the door swing; the open deep drawer clears the stairs by 5 cm.
  - **Before (the same pieces)**:
    - the bed truly centred on the window wall: x 0.75-2.25, y 1.0-3.1, 0.75 m on each side. Its headboard covers half the window;
    - the wardrobe on the door wall, just east of the door (x 1.05-2.05, front at y 0.55). The bed's foot is 0.45 m away, so its 0.5 m doors stop at about 64°;
    - the desk on the east wall (x 2.5-3.0, y 0.75-1.55), right at the bed's foot corner. The half-pulled-out chair sits 5 cm from the bed and can't move.
- **Palette**:
  - Shell: clean white. Not warm white or cream: those sit at the edge of the cream-cast zone.
  - Wood: light oak for the floor, platform, steps, desk, wardrobe doors and top cupboard. No walnut.
  - Blue is moved off the furniture: one muted blue pillow and a blue throw on the bed.
  - Colour from filled storage, two sets for the couple: rust, mustard, terracotta and white for one; sage, navy, denim and light grey for the other. Keep the warm set on the side most in frame.
  - An ochre duvet with one white and one blue pillow, on screen from 0.3 s; plain white and tan shoes; solid-colour book spines.
  - No patterns. A plain jute-coloured runner, long cut only.
- **Light**:
  - No Blender sun for this project: the bridge's sun is static and cannot fade.
  - The window beam is a roomkit spot light outside the window. The open-top "sky" in the overhead shots is a set of roomkit area lights above the room. The bridge keys both every frame.
  - Around the ceiling switch, cross-fade the overhead area lights against hidden interior fills over about 0.5 s, so the descent never darkens. Target brightness 138-178.
  - The window backdrop plane is hidden while the camera is above 2.7 m.
  - Lights on: warm lamps are added on top of the daylight, never replacing it. They are a lamp on the headboard ledge, LED strips under the platform lip and stair edges, a desk lamp and a wardrobe interior strip.

**Frame 1 and the hook**:
- **0.0 s**: the empty room from a high three-quarter angle, looking about 68° down from the south (never straight down), with a 48° field of view. The room fills about 85-90% of the frame width. The camera is already circling slowly. Three full-height white walls, a south wall cut down to 0.9 m that shows the door gap, an oak floor with a patch of window light, and pale textured ground beyond.
- **0.3 s**: the double bed drops dead centre against the window wall with a heavy thud, already made up: ochre duvet, one white and one blue pillow.
- **0.6 s**: the oak wardrobe slides onto the door wall beside the door.
- **0.9 s**: its doors swing, bonk the foot of the bed at about 64° and wobble.
- **1.1 s**: the desk and chair land on the east wall at the bed's foot corner. The chair tries to pull out and knocks the bed.
- **1.3 s**: the shuffle starts.
- No lines, labels or red X.

**15 s cut**
- **0.0-4.5 s · S1 overhead, one continuous orbit**:
  - 0.3-1.1 s: the bad layout lands.
  - 1.3-1.7 s: the chair tucks in and the desk slides 0.67 m south (clack).
  - 1.8-2.5 s: the bed slides 0.75 m east into the corner (scrape, then a heavy clack).
  - 2.6-3.3 s: the wardrobe glides into the empty west half, turns a quarter and lands against the west wall (two clacks).
  - 3.4-4.4 s: the desk slides west along the door wall and turns a quarter in the open floor inside the door (clack). It runs up the new 0.95 m aisle with 7.5 cm to spare on each side, then slides under the window (clack at 4.4 s).
  - Camera: circles the room centre at about 5° per second, 68° down, 48° field of view. No stop and no swing.
- **4.5-7.0 s · S2 drop, rise, descent**:
  - 4.5-5.0 s: the camera drops fast to about 35° down, just above wall-top height, south of the room.
  - 5.0-6.4 s: a low, slow sideways glide. The oak platform grows under the bed to 1.0 m (5.1-5.9 s), and the bed's legs fold up like landing gear. Three steps stack at its foot (5.9-6.4 s).
  - 6.4-7.0 s: the camera finishes the descent to eye level just inside the door as the field of view widens to 85°. The stair drawers pop out full of knitwear and shoes, then close (6.5-7.0 s).
- **7.3-10.7 s · S3 the aisle, seen from the window end looking south**:
  - 7.4 s: the wardrobe grows an oak top cupboard to the ceiling.
  - 8.0 s: both wardrobe doors swing wide open with no bonk.
  - 8.2-8.6 s: the rail fills with both sets of clothes.
  - 8.7 s: the doors close.
  - **8.9-9.8 s, wow**: the 1.4 m rail glides out of the platform side, loaded with shirts, across the aisle.
  - 10.3 s: the rail glides back.
  - Camera: slow push-in down the aisle, leaning left to follow the rail.
- **11.0-15.0 s · S4 wide, from the door corner looking north-east**:
  - 11.0-11.6 s: the headboard ledge fills with books, a plant and a lamp.
  - 12.2 s: lights on.
  - Slow drift to 13.2 s.
  - Then the camera tilts down and rises out of the room, and the field of view narrows back to 48°. It arrives at the exact frame-1 position at 15.0 s, circling at the same speed, so the loop cuts to the empty room and the bad layout lands again.

**Long cut (45 s)**: The same opening. The bed stays on the floor after the shuffle until 13 s, so viewers wait to see where the storage goes.
- **0.0-5.0 s · overhead, one continuous orbit**: the bad layout lands (0.3-1.1 s); the same shuffle, a little slower, 1.3-4.8 s. From 3.0 s the orbit eases from 68° to about 58° down.
- **5.0-7.0 s · the descent** to eye level by the door, with the field of view widening from 48° to 85°. The bed sits low in its corner.
- **7.0-13.0 s · window desk**:
  - A, 7.0-9.8 s, push-in from behind the chair: the desk drawers slide out and fill, and the shelf above the window fills with books and boxes.
  - B, 10.1-13.0 s, slide along the window: the chair rolls out and the lamp lands.
- **13.0-19.0 s · bed corner**:
  - C, 13.0-16.0 s, low circle: the platform grows under the bed to 1.0 m (13.2-14.2 s) as its legs fold up; then the steps stack (14.4-15.2 s).
  - D, 16.3-19.0 s, slide along the stairs: the stair drawers fill and close (16.4-17.6 s); the deep drawer slides out with a suitcase and a spare duvet (17.8-18.9 s).
- **19.0-24.0 s · wardrobe wall**:
  - E, 19.0-21.4 s, push-in facing west: the top cupboard grows (19.1-19.7 s). The doors swing wide with no bonk (20.1 s), and the rail fills with both sets of clothes (20.3-21.2 s).
  - F, 21.7-24.0 s, slide along the wardrobe toward the desk: two drawers fill with folded T-shirts (21.8-22.8 s); the top cupboard opens on boxed spare bedding; all doors close at 23.4 s.
- **24.0-31.0 s · headboard, sheets and wow**:
  - G, 24.0-27.3 s, rising glide up the stairs: the headboard ledge fills (24.2-25.2 s). The mattress slides 30 cm toward the aisle and back (25.8-26.9 s), showing how the sheets get changed.
  - H, 27.6-31.0 s, low in the aisle: **the 1.4 m rail glides out fully loaded (27.8-29.4 s, 62-65% of the runtime)**, with the camera travelling alongside. It glides back at 30.4 s.
- **31.0-38.6 s · the person**:
  - J1, 31.0-34.6 s: a tracking dolly at hip height follows the figure in from the door.
  - J2, 34.9-38.6 s: a slow push-in from the window end down the aisle, leaning toward the rail.
- **38.6-43.0 s · K, wide from the high south-east corner, looking north-west**: slow drift; lights on at 39.4 s; from 41.0 s the camera rises out of the room.
- **43.0-45.0 s · drifting overhead wide**, arriving at the frame-1 position at 45.0 s with the field of view back at 48°. No end card.

**Storage moments**
1. Window desk: two drawers slide out and fill with plain notebooks and pens; the shelf above the window fills with books and boxes.
2. The platform: an oak base grows under the same bed to 1.0 m. The bed's legs fold up and the frame settles into the deck (a build).
3. Stair drawers: three steps stack at the platform foot. Each one pulls out sideways full of knitwear and shoes, then closes.
4. Deep drawer beside the stairs: slides out 0.8 m with a suitcase and a spare duvet.
5. The old wardrobe goes full height: an oak top cupboard grows from 2.0 to 2.7 m. The doors open wide (no bonk), the rail fills with clothes and two drawers fill with folded T-shirts.
6. Headboard ledge: fills with books, a small plant and a lamp.
7. The 1.4 m pull-out hanging rail: the platform side glides out 0.55 m with about 12 shirts and blouses, no jackets (the wow).

**The person moment** (long cut only, 31.0-38.6 s): a faceless stand-in adult (`fg.figure`, default light grey).
- 31.2-32.4 s: walks in through the door, along the path that used to be jammed.
- 32.8 s: opens the wardrobe all the way with no bonk, the payoff of the opening gag; closes it at 33.8 s.
- 35.2-35.8 s: stands in the 0.95 m aisle and stretches both arms overhead (the `reach_both` preset). Arms out wide would hit the furniture.
- 36.0-36.6 s: steps back to the south end of the aisle.
- 37.0-38.5 s: pulls the rail out by its end handle and lifts a shirt off the near end. The rail glides back at 38.6 s.
- The figure stays at the south end of the aisle, shirt in hand, through lights-on and the final overhead view, so the last frame shows the room in use.
- The 15 s cut has no figure. People appear in 4 of the top 5, but also in three sampled flops, so on their own they do not separate hits from flops [measured].

**Sound**
- Landings:
  - a heavy thud for the bed; thuds for the wardrobe and desk;
  - a dry wooden clack for each shuffle move, like puzzle tiles, and a long scrape for the bed's slide;
  - three rising thunks as the steps stack; ticks for small items.
- Playful effects:
  - a dull bonk with a springy wobble at 0.9 s, then the chair's knock at 1.1 s;
  - at the no-bonk moment (8.0 s in the 15 s cut, 20.1 s in the long cut), a bright two-note chime where the bonk used to be, and a softer echo when the figure opens the wardrobe (32.8 s);
  - a smooth zip and a soft click for the rail.
- All effects are synthesised in `pipeline/music.py`: no sampled cartoon sound library, and no melody or sound that echoes a famous puzzle game.
- Music: original, 120 BPM (hits lean to 111-125 BPM, weak evidence). A light plucked lead and a soft kick, with a short fill under the descent. No licensed tracks.

**Risks and fixes**
- **It reads as a floor plan or "dimension guide"**: both dimension-guide videos flopped (13,770 and 6,836 views) [measured]. Fixes:
  - a 68° view, never straight down; three full-height walls; the camera circling from frame 1; no lines, labels or arrows; the made-up bed by 0.3 s;
  - a 48° field of view, so the room fills most of the frame and the bonk reads on a phone;
  - pale, textured ground just past the frame edge, so the overhead frames neither look like a still camera nor show the near-black world.
- **A slow start**: two flops sat nearly empty for 6-8 s, and the hits' longest still is 1.4 s against 2.6 s for flops [measured]. Fix: four landings by 1.1 s, the shuffle from 1.3 s, and no gap longer than 0.3 s between moves.
- **Impossible moves look fake or AI-made.** Every move is a slide, or a slide and a turn in open floor:
  - The bed slides; it never turns. A 1.5 × 2.1 m bed needs a clear circle 2.58 m across to turn, which this room cannot give.
  - The wardrobe turns (1.14 m circle) in the free west half, 1.5 × 2.1 m, once the bed has moved.
  - The desk turns (0.97 m circle) inside the door, at least 6 cm from everything, then runs up the aisle with 7.5 cm on each side, a satisfying near-miss.
  - These are worked out from the plan's sizes. Run the top-view collision test on the full move path, then again with every door and pull-out open one at a time.
- **The "before" looks staged.** Fix: the bed truly centred, the wardrobe at its foot (doors stop at about 64°) and the desk wedged at the bed's corner. These are clashes people live with.
- **The raised bed doesn't add up.** Fix: the frame sits in the deck, so the mattress top is at 1.2 m with 1.5 m of headroom. The long cut shows the mattress sliding out for sheet changes, and the pinned comment explains it.
- **The rail could look fake.** There is only about 0.9 m clear under a 1.0 m deck. Fix: rail at 0.88 m, shirts and blouses only, hanger plus garment modelled at 0.78 m. The hems stop at 0.10 m, at least 5 cm above the unit's 0.05 m base.
- **A "you added half a room" pile-on.** Title fights drew comments with 2.3K likes [measured]. Fix: the vanity and the mirror tower are cut. The platform holds the stairs, deep drawer, rail and ledge. The caption says the platform is the big addition, and the pin lists every added piece.
- **A grey or cool look.** The plan-view hit measured saturation 0.13 [measured], and kitchen v2 measured warmth 14.5 against a 22 target. Fixes:
  - blue is only on a pillow and a throw; oak wardrobe doors and top cupboard; the ochre duvet or knitwear in frame at every station;
  - run `hh_metrics.py` on every station, not only the first 5 s (targets: saturation 0.17-0.38, warmth 22-57, brightness 138-178).
- **The two colour fixes pull in different directions.** One review fix said "lighter blue on the wardrobe door panels"; another said "move the blue off the wardrobe". I followed the second. It cuts the cool area further and stops the room echoing top-5 #3.
- **The light could jump mid-descent** when the ceiling switches on. Fix: keyed area lights cross-faded over 0.5 s (see Light). Render test frames either side of the switch and compare brightness.
- **A crowded topic.** The newest bed-placement title ran at 0.82, and HomeCraft's big number is from 2024. Fix: the couple premise and the send line lead the caption. Post it as the Dec-Jan "fix this layout" test, not as a top bet.
- **Text or IP on props.** Fix: blank, solid-colour spines, notebooks and box faces; a suitcase with no logo; shoes with no stripes or logos.
- **It isn't very fresh.** The finished room uses the familiar kit: a raised platform, storage stairs (top-5 #2 and #5) and a window desk. Fix: the overhead tile-puzzle shuffle and the bonk-then-chime are the signature; the side pull-out rail is the hero; the blue-door wardrobe is gone.

**Build notes**
- **Reuse from `rooms/bedroom/project.py`**:
  - the materials pattern (oak floor, `wood_mats`), `garment()`, `stack()`, `cloth()` and `pillow()` for the made bed, and `plant()`;
  - the `door_z` and `drawer_fn` timeline helpers;
  - its lamp lighting and BLENDER settings as starting values, minus the sun.
  - Build a fresh shell, though: that project is its own post with a different layout.
- **Reuse from `rooms/kitchen/project.py`**: the pull-out pantry slide-and-fill pattern for the rail and the deep drawer.
- **One timeline, two cuts**: write the pieces, contents and beat functions once, and drive each cut from its own beat list.
- **Camera**: use `pipeline/camkit.py` `hold_camera` for the eye-level stations, wrapped in a custom `camera(t)` for the orbit, the low glide, the descent and the rise.
  - Patch `blender_render.py` to keyframe `cam.angle_y` from `camera(t)['vfov']` every frame (`pt.cpp` already reads it per frame; a few lines). Today it reads the field of view once, from `camera(0)`. Keep the old behaviour when `vfov` never changes.
  - 48° overhead, widening to 85° inside.
  - Starting values: about 7.4 m from the room centre along the 68° line (about 6.9 m up and 2.8 m south), circling at about 5° per second. Check with ROOM_REST stills and adjust.
  - While the camera is above 2.7 m, keep the frame's top edge below the horizon. The world is hard-coded near-black (0.05).
  - J1, J2 and every other station must clear the 1.8 camera-movement target.
- **Person**: `pipeline/figure.py`.
  - `fg.walk` for the entrance and the step back.
  - `fg.track` for the poses: a custom "open" pose with the right arm forward, `reach_both`, and a two-arm "pull".
  - The shirt follows the right forearm through `fig.transforms(...)['<inst>_farm_r']` in a `Timeline.custom`.
- **Sound**: add bonk, clack, scrape and zip events to `pipeline/music.py`, beside its thud, tick, swish and chime.
- **New pieces**:
  - the 3.0 × 3.1 × 2.7 m shell. The south wall comes in two parts: a 0.9 m base that is always there, and an upper part shown only while the camera is inside the room below 2.7 m. Switch it while it is behind the camera: as the camera passes through its plane on the way in, and at the 2.7 m crossing on the way out.
  - a ceiling that switches in the frame where the camera crosses 2.7 m, when it is seen edge-on;
  - pale, textured ground (pale oak deck or warm concrete), sized from stills to pass the frame edge in every overhead frame;
  - roomkit area lights above the open top, a spot for the window beam, and hidden interior fills;
  - the bonk doors: swing to 64°, stop, wobble to rest, close;
  - the platform (grows upward), with the bed riding up on the same lift, folding legs and a recess for the frame;
  - the mattress slide (long cut);
  - stairs with side-pull drawers, and the deep drawer;
  - the rail unit: frame, tube rail at 0.88 m and about 12 garments;
  - the top cupboard (grows up from 2.0 m), the headboard ledge, the desk drawers and the window shelf.
  - The desk and the tucked chair move as one piece during the shuffle.
- **Effort**: medium-high. About 20 animated pieces plus their contents, a new camera function and a small bridge patch.
  - The camera never stops, so no frames can be copied: 375 + 1,125 = 1,500 frames at the README's ~35 s per frame (720x1280, 4 cores) is about 14.6 CPU-hours.
  - Render the 15 s cut first, as the test. Before any full render, do low-sample test renders of the ceiling switch, the descent and the rail.
- **Hard to render, and how to avoid it**:
  - No see-through "ghost" of the old layout: the Blender bridge only supports glass and translucent mixes.
  - No cloth simulation: the duvet is a rigid `cloth()` mesh that moves with the bed.
  - Garments are simple hanging panels at their real length; the figure is faceless with no hair.
- **Variety**: no toe-kick step drawer (that beat belongs to C1 and C6). No sliding mirror panel or floating desk, which are in `rooms/bedroom`.
- **Posting**: evergreen, but best as the new-year "fix this layout" post: the trends file's slot is 27 Dec-10 Jan. Storyboard episode 2 now ("Undo": a galley kitchen with the fridge in the way), so the series continues within 2 weeks.

**Corrections to the candidate notes**
- **The 536,285-view video is not the 2nd-best 2026 upload.** In `videos.csv` it is the 4th most-viewed, after 853K, 689K and 547K. I cite it by its era-adjusted 16.75 instead.
- **The 24 s two-beds Short (991,555 views) does not have the highest camera movement of the 59.** It has the highest motion (15.5). Its camera score (11.88) is second to a 6,836-view dimension guide (12.1).
- **The bed slides, it does not spin.** The candidate had the bed pivot 90° into the corner, which can't be done without passing through the wardrobe or desk.
- **Review corrections applied to this plan:**
  - The bed family is 15 titles, median 1.74, 13 of 15 above the norm. It is not "all 12 beat the norm, median 3.04". The "11 titles give 3.17" figure is not in any file: 3.17 is one title's value.
  - "Be Bold — Stop Putting the Bed..." is 1.015, the 3rd weakest of 15. The weakest is "Flip the Bed" at 0.43.
  - The old "centred" bed (x 0.85-2.35) was 0.10 m off centre. It is now truly centred at x 0.75-2.25.
  - The 1.5 m headroom only held with the mattress on the deck; it now is.
  - The 7 cm clearances had no desk size behind them. The desk is now 0.8 × 0.5 m, with 7.5 cm each side in the aisle.
  - The rail was 1.9 m and would have hit the desk. It is now 1.4 m.
  - Problem-first openings are 2 hits and 1 flop, not 2 hits.
  - HomeCraft's 351.8K likes date from Apr 2024.

---

## Changes made in production (this copy is kept up to date)

- **Colour.** Three reviews read the ochre duvet as "mustard / cream" and too many accents. The duvet is now white, the pillow and throw a soft grey-blue (the one accent), and colour comes from the filled storage (terracotta, rust, sage, navy, denim, light grey). Mustard is dropped from the wardrobe. The oak is a slightly cooler light oak.
- **Frame 1.** The orbit radius is 8.25 m (starting at camera yaw -12°, 6°/s, pushing in 0.12 m/s). The room fills about 90% of the width. The bed drops from 3.2 m above its place, so the hook registers by 0.2 s (hh_metrics "first clear movement" 0.2 s).
- **Wow shot (15 s cut, 8.95-10.9 s).** The camera is low (1.0 m) at the south end of the aisle, looking north along the rail. From the window end the oak front panel of the rail hid the shirts. The rail glides out over 8.95-9.45 s, holds for about 1.1 s, and glides back over 10.55-10.88 s. The garments are modelled as shirts: body, rounded shoulders, sleeves and a hanger. A coloured shirt hangs nearest the camera.
- **S3 split.** The wardrobe gets its own straight-on station (7.22-8.75 s) that starts looking up at the top cupboard as it grows. Seen from the window end, the open doors would hide the interior.
- **S4 and the tail.** The ledge, window shelf and desk things land over 11.2-12.1 s, with the camera pushing in. Lights come on in a cascade at 12.18 s, and the daylight eases down 20% so the lamps read. The rise starts at 12.4 s. During it the chair rolls out (12.85 s) and the deep drawer slides out with a suitcase (13.35-14.2 s), so the overhead return keeps landing.
- **The window backdrop** shows whenever the camera is below 4 m (not only below 2.7 m), so the low S2 glide has a view out of the window.
- **Long cut.** It follows the plan's zone list. The person enters through a door leaf that opens 31.0-32.75 s and is otherwise closed. The shirt-lift at the end was simplified: the figure pulls the rail out by its end handle and stays in the aisle. The headboard ledge is a shelf over the raised headboard (1.82 m). The top cupboard's "boxed bedding" beat was cut.
