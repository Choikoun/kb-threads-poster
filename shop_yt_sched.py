#!/usr/bin/env python3
"""유튜브 쇼츠 예약 업로드(쇼핑 계정, 9223 크롬). 사용:
python shop_yt_sched.py <영상.mp4> "<제목 #shorts>" <설명파일.txt> "YYYY. M. D." "오전 9:00"
shop_yt_upload.py와 같은 순서이고 마지막에 공개 대신 '예약'을 설정한다."""
import os, sys, time
os.environ.setdefault('NAVER_PROFILE_DIR', 'shop_chrome_profile'); os.environ.setdefault('NAVER_DEBUG_PORT', '9223'); os.environ.setdefault('NAVER_BLOG_ID', 'sobok_biz')
sys.stdout.reconfigure(encoding='utf-8')
import naver_blog_poster as nb
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
vid, title, descf, date_s, time_s = os.path.abspath(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
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
print(d.execute_script('''const e=document.querySelector('#second-container-expand-button'); if(e){e.click(); return 'expand'} return 'no expand' '''))
time.sleep(2)
# 날짜
d.execute_script('''document.querySelector('#datepicker-trigger').click()'''); time.sleep(1.5)
di = [e for e in d.find_elements(By.CSS_SELECTOR, 'ytcp-date-picker input, tp-yt-paper-input input') if e.is_displayed()]
print('date inputs', [e.get_attribute('value') for e in di])
for e in di:
    v = e.get_attribute('value') or ''
    if '.' in v and ':' not in v:
        e.click(); e.send_keys(Keys.CONTROL, 'a'); e.send_keys(date_s); e.send_keys(Keys.ENTER); break
time.sleep(1.2)
# 시간
ti = [e for e in d.find_elements(By.CSS_SELECTOR, 'tp-yt-paper-input#textbox input') if e.is_displayed()]
ti[0].click(); ti[0].send_keys(Keys.CONTROL, 'a'); ti[0].send_keys(time_s); ti[0].send_keys(Keys.ENTER); time.sleep(1.5)
print(d.execute_script('''return [...document.querySelectorAll('ytcp-datetime-picker')].map(e=>e.innerText.split("\\n").join(" "))'''))
d.save_screenshot('debug_yt_sched.png')
_pk = d.execute_script('''return [...document.querySelectorAll('ytcp-datetime-picker')].map(e=>e.innerText).join(" ")''')
if date_s not in _pk or time_s not in (d.execute_script('''return [...document.querySelectorAll('tp-yt-paper-input#textbox input')].map(e=>e.value).join(" ")''')):
    sys.exit('예약 날짜/시간이 기대와 달라 중단: ' + repr(_pk) + ' (창은 열어 둠)')
print(js('_yt_click.js', '예약')); time.sleep(8)
print(str(js('_yt_dlg.js'))[:500])
