import sys,time,urllib.parse
sys.stdout.reconfigure(encoding='utf-8')
import naver_blog_poster as nb
d=nb.get_driver()
for name,law in (('jbs','종합부동산세법'),('jbse','종합부동산세법시행령')):
    d.get('https://www.law.go.kr/법령/'+urllib.parse.quote(law)); time.sleep(12)
    t=d.execute_script('return document.body.innerText')
    open(f'_law_{name}.txt','w',encoding='utf-8').write(t); print(name,len(t),flush=True)
