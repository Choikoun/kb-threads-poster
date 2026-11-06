import sys,json; sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
import shop_links as s
ids={'c2':'8431579931','cbase':'2749443','c5set':'7728382071','c5can':'9795043103','cwheel':'8622255651','cmid':'8480900050','c10set':'132992445'}
r=dict(zip(ids,s.make([f'https://www.coupang.com/vp/products/{v}' for v in ids.values()],'blog','rice')))
print(r); json.dump(r,open('blog_images/_rice_cp_links.json','w'))
