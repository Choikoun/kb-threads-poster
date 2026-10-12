import naver_blog_poster as nb, time, re
from selenium.webdriver.common.by import By
d=nb.get_driver()
first=d.window_handles[0]
d.switch_to.new_window('tab')
open('_mytab.txt','w').write(d.current_window_handle)
d.get('https://blogdex.space/connect'); time.sleep(8)
inp=d.find_element(By.XPATH,"//input[contains(@placeholder,'블로그 주소')]"); inp.click(); inp.send_keys('sobok__biz'); time.sleep(.5)
d.find_element(By.XPATH,"//button[normalize-space(.)='연결하기']").click(); time.sleep(5)
b=d.find_elements(By.XPATH,"//button[normalize-space(.)='재연결']")
if b: b[0].click(); time.sleep(6)
t=d.execute_script("return document.body.innerText"); i=t.find('내 블로그 연결'); print(t[i:i+700])
d.save_screenshot('_bl.png')
