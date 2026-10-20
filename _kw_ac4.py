import sys,re,time,requests,json
sys.stdout.reconfigure(encoding='utf-8')
from keyword_check import search_volume
from kw_research import doc_count
from concurrent.futures import ThreadPoolExecutor
UA={'User-Agent':'Mozilla/5.0'}
def ac(q):
    try:
        r=requests.get('https://ac.search.naver.com/nx/ac',params={'q':q,'con':'1','frm':'nv','ans':'2','r_format':'json','r_enc':'UTF-8','r_unicode':'0','t_koreng':'1','run':'2','rev':'4','q_enc':'UTF-8','st':'100'},headers=UA,timeout=10).json()
        return [i[0] for g in r.get('items',[]) for i in g]
    except Exception: return []
bases=['임의계속가입','건강보험임의계속','퇴직후건강보험','피부양자','피부양자요건','피부양자탈락','피부양자소득','조기연금','국민연금조기수령','연기연금','노령연금','노령연금감액','국민연금소득감액','국민연금수령나이','국민연금개혁','주택연금','주택연금조건','역모기지','퇴직금일시금','퇴직금연금수령','퇴직소득세','퇴직금IRP','가업상속공제','가업상속공제개편','가업상속공제요건','가업상속공제한도','비상장주식평가','비상장주식가치','비상장주식평가방법','주식평가','순손익가치','순자산가치','종신보험손금','종신보험법인','대표이사종신보험','법인종신보험','경영인정기','법인보험손금','법인세절세','배당소득','법인주식','주주명부','법인등기부등본','정관','법인설립','법인청산','청산소득','노노상속','은퇴생활비','노후소득']
suff=['',' ']+[' '+c for c in '가나다라마바사아자차카타파하']
sug=set()
for b in bases:
    for s in suff:
        for x in ac(b+s): sug.add(x.replace(' ',''))
    time.sleep(0.05)
print('자동완성',len(sug),flush=True)
rows={}
sl=sorted(sug)
for i in range(0,len(sl),5):
    try:
        for r in search_volume(sl[i:i+5],related=False): rows[r['keyword']]=r
    except Exception as e: time.sleep(2)
    time.sleep(0.2)
BR=re.compile(r'삼성|한화|교보|KB|신한|하나|국민은행|농협|카카오|토스|우리|미래에셋|NH|현대|흥국|메리츠|DB|라이나|AIA|메트라이프|푸본|ABL|IBK|은행|증권|주가|코인|변호사|세무사|세무서|회계|무료|계산기|양식|서식|엑셀|홈택스|국세청|추천|순위|후기|조회|신청|자동차|펫|맛집|여행|아파트|분양|청약|달러|환율|외화|공단|고객센터|전화번호')
pool=[r for r in rows.values() if r['total']>=100 and not BR.search(r['keyword'])]
print(len(rows),len(pool),flush=True)
with ThreadPoolExecutor(8) as ex: cs=list(ex.map(lambda r:doc_count(r['keyword']),pool))
out=sorted([dict(r,docs=c) for r,c in zip(pool,cs) if c],key=lambda r:r['docs'])
json.dump(out,open('_kw_ac4.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
for r in out[:45]: print(f"{r['keyword']:<18}{r['total']:>6}{r['docs']:>9} {r['comp']}")
