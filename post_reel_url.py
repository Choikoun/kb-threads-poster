#!/usr/bin/env python3
"""이미 GitHub Release에 올라간 영상 URL을 인스타 릴스로 게시. 사용: python post_reel_url.py <video_url> <caption_module> <title> <engine>"""
import sys, importlib
sys.stdout.reconfigure(encoding='utf-8')
from datetime import datetime, timezone, timedelta
from annuity_video_poster import post_reels, load_ig_log, save_ig_log
url, module, title, engine = sys.argv[1:5]
caption = importlib.import_module(module).CAPTION
ig_id = post_reels(url, caption)
if not ig_id:
    sys.exit('Instagram 포스팅 실패')
log = load_ig_log()
log.append({'ig_post_id': ig_id, 'type': 'reels', 'selected_title': title, 'engine': engine,
            'date': datetime.now(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M')})
save_ig_log(log)
print('Instagram 완료:', ig_id)
