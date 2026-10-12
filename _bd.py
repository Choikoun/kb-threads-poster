import naver_blog_poster as nb, time, sys, re
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
sys.stdout.reconfigure(encoding='utf-8')
kw=sys.argv[1]
d=nb.get_driver()
t=''
for attempt in range(14):
    d.get('https://blogdex.space/keyword'); time.sleep(8)
    t=d.execute_script("return document.body.innerText")
    if '요청이 많아' in t:
        m=re.search(r'(\d+)분 후',t); w=int(m.group(1)) if m else 3
        time.sleep(60*w+25); continue
    inp=d.find_element(By.CSS_SELECTOR,'input[placeholder="검색할 키워드를 입력하세요"]')
    inp.click(); inp.send_keys(Keys.CONTROL,'a'); inp.send_keys(Keys.DELETE); inp.send_keys(kw); inp.send_keys(Keys.ENTER); time.sleep(11)
    t=d.execute_script("return document.body.innerText")
    if '검색 기준' in t: break
open(f'_bdx_{kw}.txt','w',encoding='utf-8').write(t)
if '검색 기준' not in t: print('FAILED'); sys.exit(1)
i=t.find('검색 기준'); print(t[i:i+540].replace('\n',' | '))
j=t.find('상위 노출 지수 분포'); print(t[j:j+300].replace('\n',' | '))
j=t.find('블로그 탭 포스팅 목록'); print(t[j:j+1700])
k=t.find('종합 진단'); print(t[k:k+330])
