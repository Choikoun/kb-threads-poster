import sys; sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
import coupang_api as c
seen=set()
for k,must in [("이즈미 보풀제거기",'이즈미'),("필립스 보풀제거기",'필립스'),("멜리언스 보풀제거기",'멜리언스'),("글리너 수동 보풀제거기",'글리너'),("오르디 보풀제거기",'오르디'),("아이프리 FX-714 보풀제거기",'아이프리')]:
    code,j=c.search(k,limit=10); print('==',k,code)
    for x in j.get('data',{}).get('productData',[]):
        if must not in x['productName']: continue
        key=(x['productId'],x['productPrice'])
        if key in seen: continue
        seen.add(key); print(' ',x['productPrice'],x['isRocket'],x['productId'],x['productName'][:90])
