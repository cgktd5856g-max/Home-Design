# Lessons learned

Read this before starting work. It holds the concrete things we learned the hard way, so the next video goes faster and
looks better.

**How to add a lesson**
- Add one concrete line, with a number, a file or the fix, not a general tip.
- Put it under the right heading, with its date.
- Render sessions write theirs in their `REPORT.md` under "Lessons for next time". The coordinator copies them here
  when it merges the branch.

---

## Usage limits and coordination

- **One usage limit for everything.** The account's 5-hour limit is shared by every session and every agent. Two
  build sessions plus 8 workflow agents used it up in about 80 minutes (23 Nov, 05:50 UTC). Keep at most about 3
  sessions in the build-and-review stage at once. Blender rendering itself uses almost none of it.
- **Nothing restarts by itself after a limit stop.** Sessions and scheduled check-ins stay stalled until someone
  sends them a message (23 Nov: stalled from 05:50 to 13:31 although the limit reset at 08:40). After a reset, message
  every session.
- **There is also a 7-day limit.** `get_session` shows `rate_limit_info`. Status `allowed_warning` means it is
  close; check it before starting a new wave.
- **The weekly limit can stop everything overnight** (23-24 Nov). Ten sessions working in parallel went silent from
  about 23:50 to 15:15 UTC the next day, 15 hours with no pushes, then all resumed at once. Ten parallel sessions burn
  the weekly limit fast. Run at most 5 at once, and plan post dates with a day of slack.
- **Workflows run only 2 agents at a time on this 4-core machine** (the cap is CPUs minus 2, per workflow). For a big
  fan-out, run several workflows side by side: 4 batches of 3 ideas ran 8 agents at once.
- **A stopped workflow resumes from cache.** `resumeFromRunId` with the same script and args reuses every finished
  agent call, even after a usage-limit failure.
- **Shared pipeline files get conflicts.** Sessions add sound kinds to `pipeline/music.py` (bonk, clack, clunk, pip
  and more) on their own branches. When merging, keep both sides' additions and test every event kind (23 Nov: 3
  merges, 20 kinds, all fine).
- **Name clashes keep happening in shared files** (25-26 Nov: `boing` twice, `pluck` with two meanings). When merging,
  keep the existing name's meaning and give the newcomer a new name (`pluck_step`); test every sound kind after.
- **Shared settings must keep one meaning** (24 Nov). Two sessions gave the grade's third value opposite meanings, and
  two defined different `clack` sounds. The shared code keeps: grade gamma above 1 brightens the mid-tones (below 1
  darkens); `clack` is the single wooden tile clack, `ratchet` the three-knock lock-out, `clink` plates and cups. Before
  adding a parameter or sound to a shared file, check that the name isn't already taken.
- **Skipping the preview pass costs quality on long cuts** (26 Nov). Under the no-polish rule, two long cuts rendered
  without a tuned preview (Three of Us, Not One Handle) and each missed 3 pacing targets, with 2.6-6 s of near-still
  camera on plain white panels or closed doors. Keep the cheap low-res preview plus hh_metrics step even in lean mode:
  it costs minutes, and a weak 44 s render costs 9 hours.
- **Keep Claude out of the render loop** (25 Nov). Once a render starts, Claude should cost almost nothing. Put the
  whole tail in one detached shell script, `.render/<slug>/autopipe.sh`: restart Blender if it dies, scan and
  re-render bad frames, encode both versions, run hh_metrics, git push. Claude starts it, arms one background waiter
  (2 h maximum, re-armed with no other work) and ends its turn. Each wake-up re-reads the whole chat history, so long
  sessions get expensive: keep wake-ups to 1-2 tool calls, and don't polish after the final render has started.
- **Talking to sessions.** `send_message` to a child session works, and children reply with `send_message` to
  `@parent`. Send short pointers to files in the repo instead of long pasted text.
- **Decide the concept before a session starts.** Switching mid-build made the two-kids session rebuild its whole
  room.

## Rendering

- **Blender speed:** at 720x1280, 16 samples, adaptive 0.04, bounces 4,2,2 and `--nobevel` (4 cores):
  - 18-33 s a frame when Blender has the machine to itself;
  - 45-60 s a frame when a preview shares the CPU.
  - A 15 s cut (375 frames) takes about 2-3.5 hours. With the gliding camera every frame is new, so no frames are
    copied.
