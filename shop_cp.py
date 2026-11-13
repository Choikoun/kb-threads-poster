#!/usr/bin/env python3
"""쿠팡 검색 압축 조사(토큰 절약용, 2026-11-13).
사용: python shop_cp.py <상품명에 반드시 들어갈 단어> <검색어1> [<검색어2> ...] [--link <글키>]
출력: 가격순 한 줄씩 '가격 로켓 상품번호 이름(40자)'. 같은 상품번호의 옵션 가격은 최저~최고로 묶는다.
--link 글키 를 주면 로켓 여부와 무관하게 선택한 번호 링크를 만들 수 있도록 번호 목록만 안내한다(링크 생성은 python shop_links.py blog <글키> <상품URL...>).
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
import coupang_api as c

args = [a for a in sys.argv[1:] if not a.startswith('--')]
must, queries = args[0], args[1:]
seen = {}
for q in queries:
    code, j = c.search(q, limit=10)
    for x in j.get('data', {}).get('productData', []):
        if must not in x['productName']:
            continue
        pid = x['productId']
        p = int(float(x['productPrice']))
        e = seen.setdefault(pid, dict(lo=p, hi=p, rocket=x['isRocket'], name=x['productName']))
        e['lo'], e['hi'] = min(e['lo'], p), max(e['hi'], p)
        e['rocket'] = e['rocket'] or x['isRocket']
for pid, e in sorted(seen.items(), key=lambda kv: kv[1]['lo']):
    price = f"{e['lo']:,}" if e['lo'] == e['hi'] else f"{e['lo']:,}~{e['hi']:,}"
    print(f"{price:>16} {'로켓' if e['rocket'] else '    '} {pid} {e['name'][:40]}")
print(f'총 {len(seen)}개 상품번호')
