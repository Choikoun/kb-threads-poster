#!/usr/bin/env python3
"""유튜브 쇼츠 업로드(쇼핑 계정, 9223 헤드리스 크롬). 사용: python shop_yt_upload.py <영상.mp4> "<제목 #shorts>" <설명파일.txt>
순서: 업로드 → 제목·설명 → 아동용 '아니요' → '유료 프로모션 포함 예'(2026-10-21 추가, 공정위 표시) → 다음x3 → 공개 → 게시"""
import os, sys, time
os.environ.setdefault('NAVER_PROFILE_DIR', 'shop_chrome_profile'); os.environ.setdefault('NAVER_DEBUG_PORT', '9223'); os.environ.setdefault('NAVER_BLOG_ID', 'sobok_biz')
sys.stdout.reconfigure(encoding='utf-8')
import naver_blog_poster as nb
from selenium.webdriver.common.by import By
vid, title, descf = os.path.abspath(sys.argv[1]), sys.argv[2], sys.argv[3]
desc = open(descf, encoding='utf-8').read()
d = nb.get_driver()
js = lambda f, *a: d.execute_script(open(f, encoding='utf-8').read(), *a)
d.get('https://studio.youtube.com/channel/UCoHfUNfb812NsJRxhnDt5og/videos/upload?d=ud'); time.sleep(8)
d.find_element(By.CSS_SELECTOR, 'input[type=file]').send_keys(vid); time.sleep(12)
tb = d.find_elements(By.CSS_SELECTOR, '#textbox[contenteditable]')
tb[0].click(); d.execute_script("arguments[0].innerText=''", tb[0]); tb[0].send_keys(title)
tb[1].click(); d.execute_script("arguments[0].innerText=''", tb[1]); tb[1].send_keys(desc); time.sleep(1)
print(js('_yt_radio.js'))
# 더보기('자세히 보기') 펼쳐 유료 프로모션 선택
d.execute_script('''const hs=[...document.querySelectorAll("ytcp-button,button")].filter(e=>(e.innerText||"").trim()==="자세히 보기"); const h=hs[hs.length-1]; if(h){h.scrollIntoView({block:"center"}); h.click()}''')
time.sleep(2)
print(d.execute_script('''const r=[...document.querySelectorAll("tp-yt-paper-radio-button")].find(e=>(e.innerText||"").trim().startsWith("예, 동영상에 유료 프로모션")); if(!r) return "no promo radio"; r.scrollIntoView({block:"center"}); r.click(); return "promo yes: "+r.getAttribute("aria-checked")'''))
for _ in range(3):
    time.sleep(3); print(js('_yt_click.js', '다음'))
time.sleep(3); print(js('_yt_pub.js')); time.sleep(2)
print(js('_yt_click.js', '게시')); time.sleep(8)
print(str(js('_yt_dlg.js'))[:400])
