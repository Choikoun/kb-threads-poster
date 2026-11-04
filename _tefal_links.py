import sys,json; sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
import shop_links as s
ids={'cook28':'8297268493','daily':'7778604772','reg':'9253921276'}
r=dict(zip(ids,s.make([f'https://www.coupang.com/vp/products/{v}' for v in ids.values()],'blog','tefal')))
print(r); json.dump(r,open('blog_images/_tefal_cp_links.json','w'))
