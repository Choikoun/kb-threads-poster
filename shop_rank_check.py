#!/usr/bin/env python3
"""쇼핑 블로그(sobok_biz) 전용 순위·색인 추적 (2026-11-09). KB용 keyword_rank_check.py와 별개.
- 색인: 글 제목을 네이버 블로그 검색에 넣어 우리 글(logNo)이 나오는지
- 순위: 글 키워드로 블로그 탭 검색 결과(최대 30개(네이버가 한 번에 주는 한계))에서 우리 글의 위치
사용: python shop_rank_check.py [--maxn 30]   결과는 shop_rank_log.json 에 날짜별 누적, 표는 화면 출력
shop_posts.json 의 naver URL(숫자 logNo)이 있는 글만 대상."""
import re, sys, json, time, urllib.parse
from datetime import datetime, timezone, timedelta
import requests
sys.stdout.reconfigure(encoding='utf-8')
BLOG = 'sobok_biz'
LOG = 'shop_rank_log.json'
H = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148'}
KST = timezone(timedelta(hours=9))


def fetch_ids(q, maxn):
    """블로그 탭 검색 결과의 (blogId, logNo) 순서 목록(중복 제거). start 파라미터로 더 깊이 조회."""
    ids = []
    for start in range(1, maxn + 1, 15):
        url = 'https://search.naver.com/search.naver?ssc=tab.blog.all&sm=tab_opt&query=%s&start=%d' % (urllib.parse.quote(q), start)
        try:
            h = requests.get(url, headers=H, timeout=20).text
        except Exception:
            break
        new = 0
        for m in re.finditer(r'blog\.naver\.com/([A-Za-z0-9_]+)/(\d{9,})', h):
            t = (m.group(1), m.group(2))
            if t not in ids:
                ids.append(t); new += 1
        if new == 0:
            break
        time.sleep(0.5)
    return ids[:maxn]


def pos_of(ids, logno):
    for i, (b, n) in enumerate(ids):
        if n == logno and b == BLOG:
            return i + 1
    return None


def main():
    maxn = 30
    if '--maxn' in sys.argv:
        maxn = int(sys.argv[sys.argv.index('--maxn') + 1])
    posts = json.load(open('shop_posts.json', encoding='utf-8'))
    posts = posts if isinstance(posts, list) else posts.get('posts', [])
    today = datetime.now(KST).strftime('%Y-%m-%d')
    try:
        log = json.load(open(LOG, encoding='utf-8'))
    except Exception:
        log = {}
    rows = []
    for p in posts:
        u = str(p.get('naver', '')).rstrip('/')
        logno = u.split('/')[-1]
        if not logno.isdigit() or not p.get('keyword'):
            continue
        kw, title = p['keyword'], p.get('title', '')
        idx = pos_of(fetch_ids(title, 30), logno)   # 제목 검색: 상위 30개 안에 있으면 색인된 것으로 본다
        rank = pos_of(fetch_ids(kw, maxn), logno)
        rows.append((p.get('date', ''), kw, idx, rank))
        log.setdefault(logno, {'keyword': kw, 'title': title, 'hist': []})
        log[logno]['hist'] = [h for h in log[logno]['hist'] if h['d'] != today] + [{'d': today, 'indexed': idx is not None, 'title_pos': idx, 'rank': rank}]
    json.dump(log, open(LOG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{today} 쇼핑 글 {len(rows)}편 (순위는 상위 {maxn}개 안에서 조회)')
    print(f"{'발행':<11}{'키워드':<18}{'제목검색':<10}{'키워드순위'}")
    for d, kw, idx, rank in rows:
        print(f"{d:<11}{kw:<18}{('노출 %d위' % idx) if idx else '미노출':<10}{(str(rank) + '위') if rank else '권외(%d+)' % maxn}")
    n_idx = sum(1 for r in rows if r[2]); n_rank = sum(1 for r in rows if r[3])
    print(f'색인(제목검색 노출) {n_idx}/{len(rows)}, 키워드 순위권 {n_rank}/{len(rows)}')


if __name__ == '__main__':
    main()
