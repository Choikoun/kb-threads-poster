#!/usr/bin/env python3
"""틱톡 예약 업로드(쇼핑 계정, 9223 크롬의 TikTok Studio, 2026-11-06 확립).
사용: python shop_tt_sched.py <영상_tt.mp4> <설명파일.txt> <일(숫자)> <시(2자리)>
순서: 업로드 → 팁 닫기 → 설명 → 예약(동의창 '허용') → 날짜·시 → 설정 펼치기 → 게시물 콘텐츠 공개·브랜디드·AI 생성 → 예약.
날짜는 이번 달 기준(달 넘어가면 수정 필요). 예약 목록(tab=scheduled)에서 확인."""
import os, sys, time
os.environ.setdefault('NAVER_PROFILE_DIR', 'shop_chrome_profile'); os.environ.setdefault('NAVER_DEBUG_PORT', '9223'); os.environ.setdefault('NAVER_BLOG_ID', 'sobok_biz')
sys.stdout.reconfigure(encoding='utf-8')
import naver_blog_poster as nb
from selenium.webdriver.common.keys import Keys
vid, capf, day, hour = os.path.abspath(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
cap = open(capf, encoding='utf-8').read().strip()
d = nb.get_driver(); d.set_window_size(1280, 1000)
ex = d.execute_script
def clickbtn(t):
    return ex('''const b=[...document.querySelectorAll('button')].find(e=>e.innerText.trim()===arguments[0]&&e.getBoundingClientRect().width>0); if(b){b.click(); return true} return false''', t)
try:
    d.get('https://www.tiktok.com/tiktokstudio/content')
except Exception as e:
    print('nav', str(e)[:60])
try:
    d.switch_to.alert.accept()
except Exception:
    pass
time.sleep(3)
d.get('https://www.tiktok.com/tiktokstudio/upload'); time.sleep(8)
d.find_element('css selector', 'input[type=file]').send_keys(vid); time.sleep(15)
print('tip', clickbtn('확인')); time.sleep(1)
ed = d.find_element('css selector', '.public-DraftEditor-content, [contenteditable=true]')
ed.click(); ed.send_keys(Keys.CONTROL, 'a'); ed.send_keys(Keys.DELETE); time.sleep(0.5)
lines = cap.split('\n')
for i, line in enumerate(lines):
    ed.send_keys(line)
    if i < len(lines) - 1: ed.send_keys(Keys.SHIFT, Keys.ENTER)
time.sleep(1.5)
ex('''[...document.querySelectorAll('*')].filter(e=>e.children.length==0&&(e.innerText||'').trim()==='세부 정보').forEach(e=>e.click())''')
time.sleep(1)
ex('''const l=[...document.querySelectorAll('label,span,div')].filter(e=>e.children.length<=1&&(e.innerText||'').trim()==='예약'); l.forEach(e=>e.scrollIntoView({block:'center'})); if(l.length) l[0].click()''')
time.sleep(2); print('allow', clickbtn('허용')); time.sleep(2)
today = ex('''return [...document.querySelectorAll('*')].filter(e=>e.children.length==0&&/^2026년 \\d+월 \\d+일$/.test((e.innerText||'').trim())&&e.getBoundingClientRect().width>0).map(e=>e.innerText.trim())''')
print('date now', today)
dt = [e for e in d.find_elements('xpath', '//*[contains(text(),"2026년")]') if e.is_displayed()][0]
ex('arguments[0].click()', dt); time.sleep(1.5)
by = dt.rect['y']
n = ex('''const by=arguments[1]; const c=[...document.querySelectorAll('span,div,button')].filter(e=>e.children.length==0&&(e.innerText||'').trim()===arguments[0]&&e.getBoundingClientRect().width>0&&e.getBoundingClientRect().bottom<by&&e.getBoundingClientRect().top>by-330); if(c.length) c[0].click(); return c.length''', day, by)
print('day click', n); time.sleep(1.2)
ex('''const t=[...document.querySelectorAll('*')].filter(e=>e.children.length==0&&/^\d\d:\d\d$/.test((e.innerText||'').trim())&&e.getBoundingClientRect().width>0&&!e.className.toString().includes('TimePicker'))[0]; t.click()'''); time.sleep(1.5)
b = [e for e in d.find_elements('css selector', 'button.TimePicker__item') if e.text.strip() == hour][0]
ex('arguments[0].scrollIntoView({block:"center"}); arguments[0].click()', b); time.sleep(1.2)
ex('''[...document.querySelectorAll('*')].filter(e=>e.children.length==0&&(e.innerText||'').trim()==='설정').forEach(e=>e.click())'''); time.sleep(1)
ex('''const e=[...document.querySelectorAll('*')].filter(e=>(e.innerText||'').trim()==='펼치기'&&e.children.length<=1); if(e.length){e[e.length-1].scrollIntoView({block:'center'}); e[e.length-1].click()}''')
time.sleep(2)
def sw(label):
    return ex('''const t=[...document.querySelectorAll('*')].filter(e=>e.children.length<=1&&(e.innerText||'').trim()===arguments[0]&&e.getBoundingClientRect().width>0)[0]; if(!t) return 'no '+arguments[0]; const r=t.getBoundingClientRect(); const s=document.elementFromPoint(r.right+30, r.top+r.height/2); s.click(); return 'ok'+Math.round(r.right+30)''', label)
print('promo', sw('게시물 콘텐츠 공개')); time.sleep(1.5)
ex('''const l=[...document.querySelectorAll('*')].filter(e=>e.children.length<=1&&(e.innerText||'').trim()==='브랜디드 콘텐츠'&&e.getBoundingClientRect().width>0)[0]; if(l){const r=l.getBoundingClientRect(); document.elementFromPoint(r.left-18, r.top+r.height/2).click()}''')
time.sleep(1)
print('ai', sw('AI 생성 콘텐츠')); time.sleep(1.5); print('ai on', clickbtn('켜기')); time.sleep(1.5)
ex('''window.scrollTo(0,document.body.scrollHeight); document.querySelectorAll("*").forEach(e=>{if(e.scrollHeight>e.clientHeight+50)e.scrollTop=e.scrollHeight})''')
time.sleep(1)
chk = ex('''return [...document.querySelectorAll('*')].filter(e=>e.children.length==0&&/^(\\d\\d:\\d\\d|2026년 .*일)$/.test((e.innerText||"").trim())&&e.getBoundingClientRect().width>0).map(e=>e.innerText.trim())''')
print('check', chk)
d.save_screenshot('debug_tt_sched.png')
want_d = f'11월 {day}일'
if not any(want_d in c for c in chk) or f'{hour}:00' not in chk:
    sys.exit('날짜/시간이 기대와 달라 중단: ' + repr(chk) + ' (창은 열어 둠)')
print('submit', clickbtn('예약')); time.sleep(6)
print(d.current_url)
