#!/usr/bin/env python3
"""Fill and analyse the video inventory (same columns as research/videos.csv). Standard library only.

fetch  Lists every upload of a YouTube channel with the official YouTube Data API v3 (public data only).
       Needs a free API key: Google Cloud console > APIs & Services > enable "YouTube Data API v3" > Credentials.
       A full pull of a ~600-video channel costs about 25 of the 10,000 free daily quota units.
         python3 research/youtube_inventory.py fetch --key YOUR_KEY --out research/videos_youtube.csv
       Shorts are detected by duration <= 180 s (Shorts can be up to 3 minutes): a heuristic, check odd cases.

stats  View distribution, flops, posting cadence, growth by month, and hits vs flops per tag, for any CSV
       with these columns. The tag columns (room_type ... loopable) are filled by hand after watching.
         python3 research/youtube_inventory.py stats research/videos_youtube.csv --metric views
         python3 research/youtube_inventory.py stats research/videos.csv --metric likes --where set=genre
"""
import argparse
import csv
import datetime as dt
import json
import re
import statistics as st
import sys
import urllib.parse
import urllib.request

CHANNEL_ID = 'UCuVYKD6oo6AAo7-14U5BiIg'  # Haven Haus, youtube.com/@Havenhaus1
FIELDS = ('set,account,platform,url,date,duration_s,views,likes,comments,saves,shares,caption,hashtags,sound,'
          'watermark_or_creator,room_type,style_palette,lighting,format,reveal,reveal_what,camera_style,'
          'opening_frame,lights_on,music_type,on_screen_text,loopable,data_status,source_url,accessed,notes').split(',')
TAGS = ['room_type', 'style_palette', 'lighting', 'format', 'reveal', 'camera_style', 'opening_frame',
        'lights_on', 'music_type', 'on_screen_text', 'loopable']


def api(endpoint, key, **params):
    url = 'https://www.googleapis.com/youtube/v3/' + endpoint + '?' + urllib.parse.urlencode({**params, 'key': key})
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


def iso_seconds(d):
    m = re.fullmatch(r'P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?', d or '')
    if not m:
        return ''
    days, h, mi, s = (int(x or 0) for x in m.groups())
    return days * 86400 + h * 3600 + mi * 60 + s


def fetch(a):
    ch = api('channels', a.key, part='snippet,contentDetails,statistics', id=a.channel)['items'][0]
    s = ch['statistics']
    print(f"{ch['snippet']['title']}: {s.get('subscriberCount', '?')} subscribers, {s.get('videoCount')} videos, "
          f"{s.get('viewCount')} views, created {ch['snippet']['publishedAt'][:10]}", file=sys.stderr)
    uploads, ids, token = ch['contentDetails']['relatedPlaylists']['uploads'], [], None
    while True:
        page = api('playlistItems', a.key, part='contentDetails', playlistId=uploads, maxResults=50,
                   **({'pageToken': token} if token else {}))
        ids += [i['contentDetails']['videoId'] for i in page['items']]
        token = page.get('nextPageToken')
        if not token:
            break
    rows, today = [], dt.date.today().isoformat()
    for k in range(0, len(ids), 50):
        for v in api('videos', a.key, part='snippet,contentDetails,statistics', id=','.join(ids[k:k + 50]))['items']:
            sn, stats_ = v['snippet'], v.get('statistics', {})
            secs = iso_seconds(v['contentDetails'].get('duration'))
            short = secs != '' and secs <= 180
            url = 'https://www.youtube.com/' + ('shorts/' if short else 'watch?v=') + v['id']
            text = sn.get('title', '') + ' ' + sn.get('description', '')
            rows.append({'set': 'havenhaus', 'account': sn.get('channelTitle', ''),
                         'platform': 'youtube shorts' if short else 'youtube', 'url': url,
                         'date': sn['publishedAt'][:10], 'duration_s': secs, 'views': stats_.get('viewCount', ''),
                         'likes': stats_.get('likeCount', ''), 'comments': stats_.get('commentCount', ''),
                         'caption': sn.get('title', ''), 'hashtags': ' '.join(dict.fromkeys(re.findall(r'#\w+', text))),
                         'data_status': 'YouTube Data API v3', 'source_url': url, 'accessed': today})
    rows.sort(key=lambda r: r['date'])
    with open(a.out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f'wrote {len(rows)} videos to {a.out}', file=sys.stderr)


