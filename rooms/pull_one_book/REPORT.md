# Pull One Book: render report

Idea #6 (C13) in `research/top10_ideas.md`. A 9.2 m² kids' loft room (3.4 × 2.7 m). A child tugs the one coral book,
pushes the loaded bookcase section 0.3 m back, then slides it 0.7 m aside like a pocket door onto a lit den under the
loft. The toys on the floor then fly in.

Project: `rooms/pull_one_book/project.py`. The 15 s cut is the default; `ROOM_CUT=long` selects the 45.5 s cut. Both
share `build()`.

## What I built

- **Shell:** neutral white (sRGB 242/241/238), light oak floor planks, pale birch for every built-in, and one muted
  coral accent (loft rail, wardrobe door, desk drawer, the clue book).
- **West wall:** a birch loft deck (top 1.50 m) with a coral guard rail, mattress, duvet and pillows over a 2.10 m
  book wall. The book wall has a fixed south run, a 0.85 m sliding section and a fixed north run (about 230 plain-spined
  books). The section rides visible floor runners and a top track on an L path. It has a finger guard, shelf lips, a
  latch and castors.
- **The den behind it:** a bench toy chest with two lift-up lids, six cubbies, a floor pad, cushions, a pouf and a
  ceiling light panel. The panel snaps on mid-slide.
- **North wall:** a five-tread book stair (every riser is an open cubby of spine-out books) with a handrail, and a
  wardrobe tower with a coral door. Its plinth holds a toe-kick step drawer.
- **South wall:** window, roller blind, desk with drawer, chair, rolling cart, lamp, plant and crayon jar.
- **East wall:** door, hooks, backpack, an abstract print (three shapes, no lettering) and a corner plant.
- **The mess:** 17 toys (blocks, balls, two generic faceless plush toys, picture books, a car, a ring stacker) and a
  basket. Each toy is built where it ends up and animated from the spill to the floor, then on an arc through the
  opening into the chest or a cubby.
- **The child:** the `figure.py` child stand-in in a clear blue (`fig_kid`). It walks, reaches, pushes, sits and waves.
- **Sound:** `pipeline/music.py` gained three original kinds: 'click' (the latch), 'creak' (the slow slide with a
  runner roll) and 'pluck' (a rising pentatonic note per toy landing). It also gained a `hush` option: the drums drop
  out for the beat before the tug. The cue is original, at 120 BPM, with its own chord loop.

## 15 s cut: shot list

| Time | Station | What happens |
|---|---|---|
| 0.0-1.6 s | S1, high over the door, pushing west | Empty white room with sun on the floor. Book-wall carcasses rise (0.03 s), planks slap down far to near, the section carcass lands, the deck slams on (0.6 s), runners and track clank, shelves slide, about 230 books riffle in shelf by shelf, and the coral clue book drops last (1.48 s), 7.5 cm proud and tilted |
| 1.9-3.0 s | S1B, high over the room onto the loft | Coral rail slides on, mattress, duvet, pillows, plush, clip-on lamp, throw |
| 3.3-4.65 s | S2, low by the stair | Five step boxes stack on rising thuds, books riffle into the riser cubbies, handrail clank, plush |
| 4.95-7.0 s | S2B, wardrobe panning to the mess | Wardrobe slides in, coral door pops open, small clothes, two folded stacks, baskets, door slams. The basket lands, tips, and 17 toys spill across the floor |
| 7.3-10.85 s | S3, low from the south-east (the wow) | The child pops in, reaches up, and the clue book tilts with a click (8.05 s). The child pushes the section 0.3 m back (8.15-8.6 s), then slides it 0.7 m south behind the fixed run (8.6-9.9 s). The den light flickers on (8.9-9.1 s). The child steps aside, the chest lid lifts, the toys fly through the opening into the chest and cubbies on a rising pluck run (9.55-10.7 s), the basket flies in, and the lid drops |
| 11.1-12.6 s | S4A, the desk | Desk, drawer opens, crayons and a blank ruler drop in, drawer shuts; cart, chair tucks in, lamp, plant, jar, rug unrolls, blind rolls up |
| 12.9-15.0 s | S4, crane back to the frame-1 pose | Evening light, downlights, loft lamp and desk lamp cascade on (13.1-13.5 s). The child walks into the den and sits, a cushion lands, the child waves. The last frame is the frame-1 pose, so the video loops |

Storage moments: book wall, book stair, wardrobe, desk drawer, the sliding section, the bench chest, the den cubbies
(7), plus the cart.

## Measurements

(filled in below as the work finished)

## Reviews

- **Gate 1** (three rounds, fresh reviewer each time): 6, 6 and 6 out of 10.
  - Fixed after round 1: the wow camera moved low and close, the clue book made bigger and more prominent, and the
    stair shot tightened.
  - Fixed after round 2: the clue book is now the only coral spine (I removed terracotta, rust and blush from the
    book-wall palette), the child is clearly blue, the floor mess moved into the S3 sightline, S2B pans onto the
    tip-over, and I filled the landing gaps during the slide.
  - Fixed after round 3:
    - The child reaches from the north side with the left hand, so the book stays visible.
    - The child steps out of the sightline before the toys fly.
    - The toy arcs are slower (0.65 s).
    - The den light panel now runs to the wall line.
  - Not acted on from round 3, because the reviewer misread two things: the loop already closes (the last frame is
    the frame-1 pose), and lights-on lands at 13.1 s with the den in frame.
  - The brightness and saturation the reviewers flagged were the code renderer's preview grade. The Blender stills
    measure inside the hits' band.
- **Gate 2** (Blender stills): 6/10. Everything it flagged is fixed:
  - **Black L-lines on the stair.** Overlapping coplanar faces render black in Cycles: the cubby floor and back panel
    shared the side panel's outer plane. I inset them, and did the same for the bench, the cubby dividers and the
    wardrobe.
  - **Black slot over the den opening and silver bars on the den floor.** The metal track and runners reflected the
    black world, so they are now matte, and the runners are 3 mm thick.
  - **Dark night city in the window.** I replaced it with the day view, dimmed and cooled, as "early evening", so
    nothing in the frame is dark.
  - **Motion blur on the toy flight.** The shutter is now 0.3 frames, set by a new `BLENDER['shutter']` key in
    `blender_render.py`.
  - **The clue book read as a box.** It is now 7.5 cm proud with a smaller tilt.
