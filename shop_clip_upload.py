#!/usr/bin/env python3
"""네이버 클립(PC 웹 clipcreators.naver.com) 업로드 — 쇼핑 블로그 계정(shop_chrome_profile, 9223 헤드리스 크롬)
사용: python shop_clip_upload.py <영상.mp4> "<설명 300자 이내>" "<연결할 블로그 글 제목 일부>" [커버번호=1]
2026-10-19 휴롬 H400 업로드로 순서 검증(설명→커버→카테고리 쇼핑/쇼핑→광고·협찬 ON→콘텐츠 링크 블로그→전체 공개→등록).
설명엔 쿠팡 파트너스·쇼핑 커넥트 수수료 문구를 넣는다(후기 아님 명시). 광고·협찬 설정은 항상 켠다."""
import os, sys, time
os.environ.setdefault('NAVER_PROFILE_DIR', 'shop_chrome_profile'); os.environ.setdefault('NAVER_DEBUG_PORT', '9223'); os.environ.setdefault('NAVER_BLOG_ID', 'sobok_biz')
sys.stdout.reconfigure(encoding='utf-8')
import naver_blog_poster as nb
from selenium.webdriver.common.by import By

video, desc, blog_title = os.path.abspath(sys.argv[1]), sys.argv[2], sys.argv[3]
cover = int(sys.argv[4]) if len(sys.argv) > 4 else 1
d = nb.get_driver()
d.set_window_size(1400, 1000)


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
click(covers[min(cover, len(covers) - 1)])
# 카테고리: 추천 칩('쇼핑 > 쇼핑')을 누르면 1차·2차가 한 번에 지정된다(드롭다운 직접 선택은 2차가 누락돼 등록 실패한 적 있음)
chips = d.find_elements(By.CSS_SELECTOR, 'button[class*=categoryTag]')
click(chips[0]); time.sleep(1.5)
# 광고·협찬 설정 토글 켜기
h = vis("//*[contains(normalize-space(text()),'협찬 설정')]")[0]
tg = h.find_element(By.XPATH, "ancestor::*[.//button[contains(@class,'Toggle')]][1]//button[contains(@class,'Toggle')]")
if 'toggleOn' not in tg.get_attribute('class'):
    click(tg)
time.sleep(1)
# 콘텐츠 링크: 블로그 글 선택
click(vis("//span[normalize-space(.)='블로그']")[0]); time.sleep(3)
t = [e for e in d.find_elements(By.XPATH, f"//*[contains(normalize-space(text()),'{blog_title}')]") if e.is_displayed()]
btn = t[0].find_element(By.XPATH, "ancestor::*[.//button[normalize-space(.)='선택']][1]//button[normalize-space(.)='선택']")
d.execute_script('arguments[0].click()', btn)
print('블로그 글 선택:', btn.text)
time.sleep(2)
click(vis("//button[normalize-space(.)='등록']")[0]); time.sleep(8)
print(d.current_url)   # 성공 시 /web/contents/clips 로 이동(초안 URL에 남으면 설명·카테고리 등 필수값 누락)