def num(x):
    try:
        return float(str(x).replace(',', ''))
    except ValueError:
        return None


def fmt(x):
    return f'{x:,.0f}'


def stats(a):
    with open(a.csv, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    for cond in a.where or []:
        k, v = cond.split('=', 1)
        rows = [r for r in rows if r.get(k) == v]
    have = sorted((r for r in rows if num(r.get(a.metric)) is not None), key=lambda r: -num(r[a.metric]))
    vals = sorted(num(r[a.metric]) for r in have)
    n = len(vals)
    print(f'## {a.metric}: {n} videos with a value ({len(rows) - n} without)\n')
    if not n:
        return
    q = lambda p: vals[round(p * (n - 1))]  # nearest rank
    print('| median | mean | 10th pct | 90th pct | min | max |\n|---|---|---|---|---|---|')
    print(f'| {fmt(st.median(vals))} | {fmt(st.mean(vals))} | {fmt(q(.1))} | {fmt(q(.9))} | {fmt(vals[0])} | {fmt(vals[-1])} |\n')
    flops = [v for v in vals if v <= q(.1)]
    print(f'Top 10% threshold: {fmt(q(.9))}. Flops (bottom 10%): {len(flops)} of {n} at or below {fmt(q(.1))}.\n')
    N = min(a.top, n // 2)
    if n < 2 * a.top:
        print(f'> Small sample: top and bottom groups hold {N} each; treat differences as hints, not proof.\n')
    for title, group in (('Top', have[:N]), ('Bottom', have[-N:])):
        print(f'### {title} {N}\n\n| {a.metric} | comments | account | caption | url |\n|---|---|---|---|---|')
        for r in group:
            print(f"| {fmt(num(r[a.metric]))} | {r.get('comments', '')} | {r['account']} | {r['caption'][:60].replace('|', '/')} | {r['url']} |")
        print()
    dated = sorted((dt.date.fromisoformat(r['date']), num(r[a.metric])) for r in have if r.get('date'))
    if len(dated) >= 2:
        gaps = [(b[0] - x[0]).days for x, b in zip(dated, dated[1:])]
        weeks = max((dated[-1][0] - dated[0][0]).days, 1) / 7
        print(f'Posting: {len(dated)} dated videos, {dated[0][0]} to {dated[-1][0]}; median gap {st.median(gaps):g} days; '
              f'{len(dated) / weeks:.1f} per week.\n\n| month | videos | median {a.metric} |\n|---|---|---|')
        months = {}
        for d, v in dated:
            months.setdefault(d.strftime('%Y-%m'), []).append(v)
        for m, vs in sorted(months.items()):
            print(f'| {m} | {len(vs)} | {fmt(st.median(vs))} |')
        print()
    hits, bottom = have[:N], have[-N:]
    for t in TAGS:
        if not any(r.get(t) for r in have):
            continue
        print(f'### {t}\n\n| value | videos | median {a.metric} | in top {N} | in bottom {N} |\n|---|---|---|---|---|')
        for val in sorted({r.get(t) or '(blank)' for r in have}):
            grp = [r for r in have if (r.get(t) or '(blank)') == val]
            print(f"| {val} | {len(grp)} | {fmt(st.median(num(r[a.metric]) for r in grp))} | "
                  f"{sum(r in hits for r in grp)} | {sum(r in bottom for r in grp)} |")
        print()


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    f = sub.add_parser('fetch')
    f.add_argument('--key', required=True)
    f.add_argument('--channel', default=CHANNEL_ID)
    f.add_argument('--out', default='research/videos_youtube.csv')
    s = sub.add_parser('stats')
    s.add_argument('csv')
    s.add_argument('--metric', default='views', choices=['views', 'likes', 'comments', 'shares', 'saves'])
    s.add_argument('--where', action='append', help='column=value filter, repeatable')
    s.add_argument('--top', type=int, default=20)
    a = p.parse_args()
    fetch(a) if a.cmd == 'fetch' else stats(a)


if __name__ == '__main__':
    main()
