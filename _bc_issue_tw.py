import os, sys, time, json
os.environ['NAVER_PROFILE_DIR']='shop_chrome_profile'; os.environ['NAVER_DEBUG_PORT']='9223'; os.environ['NAVER_BLOG_ID']='sobok_biz'
sys.stdout.reconfigure(encoding='utf-8')
import naver_blog_poster as nb
d=nb.get_driver()
BASE='https://brandconnect.naver.com/1003759426647456/affiliate/'
items=json.loads(sys.argv[1])  # {key:[productId, 행 식별 문자열]}
click=open('_bc_click.js',encoding='utf-8').read(); copy=open('_bc_copy_row.js',encoding='utf-8').read()
out={}
for k,(pid,frag) in items.items():
    d.get(BASE+'products/'+pid); time.sleep(5)
    print(k,'issue',d.execute_script(click)); time.sleep(4)
    print(d.execute_script("return [...document.querySelectorAll('[role=dialog],.modal,.popup')].map(e=>e.innerText.slice(0,120))"))
    d.get(BASE+'products-link'); time.sleep(6)
    print(k,'copy',d.execute_script(copy,frag)); time.sleep(1)
    out[k]=d.execute_script('return window.__c')
    print(k,out[k])
print(json.dumps(out,ensure_ascii=False))
json.dump(out,open('blog_images/_bc_links_tw.json','w',encoding='utf-8'),ensure_ascii=False)
