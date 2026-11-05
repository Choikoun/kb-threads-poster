import sys,json; sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
import shop_links as s
ids={'izumi70':'6965246118','izumi52':'9787688730','philips':'9429836738','melians':'9790638316','gliner':'8080768634','ifree':'9288356396'}
r=dict(zip(ids,s.make([f'https://www.coupang.com/vp/products/{v}' for v in ids.values()],'blog','lint')))
print(r); json.dump(r,open('blog_images/_lint_cp_links.json','w'))
