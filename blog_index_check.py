#!/usr/bin/env python3
"""
네이버 블로그 글 색인(검색 노출) 점검 — blog_posts.json 의 네이버 글 제목을 네이버 블로그탭에서 직접 검색해
logNo가 결과 HTML에 있는지 확인한다. 결과는 blog_index_log.json 에 날짜별로 누적(같은 글이 시간이 지나며 빠지는지 추적).
사용: python blog_index_check.py [최근N개(기본 전체)]
"""
import sys, json, os, time, urllib.parse, requests
from datetime import datetime, timezone, timedelta
sys.stdout.reconfigure(encoding='utf-8')
D = os.path.dirname(os.path.abspath(__file__))
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/150 Safari/537.36'}
LOG = os.path.join(D, 'blog_index_log.json')

ps = json.load(open(os.path.join(D, 'blog_posts.json'), encoding='utf-8'))
n = int(sys.argv[1]) if len(sys.argv) > 1 else len(ps)
today = datetime.now(timezone(timedelta(hours=9))).strftime('%Y-%m-%d')
res = {}
for p in ps[-n:]:
    pid = p['naver'].split('/')[-1]
    u = 'https://search.naver.com/search.naver?ssc=tab.blog.all&sm=tab_opt&query=' + urllib.parse.quote(p['title'])
    try:
        ok = pid in requests.get(u, headers=UA, timeout=20).text
    except Exception:
        ok = None
    res[pid] = ok
    print(p['date'], {True: '노출', False: '없음', None: '오류'}[ok], p['title'][:30])
    time.sleep(2)
log = json.load(open(LOG, encoding='utf-8')) if os.path.exists(LOG) else {}
log[today] = res
json.dump(log, open(LOG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('노출', sum(1 for v in res.values() if v), '/', len(res))
