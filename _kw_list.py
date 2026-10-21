import sys; sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from keyword_check import search_volume
from kw_research import doc_count
kws=sys.argv[1:]
rows={}
for k in range(0,len(kws),5):
    for r in search_volume(kws[k:k+5],related=False): rows[r['keyword']]=r
for k in kws:
    r=rows.get(k.replace(' ',''))
    dc=doc_count(k)
    print(k,'| 검색량',r['total'] if r else '<10', '| 경쟁',r['comp'] if r else '-','| 문서',dc,'| 비율',round(r['total']/dc,2) if r and dc else '')
