import sys,json; sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
import shop_links as s
ids={'moz1l':'7701457650','moz19':'9180882238'}
r=dict(zip(ids,s.make([f'https://www.coupang.com/vp/products/{v}' for v in ids.values()],'blog','pot')))
print(r)
d=json.load(open('blog_images/_pot_cp_links.json')); d.update(r); json.dump(d,open('blog_images/_pot_cp_links.json','w'))
