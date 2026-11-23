# Why room-build videos go viral: research report

Research date: 22 Nov 2026. Every count below is as of that date unless marked otherwise. Files in this folder:
`videos.csv` (every video-level number found), `next_videos.md` (20 ranked ideas with shot outlines),
`sources.md` (links with access dates), `youtube_inventory.py` (fills and analyses the Haven Haus inventory).

Labels used throughout: **[fact]** is read from a source, **[measured]** is computed here from data or our own
render, **[inference]** is a judgement, and **[brief]** comes from the owner's research brief and was not re-checked.

## Summary

1. **Haven Haus's per-video numbers could not be collected from this session** (section 1). Instagram, X and
   YouTube's feeds refuse automated reading, YouTube's video grid needs a browser, and the browser extension was
   not connected. No number in this report is estimated or invented. The known points: their kitchen Reel (587K)
   beat their gaming-PC Reel (6.4K) by about 92 times [brief, measured ratio]. With three data points, that is
   a hint, not proof.
2. **The source clips are almost certainly made with Kujiale (Coohom outside China) "growth animation"**
   [inference, medium-high]. Kujiale shipped growth animation in 2020 and says it spread widely on Douyin. Its
   video tools add lights switching on, and since March 2024 custom cabinet doors that open and then close by
   default [fact]. That is exactly the "doors appear open, then slam shut" look.
3. **In the genre, the giant hits have a premise, not just a room** [measured, confounded]. Six "impossible
   constraint" videos (0 m², 3.88 m² for eight kids, a coffin room) have a median of 307,650 likes. Six plain 3D room
   showcases have a median of 634. One very large account makes all six premise videos, so account
   size explains part of the gap.
4. **Hits get sent, not just liked** [measured]. On the three premise hits where saves and shares were visible,
   shares were 9.4% to 17.7% of likes. Instagram says sends per reach, watch time and likes per reach are its
   strongest ranking signals [fact].
5. **2026 platform rules favour originals** [fact]. Instagram (30 Apr 2026) stops recommending accounts that
   mostly repost. TikTok keeps unoriginal re-uploads out of For You. YouTube updated Shorts recommendations to
   favour original content (Oct 2026, secondary source). An aggregator like Haven Haus is on the wrong side of
   all three. Code-rendered originals are on the right side.
6. **Our kitchen render already follows most of the formula** [measured]. It opens on the empty room, swings
   in 0.23-0.27 s, holds the final wide for 2.47 s, and has three storage reveals, a lights-on moment and
   126 BPM music. The main gap is two visually quiet stretches (about 1.9 s and 2.7 s of low motion) where
   only small or half-hidden pieces move.
7. **The inventory can be completed in about 10 minutes** once a free YouTube Data API key exists:
   `youtube_inventory.py fetch`, then tag by hand, then `stats` prints the hits-vs-flops tables.

## 1. What could and could not be accessed

| Source | What I got | Why not more |
|---|---|---|
| YouTube @Havenhaus1 (mirror) | Channel ID `UCuVYKD6oo6AAo7-14U5BiIg`, description, page keywords | The Shorts grid is drawn by JavaScript, so the page reader sees no list. The RSS feed refuses automated readers. This workspace's network cannot reach YouTube or Google APIs. |
| Instagram @havenhaus_1 | A search-engine snapshot of the profile (1M followers, 346 posts) | Instagram refuses automated readers. |
| X repost of a Haven Haus clip | Headline and date | X refuses automated readers. |
| TikTok | Search snapshots of 10 video pages, 2 profiles and 11 discover or tag pages: likes, comments, saves, shares, captions | Video pages refuse automated readers, but search snippets carry the counts. |
| Douyin | A few indexed user and video pages | The two watermark accounts were not in the index. The workspace network blocks Douyin. |
| Your Chrome (Claude in Chrome) | Nothing | The extension was not connected because the request came from the mobile app. |
| Video files for frame-by-frame work | Nothing | There was no way to download them. We would not re-host others' videos anyway. |

