#!/usr/bin/env python3
"""기존 네이버 글의 태그만 교체한다(본문·제목·이미지는 건드리지 않음).
사용: python naver_tag_update.py <logNo> "태그1,태그2,..." [--dry]
update 모드(naver_blog_poster.py update)는 본문을 지우고 다시 쓰므로 태그 실험에는 쓰지 않는다."""
import sys, time
sys.stdout.reconfigure(encoding='utf-8')
import naver_blog_poster as nb
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ln, tags = sys.argv[1], [t.strip() for t in sys.argv[2].split(',') if t.strip()]
DRY = '--dry' in sys.argv
d = nb.get_driver(); nb.acquire_work_tab(d)
d.execute_cdp_cmd('Emulation.setFocusEmulationEnabled', {'enabled': True})
d.get(f'https://blog.naver.com/{nb.BLOG_ID}?Redirect=Update&logNo={ln}')
w = WebDriverWait(d, 20)
w.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'mainFrame'))); time.sleep(3)
try: w.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button.se-image-toolbar-button')))
except Exception: pass
time.sleep(2); nb.dismiss_draft_popup(d); time.sleep(1)
title = d.execute_script("var t=document.querySelector('.se-documentTitle');return t?t.innerText.trim():''")
print('편집 중인 글 제목:', title)
btn = w.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@class,"publish_btn")]')))
nb.safe_click(d, btn); time.sleep(1.5)
box = w.until(EC.presence_of_element_located((By.XPATH, '//input[contains(@placeholder,"태그")] | //textarea[contains(@placeholder,"태그")]')))
before = d.execute_script("return [...document.querySelectorAll('[class*=tag_item],[class*=tag] a,[class*=tag] span')].map(e=>e.innerText.trim()).filter(x=>x)")
print('기존 태그 요소:', before)
d.save_screenshot('debug_tag_layer.png')
def chips():
    return d.execute_script("return [...document.querySelectorAll('span[class*=tag__] > span[class*=text__]')].map(e=>e.innerText.trim().replace(/^#/,''))")
inp = d.find_element(By.ID, 'tag-input'); nb.safe_click(d, inp)
for _ in range(20):
    if not chips(): break
    inp.send_keys(Keys.BACKSPACE); time.sleep(0.25)
print('삭제 후 태그:', chips())
for t in tags:
    inp.send_keys(t); inp.send_keys(Keys.ENTER); time.sleep(0.3)
now = chips()
print('입력 후 태그:', now)
if now != tags:
    d.save_screenshot('debug_tag_mismatch.png'); sys.exit('태그가 기대와 다릅니다. 발행하지 않았습니다.')
d.save_screenshot('debug_tag_layer.png')
if DRY:
    print('--dry: 발행하지 않았습니다.'); sys.exit(0)
conf = [b for b in d.find_elements(By.XPATH, '//button[contains(@class,"confirm_btn")]') if b.is_displayed()]
nb.safe_click(d, conf[0]); time.sleep(5)
d.switch_to.default_content()
print('발행 후 URL:', d.current_url)
