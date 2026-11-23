# Research brief: why room-build videos go viral (paste this into the research agent)

## Your mission
Do a deep, data-driven study of the viral "3D room-build" short videos made popular by the Instagram account
**@havenhaus_1 (Haven Haus)**, and of the genre around it. The output is a **viral formula** and a **ranked list of
next videos** that we will produce ourselves. We make **original** videos only. This is analysis, not reposting.

## What we make (so your recommendations fit)
- Vertical 1080x1920, 13-16 s, 25 fps; Instagram Reels, TikTok and YouTube Shorts.
- Code-rendered 3D (Python + Blender Cycles, photo-real). It starts on an empty room, then every piece flies in and lands
  separately: tiles, cabinets, counters, doors, drawers, contents, lights. Each landing has a sound, over original music.
- Storage moments: drawers open, fill and close; doors slam; a pull-out pantry slides out, fills and slides back; lights come on.
- Camera: still shots joined by fast 0.3 s swings, ending on a wide shot held for about 2 s.
- **No on-screen text** (owner's choice). Hooks must be visual.
- What renders best: cabinetry and storage-heavy rooms (kitchens, wardrobes and walk-ins, kids' rooms, laundry, studio
  apartments). Soft furnishings (sofas, bedding) are possible but look simpler.

## What we already know (verify and extend)
- @havenhaus_1: about 1.8M followers and 579 posts at last check (an older snapshot showed about 1M and 346). The bio sells
  "MK Design Studio, 2D & 3D interior & architectural design, from $30/m²". It links to "MK DESIGN STU…" and "MK INTERIOR ST…"
  accounts, with highlights for YouTube, Snapchat, TikTok and Facebook.
- YouTube mirror with public view counts: https://www.youtube.com/@Havenhaus1/shorts (same tagline: "interior design ideas
  to help you create a warm, stylish, modern home").
- Known Reels: kitchen (white uppers, wood base cabinets, black counter, flower cement tiles, window with blind) **587K**;
  empty dark room/hallway with kitchen behind **121K**; gaming-PC setup **6.4K**.
- **They repost Douyin creators.** Watermarks seen: `@设计师温倪` (on the 587K kitchen) and `@设计师阳阳` (on a grey
  channel-tufted headboard video); a "YT" watermark on another.
- Instagram has favoured original content since 2022; an April 2026 update hides accounts built mostly on reposts from
  Explore and recommendations.
- Baseline from frame-by-frame analysis of 4 viral room-build videos:
  - an empty room in frame 1, with no intro;
  - a landing every 0.3-0.6 s, about 20-55 landings in 13-16 s;
  - storage reveals are the star;
  - a lights-on moment;
  - music at about 125-128 BPM from the first frame, with landings not locked to the beat;
  - 3 of the 4 videos used TikTok "reply to comment" stickers as hooks.

## Tasks
1. **Account inventory.** List every Short/Reel you can reach on the YouTube mirror (and Instagram/TikTok/Facebook if
   accessible). For each video record:
   - URL, date, duration, views, likes, comments, title/caption and hashtags;
   - watermark/original creator, if visible.
   Then compute: view distribution (median, top 10%, flops), posting cadence, and growth over time.
2. **Tag each video:**
   - room type;
   - style/palette (white+wood, cream, dark/moody, colourful);
   - day or night lighting;
   - format (pieces flying in, walkthrough, before/after, real footage);
   - storage or transformation reveal (yes/no, and what);
   - camera style; opening frame (empty or finished room); lights-on moment;
   - length; music type (trending song or ambient); on-screen text; loopability.
3. **Hits vs flops.** Compare the top 20 with the bottom 20. Which features predict views? Give numbers, not vibes, and
   flag small samples.
4. **Frame-by-frame breakdown of the top 5 hits.** For each:
   - every camera move and every placement with start and land times;
   - landings per second;
   - when the "wow" moment happens and what it is;
   - length of the final hold;
   - why it loops.
5. **Source creators.** Identify the Douyin designers behind their reposts (start with the watermarks above): follower
   counts, top videos, posting rate, and the software they use (Kujiale/Coohom, 3vjia, D5 Render, Lumion, 3ds Max). Cite evidence.
6. **Genre scan.** Find 10-20 other accounts in this niche on TikTok, Instagram and YouTube, plus their top videos and
   views. Which room types, twists and palettes recur in the biggest hits?
7. **Comments.** What do viewers ask or request ("do my room", price, which app, complaints)? Which video types pull the
   most comments and shares?
8. **Platform mechanics (2026).** Ideal length, posting cadence, trending sound versus original audio, how originality
   rules affect accounts like this, and what to do instead of on-screen text hooks.

## Deliverables
- `videos.csv`: one row per video with all metrics and tags.
- `report.md`:
  - findings with simple charts or tables;
  - the **viral formula** as a checklist;
  - the top-5 frame-by-frame breakdowns;
  - what you could not access and why.
- `next_videos.md`: **20 ranked video ideas** (room + twist/reveal + palette + why it should hit). Each has a 15 s shot
  outline: camera stations, landing order, the storage/wow moment and its timing, and the final shot. No text overlays.
- A sources list with links and **access dates** (view counts change).
- If you have access to GitHub repo `cgktd5856g-max/home-design`, save these in `research/` on branch
  `claude/viral-video-research-vq8gmc`.

## Rules
- Analysis only: don't repost or republish anyone's videos, and don't copy their on-screen text, watermarks, end cards or music.
- Use only public data and respect platform terms. If a site needs a login you don't have, say so and use other sources.
- Separate facts from inferences. Give sample sizes and confidence. Never invent numbers.
