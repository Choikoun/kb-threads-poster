import os,sys,time,re
os.environ['NAVER_PROFILE_DIR']='shop_chrome_profile'; os.environ['NAVER_DEBUG_PORT']='9223'; os.environ['NAVER_BLOG_ID']='sobok_biz'
sys.stdout.reconfigure(encoding='utf-8')
import naver_blog_poster as nb
d=nb.get_driver()
d.get('https://blog.naver.com/PostList.naver?blogId=sobok_biz&categoryNo=0&from=postList'); time.sleep(6)
fr=d.find_elements('css selector','iframe#mainFrame')
if fr: d.switch_to.frame(fr[0])
t=d.execute_script("return [...document.querySelectorAll('a')].filter(a=>/logNo=\d+|sobok_biz\/\d+/.test(a.href)).map(a=>a.href+' | '+a.innerText.trim().slice(0,50)).filter(x=>x.split('|')[1].trim())")
seen=set()
for x in t[:14]:
    if x not in seen: print(x); seen.add(x)
print(d.current_url)
