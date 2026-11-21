"""기존 글 제목만 교체: python _retitle.py <logNo> "<새 제목>" """
import sys, time
sys.stdout.reconfigure(encoding='utf-8')
import naver_blog_poster as nb
from naver_blog_poster import By, Keys, WebDriverWait, EC
log, title = sys.argv[1], sys.argv[2]
d = nb.get_driver(); nb.acquire_work_tab(d)
d.get(f'https://blog.naver.com/{nb.BLOG_ID}?Redirect=Update&logNo={log}')
w = WebDriverWait(d, 20)
w.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'mainFrame'))); time.sleep(4)
nb.dismiss_draft_popup(d); time.sleep(1)
t = w.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.se-section-documentTitle')))
nb.safe_click(d, t); time.sleep(0.3)
nb.send_chord(d, Keys.CONTROL, 'a'); time.sleep(0.2)
nb.send(d, Keys.DELETE); time.sleep(0.3)
nb.type_title(d, w, title)
print('제목:', d.find_element(By.CSS_SELECTOR, '.se-section-documentTitle').text)
b = w.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@class,"publish_btn")]')))
nb.safe_click(d, b); time.sleep(1.5)
c = [x for x in d.find_elements(By.XPATH, '//button[contains(@class,"confirm_btn")]') if x.is_displayed()]
nb.safe_click(d, c[0]); time.sleep(5)
d.switch_to.default_content(); print('결과 URL:', d.current_url)