**Consequence.** Tasks 1-4 of the brief (full inventory, tags, hits vs flops, top-5 frame breakdowns) cannot be
done with real Haven Haus numbers yet. Instead this report gives: everything verifiable about Haven Haus
(section 2), the software and source evidence (3), a genre sample with real counts (4), comment signals (5),
platform rules (6), a measured breakdown of our own render (7), and the formula (8).

**How to unblock (any one works):**
1. Create a free YouTube Data API key (Google Cloud console, enable "YouTube Data API v3", Credentials), then run
   `python3 research/youtube_inventory.py fetch --key KEY`. A full pull costs about 25 of 10,000 free daily quota
   units. Tag the rows by watching the videos, then run
   `python3 research/youtube_inventory.py stats research/videos_youtube.csv --metric views`.
2. Open this chat on a computer with Chrome and the Claude extension, then ask for a rerun. I will read the Shorts
   grid and video pages directly.
3. For frame-by-frame breakdowns of the top 5: save the five files privately and run
   `python3 -I pipeline/analyze_reference.py <video> <out_dir>`. Use them for analysis only and never re-upload.

## 2. Haven Haus: what is verifiable

**Account**
- Search snapshot of the Instagram profile: 1M followers, 3 following, 346 posts. The bio then was "Interior design
  ideas to help you create a warm, stylish, modern home. Dm For collab & pr" [fact; snapshot date unknown].
- The owner's later check: 1.8M followers, 579 posts, a bio selling MK Design Studio from $30/m² [brief].
  That is +0.8M followers over +233 posts, about 3,400 followers per post. This is rough because neither snapshot
  is dated [measured].
- YouTube mirror: channel `UCuVYKD6oo6AAo7-14U5BiIg`, same tagline. Page keywords include *interior design,
  kitchen makeover, wardrobe design, small space design* [fact]. Their own SEO bets on kitchens, wardrobes and
  small spaces.
- A Pinterest user saved the Instagram profile on 20 Nov 2025 [fact; a weak signal of interest off the platform].

**Known videos** (n = 5; full rows in `videos.csv`)

| Video | Views | Watermark | Note |
|---|---|---|---|
| Kitchen: white uppers, wood base, black counter, flower cement tiles, window with blind | 587K | `@设计师温倪` | best known [brief] |
| Empty dark room / hallway with kitchen behind | 121K | none noted | [brief] |
| Grey channel-tufted headboard wall | unknown | `@设计师阳阳` | [brief] |
| Gaming-PC setup | 6.4K | "YT" | worst known [brief] |
| Balcony cabinet "with fully functional areas" | unknown | credited to havenhaus_1 | reposted on X by Massimo (@Rainmaker1973), 12 Dec 2025 [fact] |

- The kitchen got about 92 times the gaming setup's views and 4.9 times the hallway's [measured].
  [inference, low confidence, n = 3] Rooms dense with cabinetry and storage beat gadget setups.
- Haven Haus clips get reposted again **with credit to havenhaus_1**: by the X account Massimo, and by Brazilian
  TikTok and Kwai accounts ("Vídeo original por @lux_.interiors e @havenhaus_1"; "Will Construindo") [fact].
- [inference] Each repost hop drops the real Douyin designer from the credit. Instagram already swaps reposts for
  the original in recommendations, and since April 2026 it removes repost-heavy accounts from recommendations
  entirely. That is the main risk to Haven Haus's model and the opening for genuinely original renders.

## 3. Source creators and the software behind the look

**The two watermarks.** I searched Douyin's indexed user pages and the Chinese web for `@设计师温倪`
("Designer Wen Ni", also as 温妮) and `@设计师阳阳` ("Designer Yangyang"). There was no matching interior-design
account, only unrelated accounts with similar names (a hairdresser, a dance teacher, a lifestyle account). Their
follower counts, top videos and posting rates are **not found**.

**Software evidence**
- **Kujiale (酷家乐; Coohom outside China)** [fact]
  - Kujiale's help centre: growth animation (生长动画, "from bare shell to finished room") launched in April 2020
    and was often seen trending on Douyin. In February 2021 Kujiale added a render-video product: walkthrough
    video, growth animation, light animation and model animation, each frame rendered at still-image quality.
  - Template videos: models growing in, lights switching on and off, colour-temperature changes and material
    overlays, with one-click publishing to Douyin and Kuaishou.
  - March 2024 (Kujiale tutorial on Douyin): walkthrough videos gained open/close animations for custom cabinets
    and growth presets. **The default is to open the doors first, then close them**, with an adjustable gap
    between growing and opening.
  - Sina Home (2021) reports a vendor claim: a skilled Douyin designer with 1M followers needed 3 days per video
    with other software, and about 1 hour with Kujiale's templates.
