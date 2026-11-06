import sys; sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
import coupang_api as c
seen=set()
for k,must in [("테팔 테이스티 BJ551",'테팔'),("자일렉 전기포트 올스텐",'자일렉'),("한경희 전기포트 HEP-2010",'한경희'),("다룸 멜로우 전기포트",'다룸'),("보아르 다이닝온 전기포트",'보아르'),("모즈스웨덴 전기포트 1.7L",'모즈')]:
    code,j=c.search(k,limit=10); print('==',k,code)
    for x in j.get('data',{}).get('productData',[]):
        if must not in x['productName']: continue
        key=(x['productId'],x['productPrice'])
        if key in seen: continue
        seen.add(key); print(' ',x['productPrice'],x['isRocket'],x['productId'],x['productName'][:90])
