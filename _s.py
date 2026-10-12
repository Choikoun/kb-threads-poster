import os, time, sys
os.environ.update(NAVER_PROFILE_DIR='shop_chrome_profile', NAVER_DEBUG_PORT='9223', NAVER_BLOG_ID='sobok_biz')
sys.stdout.reconfigure(encoding='utf-8')
import naver_blog_poster as nb
from selenium.webdriver.common.by import By
d=nb.get_driver()
d.switch_to.window([h for h in d.window_handles if h.startswith('3F707')][0])
b=d.find_element(By.XPATH,"//button[normalize-space(.)='다음으로 가기']"); d.execute_script("arguments[0].scrollIntoView({block:'center'})",b); b.click(); time.sleep(5)
print(d.current_url); print(d.execute_script("return document.body.innerText.slice(0,2500)"))
d.save_screenshot('_bc.png')
