# Why room-build videos go viral: research report

Research date: 22 Nov 2026. Updated the same evening with Haven Haus's YouTube data, read through your browser.
Every count below is as of that date unless marked otherwise. Files in this folder: `videos.csv` (every
video-level number), `next_videos.md` (20 ranked ideas), `sources.md` (links with access dates),
`youtube_inventory.py` (re-pulls and re-analyses the inventory later).

Labels: **[measured]** is computed here from data or frames, **[fact]** is read from a source, **[inference]**
is a judgement, and **[brief]** comes from the owner's brief and was not re-checked.

## Summary

1. **Haven Haus's YouTube mirror**: 151K subscribers and 309 videos, 298 of them Shorts. The Shorts total about
   110 million views. The median Short has 64K views, 14 passed 1 million, and the top 10% (29 videos) earned 76%
   of all views. The top five alone earned 47% [measured].
2. **The hits are 34-53 s full-room tours, not 15 s clips** [measured]. 33 videos have exact lengths. Of those
   between 40 and 60 s, 8 of 11 passed 1M views; from 30 to 39 s, 4 of 11; under 30 s, none of 11. In
   May-July 2025 all four 21-22 s Shorts stalled at 17-26K views, while the 38-53 s ones reached 57K to 19.3M.
   The sample includes every top-12 video, so read it as "full tours win", not as an exact length rule.
3. **The top five share one structure** [measured, frame by frame]. Four open on an empty room and one on a wall
   breaking open. Then 4-10 storage zones are built and revealed in turn, 3D people use the furniture in four of
   them, and all end on a 1-2 s "like and follow" card.
4. **Bedrooms and kids' rooms win** [measured, era-adjusted]. Bedroom videos run at 1.51 times the channel's
   norm for their period and kids' rooms at 1.35 times. Titles naming a size (8 m², 24 m²) reach 1.34 times,
   and "two kids, one room" 1.36 times. Bathrooms (0.85), entryways (0.75) and living or dining rooms (0.70)
   trail.
5. **The account peaked in 2025** [measured]. All 14 million-view Shorts came out between May and December 2025.
   Nothing from 2026 has passed 853K. Posting fell from 5-6 a week to 2-3, and newer uploads use
   machine-translated captions and re-cut clips. The 19.3M kitchen re-cut as a 19 s clip got 24K views and no
   comments.
6. **The comments are arguments, from all over the world** [measured]. The most-liked comments attack
   practicality, such as a fridge with no room to vent (167 likes) or "how do you make that bed?" (32), or the
   title: a "24 m² apartment" with no kitchen or bathroom drew 2.3K and 2.2K likes and the channel's most
   comments (1,102). Comments arrive in Italian, Spanish, Turkish, Arabic, Korean and Japanese, and the Turkish
   version of the Little John meme ("Hasan" and "galvanized square steel") appears under the hits.
7. **The 2026 platform rules favour originals** [fact]. Instagram (30 Apr 2026) stops recommending accounts that
   mostly repost, TikTok keeps unoriginal re-uploads out of For You, and YouTube updated Shorts recommendations
   to favour original content in Oct 2026 (secondary source).
8. **Our kitchen render** [measured] matches the opening, the storage reveals, lights-on and the music. It is a
   15 s single-room build, while the proven hits are 35-50 s multi-zone tours with people in them.

## 1. What was accessed

| Source | Collected | How |
|---|---|---|
| Haven Haus YouTube (@Havenhaus1) | All 298 Shorts with title and views (as displayed, rounded); exact length, views, likes and upload date for 33; frame contact sheets for 7 (top 5 + 2 recent flops); top comments for 6 | your Claude desktop browser, 22 Nov 2026, public pages only |
| Haven Haus Instagram (@havenhaus_1) | Profile snapshot only (1M followers, 346 posts; owner later saw 1.8M and 579) | search engine copy; Instagram refuses automated readers |
| TikTok genre accounts | 21 videos with likes and comments, plus profile counts | search engine copies of TikTok pages |
| Douyin source creators | Not found | the watermark accounts are not in any index I could reach |
| Software and platform rules | Help-centre pages, official blogs, coverage | web search and page fetches |