- **Other tools seen** [fact]: 知户型 (Zhihuxing) claims it was first with growth animation; 3ds Max courses
  sold as "Douyin-viral growth animation" (2020); a Zhihu answer names SketchUp with Enscape or Lumion, or
  Chinese renderers built on Unreal Engine 4. D5 and Lumion "phasing" are covered in `RESEARCH.md`.
- **Judgement** [inference, medium-high for the tool family, unconfirmed per creator]: catalogue whole-room
  cabinetry, pieces growing into place, doors opening then closing in place, and lights switching on add up to
  Kujiale growth animation plus its custom-cabinet door presets.
- **Repost economy** [fact]: an Etsy listing sells a bundle of 900 3D animated home-design videos for Reels and
  TikTok. The same renders circulate across many accounts, so originality is scarce, and scarcity is what the
  platforms now reward.

**What this means for us** [inference]: template clips share tells. Pieces grow from the floor with the same
easing, doors open and close in place, and the props are catalogue items. Stay in the genre but beat the
templates on: physical landings (drop, squash, small bounce, sound), contents filling in rhythm, real camera
swings, and payoffs a template can't make (a pull-out pantry that slides out, fills and slides back).

## 4. Genre scan

Eighteen accounts are listed here, and `videos.csv` holds four more small ones. Followers are shown where a source
gives them. Video counts are in `videos.csv`.

| Account | Platform | Followers | Evidence | Format |
|---|---|---|---|---|
| @designer_bob | TikTok | 3M (May 2024, Know Your Meme) | Started 22 Apr 2022. Wired: the format spawned hundreds of copycats | small-space redesigns, mostly straight |
| @homedesign369 | TikTok | 2.3M, 58.3M likes (22 Nov 2026) | 3.88 m² tiny home 862.6K likes; coffin room 515.4K; 1 billion kids' bedroom 395.6K | satirical "Little John" builds with an impossible premise |
| @dy02449xjp | TikTok | 480K (May 2024, KYM) | One of three main "unhinged home design" accounts | satirical |
| Room Design | YouTube | not given | KYM: similar, more extreme rooms | satirical |
| @_luxury_3d_house | Instagram | 445K, 138 posts (2024 snapshot) | "3D animated interior design" | 3D interior animations |
| @layoutroom (Room Design) | TikTok | not given | bedroom designs set to a cute track | 3D room design |
| @zn_homedecor | TikTok | not given | bedroom transformation 166.3K likes | real footage (benchmark) |
| @setups_ai | TikTok | not given | "design your room in 3D" website tip 201.7K likes | tool promo |
| @xuannhichan | TikTok | not given | room made in Coohom 12K likes | tool demo |
| @marcusdimitri211 | TikTok | not given | chairs that vanish into cabinetry 5,717 likes, 288 comments | AI concept, hidden storage |
| @mrwhoi | TikTok | not given | small bedroom 3D design 5,439 likes | plain 3D showcase |
| @n.ko.design | TikTok | not given | cozy kitchen design process 1,967 likes | design process |
| @foshan.guchi.furni | TikTok | not given | twisting chest of drawers 1,650 likes | furniture demo |
| @farrukhdes | TikTok | not given | interior animation 1,649 likes | plain 3D showcase |
| @visionofluxury | TikTok | not given | tiny bedroom 3D 1,048 likes | plain 3D showcase |
| @spacedesigning, @diy.home.decor.in, @enchantedspacesco | TikTok | not given | 219, 31 and 5 likes | plain 3D showcase |

**Patterns in the biggest hits**
1. **Premise beats showcase** [measured; confounded by account size]. Satirical-premise videos: n = 6, median
   307,650 likes. Plain 3D build showcases: n = 6, median 634. Wired and Know Your Meme describe the same
   mechanic: a domestic problem solved by an extreme renovation. **Without text overlays, the premise has to
   show in frame 1** [inference]: an absurdly tiny or narrow room, or a room that obviously can't hold what is
   coming (three beds, a whole laundry).
