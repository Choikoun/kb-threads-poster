import os, sys, time
os.environ['NAVER_PROFILE_DIR']='shop_chrome_profile'; os.environ['NAVER_DEBUG_PORT']='9223'; os.environ['NAVER_BLOG_ID']='sobok_biz'
sys.stdout.reconfigure(encoding='utf-8')
import naver_blog_poster as nb
from selenium.webdriver.common.by import By
d = nb.get_driver()
vid = os.path.abspath('_tmp_vid/kai_reel.mp4')
title = '카이 손톱깎이 중 사이즈 네이버 4,800원 쿠팡 5,800원 #shorts'
desc = open('_yt_desc.txt', encoding='utf-8').read()
d.get('https://studio.youtube.com/channel/UCoHfUNfb812NsJRxhnDt5og/videos/upload?d=ud')
time.sleep(8)
def js(f, *a): return d.execute_script(open(f, encoding='utf-8').read(), *a)
inp = d.find_element(By.CSS_SELECTOR, 'input[type=file]')
inp.send_keys(vid)
time.sleep(10)
tb = d.find_elements(By.CSS_SELECTOR, '#textbox[contenteditable]')
print('textboxes', len(tb))
tb[0].click(); d.execute_script("arguments[0].innerText=''", tb[0]); tb[0].send_keys(title)
tb[1].click(); d.execute_script("arguments[0].innerText=''", tb[1]); tb[1].send_keys(desc)
time.sleep(1)
print(js('_yt_radio.js'))
for step in range(3):
    time.sleep(3)
    print(d.execute_script(open('_yt_click.js', encoding='utf-8').read(), '다음'))
time.sleep(3)
print(js('_yt_pub.js'))
time.sleep(2)
print(d.execute_script(open('_yt_click.js', encoding='utf-8').read(), '게시'))
time.sleep(8)
print(d.execute_script(open('_yt_dlg.js', encoding='utf-8').read()))
