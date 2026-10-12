import naver_blog_poster as nb, time, json, re, sys
from selenium.webdriver.common.by import By
sys.stdout.reconfigure(encoding='utf-8')
d=nb.get_driver()
bd=open('_mytab.txt').read(); nv=open('_naver_tab.txt').read()
orig=json.load(open('_intro_backup.json',encoding='utf-8'))['introduce']
# 1) 블덱스 코드 발급
d.switch_to.window(bd); d.get('https://blogdex.space/connect'); time.sleep(8)
inp=d.find_element(By.XPATH,"//input[contains(@placeholder,'블로그 주소')]"); inp.click(); inp.send_keys('sobok__biz'); time.sleep(.5)
d.find_element(By.XPATH,"//button[normalize-space(.)='연결하기']").click(); time.sleep(5)
b=d.find_elements(By.XPATH,"//button[normalize-space(.)='재연결']")
if b: b[0].click(); time.sleep(6)
t=d.execute_script("return document.body.innerText"); code=re.search(r'G-\d+',t)
print('code', code.group(0) if code else None)
if not code: sys.exit(1)
code=code.group(0)
def set_intro(text):
    d.switch_to.window(nv); d.get('https://admin.blog.naver.com/sobok__biz/config/bloginfo'); time.sleep(5)
    d.switch_to.frame(d.find_elements('tag name','iframe')[5])
    d.execute_script("const t=document.querySelector('#frmIntroduce'); t.focus(); t.value=arguments[0]; t.dispatchEvent(new Event('input',{bubbles:true})); t.dispatchEvent(new Event('change',{bubbles:true}));", text)
    d.execute_script("document.querySelector('input._btnConfirm').click()"); time.sleep(3)
    try:
        a=d.switch_to.alert; print('alert:',a.text); a.accept()
    except Exception: pass
    time.sleep(2)
# 2) 소개글에 코드 삽입
set_intro(orig+'\n'+code)
# 3) 블덱스 확인 대기
d.switch_to.window(bd)
ok=False
for i in range(14):
    time.sleep(10)
    t=d.execute_script("return document.body.innerText")
    if '블로그 연결 확인 중' not in t:
        ok=True; break
print('연결확인', ok, d.current_url); print(t[:300].replace('\n',' | '))
# 4) 소개글 원복
set_intro(orig)
d.switch_to.window(nv); d.get('https://admin.blog.naver.com/sobok__biz/config/bloginfo'); time.sleep(4)
d.switch_to.frame(d.find_elements('tag name','iframe')[5])
print('복원 확인:', d.execute_script("return document.querySelector('#frmIntroduce').value")==orig)
