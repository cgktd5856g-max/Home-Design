# Handoff: why room-build videos go viral (Haven Haus study)

Prepared 22 Nov 2026. Read this first, then `research/report.md` for the evidence and
`research/next_videos.md` for what to make. All paths are relative to the project folder.

## 1. The project

- **What the owner makes**: original vertical "room-build" videos for TikTok, Reels and Shorts, rendered
  entirely from code. Python describes the room. Version 1 used a small C++ path tracer; version 2 uses Blender
  Cycles.
- **The format**: 1080x1920, 13-16 s, 25 fps.
  - It opens on the empty room.
  - Every piece flies in and lands with a sound, over original music.
  - Storage moments: drawers fill, doors open.
  - Still camera stations are joined by ~0.3 s swings, and the lights come on near the end.
  - It ends on a held final wide. **No on-screen text.**
- **The owner's standing preferences**:
  - packed smart storage and a different layout every video;
  - clean, bright renders, never dark or grainy;
  - no on-screen text;
  - theme and fandom ideas are welcome, but no copyrighted characters or logos;
  - code-only rendering (no Coohom or other design apps);
  - lean, efficient work.
- **The research question**: why do @havenhaus_1 (Haven Haus) 3D room-build videos go viral, what is the
  formula, and what should the owner make next. The original brief is `research/agent_research_prompt.md`.

## 2. Rules to keep following

- **Analysis only.** Don't repost or republish anyone's videos, and don't copy their on-screen text,
  watermarks, end cards or music.
- **Public data only, within platform terms.** If a site needs a login you don't have, say so and use other
  sources.
- **Facts apart from inferences.** Give sample sizes and confidence, and never invent numbers. The report labels
  every claim [measured], [fact], [inference] or [brief].

## 3. What was studied

- **Haven Haus's YouTube mirror (@Havenhaus1)**: 151K subscribers, 309 videos, 298 Shorts dated 19 May 2025
  to 21 Nov 2026, about 110M views. Collected:
  - titles and views for all 298;
  - exact length, likes and date for 33;
  - frame-by-frame breakdowns of the top 5;
  - top comments under 6 videos.
- **In-depth comparison, 59 Shorts** played in full and measured every 0.2 s. Measured: motion, scene changes,
  still stretches, camera movement, colour and sound. Five frames of each were also coded by eye.
  - 25 hits (654K-19.3M views), each paired with a flop from the same weeks (12.8K-88K).
  - The 4 best and the 5 worst 2026 uploads.
- **Also covered**: TikTok genre accounts (from search-engine copies), 2026 platform rules, the likely source
  software (Kujiale), and the owner's own renders measured the same way.

## 4. Findings, most important first

1. **A whole room, not one piece.** 28 of 29 hits build or transform a whole room, against 12 of 30 flops. The
   other flops show one cabinet, wall or corner.
2. **The camera never stops.** The hits' camera glides through every shot, while flops hold locked-off shots.
   In the 25 same-week pairs:
   - the hit's camera moved more in 21;
   - motion per 0.2 s was 8.4 against 5.1, higher in the hit in 21 of 24;
   - the longest still stretch was 1.4 s against 2.6 s, shorter in the hit in 20 of 24.
3. **A clean colour band.** Hits use a white or pale-grey shell and light or mid wood, with the colour coming
   from filled storage. The middle 80% of hits run saturation 0.17-0.38 and warmth 22-57. Off the band (cream or
   orange cast, oversaturated, or dark): 2 of 25 hits against 13 of 25 flops.
4. **Long full tours.** Hits run 34-53 s (median 39 s against 32 s for flops; the hit was longer in 22 of 25
   pairs).
   - Of 33 videos with exact lengths, 8 of 11 between 40 and 60 s passed 1M views; 0 of 11 under 30 s did.
   - Hits are longer because they show more zones, not because they cut faster: shots run about 2.8 s in both.
5. **Room type**, era-adjusted (1.00 is normal for the period):
   - bedroom 1.51, kids' room 1.35, wardrobe 1.05;
   - kitchen 1.00, though it has the single biggest hit at 19.3M;
   - balcony 0.92, bay window 0.90, bathroom 0.85, entryway 0.75, living or dining room 0.70.
   - Titles naming a size (8 m²) reach 1.34, and "two kids, one room" 1.36.
6. **The top-5 structure**:
   - frame 1 is the empty room, or a wall breaking open;
   - 6-12 storage moments are built and revealed;
   - a new zone every 3-8 s;
   - a 3D person uses a feature in 4 of the 5.
7. **Sound does not separate hits from flops.** Sound density and loudness are the same, and scene changes
   don't land on the beat. Tempo leans to 111-125 BPM in hits, but the evidence is weak. Commenters do notice
   playful sound effects.
8. **2026 is a slump.** No 2026 upload passed 853K. Posting fell, and uploads turned to re-cuts and
   machine-translated captions.
   - Pacing was the same for the best and the worst 2026 videos.
   - Every 2026 hit was a bedroom or kids' room with a raised or loft bed. The flops were single features and
     "dimension guides".
