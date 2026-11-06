import sys,json; sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
import shop_links as s
ids={'pro97':'8634198169','pro191':'9212867630'}
r=dict(zip(ids,s.make([f'https://www.coupang.com/vp/products/{v}' for v in ids.values()],'blog','c3')))
print(r); json.dump(r,open('blog_images/_c3_cp_links.json','w'))
