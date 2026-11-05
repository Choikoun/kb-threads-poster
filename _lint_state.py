import os,sys,time
os.environ['NAVER_PROFILE_DIR']='shop_chrome_profile'; os.environ['NAVER_DEBUG_PORT']='9223'; os.environ['NAVER_BLOG_ID']='sobok_biz'
sys.stdout.reconfigure(encoding='utf-8')
import naver_blog_poster as nb
d=nb.get_driver()
print(d.get_window_size())
for h in d.window_handles:
    d.switch_to.window(h); print(h, d.current_url[:120], d.title[:40])
d.set_window_size(1280,1000); time.sleep(2)
d.save_screenshot('_lint_state.png')
