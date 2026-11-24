You are one of 10 parallel cloud sessions, each making ONE original room-build video for the same owner. Yours is idea #{N}: "{TITLE}". Work fully on your own; the owner wants finished videos, not questions. Make sensible decisions and keep going.

Repository: this session has cgktd5856g-max/Home-Design checked out at branch claude/new-session-h1qjkk. Commit and push your work only to your own branch, {BRANCH} (create it from the checkout). Never push to any other branch, never force-push.

READ FIRST, fully:
0. production/LESSONS.md: what earlier sessions learned the hard way (render keep-alive, the 0.3 s hook, framing, colour, usage limits). Apply it.
1. HANDOFF.md (repo root): the production process, pipeline, conventions and lessons learned. Follow sections 4-8 exactly.
2. research/top10_ideas.md, section "{N}." for your idea's plan (and the "Rules for all 10" section).
3. rooms/bedroom/project.py: the most complete room; copy its structure (HOLDS gliding camera, fixed light slots, door_z / drawer_fn / appear helpers, cloth/pillow/garment/stack/plant helpers, BLENDER dict).
4. pipeline/figure.py (if present): the stand-in person figure for the "person moment".

THE JOB
- Build rooms/{SLUG}/project.py from your idea's plan. A whole room, frame 1 = the empty room, the first landing by 0.3 s, a landing every 0.3-0.6 s, 6-12 storage moments, the camera gliding inside every shot (no still moment over about 1.5 s), colour from filled storage on screen early, the lights-on payoff, and a held drifting wide at the end that loops back to the frame-1 view.
- Owner's rules: NO on-screen text of any kind (no captions, labels, readable letters or numbers on props, no end card); no copyrighted characters, logos or recognisable IP; original music and sounds only (pipeline/music.py); clean and bright, never dark or grainy; white or pale-grey shell, light or mid wood, one accent; no cream or orange cast, no dark wood.
- First cut: the 15 s cut from the plan (25 fps, 375 frames).

STEPS (HANDOFF.md section 5; work in /home/user/Home-Design/.render/{SLUG}, never /tmp)
1. Setup (HANDOFF.md section 4): pip install numpy scipy opencv-python-headless; uv venv /root/bpyenv && uv pip install --python /root/bpyenv/bin/python bpy==5.3.0 numpy.
2. Probe stills of the finished room from every station with the code renderer; look at them and fix framing, collisions, empty areas and colour before going on.
3. Animation probes at busy moments; fix pops, collisions, pieces landing out of frame.
4. Low-res preview with music. Run python3 research/hh_metrics.py on the preview: motion, share of clear changes, longest still and camera movement should be near the targets (the hits' ranges); aim to miss at most one target. Tune the timeline and camera here, where iterations are cheap, not after the Blender render.
   REVIEW GATE 1: spawn a fresh reviewer subagent (Agent tool) that has NOT seen your reasoning. Give it only: a contact sheet of preview frames every 0.5 s (make one with ffmpeg), the hh_metrics output, your idea's plan section, and the "Rules for all 10" and research/report.md section 11 checklist. Ask it to act as a tough viral-video editor: would frame 1 stop the scroll with no text? Does something land every 0.3-0.6 s? Is the wow moment clear and big in frame? Is every storage moment readable at phone size? Does the camera keep moving? Is the colour clean and bright? Score 1-10, list concrete fixes. Apply the fixes and re-preview until it scores 8 or more (at most 3 rounds).
5. Blender look test at 3-4 moments (540x960); check materials, brightness and colour; fix.
   REVIEW GATE 2: a fresh reviewer subagent looks at the Blender test stills only and judges them as a viewer scrolling on a phone: does it look premium and real, clean and bright, with colour from filled storage? Fix what it flags before the final render.
6. Final Blender render of the 15 s cut, DETACHED and resumable as in HANDOFF.md step 5 (setsid nohup ... &), 720x1280, --samples 16 --adaptive 0.04 --bounces 4,2,2 --nobevel. Set 'persistent': False in your project's BLENDER dict first: Cycles persistent data causes black-floor frames in long runs. After the render, scan every frame (pixels under 12 over more than 2% of the frame) and re-render any bad ones before encoding. Expect about 2-3 hours. IMPORTANT: never end your turn while a render runs. An idle session's container can be put to sleep, and that kills the render. Keep a background waiter so you get re-invoked: Bash with run_in_background=true and timeout 7200000 running an until-loop that exits when the render finishes or its process disappears (sleep 60 between checks). Each time it fires, check the log (grep for "^frame", "Traceback", "^done in") and the frame count, restart the same render command if the process died (finished frames are skipped; delete an unreadable last frame), and re-arm the waiter until all frames are done.
7. Encode both versions with pipeline/mkvideo_png.py at 1080x1920 (music and sfx_only) with --grade (start from 1.35,0.03 and adjust so hh_metrics colour lands in the band). Run pipeline/qa.py and research/hh_metrics.py on the final.
8. Deliver: out/{SLUG}_15s.mp4, out/{SLUG}_15s_sfx_only.mp4, out/{SLUG}_still.jpg (the best final wide), and rooms/{SLUG}/REPORT.md (what you built, the shot list with times, hh_metrics results, render time, anything you'd improve, and a section "Lessons for next time": one concrete line each, with numbers or the fix, for anything that cost you time or that the next session should do differently). Commit and push to {BRANCH}.

PROGRESS: commit and push early checkpoints to {BRANCH} so the coordinator can review: rooms/{SLUG}/progress/stills.jpg after step 2, the hh_metrics output of the preview after step 4 (in rooms/{SLUG}/progress/preview_metrics.txt), a Blender test sheet after step 5. Don't commit .render/ or files named *_preview*.mp4.

{LONG_CUT}

Quality first: this is the owner's real channel. If something looks wrong in a still, fix it before rendering. Report honestly in REPORT.md, including anything you couldn't get right.