- **Never end your turn while a render runs.** An idle session's container goes to sleep and kills detached
  processes. Three sessions lost renders this way on 23 Nov.
  - Keep a background waiter: Bash with `run_in_background`, an until-loop that exits when the render finishes or its
    process disappears.
  - Each time it fires, check the frame count, restart the render if it died (finished frames are skipped) and re-arm
    the waiter.
- **Don't run a preview next to a final render.** It makes the render 2-3 times slower.
- **Check every final frame before encoding.** In one long run, 62 frames came out with a black floor (advent, 23 Nov),
  and a fresh process did not reproduce it.
  - Compute each frame's mean brightness, flag the outliers, and re-render those frames in fresh processes.
- **Root cause of the black-floor frames: Cycles "persistent data" in long sequential runs** (advent, 24 Nov). A long
  run produced 135 bad frames in 218; fresh renders are clean. Set `BLENDER['persistent'] = False` in the project for
  any long render (`pipeline/blender_render.py` reads it; the default stays on), and still scan every frame.
- **Detect black-frame glitches automatically** (advent, 23 Nov). After every render, flag frames where pixels under 12
  cover more than 2% of the frame. Re-render those with a slightly different sample count, which changes the sampling
  pattern; a plain re-render can repeat the glitch.
- **Coplanar faces render as black squares in Cycles** (a drawer front flush with a block, overlapping window-frame
  boxes) but look fine in the code renderer. Leave a gap or recess of a few millimetres.
- **Code-renderer previews cost about 3 times more with the gliding camera,** because every frame moves. Preview at
  216x384.
- **Per-frame lens.** `pipeline/blender_render.py` keyframes the lens when the field of view changes per frame. Two
  sessions added this on 23 Nov, so check for a conflict when merging their branches.

## Making it look right (the hits' range)

- **The hook.** The first big landing must be in frame by 0.3 s. Most first previews missed this: the advent video's
  first movement was at 1.6 s. Slam something big down close to the camera, like a bed dropped from 3 m or a loft deck.
- **Measure the hook on a graded preview** (advent, 23 Nov). The raw code-renderer preview is washed out and hides
  motion, and floor planks on a pale subfloor barely register. Grade the preview to the final look before reading
  `fb`.
- **Overhead and cut-away shots.** The room must fill the frame. Surround it with a pale ground (about 236 grey),
  never a dark or noisy void.
- **One muted accent.** Reviewers read strong yellow, mustard and ochre duvets as "mustard" or "cream". A white duvet
  with one grey-blue or sage accent works. The colour should come from filled storage: clothes, books, toys.
- **Ceilings.** Nothing can drop onto a tall unit under a 2.7 m ceiling. Slide it in whole from the aisle.
- **Pieces land whole.** Nothing grows or morphs, because that reads as AI.
- **Check the plan's numbers before modelling** (bed on the ceiling, 23 Nov). A pedestal drawer would have opened into
  the wardrobe, which cost a layout change after two review rounds. Probe every camera station at its start AND end
  pose: a pose inside a carcass, or 0.4 m from a post, looks fine in the plan's numbers.
- **Tilted openings.** A camera tilted down for frame 1 loses a rising object off the top of the frame. Set the
  opening pitch from that object's height.
- **Seated figures.** `figure.sit_pose` puts the pelvis at `at`; for a bed edge, place `at` 0.1 m inside the mattress.
- **A low "first movement" score isn't always a dead opening** (Dinner long cut, 26 Nov). hh_metrics reported 3.0 s,
  but plates were falling and the floor sliding in from frame 1; the landings were just gentle (change 6-9 per 0.2 s,
  under its threshold of 10). Look at the first 3 s before re-rendering: make the first landing bigger and closer if it
  really is soft.
- **Make the hook register.** `hh_metrics` counts the first movement only when the mean change on its 45x80 grid tops
  10, so planks close in brightness to the subfloor never count. Make the subfloor clearly darker and land the planks
  big and early.
- **The grade depends on the room.** The default `--grade 1.35,0.03` left a neutral-white room at brightness 138, the
  edge of the band; a gamma of 1.18 fixed it. Measure after grading.
- **Overlapping boxes render black dots or seams in Cycles** (three of us, 23 Nov): frame members and rails laid over
  posts. Build members that butt, never overlap.
- **Put a white studio box around the set from the start.** Hidden walls leave a black void in swings and odd angles.
- **Choose each station by which way the moving fronts face.** Drawers facing south need a camera from the south;
  decide this before modelling.
