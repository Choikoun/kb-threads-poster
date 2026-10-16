#!/usr/bin/env python3
"""Gemini Deep Research 실행 → 결과 텍스트 저장.
사용: python gemini_deep_research.py "질문" out.txt
자동화 크롬(9222)의 구글 로그인 세션 사용. 계획 단계의 '리서치 시작' 버튼을 자동 클릭하고 완료까지 폴링(최대 30분)."""
import sys, time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
sys.argv_saved = sys.argv[:]
import naver_blog_poster as nb
sys.stdout.reconfigure(encoding='utf-8')

q = sys.argv_saved[1]
out = sys.argv_saved[2] if len(sys.argv_saved) > 2 else '_gemini_dr.txt'

JS_CLICK_TEXT = """
const want = arguments[0];
const els = [...document.querySelectorAll('button,[role=menuitem],a')].filter(e => e.offsetParent);
const hit = els.find(e => ((e.innerText||'') + ' ' + (e.getAttribute('aria-label')||'')).includes(want));
if (hit) { hit.click(); return true; } return false;
"""
JS_LAST = "const m=document.querySelectorAll('model-response,message-content');return m.length?m[m.length-1].innerText:''"

d = nb.get_driver()
d.get('https://gemini.google.com/app')
time.sleep(6)
d.execute_script("[...document.querySelectorAll('button')].find(b=>(b.getAttribute('aria-label')||'').includes('업로드 및 도구'))?.click()")
time.sleep(2)
print('Deep Research 선택:', d.execute_script(JS_CLICK_TEXT, 'Deep Research'), flush=True)
time.sleep(2)
box = d.find_element(By.CSS_SELECTOR, 'div.ql-editor')
box.click()
d.execute_script("arguments[0].focus();document.execCommand('insertText',false,arguments[1]);", box, q)
time.sleep(1)
n = d.execute_script("return document.querySelector('div.ql-editor').innerText.length")
print('입력 길이', n, flush=True)
if n < 5:  # 붙여넣기가 안 먹으면 타이핑
    for line in q.split(chr(10)):
        box.send_keys(line)
        box.send_keys(Keys.SHIFT, Keys.ENTER)
box.send_keys(Keys.ENTER)
print('전송', flush=True)

t0 = time.time()
started = False
last, stable = '', 0
while time.time() - t0 < 1800:
    time.sleep(15)
    if not started and d.execute_script(JS_CLICK_TEXT, '리서치 시작'):
        started = True
        print('리서치 시작 클릭', round(time.time() - t0), flush=True)
        continue
    t = d.execute_script(JS_LAST)
    if started:
        done_btn = d.execute_script("return [...document.querySelectorAll('button')].some(b=>b.offsetParent&&(((b.innerText||'')+(b.getAttribute('aria-label')||'')).includes('내보내기')||((b.innerText||'')+(b.getAttribute('aria-label')||'')).includes('Export')))")
        if len(t) > 3000 and done_btn and len(t) == len(last):
            stable += 1
        else:
            stable = 0
        last = t
        if stable >= 2:
            break
    else:
        last = t
        if 0 < len(t) < 300 and t == last and time.time() - t0 > 120:
            print('계획 단계에서 정지/거절 추정:', t[:100], flush=True)
            break
    print(round(time.time() - t0), 'sec / len', len(t), flush=True)
open(out, 'w', encoding='utf-8').write(last)
print('저장', len(last), '자 →', out)