2. **Tiny spaces and many kids recur in the top videos** [fact]: 0 m², 2 m², 3.88 m² for eight kids, the coffin
   room, the billion-kids bedroom. Small-bedroom and kids'-room showcases with no premise sit at 5 to 5,439 likes.
3. **Shares are huge on premise hits** [measured]: 9.4%, 13.2% and 17.7% of likes; saves 5.7% to 9.9%. Save and
   share labels follow TikTok's button order (like, comment, save, share), so the labels are an inference.
4. **Comments** [measured]: median 0.99% of likes (n = 19 videos with 100 or more likes). The hidden-storage
   concept (chairs vanishing into cabinetry) reached 5.04%. Hidden-storage tricks start arguments in the comments.
   The website tip reached only 0.13%: people save tools but don't talk about them.
5. **Sound** [fact]: homedesign369's hits use one recurring trending track ("Morsmordre" by Crazy Donkey) or
   original sound. The FADER notes the same pairing with "metronomic chill house". A recurring sound works as a
   signature.
6. **Palette**: no reliable palette data, because the videos could not be viewed. Haven Haus's best known number
   (587K) is white uppers, wood base, black counter and patterned floor.

**Sample caveat**: this is a convenience sample of pages that search engines index. It leans toward popular
pages, and one account supplies all the premise videos. Use it for direction, not effect sizes.

## 5. Comments: what viewers ask

Comment text could not be read (every comment surface refuses automated readers). The indirect evidence:
- **"Which app?" is the standing question** [fact]. Know Your Meme wrote a section answering it (its answer: 3D
  animation software, not interior-design apps). Chinese viewers ask the same on Zhihu and Baidu: what software
  makes those Douyin interior animations?
- **Creators answer it with reply videos** [fact]: the Coohom tag on TikTok shows a "Replying to @…" video about
  finding the software.
- **Requests drive the format** [brief]: 3 of the 4 viral reference videos used TikTok reply-to-comment stickers.
- **Fans police recurring elements** [fact]: viewers complain when the signature material ("galvanized square
  steel") is missing from a Little John video.

**Which types pull comments and shares** (section 4): premise or challenge videos first, then hidden-storage
tricks, then plain showcases, with tool promos last on comments.

**Implications** [inference]
- Pin a comment answering "which app?" honestly (rendered from code, no design app). It answers the top question
  and invites replies.
- Ask for rooms in the caption ("comment your room"), then answer with reply videos.
- Keep a signature beat (for example the same lights-on chime), so returning viewers recognise it and comment on it.

## 6. Platform mechanics in 2026

**Instagram** [fact]
- 30 Apr 2026: accounts that mostly post unoriginal content, now including photos and carousels as well as Reels,
  are no longer recommended. Followers still see them. Instagram says 75% of US recommendations now come from
  original posts. Accounts can check their standing in Account Status, remove content or appeal.
- Since 2024, the original replaces the repost in recommendations, and aggregators are removed from recommendations.
- Ranking: watch time, likes per reach and sends per reach carry the most weight (Adam Mosseri, January 2025,
  repeated in 2026 guides). Third-party guides report that Reels carrying TikTok watermarks are suppressed.
- Length: stay under 3 minutes to reach new people (Mosseri, via SocialPilot).

**TikTok** [fact]
- Unoriginal or reproduced content without new creative changes is not eligible for the For You feed. Creators
  can see the reason in analytics and appeal. The current guidelines took effect on 24 Sep 2026 (secondary source).

**YouTube Shorts** [fact]
- Shorts views count every start and replay since 31 Mar 2025. All formats count from the first frame since
  24 Aug 2026. Recommendations did not change, and earnings use engaged views.
- 1 Oct 2026: Shorts recommendations updated to favour original content (secondary source: AIR Media-Tech).
- In one 2026 analysis, 61% of organic views came from the Shorts feed, 11% from subscribers and 9% from search
  (eMarketer). Recommendation surfaces matter more than subscriber count.

**Length** [fact]
- Virlo data (via Bizcommunity): Reels 11-17 s for entertainment-first content, Shorts 15-35 s, and virality
  clusters at 30 s or under. vidIQ: Shorts of 13 s or 60 s tend to do best.
- [inference] Our 13-16 s target fits all three platforms. Keep it.

**Where views come from** [fact]: Metricool's 2026 report finds TikTok gives the most views per video (up to 42%
more than Reels, about 6 times Shorts), while Reels lead in shares and comments.

