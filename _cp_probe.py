import sys; sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
import coupang_api as c
for k in sys.argv[1:]:
    try: r=c.search(k,limit=10)
    except Exception as e: print(k,'ERR',e); continue
    code,j=r; items=j.get("data",{}).get("productData",[])
    ps=[(x['productPrice'],x['isRocket'],x['productName'][:34]) for x in items]
    print('==',k,len(ps),'가격',min(p[0] for p in ps) if ps else '-',max(p[0] for p in ps) if ps else '-')
    for p in ps[:5]: print('  ',p)
