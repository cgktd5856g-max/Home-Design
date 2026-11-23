"""Write a render-session brief for one video.

usage: python3 -I production/tools/make_brief.py production/tools/session_template.md production/sessions/<slug>.md \
           <plan id> "<title>" <slug> claude/video-<short> <long 0|1> <rank in research/top10_ideas.md>
"""
import sys
tpl, out, cid, title, slug, branch, long_ = sys.argv[1:8]
T = open(tpl).read()
rank = sys.argv[8] if len(sys.argv) > 8 else '?'
plan_item = (f'2. research/top10_ideas.md: the "Rules for all 10" and "Posting plan" sections, and section "## {rank}." which is your idea\'s '
             f'FINAL, fact-checked plan (its earlier draft is production/plans/{cid}.md; where they differ, the top10 section wins). '
             f'Copy your section to rooms/{slug}/PLAN.md and update that copy as you make changes.')
T = T.replace('2. research/top10_ideas.md, section "{N}." for your idea\'s plan (and the "Rules for all 10" section).', plan_item)
T = T.replace("your idea's plan section", f'rooms/{slug}/PLAN.md').replace('and the "Rules for all 10" and research/report.md section 11 checklist',
                                                                         "the owner's rules above, and the research/report.md section 11 checklist")
LONG = ("LONG CUT (after the 15 s cut is pushed): build the 40-50 s long cut of the same room as the plan describes "
        "(the same opening, a new zone every 6-10 s, a new angle every 2-4 s, the wow at 60-70% of the runtime, a 2 s drifting wide at the end, no end card). "
        "Use a separate timeline in the same project (e.g. ROOM_CUT=long selects it) so build() is shared. Preview, run hh_metrics, pass both review gates, "
        f"render detached, encode, and push out/{slug}_long.mp4 and out/{slug}_long_sfx_only.mp4, then update REPORT.md.")
T = T.replace('{LONG_CUT}', LONG if long_ == '1' else 'After the 15 s cut is pushed and REPORT.md is written, you are done.')
USAGE = ("\nUSAGE LIMIT: all sessions share one account usage limit. Work efficiently: no needless re-reads of big files, keep subagent briefs short, "
         "and while the Blender render runs, check its log only every 15-20 minutes (sleep in between). If you hit a usage limit, stop and wait; "
         "the coordinator will nudge you when it resets.\n")
T = T.replace('Quality first:', USAGE + '\nQuality first:')
for k, v in dict(N=cid, TITLE=title, SLUG=slug, BRANCH=branch).items():
    T = T.replace('{' + k + '}', v)
left = [x for x in ('{N}', '{TITLE}', '{SLUG}', '{BRANCH}', '{LONG_CUT}') if x in T]
assert not left, left
open(out, 'w').write(T)
print(out, len(T))
