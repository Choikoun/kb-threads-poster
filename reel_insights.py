#!/usr/bin/env python3
"""
인스타그램 릴스 지표 수집 → reel_insights.json / reel_insights.md
- instagram_log.json 의 type=reels 최근 N개(기본 80)의 조회수·도달·좋아요·저장·공유·댓글·평균시청시간을 가져온다.
- 토큰은 GitHub secrets 에만 있으므로 reel_insights.yml 워크플로우에서 실행한다.
"""
import os, sys, json, requests
from dotenv import load_dotenv
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'https://graph.facebook.com/v21.0'
TOKEN = os.environ['INSTAGRAM_ACCESS_TOKEN']
N = int(sys.argv[1]) if len(sys.argv) > 1 else 80
D = os.path.dirname(os.path.abspath(__file__))

METRICS = 'reach,views,likes,comments,shares,saved,ig_reels_avg_watch_time,ig_reels_video_view_total_time'

log = json.load(open(os.path.join(D, 'instagram_log.json'), encoding='utf-8'))
reels = [x for x in log if x.get('type') == 'reels'][-N:]
rows = []
for x in reels:
    r = requests.get(f"{BASE}/{x['ig_post_id']}/insights",
                     params={'metric': METRICS, 'access_token': TOKEN}, timeout=30).json()
    row = {'id': x['ig_post_id'], 'date': x.get('date', ''), 'title': x.get('selected_title', '')}
    if 'data' in r:
        m = {d['name']: d['values'][0]['value'] for d in r['data']}
        row.update({
            'views': m.get('views'), 'reach': m.get('reach'), 'likes': m.get('likes'),
            'comments': m.get('comments'), 'shares': m.get('shares'), 'saved': m.get('saved'),
            'avg_watch_s': round((m.get('ig_reels_avg_watch_time') or 0) / 1000, 1),
        })
    else:
        row['error'] = r.get('error', {}).get('message', '')[:120]
    rows.append(row)

json.dump(rows, open(os.path.join(D, 'reel_insights.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

lines = ['| 날짜 | 제목 | 조회 | 도달 | 좋아요 | 저장 | 공유 | 댓글 | 평균시청(초) |', '|---|---|---|---|---|---|---|---|---|']
for r in rows:
    if 'error' in r:
        lines.append(f"| {r['date'][:10]} | {r['title'][:30]} | 오류: {r['error'][:40]} |||||||")
    else:
        lines.append(f"| {r['date'][:10]} | {r['title'][:30]} | {r['views']} | {r['reach']} | {r['likes']} | {r['saved']} | {r['shares']} | {r['comments']} | {r['avg_watch_s']} |")
open(os.path.join(D, 'reel_insights.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print(f'{len(rows)}개 릴스 지표 저장 (오류 {sum(1 for r in rows if "error" in r)}개)')
