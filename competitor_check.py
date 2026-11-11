#!/usr/bin/env python3
"""키워드별 네이버 블로그 상위 노출 글/블로그 분석.
각 키워드의 모바일 블로그 검색 상위 N개에서 블로그별로: 글 작성일, 블로그 총 글수, 이웃수, 첫 글 날짜(개설 시점 근사),
최근 30일 발행 수, 본문 글자수·이미지 수를 모은다. 네이버는 '블로그 지수'를 공개하지 않으므로 이 값들을 대용 지표로 쓴다.
사용: python competitor_check.py 키워드1 키워드2 ...   (결과는 competitor_out.json 에 누적)
"""
import sys, re, json, time, os, urllib.parse
from datetime import datetime, timedelta
import requests
sys.stdout.reconfigure(encoding='utf-8')
H = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148'}
OUT = 'competitor_out.json'
TOPN = 10
_blog_cache = {}

def get(u, **kw):
    for i in range(3):
        try:
            return requests.get(u, headers=H, timeout=20, **kw)
        except Exception:
            time.sleep(2)
    return None

def top_results(keyword):
    r = get('https://m.search.naver.com/search.naver?ssc=tab.m_blog.all&query=' + urllib.parse.quote(keyword))
    seen = []
    for b, n in re.findall(r'blog\.naver\.com/([A-Za-z0-9_]+)/(\d{9,})', r.text if r else ''):
        if n not in [s[1] for s in seen]:
            seen.append((b, n))
    return seen

def titlelist(b, page, per=30):
    r = get(f'https://blog.naver.com/PostTitleListAsync.naver?blogId={b}&viewdate=&currentPage={page}&categoryNo=0&parentCategoryNo=&countPerPage={per}')
    if not r:
        return None
    try:
        return json.loads(r.text.replace("\\'", "'"), strict=False)
    except Exception:
        return None

def parse_date(s):
    m = re.match(r'(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})', s or '')
    if m:
        return datetime(int(m[1]), int(m[2]), int(m[3]))
    return None

def blog_info(b):
    if b in _blog_cache:
        return _blog_cache[b]
    d = titlelist(b, 1)
    info = {'blog': b}
    if d:
        total = int(d.get('totalCount') or 0)
        info['posts'] = total
        posts = d.get('postList', [])
        dates = [parse_date(p.get('addDate')) for p in posts]
        info['dates_p1'] = [x.strftime('%Y-%m-%d') for x in dates if x]
        last = d
        if total > 30:
            pages = (total + 29) // 30
            last = titlelist(b, pages) or d
        ld = [parse_date(p.get('addDate')) for p in last.get('postList', [])]
        ld = [x for x in ld if x]
        info['first_post'] = min(ld).strftime('%Y-%m-%d') if ld else None
        cutoff = datetime.now() - timedelta(days=30)
        vd = [x for x in dates if x]
        info['posts_30d'] = sum(1 for x in vd if x >= cutoff) if (not vd or total <= 30 or min(vd) < cutoff) else '30+'
    t = get(f'https://m.blog.naver.com/{b}')
    if t:
        m = re.search(r'(\d[\d,]*)명의 이웃', t.text)
        info['buddies'] = int(m[1].replace(',', '')) if m else None
    _blog_cache[b] = info
    time.sleep(0.5)
    return info

def post_info(b, n):
    out = {}
    d = None
    for page in range(1, 6):
        d = titlelist(b, page)
        if not d:
            break
        hit = [p for p in d.get('postList', []) if p.get('logNo') == n]
        if hit:
            out['date'] = parse_date(hit[0].get('addDate')).strftime('%Y-%m-%d') if parse_date(hit[0].get('addDate')) else None
            out['title'] = urllib.parse.unquote_plus(hit[0].get('title', ''))
            break
        if page * 30 >= int(d.get('totalCount') or 0):
            break
    r = get(f'https://m.blog.naver.com/{b}/{n}')
    if r:
        body = r.text
        paras = re.findall(r'<p class="se-text-paragraph[^"]*"[^>]*>(.*?)</p>', body, re.S)
        text = ''.join(re.sub(r'<[^>]+>', '', p) for p in paras)
        out['chars'] = len(re.sub(r'\s+', '', text))
        out['imgs'] = body.count('se-image-resource')
    time.sleep(0.5)
    return out

def run(keyword, mine='sobok__biz'):
    res = top_results(keyword)
    rows = []
    for rank, (b, n) in enumerate(res[:TOPN], 1):
        row = {'rank': rank, 'blog': b, 'logNo': n}
        row.update(post_info(b, n))
        row.update({k: v for k, v in blog_info(b).items() if k not in ('blog', 'dates_p1')})
        rows.append(row)
    mine_rank = next((i + 1 for i, (b, n) in enumerate(res) if b == mine), None)
    return {'keyword': keyword, 'checked': datetime.now().strftime('%Y-%m-%d'), 'total': len(res), 'mine_rank': mine_rank, 'top': rows}

if __name__ == '__main__':
    data = json.load(open(OUT, encoding='utf-8')) if os.path.exists(OUT) else {}
    for k in sys.argv[1:]:
        r = run(k)
        data[k] = r
        print(f"\n## {k} (우리 순위: {r['mine_rank']})")
        for x in r['top']:
            print(x['rank'], x['blog'], '글', x.get('date'), '| 총글', x.get('posts'), '이웃', x.get('buddies'), '첫글', x.get('first_post'), '30일', x.get('posts_30d'), '| 본문', x.get('chars'), '자 이미지', x.get('imgs'))
        json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
