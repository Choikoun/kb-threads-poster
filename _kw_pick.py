import sys, time
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from concurrent.futures import ThreadPoolExecutor
from keyword_check import search_volume
from kw_research import doc_count
seeds=sys.argv[1:]
rows={}
for i in range(0,len(seeds),5):
    for r in search_volume(seeds[i:i+5],related=True): rows[r['keyword']]=r
    time.sleep(0.4)
pool=[r for r in rows.values() if 200<=r['total']<=6000]
pool.sort(key=lambda r:-r['total']); pool=pool[:90]
with ThreadPoolExecutor(8) as ex: dc=list(ex.map(lambda r:doc_count(r['keyword']),pool))
out=[]
for r,n in zip(pool,dc):
    if n: out.append((round(r['total']/n,2),r['keyword'],r['total'],r['comp'],n))
out.sort(reverse=True)
print('연관어',len(rows),'후보',len(out))
for x in out[:25]: print(f'비율{x[0]} | {x[1]} | 검색량{x[2]} | 경쟁{x[3]} | 문서{x[4]}')
