# How the "havenhaus_1" room-build videos are made, and how we make our own

## 1. What havenhaus_1 actually is

Instagram account **Haven Haus (@havenhaus_1)**: 1.8M followers, 579 posts. The bio sells a service:
"MK Design Studio, 2D & 3D Interior & Architectural Design, from $30/m²".

**Most of their viral Reels are reposts of Douyin (Chinese TikTok) designers.** Douyin stamps the
creator's `@handle` onto every downloaded video, and those stamps are still visible on their posts:

| Their Reel | Watermark found | Meaning |
|---|---|---|
| Kitchen, 587K views | `@设计师温倪` (top-left) | "Designer Wen Ni", a Douyin creator |
| Grey channel-tufted headboard / sofa wall | `@设计师阳阳` | "Designer Yangyang", a second Douyin creator |
| Gaming-PC setup, 6.4K views | `YT` | YouTube repost |

Two different Douyin designers on one feed is the pattern of an **aggregator account**: download
trending Douyin room videos, repost them to Instagram, and send the new followers to a paid design
service.

## 2. What the original Douyin designers render with

They don't animate in Blender by hand. These clips come from interior-design and visualisation tools
that can play a build animation on a finished room:

- **Kujiale (酷家乐), sold outside China as Coohom.** This is the dominant room-design / custom-cabinetry
  platform in China. Coohom's help centre describes template videos that "come with animation effects
  of 3D models".
- **D5 Render 2.9+**: a "Phasing Animation" feature with templates (Drop/Rise, Ascend/Descend) that
  makes objects appear one after another without keyframing.
- **Lumion**: phasing animations such as "sky drop" (objects fall from the ceiling one by one) and
  "ground rise".
- **3ds Max / Blender**: keyframed by hand for custom shots.
- The finished clip is usually cut in CapCut (剪映) with a trending sound.

Honest limit: we could not confirm which exact program each creator uses, because Douyin pages
cannot be read from here. The look of these clips (whole-room custom cabinetry, catalogue materials,
pieces flying in) matches the Kujiale/Coohom-style tools above.

## 3. Why we should NOT copy their strategy (reposting)

- Instagram has ranked original content above reposts since 2022 (Adam Mosseri). In April 2026 it
  extended this to photos and carousels, aimed directly at accounts built on reposted content: if
  most of an account's output is reposts, it effectively disappears from Explore and recommendations,
  and Instagram swaps reposted Reels for the original clip when it finds both.
- Reposting other designers' work also invites copyright takedowns.

Original videos in the same style are the safer and more durable route.

## 4. How we make ours (this repo)

`pipeline/` is a complete code-only renderer. There is no Blender, no design app, no GPU and no
network. It runs on a normal 4-core cloud machine:

1. `rooms/<room>/project.py` describes the room in Python: walls, tiles, every cabinet, drawer, door,
   plate and plant as a named piece, plus materials, lights and camera stations.
2. A timeline makes **every piece move in on its own**. Floor tiles slap down row by row, cabinets
   slide out of the walls, counters drop, uppers fly in, a drawer opens, fills and closes, doors
   slam shut, the blind lowers, and the lights switch on.
3. A C++ path tracer renders each frame and a denoiser cleans it up.
4. Grading adds bloom and a "punch" on every landing.
5. **Original synthesized music** is added, with a sound on every landing.
6. The output is two vertical 1080x1920 MP4s: one with music, and one with sound effects only, so you
   can lay a trending sound over it in TikTok or Instagram.

| Step | Time on this machine (15 s video) |
|---|---|
| Low-res preview (540x960) | about 5 min |
| Final (720p render, 1080x1920 file) | about 20-25 min |
| Native 1080p render | about 1 h |

New rooms (bedroom, studio apartment, walk-in closet, bathroom, laundry and so on) are new
`project.py` files. Send a screenshot of any room you like and we model our own version of it.

### Other ways to make them (if you want to do it by hand)

| Route | What you need | Effort per video | Notes |
|---|---|---|---|
| Coohom / Kujiale | Subscription, PC or browser | 1-3 h | Closest to the Douyin look; big furniture catalogue |
| D5 Render (phasing) | Windows + NVIDIA GPU | 2-4 h | Templates for drop/rise build effects |
| Lumion (phasing) | Windows + strong GPU, paid licence | 2-4 h | Same idea as D5 |
| Blender | Free, steep learning curve | Hours to days | Unlimited control, needs modelling skill |
| AI video (Kling, Veo, Higgsfield and similar) | Credits per clip | Minutes | Morphs "empty to furnished"; little control over individual pieces landing |
| **This repo** | Nothing extra | Room model + render time | Every piece animated, original music, no licences |

## 5. What makes these videos work (measured from reference room-build videos)

- **Frame 1 is already the empty room.** No intro and no logo. Music is loud from the first frame (about 125-128 BPM).
- **A landing every 0.3-0.6 s**, each move 0.2-0.5 s long, 20-55 landings in 13-16 s.
- **Storage is the star.** Drawers open, fill and close; doors appear open and slam shut; interiors fill with plates and boxes.
- **A lights-on moment** near the end (LED strips, downlights).
- **Camera:** still shots joined by fast 0.3 s swings, then a pull-back to a wide final shot held for 2-3 s (people pause to look).
- **Hook:** many top clips are replies to real comments ("design a small kitchen for me") using
  TikTok's *reply with video*. Ask your audience for requests and answer them with videos. Never fake
  the reply sticker.
- **Series beat one-offs:** small kitchen, boys' room, studio apartment, closet, laundry, each with
  "comment your room and I'll design it".

## Sources

- [Instagram ranking change to favour original content (TechCrunch, 2022)](https://techcrunch.com/2022/04/20/instagram-ranking-system-recommend-original-content/)
- [Instagram algorithm overhaul rewards original content, penalises aggregators (Engadget)](https://www.engadget.com/instagrams-algorithm-overhaul-will-reward-original-content-and-penalize-aggregators-130018977.html)
- [New Instagram policies target reposted content (PetaPixel, 30 Apr 2026)](https://petapixel.com/2026-04-30/new-instagram-policies-target-reposted-content/)
- [Coohom help centre: template videos with 3D model animation](https://www.coohom.com/helpcenter/3FO4K4WKSVYN?hl=en)
- [D5 Render 2.9 Phasing Animation (ArchDaily)](https://www.archdaily.com/1024827) and [D5 forum thread on phasing](https://forum.d5render.com/t/phasing-animation/37313)
- [Lumion: creating phasing animations](https://lumion.com/tips-guides/creating-phasing-animations)
- [Know Your Meme: where the animated home-design videos come from](https://knowyourmeme.com/editorials/where-do-these-unhinged-home-design-videos-come-from-animated-videos-about-tiny-apartments-explained)
