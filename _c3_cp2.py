import sys; sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
import coupang_api as c
for k in ["타임모어 C3S PRO 그라인더","타임모어 그라인더","타임모어 C3 수동 그라인더"]:
    code,j=c.search(k,limit=10); n=j.get('data',{}).get('productData',[])
    print('==',k,code,len(n), str(j)[:150] if not n else '')
    for x in n: print(' ',x['productPrice'],x['isRocket'],x['productId'],x['productName'][:80])