Dates for the 265 Shorts without an exact date were interpolated from the 33 exact dates by grid position
(the grid lists newest first). Those are labelled "est." in `videos.csv`.

## 2. Haven Haus: the account

- YouTube: **151K subscribers, 309 videos**. The first Short is dated 19 May 2025 and the latest 21 Nov 2026,
  which averages 3.8 Shorts a week [measured].
- Instagram: 1M followers and 346 posts in an older snapshot; 1.8M and 579 at the owner's later check, with a
  bio selling MK Design Studio from $30/m² [fact; brief].
- Titles and descriptions are English, but the audience is global (section 6).
- The account reposts Douyin designers' videos (watermarks `@设计师温倪` and `@设计师阳阳` on Instagram [brief])
  and adds an end card. The end cards misspell the brand as "Hevan haus" and "Heavan Haus" [measured].
- Other accounts repost Haven Haus clips with credit to it: Massimo (@Rainmaker1973) on X, and Brazilian TikTok
  and Kwai accounts [fact].

## 3. View distribution and growth

| | Value [measured] |
|---|---|
| Shorts | 298 |
| Median views | 64,000 |
| 10th / 25th / 75th / 90th percentile | 24K / 39K / 163K / 536K |
| Videos with 1M+ / 100K+ / under 30K | 14 / 103 / 43 |
| Share of all views from the top 10% (29 videos) | 76% |
| Share from the top 5 | 47% |
| Likes per view (33 exact videos) | median 1.17%; top 12 median 0.91% |

**By quarter** (dates estimated for most videos; recent quarters are still collecting views)

| Quarter | Shorts | Per week | Median views | Best video | 1M+ videos |
|---|---|---|---|---|---|
| 2025 Q2 (from 19 May) | 33 | 5.5 | 33,000 | 19.3M | 3 |
| 2025 Q3 | 69 | 5.3 | 136,000 | 9.9M | 6 |
| 2025 Q4 | 81 | 6.2 | 82,000 | 5.5M | 5 |
| 2026 Q1 | 44 | 3.5 | 47,000 | 547K | 0 |
| 2026 Q2 | 28 | 2.2 | 36,000 | 689K | 0 |
| 2026 Q3 | 20 | 1.6 | 33,500 | 853K | 0 |
| 2026 Q4 (to 21 Nov) | 23 | 3.1 | 24,000 | 129K | 0 |

**What changed between the 2025 peak and 2026** [measured from titles and frames; reasons are inference]
- Titles moved from English SEO ("Modern Kitchen Design Setup 2025 | Smart & Stylish Layout Ideas") and hook
  headlines ("Be Bold — Even the Smallest Bedroom Can Fit a Walk-In Closet!") to machine-translated Chinese
  captions ("#WholeHouseCustomization", "#allCustomizedHome").
- Old footage came back as shorter re-cuts. The 19.3M kitchen returned as a 19 s fridge-wall clip on
  14 Nov 2026: 24K views, no comments.
- Recent uploads open on finished rooms more often.
- Possible platform causes [inference]: YouTube favouring original Shorts (Oct 2026) and recycled-content
  detection. The data cannot separate those from audience fatigue.

## 4. Hits vs flops

**Method.** Older videos have had longer to collect views, so each video is compared with the median of its 20
neighbours in upload order ("era-adjusted": 1.00 is normal for its period, 2.00 is double). Room type comes from
title keywords.

**By room type** [measured]

