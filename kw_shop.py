#!/usr/bin/env python3
"""쇼핑 리뷰 블로그용 키워드 발굴: 검색광고 API 연관어(검색량) + NAVER API HUB 블로그 total(발행량)
사용: python kw_shop.py [시드...]  → 검색량÷발행량 높은 순. 결과 kw_shop_out.json
의약품·건강기능식품·성인·효능 주장 소지가 있는 단어는 제외(광고 규제)."""
import sys, os, json, re, time
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')
from keyword_check import search_volume
from kw_research import doc_count

SEEDS = ['에어프라이어','전기포트','무선청소기','로봇청소기','가습기','제습기','선풍기','서큘레이터','전기장판','온풍기',
 '밀폐용기','수납박스','수납장','행거','빨래건조대','세탁망','주방세제','설거지','식기건조대','도마',
 '프라이팬','냄비','텀블러','보온병','도시락','전기밥솥','믹서기','핸드블렌더','커피머신','드립커피',
 '이불','베개','매트리스커버','샤워기','수건','욕실용품','발매트','쓰레기통','청소도구','문틈막이']
EXC = re.compile(r'효능|효과|부작용|치료|다이어트|영양제|건강기능|약|성인|여성|임신|아기|유아|신생아|분유|기저귀|의료|혈압|당뇨|탈모|화장품|세럼|마스크팩|보톡스|담배|술|와인|맥주|총|칼날|무기|중고|당근|렌탈|리스|설치|수리|AS|고장|서비스센터|매뉴얼|사용법|비밀번호|리콜|이벤트|쿠폰|할인코드|주가|주식')
GEN = re.compile(r'^[가-힣A-Za-z0-9 ]+$')

if __name__ == '__main__':
    seeds = sys.argv[1:] or SEEDS
    rows = {}
    for i in range(0, len(seeds), 5):
        for r in search_volume(seeds[i:i + 5], related=True):
            rows[r['keyword']] = r
        time.sleep(0.4)
    pool = [r for r in rows.values() if 200 <= r['total'] <= 4000 and not EXC.search(r['keyword']) and GEN.match(r['keyword'])]
    print('연관어', len(rows), '후보', len(pool), flush=True)
    with ThreadPoolExecutor(8) as ex:
        counts = list(ex.map(lambda r: doc_count(r['keyword']), pool))
    out = []
    for r, c in zip(pool, counts):
        if c:
            r['docs'] = c; r['ratio'] = round(r['total'] / c, 3); out.append(r)
    out.sort(key=lambda r: -r['ratio'])
    json.dump(out, open('kw_shop_out.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"{'키워드':<20}{'검색':>6}{'발행':>9}{'비율':>7} 경쟁")
    for r in out[:70]:
        print(f"{r['keyword']:<20}{r['total']:>6}{r['docs']:>9}{r['ratio']:>7} {r['comp']}")
