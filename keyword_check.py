#!/usr/bin/env python3
"""
네이버 검색광고 API로 키워드 월간 검색수 조회 (롱테일 키워드 선정용)

사용법:
    python keyword_check.py "연금보험 사망시" "연금 개시 후 사망" ...
    python keyword_check.py --related "연금보험 사망시"   # 연관 키워드까지 넓게

출력: 키워드 | PC | 모바일 | 합계 | 경쟁도  (합계 기준 정렬)
키는 .env 의 NAVER_AD_API_KEY / NAVER_AD_SECRET / NAVER_AD_CUSTOMER_ID
"""
import os, sys, time, hmac, hashlib, base64, requests
from dotenv import load_dotenv
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'https://api.searchad.naver.com'
API_KEY = os.environ['NAVER_AD_API_KEY']
SECRET = os.environ['NAVER_AD_SECRET']
CUSTOMER_ID = os.environ['NAVER_AD_CUSTOMER_ID']


def _headers(method, uri):
    ts = str(int(time.time() * 1000))
    msg = f'{ts}.{method}.{uri}'
    sig = base64.b64encode(hmac.new(SECRET.encode(), msg.encode(), hashlib.sha256).digest()).decode()
    return {'X-Timestamp': ts, 'X-API-KEY': API_KEY, 'X-Customer': CUSTOMER_ID, 'X-Signature': sig}


def _num(v):
    # API는 10 미만을 '< 10' 문자열로 줌
    if isinstance(v, str):
        return 5 if '<' in v else int(v.replace(',', ''))
    return int(v)


def search_volume(keywords, related=False):
    """keywords(list[str]) → [{'keyword','pc','mobile','total','comp'}] 합계 내림차순"""
    uri = '/keywordstool'
    results = {}
    # hintKeywords는 한 번에 최대 5개, 공백 제거 필요
    for i in range(0, len(keywords), 5):
        chunk = [k.replace(' ', '') for k in keywords[i:i+5]]
        r = requests.get(BASE + uri, headers=_headers('GET', uri),
                         params={'hintKeywords': ','.join(chunk), 'showDetail': '1'}, timeout=15)
        r.raise_for_status()
        for row in r.json().get('keywordList', []):
            kw = row['relKeyword']
            if not related and kw not in chunk:
                continue
            pc, mo = _num(row['monthlyPcQcCnt']), _num(row['monthlyMobileQcCnt'])
            results[kw] = {'keyword': kw, 'pc': pc, 'mobile': mo, 'total': pc + mo,
                           'comp': row.get('compIdx', '')}
    return sorted(results.values(), key=lambda x: -x['total'])


def print_table(rows, limit=40):
    print(f"{'키워드':<22}{'PC':>7}{'모바일':>8}{'합계':>8}  경쟁")
    for r in rows[:limit]:
        print(f"{r['keyword']:<22}{r['pc']:>7}{r['mobile']:>8}{r['total']:>8}  {r['comp']}")


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        print(__doc__); sys.exit(0)
    print_table(search_volume(args, related='--related' in sys.argv))