9. **Comments are debates.** People argue about practicality and about misleading titles, from all over the
   world. No text is needed for them to engage.
10. **2026 platform rules favour original content**: Instagram from 30 Apr 2026; TikTok; YouTube Shorts from
    Oct 2026 (secondary source). The owner's renders are original by construction.

## 5. Our renders against the hits

Measure any render with `python3 research/hh_metrics.py <video>` (needs ffmpeg and numpy).

| Measure | Target (hits' range) | Kitchen v1 | Kitchen v2 (Blender) |
|---|---|---|---|
| Motion per 0.2 s | 7.5 or more | 2.1 | 3.0 |
| Share of 0.2 s steps with a clear change | 0.39 or more | 0.12 | 0.24 |
| Longest near-still stretch | 1.8 s or less | 2.4 s | 2.4 s |
| Camera movement (quietest tiles, per 0.4 s) | 1.8 or more | 0.8 | 1.06 |
| First clear movement | 0.4 s or less | 0.4 s ✓ | 0.4 s ✓ |
| Brightness (0-255) | 138-178 | 200 | 170 ✓ |
| Saturation | 0.17-0.38 | 0.11 | 0.11 |
| Warmth (red minus blue) | 22-57 | 18.3 | 14.5 |
| Length, long cut | 34-46 s | 15.0 s | 15.4 s |

The biggest gaps are that the camera stands still between swings, there is too little motion, and the colour is
grey and slightly cool.

## 6. What to make next

The top 10 of the ranked list are below. The full list of 20, with 15 s outlines and long-cut plans, is in
`research/next_videos.md`.

1. Three kids, one 9 m² room
2. 7 m² bedroom with a loft bed and walk-in closet
3. Galley kitchen with a step drawer and pull-out pantry
4. 18 m² studio where everything folds away
5. Couple's bedroom with a lift-up bed and full wardrobe
6. Two-desk study in 9 m²
7. Space-capsule kids' room
8. Nursery
9. Walk-in wardrobe in a 1.5 m corridor
10. Holiday baking kitchen with a mixer lift

**Rules for every video**:
- Open on the empty room, with the first landing by 0.3 s.
- Build the whole room.
- Keep the camera gliding (a slow push-in, slide or orbit) inside every station.
- White or pale-grey shell, light wood, and colourful filled storage.
- A sound on every landing, over original music at about 115-125 BPM.
- No on-screen text.

Make ideas 1-5 in two cuts, 15 s and 40-50 s, and compare them after 7 days.

## 7. Suggested next tasks

1. **Add a slow continuous camera move inside every station**, keeping the 0.3 s swings. The pipeline is
   `pipeline/blender_render.py` with the room timelines in `rooms/*/project.py`; see `README.md`.
2. **Warm the palette**: light oak floor or fronts, and storage filled with colourful things (books, clothes,
   jars).
3. **Render idea 1 or 2** as a 15 s and a 45 s cut, and iterate until `hh_metrics.py` passes.
4. **Post, then measure.** After 7 days, add each video's numbers to `research/videos.csv` (set = `ours`) and
   run `python3 research/youtube_inventory.py stats research/videos.csv --where set=ours`.

## 8. Gaps and confidence

- **Not found or not available**:
  - the Douyin designers behind the watermarks (`@设计师温倪`, `@设计师阳阳`);
  - Instagram per-post numbers, which need a login;
  - live TikTok genre numbers, since they come from search-engine copies of the pages.
- **Judged by eye, not blind**: "whole room" and palette were coded by someone who knew which videos were hits.
  A blind pixel measure agrees on colour.
- **Weak evidence**: the tempo finding.
- **Data limits**: dates for 265 Shorts are estimated from their position on the channel, and all view counts
  are as of 22 Nov 2026.

## 9. Files

| File | What it is |
|---|---|
| `research/report.md` | full evidence: 13 sections, with tables, confidence and sources |
| `research/next_videos.md` | 20 ranked ideas with 15 s outlines and long-cut plans |
| `research/videos.csv` | 325 rows: all 298 Haven Haus Shorts, plus TikTok, Instagram and X genre examples |
| `research/deep_analysis.csv` | the 59 measured Shorts: every pixel, camera and sound measure and code, with links |
| `research/sources.md` | every source, with access dates |
| `research/hh_metrics.py` | measures a render against the hits' ranges |
| `research/youtube_inventory.py` | re-pulls the YouTube inventory (needs a YouTube Data API key) and runs stats on the CSV |
| `research/agent_research_prompt.md` | the original brief |
| `RESEARCH.md` | earlier note: how viral accounts source their videos, and why we make originals |
| `README.md`, `pipeline/`, `rooms/` | the render pipeline, the kitchen project and an 11 m² bedroom project in progress (`rooms/bedroom/`) |
| `out/*.jpg`, `out/*.png` | stills of our kitchen renders. The videos are in the GitHub repo (`cgktd5856g-max/Home-Design`, branch `claude/viral-video-research-vq8gmc`) |