**Posting cadence** [fact]
- Buffer, 2M Instagram posts: 3-5 posts a week is the sweet spot, with about 12% more reach per post than 1-2.
- Buffer, 11M TikTok posts: 2-5 posts a week gives up to 17% more views per post than 1; 6-10 gives up to 29%.
- [inference] With 20-25 minutes of render per final video, 3-4 originals a week cross-posted natively to all
  three platforms is sustainable and sits in both sweet spots.

**Trending sound vs original audio**
- Later's 2026 guide lists original audio among Instagram signals [secondary]. In homedesign369's hits, the
  trending track and original sound both appear [fact].
- [inference] Keep our original music as the master: it owns the audio page and carries no rights risk. The repo
  already renders an SFX-only version, so a trending sound can be laid on in TikTok when one clearly dominates
  the niche.

**Hooks without on-screen text** [inference]
1. Something moves by 0.3 s. Frame 1 stays the empty room.
2. The empty room itself is the problem: tiny, narrow, oddly shaped, or obviously too small for its job.
3. Show a "promise" object: an open empty carcass or a bare shelving wall that viewers know will be filled.
4. Use an unusual first viewpoint: through the doorway, top-down, or from inside a cabinet.
5. End on the frame-1 viewpoint so the loop seam reads as "build it again".
6. Decide whether TikTok's native reply sticker counts as on-screen text. It is app UI, not burned-in text, and
   3 of 4 references used it.

## 7. Our kitchen render against the formula (measured)

The tool was the repo's `pipeline/analyze_reference.py`, run on `out/kitchen_build.mp4`, alongside the timeline in
`rooms/kitchen/project.py`. The committed file is 1080x1920, 30 fps, 15.0 s. The brief says 25 fps.
`project.py` now schedules a pull-out pantry finale at 12.80-13.98 s (duration 15.5 s) that is **not in the
committed file** (the end frames show the tall cabinet closed). These numbers describe the committed file.

| Formula item | Baseline [brief] | Our kitchen [measured] | Verdict |
|---|---|---|---|
| Frame 1 | empty room, no intro | empty room; first floor tile lands at 0.30 s | ✓ |
| Landing rate | one every 0.3-0.6 s, 20-55 in 13-16 s | the current timeline in `project.py` (pantry finale included) moves 57 pieces with 65 sound events from 0.30 s to 14.2 s (most are landings). The analyzer resolves only 13 distinct motion peaks, median spacing 0.62 s, because it merges near-simultaneous landings and misses small ones | ✓ |
| Gaps | none until the final hold | Longest stretches without a sound event: 10.20-11.78 s (1.58 s), 7.09-8.08 s (0.99 s) and 2.72-3.64 s (0.92 s), each spanning a camera swing. By visible motion the quiet stretches are longer: no detected peak 1.83-3.77 s and 9.17-11.83 s. In the first, the tall pantry grows at the left edge, mostly out of shot, and the heater and splashback are small. In the second, only the blind (9.30 s) and a plant (9.86 s) move | ✗ fix |
| Storage reveals | the star | drawer opens, tray and cutlery drop in, drawer closes (4.88-5.59 s); upper doors close over filled shelves (6.30-6.92 s); sink doors close over the bin and bottles (8.92-8.98 s) | ✓ |
| Lights-on | near the end | 12.45 s, with a chime | ✓ |
| Camera | stills plus 0.3 s swings, wide hold about 2 s | swings 3.07-3.30, 7.53-7.80 and 10.73-11.00 s (0.23-0.27 s); final hold 12.53-15.00 s (2.47 s) | ✓ |
| Music | 125-128 BPM from frame 1, landings not beat-locked | 126 BPM (`music.py` default; the analyzer reads half-time, 63). Mean landing offset from the beat 215 ms against 238 ms for random timing | ✓ |