| Room type (from title) | Shorts | Median views | Era-adjusted median | In the top 30 (era-adjusted) |
|---|---|---|---|---|
| Bedroom (incl. small bedroom, study) | 47 | 130,000 | 1.51 | 8 |
| Kids' room | 48 | 111,500 | 1.35 | 6 |
| Wardrobe / closet | 50 | 81,000 | 1.05 | 6 |
| Kitchen | 54 | 50,500 | 1.00 | 7 |
| Balcony / laundry | 21 | 53,000 | 0.92 | 0 |
| Bay window | 14 | 56,500 | 0.90 | 0 |
| Bathroom | 17 | 46,000 | 0.85 | 0 |
| Entryway / shoe cabinet | 17 | 79,000 | 0.75 | 1 |
| Living, dining, TV wall | 17 | 45,000 | 0.70 | 0 |
| Whole small home (studio, loft, apartment) | 5 | 120,000 | 0.70 | 2 (including the 12.8M loft and the 5.5M 24 m² flat) |

The kitchen is the paradox: a median category with the single biggest hit (19.3M). Kitchens can explode, but
most don't.

**By title wording** [measured; era-adjusted median with the phrase vs without]

| Phrase in title | Shorts | With | Without |
|---|---|---|---|
| A size (㎡, m², "square meters") | 15 | 1.34 | 1.00 |
| Two kids / one room / two beds | 13 | 1.36 | 1.00 |
| Small / tiny | 72 | 1.13 | 1.00 |
| Genius / hack / smart | 66 | 1.13 | 0.99 |
| Bold / stop / don't | 29 | 1.12 | 1.00 |

**By length** [measured; 33 videos with exact length, chosen to include the top 12 plus a spread across time]

| Length | Videos | Median views | Era-adjusted median | 1M+ |
|---|---|---|---|---|
| Under 30 s | 11 | 25,898 | 0.73 | 0 |
| 30-39 s | 11 | 83,448 | 0.98 | 4 |
| 40-60 s | 11 | 2,571,206 | 20.83 | 8 |

- Rank correlation between length and views: 0.68, or 0.48 era-adjusted. The top 12 run 34-53 s (median 43).
- Cleanest comparison, from the same weeks (May-July 2025): 21, 22, 22 and 22 s got 16.9K-25.9K views; 38, 38,
  41, 47, 50, 53 and 53 s got 56.8K-19.3M.
- [inference] Length here is a stand-in for format: the long videos are full multi-zone tours with many reveals,
  and the short ones are single-feature clips.

## 5. Top-5 frame-by-frame breakdowns

Frames were sampled every 1-2 s from the public videos in your browser, for analysis only. Times are approximate
to the sampling step.

**#1 Kitchen: 19,269,469 views, 173K likes, 220 comments, 53 s, 26 Jun 2025**
- 0-3 s: a finished kitchen seen through a wall; the wall cracks and breaks away to open the room (the hook).
- 4-8 s: fridge wall; the cabinet above fills with baskets.
- 9-11 s: tall pantry; shelves fill with bins.
- 12-17 s: appliance cabinet: empty shelf, microwave lands, flap opens, rice cooker and kettle land.
- 18-28 s: hood corner, then lower pull-outs open and fill.
- **29-32 s, wow**: a 3D woman stands on a pull-out step drawer to reach the top cabinet. The second comment calls
  this "genius".
- 33-38 s: a narrow cabinet fills with bottles; a pull-out rack slides from beside the sink.
- 39-51 s: island with wine storage; a hidden table slides out and a chair lands.
- 52-53 s: black end card, "Hevan haus please like and follow".
- About 10 reveals, a cut every 3-6 s, no lights-on beat.

**#2 Loft: 12,761,012 views, 154K likes, 323 comments, 50 s, 28 May 2025**
- 0 s: black frame. 1-8 s: an empty walk-in-closet carcass fills with clothes; drawers and an ottoman pull out.
- 9-11 s: a hidden door in the wall opens onto the closet.
- 12-17 s: the loft bed builds (wire frame, platform, headboard, bedding, teddy); lights come on at 17 s.
- 18-22 s: the under-loft desk and shelves fill.
- 24-33 s: stairs with drawers that pull out and fill; a boy walks in.
- 34-43 s: an empty nook gets shelves, books, platform drawers and a fold-down desk.
- **44-46 s**: a woman sits at the new desk. 49 s: end card, "Heavan Haus LIKE AND FOLLOW".
- Commenters describe a mum vanishing into the wall at the start, and a scream. People and sound make a story.

