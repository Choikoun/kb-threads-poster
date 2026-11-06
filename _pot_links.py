import sys,json; sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
import shop_links as s
ids={'tefal':'9801706431','zilec':'8513431159','hk':'8155934787','darum':'9271827286','boar':'8918595360'}
r=dict(zip(ids,s.make([f'https://www.coupang.com/vp/products/{v}' for v in ids.values()],'blog','pot')))
print(r); json.dump(r,open('blog_images/_pot_cp_links.json','w'))
