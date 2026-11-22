# Home-Design: viral room-build videos, rendered from code

Douyin/TikTok-style "room build" reels. The video starts on an empty room, then every tile, cabinet,
drawer, door, plate and lamp flies in and lands, with original music and a sound on every landing.
There is no Blender, no design app and no GPU: Python describes the room, and a small C++ path tracer
renders it.

See **[RESEARCH.md](RESEARCH.md)** for how the viral accounts (like @havenhaus_1) get their videos and
why we make originals instead.

## Output

- `out/kitchen_build.mp4`: 1080x1920 with original music
- `out/kitchen_build_sfx_only.mp4`: landing sounds only (add a trending sound in TikTok/IG)
- previews (`out/*_preview*.mp4`) are not committed; regenerate them with `run.py ... preview`
- `out/kitchen_still.jpg`: stills of the finished room

## Make a video

```bash
pip install numpy scipy opencv-python-headless      # plus g++ (OpenMP) and ffmpeg
P=rooms/kitchen; WORK=/tmp/kitchen_work

# stills of the finished room from each camera station (seconds)
ROOM_REST=1 python3 pipeline/run.py $P/project.py $WORK probe 0.5,1.5,2.5,3.5

# check poses at busy moments of the animation
python3 pipeline/run.py $P/project.py $WORK probe 1.0,4.9,6.5,12.6

# low-res preview with music (about 5 min on 4 cores)
python3 pipeline/run.py $P/project.py $WORK preview --out out/kitchen_preview.mp4

# final (about 20-25 min on 4 cores); add --size 1080x1920 for a native 1080p render (about 2.5x slower)
python3 pipeline/run.py $P/project.py $WORK final --out out/kitchen_build.mp4
python3 pipeline/qa.py $WORK out/kitchen_build.mp4
```

## New room

Copy `rooms/kitchen/project.py` and edit it:

- `build()`: one named piece per thing that moves on its own
- `camera()`: still stations joined by short swings, ending on a wide shot
- `lights()`
- `timeline()`: `drop`, `slide`, `fly`, `grow`, `from_camera`, or `custom` for doors and drawers

Units are metres; x = east, y = north, z = up.

## Layout

```
pipeline/   roomkit.py (scene)  animkit.py (timeline)  pt.cpp (path tracer)  dn.cpp (denoiser)
            post.py / mkvideo.py (grade + encode)  music.py (original music + SFX)  qa.py  run.py
rooms/      one folder per room: kitchen/project.py
out/        rendered videos and stills
```
