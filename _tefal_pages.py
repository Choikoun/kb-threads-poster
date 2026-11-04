import os,sys,time,json,re
os.environ['NAVER_PROFILE_DIR']='shop_chrome_profile'; os.environ['NAVER_DEBUG_PORT']='9223'; os.environ['NAVER_BLOG_ID']='sobok_biz'
sys.stdout.reconfigure(encoding='utf-8')
import naver_blog_poster as nb
d=nb.get_driver()
r=json.load(open('_bc_tefal2.json',encoding='utf-8'))
want={'cook28':'939327364968512','cook24':'939327364964416','cook20':'923773337701697','simply28':'939327364993088','light28':'939327365226560','daily28':'939327364644928','reg28':'939327365500992','touch28':'939327365386304','trat28':'956341915277184','steel20':'956341915592576'}
od='blog_images/shop_2026-11-04_데팔후라이팬/cap'
out={}
d.set_window_size(480,1000)
for k,pid in want.items():
    c=[x for x in r if x['h'].endswith(pid)][0]
    d.get(c['h']); time.sleep(5)
    ss=d.execute_script(r"return [...document.querySelectorAll('a')].map(a=>a.href).filter(h=>/smartstore|brand\.naver/.test(h))[0]")
    d.get(ss); time.sleep(8)
    for n,y in enumerate([0,500]):
        d.execute_script(f'window.scrollTo(0,{y})'); time.sleep(1.5)
        d.save_screenshot(f'{od}/{k}_{n}.png')
    t=d.execute_script('return document.body.innerText')
    j=t.find('상품정보\n상품번호')
    print('=====',k,pid,ss); print(c['t'][:120])
    i=t.find('평점'); print(t[i:i+330].replace('\n',' | '))
    print(t[j:j+520].replace('\n',' | '))
    out[k]=ss
json.dump(out,open('_tefal_ss.json','w'))
