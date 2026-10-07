#!/usr/bin/env python3
"""준최3 블로그용 키워드 발굴: 검색광고 API 연관어(검색량) + NAVER API HUB 블로그 검색 total(발행량)
사용: python kw_research.py [시드...]   → 검색량/발행량 비율이 높은(경쟁 낮은) 순 출력, kw_research_out.json 저장
기준: 검색량 > 발행량(블덱스 '검색이 글보다 많음')이면 최상, 발행량 5천 이하·검색량 150+ 우선."""
import sys, os, json, re, time, requests
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')
from keyword_check import search_volume

H = {'X-NCP-APIGW-API-KEY-ID': os.environ['NAVER_APIHUB_ID'], 'X-NCP-APIGW-API-KEY': os.environ['NAVER_APIHUB_SECRET']}
URL = 'https://naverapihub.apigw.ntruss.com/search/v1/blog'
SEEDS = ['사망보험금','종신보험','변액연금','연금보험','저축보험','경영인정기보험','법인보험','보험료대납','보험약관대출','보험금상속',
 '상속세','증여세','상속포기','한정승인','유류분','부담부증여','주식증여','가업승계','비상장주식','가지급금',
 '가수금','법인전환','법인세','퇴직연금','IRP','연금소득세','연금수령','건강보험료','지역가입자','피부양자',
 '양도세','종부세','임대사업자','상가임대','토지','배우자증여','부모님증여','자녀증여','사업자','폐업',
 '달러보험','외화보험','달러연금','연금개시','노후자금','은퇴자금','자산관리','절세','금융소득','배당']
USED = ['퇴직금정산','연금저축해지','며느리증여','가족간차용증','특정법인증여의제','부동산증여세','임대소득세','다주택자양도세','부부공동명의','유족연금','상속세개편','보험계약자변경','대표이사퇴직금','축의금증여세','해외금융계좌신고','퇴직연금세액공제','증여세계산','저가양도','사망보험금세금','배당소득세','달러통장']
EXC = re.compile(r'변호사|세무사|세무서|회계|무료|계산기|양식|서식|엑셀|삼성|한화|교보|KB|신한|하나|국민|농협|카카오|토스|네이버|홈택스|국세청|미래에셋|NH|현대|동양|흥국|메리츠|DB|라이나|AIA|메트라이프|추천|순위|후기|가입|설계사|펀드|ETF|주가|전망|금리|이자율|대출|청구|조회|신청|환급금|고지서|자동차|운전자|펫|반려|어린이|태아|치아|암|뇌|심장|실손|간병|맛집|여행|아파트|분양|청약|코인|비트코인')
REL = re.compile(r'보험|연금|상속|증여|세|법인|대표|퇴직|양도|배당|가지급|가수금|사업|폐업|주식|건물|임대|상가|토지|IRP|절세|금융소득|노후|은퇴|달러|외화|유류분|한정승인')


def doc_count(kw):
    for _ in range(3):
        try:
            r = requests.get(URL, params={'query': kw, 'display': 1}, headers=H, timeout=20)
            if r.status_code == 200:
                return r.json().get('total')
            time.sleep(1)
        except Exception:
            time.sleep(1)
    return None


if __name__ == '__main__':
    seeds = sys.argv[1:] or SEEDS
    rows = {}
    for i in range(0, len(seeds), 5):
        for r in search_volume(seeds[i:i + 5], related=True):
            rows[r['keyword']] = r
        time.sleep(0.4)
    pool = [r for r in rows.values() if 100 <= r['total'] <= 3000 and REL.search(r['keyword'])
            and not EXC.search(r['keyword']) and not any(u in r['keyword'] for u in USED)]
    print('연관어', len(rows), '후보', len(pool), flush=True)
    with ThreadPoolExecutor(8) as ex:
        counts = list(ex.map(lambda r: doc_count(r['keyword']), pool))
    out = []
    for r, c in zip(pool, counts):
        if c:
            r['docs'] = c
            r['ratio'] = round(r['total'] / c, 3)
            out.append(r)
    out.sort(key=lambda r: -r['ratio'])
    json.dump(out, open('kw_research_out.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"{'키워드':<18}{'검색':>6}{'발행':>9}{'비율':>7} 경쟁")
    for r in out[:60]:
        print(f"{r['keyword']:<18}{r['total']:>6}{r['docs']:>9}{r['ratio']:>7} {r['comp']}")
