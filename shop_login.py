#!/usr/bin/env python3
"""쇼핑 리뷰용 새 네이버 계정 로그인 전용 — 더블클릭/`python shop_login.py` 로 실행.
창이 뜨면 새 네이버 계정으로 직접 로그인('로그인 상태 유지' 체크)한 뒤, 창은 닫지 말고 Claude에게 알려주세요.
(기존 보험 블로그 계정/프로필과는 완전히 분리된 shop_chrome_profile 을 씁니다.)"""
import os
os.environ['NAVER_PROFILE_DIR'] = 'shop_chrome_profile'
os.environ['NAVER_DEBUG_PORT'] = '9223'
import naver_blog_poster as nb
nb.start_chrome(headed=True)
print('새 네이버 계정으로 로그인하세요. 창은 닫지 마세요.')
