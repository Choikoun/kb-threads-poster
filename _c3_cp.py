import sys; sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
import coupang_api as c
seen=set()
for k,must in [("타임모어 C3 핸드밀",'타임모어'),("타임모어 C3S PRO",'타임모어'),("타임모어 C3S MAX PRO",'타임모어')]:
    code,j=c.search(k,limit=12); print('==',k,code)
    for x in j.get('data',{}).get('productData',[]):
        if must.lower() not in x['productName'].lower() and 'timemore' not in x['productName'].lower(): continue
        key=(x['productId'],x['productPrice'])
        if key in seen: continue
        seen.add(key); print(' ',x['productPrice'],x['isRocket'],x['productId'],x['productName'][:90])
