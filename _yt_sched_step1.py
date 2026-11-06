import os, sys, time
os.environ.setdefault('NAVER_PROFILE_DIR', 'shop_chrome_profile'); os.environ.setdefault('NAVER_DEBUG_PORT', '9223'); os.environ.setdefault('NAVER_BLOG_ID', 'sobok_biz')
sys.stdout.reconfigure(encoding='utf-8')
import naver_blog_poster as nb
from selenium.webdriver.common.by import By
vid, title, descf = os.path.abspath(sys.argv[1]), sys.argv[2], sys.argv[3]
desc = open(descf, encoding='utf-8').read()
d = nb.get_driver()
d.set_window_size(1280, 1000)
js = lambda f, *a: d.execute_script(open(f, encoding='utf-8').read(), *a)
d.get('https://studio.youtube.com/channel/UCoHfUNfb812NsJRxhnDt5og/videos/upload?d=ud'); time.sleep(8)
d.find_element(By.CSS_SELECTOR, 'input[type=file]').send_keys(vid); time.sleep(12)
tb = d.find_elements(By.CSS_SELECTOR, '#textbox[contenteditable]')
tb[0].click(); d.execute_script("arguments[0].innerText=''", tb[0]); tb[0].send_keys(title)
tb[1].click(); d.execute_script("arguments[0].innerText=''", tb[1]); tb[1].send_keys(desc); time.sleep(1)
print(js('_yt_radio.js'))
d.execute_script('''const hs=[...document.querySelectorAll("ytcp-button,button")].filter(e=>(e.innerText||"").trim()==="자세히 보기"); const h=hs[hs.length-1]; if(h){h.scrollIntoView({block:"center"}); h.click()}''')
time.sleep(2)
print(d.execute_script('''const r=[...document.querySelectorAll("tp-yt-paper-radio-button")].find(e=>(e.innerText||"").trim().startsWith("예, 동영상에 유료 프로모션")); if(!r) return "no promo radio"; r.scrollIntoView({block:"center"}); r.click(); return "promo yes: "+r.getAttribute("aria-checked")'''))
for _ in range(3):
    time.sleep(3); print(js('_yt_click.js', '다음'))
time.sleep(3)
print(d.execute_script('''return [...document.querySelectorAll('tp-yt-paper-radio-button')].map(e=>e.getAttribute('name')+'|'+e.innerText.trim().replace(/\n/g,' ').slice(0,60))'''))
d.save_screenshot('debug_yt_vis.png')