**#3 Bedroom: 9,937,285 views, 115K likes, 184 comments, 41 s, 1 Jul 2025**
- 0 s: empty room. 2 s: a slatted lift-up bed base. 3 s: the bed is made.
- 5-11 s: arched partition, a blue door, shelving whose bins fill.
- 14-18 s: bed nook; the bed lifts and a drawer slides out underneath.
- 20-24 s: the wardrobe fills with clothes.
- 26-32 s: window desk, chair, bench; two people use the desk and window seat.
- 33-39 s: bench drawers and wardrobe details.

**#4 8 m² kids' room: 5,673,214 views, 64K likes, 103 comments, 53 s, 31 Jul 2025**
- 0 s: empty room. 2-10 s: a steel platform frame, then boards, a drawer and the bed.
- 18-26 s: the desk and bookshelves build; a child sits at the desk.
- **28-32 s**: a chalkboard door; the child draws on it, then it opens.
- 36-44 s: platform drawers open full of things; the wardrobe fills.
- 48-50 s: final wide with a sunflower rug. 52 s: end card.

**#5 24 m² "apartment": 5,513,915 views, 118K likes, 1,102 comments, 37 s, 11 Oct 2025**
- 0 s: empty double-height room. 2-6 s: platform, steel loft frame, loft deck.
- 7-13 s: arched partition, window frames, storage stairs whose drawers fill.
- 14-19 s: the nook under the loft becomes a sofa; drawers slide out beneath it.
- 21-30 s: projector screen; window desk, chair and rug.
- 31-35 s: wall cabinets, photo wall, final wide. 37 s: end card, "Haven Haus FOLLOW FOR".
- Commenters single out the cartoon sound effects (214 likes).

**What the five share** [measured]
- Length 37-53 s. A cut to a new zone every 3-8 s.
- Opening: an empty room in four of five; a wall breaking open in the kitchen.
- 6-12 build-and-reveal moments per video, almost all storage (drawers fill, doors open, hidden tables, stair
  drawers, lift-up beds).
- People in four of five: someone uses a feature (steps on a drawer, sits at a fold-down desk, draws on a door).
- An end card with text, which you will skip.

**What the recent flops look like** [measured]
- The 19 s re-cut of the #1 kitchen: one zone, no opening hook, no person. 24K views.
- A 35 s kitchen with busy black-and-white floral wallpaper that opens on the finished room: 6.8K views.

## 6. Comments: what viewers say

Read under the top five and one recent flop [measured].

| Theme | Examples (likes) |
|---|---|
| Practicality attacks | the fridge has no room to vent (167; repeated in Korean and Arabic); "how do you make your bed?" (32); "need ceiling fans here"; "the more cabinets, the smaller the room" (Vietnamese, 10); "what about radiators?" (Turkish) |
| Title fights | "it's not an apartment, it's a bedroom, no bathroom or kitchen" (2.3K); "I'd rather have a bathroom than two couch seating areas" (2.2K); "where is the kitchen area?" (1.2K) |
| Admiration | "the pull-out box doubling as a stool is genius"; "a kitchen with the groceries already done, the world of dreams" (Italian, 75) |
| Meme culture | Turkish "Hasan + galvanized square steel" jokes (43, 122); an Arabic comment, "finally the original video without the narration" (237) |
| Sound | "the Scooby-Doo sound effects" (214); "bro got way too excited with the sound effects" |
| Requests | "design a compact bedroom for a husband, wife and newborn: 3 m x 2 m, ceiling 2.9 m"; a home painting studio |

**Implications** [inference]
- Comment volume comes from debate. Designs that are clever but contestable (a bed in an alcove, a fridge
  tucked in) and bold captions draw replies. Keep claims defensible: "24 m² apartment" earned reach and a pile-on.