**Fixes, in order**
1. Fill gap 1 with a visible heavy landing. Bring the pantry fully into frame and make it thud at about 2.2 s,
   or slam a tall door.
2. Fill gap 2 with a reveal: the under-sink pull-out or a door slam at about 10 s.
3. Choose one "wow" and stage it inside a held shot at 8-11 s. The new pantry pull-out is the strongest candidate.
   Placed in the final wide (as `project.py` does now), it cuts the still hold to about 1 s.

## 8. The viral formula (checklist)

- [ ] **Frame 1 is the empty room**, with no logo or intro, and something moves by 0.3 s. [brief 4/4; ours ✓]
- [ ] **The empty room is the hook**: visibly hard (tiny, narrow, odd-shaped, too small for its job).
      [genre: premise median 307,650 vs 634 likes, confounded]
- [ ] **A storage-dense room**: kitchen, wardrobe or walk-in, kids' room, laundry or balcony, studio.
      [Haven Haus 587K kitchen vs 6.4K gaming; balcony cabinet travelled via a big X account]
- [ ] **30-45 landings in 13-16 s**: one every 0.3-0.6 s, and no stretch over about 0.8 s without a landing before
      the final hold. [brief; our two gaps]
- [ ] **2-3 storage reveals that escalate**: drawer open, fill, close; then doors slam; then one hidden-storage
      payoff (pull-out pantry, lift-up bed, stair drawers, fold-out table, toe-kick drawer).
      [brief "storage is the star"; hidden storage drew a 5.0% comment rate]
- [ ] **One wow at about 8-11 s**, staged in a held shot. [inference]
- [ ] **Lights-on** just before or as the final wide lands. [brief]
- [ ] **Camera**: 3-4 still stations, 0.25-0.3 s swings, final wide held 2-2.5 s. [brief; ours 0.23-0.27 s and 2.47 s]
- [ ] **Original music at 125-128 BPM from frame 1**, a sound on every landing, landings not locked to the beat.
      [brief; ours ✓]
- [ ] **Loop**: the final wide uses (nearly) the frame-1 viewpoint. [inference; watch time and replays are top signals]
- [ ] **Sendable situation**: tiny flat, three kids in one room, small-kitchen fixes. [Instagram sends per reach;
      shares 9-18% of likes on premise hits]
- [ ] **Original and native**: no reposts, no watermarks, native upload per platform. [Instagram, TikTok and
      YouTube 2026 rules]
- [ ] **Series and comment loop**: recurring room types, rooms requested in the caption, reply videos, and a pinned
      "rendered from code" answer. [brief 3/4 reply stickers; KYM "what app" section]
- [ ] **Length 13-16 s**. [Virlo via Bizcommunity; vidIQ]
- [ ] **Palette**: start from white + wood + black counter, then test dark finishes and colourful sets one variable
      at a time, keeping exposure bright. [Haven Haus 587K; inference]

## 9. Top-5 frame-by-frame breakdowns

**Not possible in this session** (section 1). The substitutes are the 4-video baseline in the brief, which still
stands, and the measured breakdown of our own render (section 7). To fill this section: get the top 5 by views
from `youtube_inventory.py stats`, save the files privately, and run `analyze_reference.py` on each. It reports
cuts, camera segments with speeds, placement times, pace, BPM and beat offsets, and writes contact sheets.

## 10. Confidence and open questions

| Claim | Confidence | Why |
|---|---|---|
| Haven Haus hits vs flops | unknown | only 3 known numbers |
| Premise beats showcase | medium | strong direction, but one account and a search-biased sample |
| Shares are high on hits | medium | 3 videos; button labels inferred |
| Kujiale growth animation is the source tool | medium-high | feature-for-feature match; not confirmed per creator |
| 2026 platform rules | high | official posts, except items marked secondary |
| Our render measurements | high | measured from our own file and timeline |

Open: who is behind `@设计师温倪` and `@设计师阳阳` (needs Douyin in a browser); the real Haven Haus view
distribution and cadence (needs an API key or browser); comment texts (needs a browser).
