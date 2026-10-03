#!/usr/bin/env python3
"""블로그 유도 릴스 큐 — 매일 16:00 KST(도달이 유지되는 슬롯)에 대기 중인 첫 항목 1건 발행.
reels_queue.json: [{"module": "xxx_reels_post", "status": "pending|done", "queued": "YYYY-MM-DD"}]
발행된 instagram_log 항목에는 slot='16h_queue'를 달아 기존(비정기 시간) 릴스와 비교한다."""
import sys, json, importlib
from datetime import datetime, timezone, timedelta
sys.stdout.reconfigure(encoding='utf-8')
from annuity_video_poster import load_ig_log, save_ig_log

QUEUE = 'reels_queue.json'
KST = timezone(timedelta(hours=9))

q = json.load(open(QUEUE, encoding='utf-8'))
pending = [x for x in q if x['status'] == 'pending']
if not pending:
    print('큐 비어있음 - 종료')
    sys.exit(0)
item = pending[0]
print('발행 대상:', item['module'])
before = {e.get('ig_post_id') for e in load_ig_log()}
importlib.import_module(item['module']).main()
log = load_ig_log()
for e in log:
    if e.get('ig_post_id') not in before:
        e['slot'] = '16h_queue'
save_ig_log(log)
item['status'] = 'done'
item['posted'] = datetime.now(KST).strftime('%Y-%m-%d %H:%M')
json.dump(q, open(QUEUE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
