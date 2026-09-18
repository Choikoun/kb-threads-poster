#!/usr/bin/env python3
"""블로그용 Pexels 실사 이미지 2장 다운로드 (1회성)"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()

from stock_card_poster import search_pexels_photo

OUT_DIR = 'blog_images/2026-09-18_연금보험-가입시기-비교'

p1 = search_pexels_photo('senior couple reviewing documents finances home',
                          output_path=f'{OUT_DIR}/01_대표이미지_실사.jpg', orientation='portrait')
print('hero:', p1)

p2 = search_pexels_photo('senior couple sunset dock embrace tranquil',
                          output_path=f'{OUT_DIR}/05_클로징삽화_실사.jpg', orientation='portrait')
print('closing:', p2)