- No dialogue or text is needed. Viewers in a dozen languages engage with the pictures and sounds alone, which
  supports the no-text rule.
- Sound matters: commenters notice cartoon effects and screams. Our landing SFX are in the right territory.
- Requests come with dimensions. Answer them as a series.
- These clips also travel as dubbed meme narrations (Little John and Hasan), which multiplies exposure.

## 7. Source creators and software

- The watermark accounts (`@设计师温倪`, `@设计师阳阳`) were not found in Douyin's indexed pages or on the
  Chinese web.
- **The tool is most likely Kujiale (Coohom)** [inference, medium-high]:
  - Growth animation (bare shell to finished room) launched in April 2020 and spread widely on Douyin [fact].
  - The February 2021 render-video product adds walkthrough, growth, light and model animations, each frame at
    still-image quality [fact].
  - Since March 2024, custom cabinet doors open and then close by default [fact].
  - Template videos add lights switching on and material changes, with one-click publishing to Douyin [fact].
- Others in the same space [fact]: Zhihuxing growth animation; 3ds Max courses; SketchUp with Enscape or Lumion;
  D5 and Lumion phasing.
- The Haven Haus hits add 3D people and sound effects on top of the growth animation, so at least some source
  videos are custom-animated beyond the templates [inference].
- An Etsy listing sells 900 3D home-design videos as a Reels bundle [fact]. These renders circulate widely, so
  originality is scarce.

## 8. Genre scan (TikTok, from search snapshots)

- **@homedesign369**: 2.3M followers, 58.3M likes. Satirical "Little John" builds with an impossible premise:
  3.88 m² home 862.6K likes; coffin room 515.4K; billion-kids bedroom 395.6K.
- **@designer_bob**: 3M followers (May 2024), where the format started in 2022.
- **@dy02449xjp**: 480K followers (May 2024).
- **Plain 3D showcases** from small accounts: 5 to 5,439 likes.
- **Patterns** [measured, confounded by account size]:
  - Premise videos have a median of 307,650 likes against 634 for plain showcases.
  - Shares run at 9.4-17.7% of likes on the premise hits.
  - Hidden-storage tricks draw the highest comment rate (5.0%).
- Haven Haus confirms the same mechanics on YouTube: size premises ("8 m²", "24 m²", "6 m²") and
  two-kids-one-room premises outperform.

## 9. Platform mechanics (2026)

- **Instagram** [fact]:
  - From 30 Apr 2026, accounts that mostly post unoriginal content (now photos and carousels as well as Reels)
    are not recommended. 75% of US recommendations now come from original posts.
  - Originals replace reposts in recommendations (since 2024).
  - The strongest signals are watch time, likes per reach and sends per reach.
- **TikTok** [fact]: unoriginal or reproduced content without creative changes is not eligible for For You.
  Creators can see the reason and appeal.
- **YouTube Shorts** [fact]:
  - Views count from the first frame (Shorts since March 2025, everything since 24 Aug 2026). Earnings use
    engaged views.
  - Shorts recommendations favour original content (1 Oct 2026, secondary source).
- **Length**: third-party studies put entertainment Reels at 11-17 s and Shorts at 15-35 s [fact].
  - [inference] Haven Haus's own record says something else: on this niche, full tours of 35-50 s hold attention.
    Watch time, not shortness, is what the algorithm rewards.
- **Cadence** [fact]: Buffer finds 3-5 posts a week is the Instagram sweet spot and 2-5 on TikTok.
  - Haven Haus posted 5-6 a week during its 2025 peak [measured].
- **Originality** [inference]: the risk to Haven Haus's model (reposts, re-cuts) is our opportunity, because our
  renders are original by construction.

## 10. Our kitchen render against Haven Haus's hits

The tool was `pipeline/analyze_reference.py`, run on `out/kitchen_build.mp4` (15.0 s, 30 fps), alongside the
timeline in `rooms/kitchen/project.py`.