- **Hanging garments seen end-on read as one slab.** To read as "sparse", hang a few short garments parallel to the
  front.
- **A small, very bright light hidden from most points speckles the code renderer** (a north-window sun under a deck).
  Mark it always-sampled.
- **Moving furniture.**
  - Draw the swing arc in a top view at the swing time before modelling.
  - Keep stand-in figures out of moving arcs.
  - Mirrored meshes (negative scale) flip their triangles: re-wind them.
- **Dead time.** A close station where closed doors fill the frame for 0.5 s reads as dead time. Pull back or cut away.
- **Check brightness over time, not just the average** (tape line, 23 Nov). The mean was 151 (in range), but the dusk
  ending sat at 99-124 against 193 at frame 1, so the lights-on read grey and the loop jumped in brightness. Keep
  every second at 140 or above: daylight at 85% or more, with lamps adding warmth on top.
- **The wow needs time and the right angle.** A 0.6 s swing seen side-on reads as "turning in place". Give the big move
  1.2-1.5 s with an ease, from the angle that shows the whole arc (for a pivot, near-overhead).
- **The grade.** `--grade 1.35,0.03` usually brings brightness and saturation into range. Always measure after it.
- The older lessons in `HANDOFF.md` section 8 still apply: lift-up beds seen from the side, black renders from
  winding, window views in `separate`.

## Process and reviews

- **`hh_metrics.py` targets are a direction, not a gate.** Only 9 of 29 hits pass every one. Aim to miss at most one.
- **Tune on the preview.** Measure the low-res preview with `hh_metrics.py` before any Blender time, where changes are
  cheap. After the final grade, brightness usually drops about 10.
- **Independent reviewers score previews harshly.** Typical scores are 5.5-6.5 (8.5 once). Cap it at 3 rounds and move
  on; the measured numbers matter more.
- **How ideas are made.** The pipeline of 8 lenses, a merge, 5 judges, then develop, attack and revise produced strong,
  varied plans, and the attacks caught real geometry errors (the wardrobe arc, drops through the ceiling).
  - `research/top10_ideas.md` holds the final plans; `production/plans/*.md` are drafts.

## Results so far

Fill in the views after posting (7 days).

| Video | 15 s metrics (motion / longest still / camera / first move / brightness / saturation / warmth) | Reviewer | Posted | Views after 7 days |
|---|---|---|---|---|
| #2 Same Bed, Better Room | 8.8 / 1.2 s / 7.17 / 0.2 s / 173 / 0.19 / 30.2: all in range | 6.5 | | |
| #4 The Advent Stair | 7.7 / 0.4 s / 5.22 / 0.2 s / 164 / 0.27 / 44: all in range (65 glitched frames re-rendered) | 6-6.5 | | |
| #5 The Bed on the Ceiling | 12.7 / 0.4 s / 10.88 / 0.2 s / 150 / 0.25 / 36.3: all in range | 6 | | |
| #3 Three of Us in 3 × 2 m | 8.6 / 0.6 s / 5.72 / 0.6 s / 142 / 0.30 / 42.5: misses clear-change share (0.36) and first move (0.6 s) | – | | |
| #1 Tape Line, Turning Wall (v1) | 9.3 / 0.4 s / 6.31 / 0.4 s / 151 / 0.24 / 34.4: all in range; dusk too dark, v2 ordered | 8.5 / 7.5 | | |
| #8 Dinner for Eight | 10.3 / 0.6 s / 8.51 / 0.6 s / 154 / 0.23 / 36.0: misses first move (0.6 s) | – | | |
| #10 Kitchen Behind the Wall | 10.1 / 0.4 s / 7.14 / 0.2 s / 154 / 0.27 / 42.4: all in range | – | | |
| #7 Not One Handle in Sight | 11.6 / 1.0 s / 8.29 / 0.2 s / 173 / 0.23 / 37.3: all in range | – | | |
| #9 Count the Beds | 9.7 / 0.2 s / 6.77 / 0.2 s / 167 / 0.22 / 32.1: all in range | – | | |
| #6 Pull One Book | 11.4 / 0.0 s / 7.63 / 0.2 s / 176 / 0.24 / 44.8: all in range | – | | |
| #1 Tape Line v2 (posting version) | 10.5 / 0.4 s / 7.07 / 0.4 s / 163 / 0.22 / 33.9: all in range; one second at 131 | – | | |
