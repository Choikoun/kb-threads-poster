import os,sys,time,json
os.environ['NAVER_PROFILE_DIR']='shop_chrome_profile'; os.environ['NAVER_DEBUG_PORT']='9223'; os.environ['NAVER_BLOG_ID']='sobok_biz'
sys.stdout.reconfigure(encoding='utf-8')
import naver_blog_poster as nb
d=nb.get_driver()
r=json.load(open('_bc_c3.json',encoding='utf-8'))
want={'maxpro':'891931191195520','pro_off':'891931191191425','pro_sel':'918883792562080','pro_mirae':'895415294833728','pro_km':'895416156877344','c3s':'895415934243552','c3s_black':'1003857772671680'}
OD='blog_images/shop_2026-11-06_타임모어C3'
os.makedirs(OD+'/cap',exist_ok=True)
out={}
d.set_window_size(480,1000)


def one(k,pid):
    c=[x for x in r if x['h'].endswith(pid)][0]
    d.get(c['h']); time.sleep(6)
    ss=d.execute_script(r"return [...document.querySelectorAll('a')].map(a=>a.href).filter(h=>/smartstore|brand\.naver/.test(h))[0]")
    if not ss: raise RuntimeError('no link')
    d.get(ss); time.sleep(8)
    for n,y in enumerate([0,500]):
        d.execute_script(f'window.scrollTo(0,{y})'); time.sleep(1.5)
        d.save_screenshot(f'{OD}/cap/{k}_{n}.png')
    t=d.execute_script('return document.body.innerText')
    open(f'{OD}/cap/{k}.txt','w',encoding='utf-8').write(t)
    j=t.find('상품정보\n상품번호')
    print('=====',k,pid,ss); print(c['t'][:140])
    i=t.find('평점'); print(t[i:i+200].replace('\n',' | '))
    k2=t.find('배송'); print(t[k2:k2+160].replace('\n',' | '))
    print(t[j:j+700].replace('\n',' | '))
    out[k]=ss


for k,pid in want.items():
    for _ in range(3):
        try:
            one(k,pid); break
        except Exception as e:
            print('retry',k,str(e)[:60]); time.sleep(4)
json.dump(out,open('_c3_ss.json','w'))
