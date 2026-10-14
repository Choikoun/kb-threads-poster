#!/usr/bin/env python3
"""쇼핑 계정 유튜브(구글)·틱톡 로그인용 — 창이 뜨면 직접 로그인하고 창은 닫지 말고 Claude에게 알리세요.
shop_chrome_profile(네이버·브랜드커넥트 로그인과 같은 프로필)을 씁니다. 실행 중이던 헤드리스 크롬은 먼저 닫습니다."""
import os, sys, time, subprocess
os.environ['NAVER_PROFILE_DIR'] = 'shop_chrome_profile'
os.environ['NAVER_DEBUG_PORT'] = '9223'
import naver_blog_poster as nb
try:
    d = nb.get_driver()
    d.execute_cdp_cmd('Browser.close', {})
    time.sleep(3)
except Exception:
    pass
args = [nb.find_chrome(), f'--remote-debugging-port={nb.DEBUG_PORT}', f'--user-data-dir={nb.PROFILE_DIR}',
        '--disable-extensions', '--window-size=1300,950', '--window-position=120,60',
        'https://accounts.google.com/ServiceLogin?service=youtube&continue=https://studio.youtube.com',
        'https://www.tiktok.com/login']
subprocess.Popen(args)
print('크롬 창이 떴어요: 구글(유튜브)과 틱톡에 로그인하세요.')
