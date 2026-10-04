#!/usr/bin/env python3
"""블로그 글 발행 당일 추가 릴스 즉시 발행 (16시 큐와 별개). 사용: python blog_reel_now.py <module>
큐(reels_queue.json)에 같은 모듈이 pending이면 중복 방지를 위해 done 처리한다."""
import sys, json, importlib
from datetime import datetime, timezone, timedelta
sys.stdout.reconfigure(encoding='utf-8')
mod = sys.argv[1]
importlib.import_module(mod).main()
KST = timezone(timedelta(hours=9))
try:
    q = json.load(open('reels_queue.json', encoding='utf-8'))
    for x in q:
        if x['module'] == mod and x['status'] == 'pending':
            x['status'] = 'done'
            x['posted'] = datetime.now(KST).strftime('%Y-%m-%d %H:%M') + ' (당일 추가 발행)'
    json.dump(q, open('reels_queue.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
except Exception as e:
    print('큐 갱신 생략:', e)
