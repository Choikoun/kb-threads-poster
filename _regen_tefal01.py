import sys; sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from stock_card_poster import search_pexels_photo
OUT='blog_images/shop_2026-11-04_데팔후라이팬'
print(search_pexels_photo('frying pan on induction stove cooking', output_path=f'{OUT}/01_데팔후라이팬_대표이미지.jpg', orientation='landscape'))
