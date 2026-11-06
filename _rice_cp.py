import sys; sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
import coupang_api as c
seen=set()
for k in ["락앤락 쌀통","락앤락 쌀통 10kg","락앤락 쌀통 5kg","락앤락 잡곡통 2kg","락앤락 쌀통 20kg"]:
    code,j=c.search(k,limit=10); print('==',k,code)
    for x in j.get('data',{}).get('productData',[]):
        key=x['productId']
        if key in seen: continue
        seen.add(key); print(' ',x['productPrice'],x['isRocket'],x['productId'],x['productName'][:95])
