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
    except Exception as e: return []
base=['달러','달러연금','달러보험','달러종신','달러통장','달러 연금보험','달러 변액','달러 적립','달러 저축','달러 일시납','달러 해지','달러 수령','달러 세금','달러 환율 보험','달러 자산','달러 노후','달러 은퇴','달러 상속','달러 증여','달러 법인','달러 사업자','달러 비과세','외화 연금','외화 보험','외화 저축','미국 달러 보험','달러 분산','달러 노후자금','달러 연금 수령','달러 연금 환율']
sug=set()
for b in base:
    for s in ac(b)+ac(b+' '): sug.add(s.replace(' ',''))
    time.sleep(0.15)
sug={s for s in sug if re.search(r'달러|외화',s)}
print('자동완성',len(sug),flush=True)
rows={}
sl=list(sug)
for i in range(0,len(sl),5):
    try:
        for r in search_volume(sl[i:i+5],related=False): rows[r['keyword']]=r
    except Exception as e: print('err',e)
    time.sleep(0.3)
BR=re.compile(r'삼성|한화|교보|KB|신한|하나|국민|농협|카카오|토스|우리|미래에셋|NH|현대|흥국|메리츠|DB|라이나|AIA|메트라이프|푸본|ABL|IBK|은행|증권|ETF|주가|코인|환율조회|환율계산|엔화|위안|유로|파운드|바트|홍콩|대만|호주|캐나다|베트남|일본|중국|태국|필리핀|추천|인덱스|환전|시세|오늘')
pool=[r for r in rows.values() if r['total']>=50 and not BR.search(r['keyword'])]
print(len(rows),len(pool),flush=True)
with ThreadPoolExecutor(8) as ex: cs=list(ex.map(lambda r:doc_count(r['keyword']),pool))
out=sorted([dict(r,docs=c) for r,c in zip(pool,cs) if c],key=lambda r:r['docs'])
json.dump(out,open('_kw_ac.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
for r in out[:60]: print(f"{r['keyword']:<18}{r['total']:>6}{r['docs']:>9} {r['comp']}")
