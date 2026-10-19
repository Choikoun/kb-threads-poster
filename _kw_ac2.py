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
bases=['달러변액연금','달러저축보험','달러CMA','달러RP','달러적금','달러MMF','달러채권','달러펀드','달러예금','외화RP','외화적금','외화보험','외화저축','달러연금','달러보험','달러종신','달러통장','달러ETF','달러자산','달러투자','달러상품','외화상품','외화변액','달러적립식','달러일시납','달러보험해지','달러연금수령','달러보험환급','달러보험세금','달러보험비교','달러보험가입','달러보험사망보험금','달러변액','달러확정금리','달러금리','달러예금금리','달러RP금리','외화RP금리','달러채권금리','미국채','달러보험환율','달러보험환차손','달러연금환율','달러연금해지','달러보험 중도인출','달러보험 담보대출','달러보험 법인','달러보험 증여','달러보험 상속','달러보험 연금전환']
suff=['',' ']+[' '+c for c in '가나다라마바사아자차카타파하']
sug=set()
for b in bases:
    for s in suff:
        for x in ac(b+s): sug.add(x.replace(' ',''))
    time.sleep(0.1)
sug={s for s in sug if re.search(r'달러|외화|미국채',s)}
print('자동완성',len(sug),flush=True)
rows={}
sl=sorted(sug)
for i in range(0,len(sl),5):
    try:
        for r in search_volume(sl[i:i+5],related=False): rows[r['keyword']]=r
    except Exception as e: print('err',str(e)[:60]); time.sleep(2)
    time.sleep(0.25)
BR=re.compile(r'삼성|한화|교보|KB|신한|하나|국민|농협|카카오|토스|우리|미래에셋|NH|현대|흥국|메리츠|DB|라이나|AIA|메트라이프|푸본|ABL|IBK|은행|증권|주가|코인|환율조회|환율계산|엔화|위안|유로|파운드|바트|홍콩|대만|호주|캐나다|베트남|일본|중국|태국|필리핀|추천|인덱스|환전|시세|오늘|계산기|환율전망|환산')
pool=[r for r in rows.values() if r['total']>=50 and not BR.search(r['keyword'])]
print(len(rows),len(pool),flush=True)
with ThreadPoolExecutor(8) as ex: cs=list(ex.map(lambda r:doc_count(r['keyword']),pool))
out=sorted([dict(r,docs=c,ratio=round(r['total']/c,3)) for r,c in zip(pool,cs) if c],key=lambda r:r['docs'])
json.dump(out,open('_kw_ac2.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
for r in out[:45]: print(f"{r['keyword']:<20}{r['total']:>6}{r['docs']:>9}{r['ratio']:>7} {r['comp']}")
