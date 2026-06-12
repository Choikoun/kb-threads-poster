import sys, json
sys.stdout.reconfigure(encoding='utf-8')
import news_auto_poster as nap

DATA_FILE = sys.argv[1]

with open(DATA_FILE, encoding='utf-8') as f:
    content = json.load(f)

print(f"포스팅 대상: {content['selected_title'][:40]}")

print('이미지 탐색 중...')
search_query = content.get('youtube_keyword', '')
print(f'  YouTube 검색: {search_query}')
img_bytes = nap.get_youtube_thumbnail(search_query)
image_url = None
if img_bytes:
    image_url = nap.upload_to_imgbb(img_bytes)

if not image_url:
    print('이미지 없이 진행')

print('Threads 포스팅 중...')
main_id = nap.post_to_threads(content['main'], content['comments'], image_url)
print(f'완료! 메인 포스트 ID: {main_id}')
