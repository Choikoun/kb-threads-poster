import sys; sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
import coupang_api as c
seen=set()
for k in ["테팔 티타늄 1X 쿡이지 프라이팬 28cm","테팔 인덕션 티타늄 2X 데일리엑스퍼트 28cm","테팔 퍼펙트 레지스트 3X 프라이팬 28cm","테팔 트라토리아 주물 프라이팬 28cm","테팔 인덕션 프라이팬 28cm"]:
    code,j=c.search(k,limit=10); print('==',k)
    for x in j.get('data',{}).get('productData',[]):
        if '테팔' not in x['productName']: continue
        key=(x['productId'],x['productPrice'])
        if key in seen: continue
        seen.add(key); print(' ',x['productPrice'],x['isRocket'],x['productId'],x['productName'][:90])