| Item | Haven Haus hits | Our kitchen (committed file) |
|---|---|---|
| Length | 37-53 s | 15.0 s |
| Opening | empty room (4 of 5) or a wall breaking open | empty room; first tile lands at 0.30 s ✓ |
| Zones | 4-10, a cut every 3-8 s | 3 stations joined by swings of 0.23-0.27 s |
| Reveals | 6-12 | 3 (drawer fill, upper doors, sink doors) |
| People | 4 of 5 | none |
| Lights-on | 1 of 5 | 12.45 s ✓ |
| Ending | end card with text | 2.47 s held wide (no text) ✓ |
| Pacing gaps | not applicable | visually quiet 1.8-3.8 s and 9.2-11.8 s (small or half-hidden pieces) |

`project.py` now schedules a pull-out pantry finale (12.80-13.98 s) that is not in the committed file.

**Fixes** [inference]
1. Add a **long cut (40-50 s)**: chain 3-4 zones of the same room (or room plus wardrobe), each with a build and
   a reveal.
2. Stage **one feature in use**. A simple stand-in figure is enough, or show the feature working: the step drawer
   pulling out, the pantry sliding out and filling.
3. Fill the two quiet stretches with heavy, fully visible landings.
4. Keep the 15 s cut as well and compare the two after 7 days. The long cut takes about 3 times the render time.

## 11. The viral formula (checklist)

- [ ] **Frame 1 hooks with no text**: the empty room, or a wall breaking open. Something moves by 0.3 s.
      [top 5: 4 empty, 1 wall break]
- [ ] **Room type**: small bedroom, kids' room (two kids, one room), wardrobe, or a kitchen with hidden tricks.
      [era-adjusted 1.51 / 1.35 / 1.05 / 1.00; bathroom, entry, living trail]
- [ ] **A visible constraint**: a tiny room you can see is tiny. Put the size in the caption ("8 m²").
      [size titles 1.34; two-kids 1.36]
- [ ] **A full tour, 35-50 s, for the main cut**: 4-10 zones with a cut every 3-8 s. Keep a 15 s cut to compare.
      [8 of 11 videos of 40 s+ passed 1M; 0 of 11 under 30 s]
- [ ] **6-12 reveals, all storage**: drawers fill, doors open, a hidden table, stair drawers, a lift-up bed.
      [all top 5]
- [ ] **One feature in use**: a person (or a convincing stand-in) uses the cleverest piece. [4 of 5; the step-stool
      drawer is the most praised moment]
- [ ] **A sound story**: a sound on every landing, plus a playful effect or two. [comments call out the effects
      and the scream]
- [ ] **Clever but contestable design and a bold, defensible caption** to start debate. [top comments are
      debates]
- [ ] **Clean, bright palettes**: warm white, light wood, one accent (green tile, olive sofa, blue door).
      Avoid busy patterns. [top 5; the floral-wallpaper flop]
- [ ] **End on a held wide that loops** instead of a text end card. [owner's rule; watch time and replays are
      top signals]
- [ ] **Original only, posted natively 3-5 times a week**, never re-cuts of old work. [platform rules; the
      re-cut flop]
- [ ] **A series from requests**: answer room requests that come with dimensions. [comments]

## 12. Confidence and open questions

| Claim | Confidence | Why |
|---|---|---|
| View distribution and concentration | high | all 298 Shorts (rounded display counts) |
| Bedrooms and kids' rooms outperform | medium-high | 95 videos, era-adjusted; tagged from titles |
| Long full tours outperform short clips | medium | 33 exact lengths, sample includes the top 12; the same-period comparison is strong |
| Top-5 structure | high | frame contact sheets |
| Comment themes | medium | top ~20 comments on 6 videos |
| Why 2026 declined | low | several causes possible |
| Kujiale as the source tool | medium-high | feature match |

Open: the Douyin creators behind the watermarks; Instagram per-post numbers (needs an Instagram login in your
browser, if you want that); audio analysis of the hits (BPM, SFX density). That needs a capture route we don't
have, or the original files.
