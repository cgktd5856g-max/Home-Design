# Home-Design: original room-build videos rendered from code

Vertical room-build videos (1080x1920) for TikTok, Reels and Shorts. Python describes the room, and Blender Cycles
renders it. The video opens on an empty room, every piece flies in and lands with a sound, storage fills, the lights
come on, and it ends on a wide shot that loops.

## Read first
- `production/LESSONS.md`: what we have learned. Read it before you start; it saves hours.
- `HANDOFF.md`: the production process, the pipeline and its conventions.
- `research/top10_ideas.md`: the current 10 videos, their final plans and the posting calendar.
- `research/report.md` and `research/trends_nov2026.md`: the evidence behind the rules.

## The owner's rules
- No on-screen text of any kind: no captions, labels, readable letters or numbers on props, or end card.
- Original work only: no copyrighted characters, logos or recognisable IP, and original music and sounds.
- Clean and bright, never dark or grainy:
  - a white or pale-grey shell, light wood, one muted accent;
  - the colour comes from filled storage;
  - no cream or orange cast.
- Packed smart storage, a whole room (not one piece) and a different layout every video.
- Code-only rendering, free tools, lean work. Ask before spending money (for example a rented GPU).

## Working rules
- **Usage limit.** All sessions share one account limit. Keep at most about 3 sessions building at once; renders cost
  almost nothing.
- **Renders.** Never end your turn while a render runs: keep a background waiter (see `production/LESSONS.md`).
- **Before Blender.** Make probe stills and a low-res preview, and run `python3 research/hh_metrics.py` on it, before
  any Blender time.
- **Git.** Push only to your own branch. Don't commit `.render/` or `*_preview*.mp4`.

## Starting a render session for a new video
```bash
python3 -I production/tools/make_brief.py production/tools/session_template.md \
    production/sessions/<slug>.md <plan id> "<title>" <slug> claude/video-<short> <long 0|1> <rank in top10>
```
Commit and push the brief, then start a cloud session on this branch with: "read production/sessions/<slug>.md and
follow it".

## Keep getting better
When you learn something that would save the next person time or improve the videos, write it down as one concrete
line in `production/LESSONS.md`. If you are a render session on your own branch, put it under "Lessons for next time"
in your `REPORT.md` instead. Keep this file short; details go in LESSONS.md.
