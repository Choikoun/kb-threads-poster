#!/usr/bin/env python3
"""네이버 클립(PC 웹 clipcreators.naver.com) 업로드 — KB 블로그 계정(자동화 크롬 9222, 클립 아이디 moneyletter_kr).
사용: python naver_clip_poster.py <영상.mp4> "<설명 300자 이내>" "<연결할 블로그 글 제목 일부>" [커버번호=1] [--dry]
순서: 설명 → 커버 → 카테고리 경제/재테크 → AI 활용 ON(TTS 음성·자동생성 영상) → 콘텐츠 링크 블로그 → 전체 공개 → 등록.
--dry 는 등록 직전에 멈춘다. 쇼핑용(shop_clip_upload.py)은 별도 계정이라 건드리지 않는다."""
import os, sys, time
sys.stdout.reconfigure(encoding='utf-8')
import naver_blog_poster as nb
from selenium.webdriver.common.by import By

DRY = '--dry' in sys.argv
args = [a for a in sys.argv[1:] if a != '--dry']
video, desc, blog_title = os.path.abspath(args[0]), args[1], args[2]
cover = int(args[3]) if len(args) > 3 else 1
d = nb.get_driver()
d.set_window_size(1400, 1800)


def vis(xpath):
    return [e for e in d.find_elements(By.XPATH, xpath) if e.is_displayed()]


def click(el):
    d.execute_script('arguments[0].scrollIntoView({block:"center"}); arguments[0].click()', el)


d.get('https://clipcreators.naver.com/web/upload'); time.sleep(7)
d.find_element(By.CSS_SELECTOR, 'input[type=file]').send_keys(video)
for _ in range(30):
    time.sleep(3)
    if '/draft/' in d.current_url and d.find_elements(By.CSS_SELECTOR, 'textarea'):
        break
time.sleep(5)
ta = d.find_element(By.CSS_SELECTOR, 'textarea'); ta.click(); ta.send_keys(desc)
covers = d.find_elements(By.CSS_SELECTOR, 'img[class*=coverImg]')
if covers:
    click(covers[min(cover, len(covers) - 1)])
click(vis("//span[normalize-space(.)='1차 카테고리']")[0]); time.sleep(1)
click(vis("//button[normalize-space(.)='경제']")[0]); time.sleep(1)
click(vis("//span[normalize-space(.)='2차 카테고리']")[0]); time.sleep(1)
click(vis("//button[normalize-space(.)='재테크']")[0]); time.sleep(1)
# AI 활용 설정 토글(TTS 음성·자동 생성 영상이라 켠다)
print('AI 활용 토글:', d.execute_script('''const t=[...document.querySelectorAll("*")].find(e=>e.children.length==0&&(e.innerText||"").trim()=="AI 활용 설정");
let p=t; for(let i=0;i<5&&p;i++){const b=p.querySelector&&p.querySelector("button[class*=Toggle]"); if(b){b.click(); return true} p=p.parentElement} return false'''))
time.sleep(1)
# 콘텐츠 링크: 블로그 글 선택 (제목을 포함한 가장 작은 행의 '선택' 버튼)
click(vis("//span[normalize-space(.)='블로그']")[0]); time.sleep(3)
btns = vis(f"//*[contains(normalize-space(.),'{blog_title}')]/ancestor::*[.//button[normalize-space(.)='선택']][1]//button[normalize-space(.)='선택']")
print('블로그 글 선택 버튼:', len(btns))
if btns:
    click(btns[0])
time.sleep(2)
d.save_screenshot('_clip_ready.png')
if DRY:
    print('--dry: 등록 직전에서 멈춤 (_clip_ready.png)')
    sys.exit(0)
click(vis("//button[normalize-space(.)='등록']")[0]); time.sleep(8)
print(d.current_url)
