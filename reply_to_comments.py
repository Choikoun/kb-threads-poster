"""
외부 댓글에 답글 게시 (재사용 스크립트)
사용법: python reply_to_comments.py replies.json
replies.json = [{"comment_id": "...", "text": "..."}, ...]
"""
import sys, os, json, time, requests
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()

BASE = 'https://graph.threads.net/v1.0'
token = os.environ.get('THREADS_ACCESS_TOKEN')

DATA_FILE = sys.argv[1]
with open(DATA_FILE, encoding='utf-8') as f:
    items = json.load(f)

user_id = requests.get(f'{BASE}/me', params={'access_token': token}, timeout=15).json().get('id')

for item in items:
    rc = requests.post(f'{BASE}/{user_id}/threads', params={
        'media_type': 'TEXT',
        'text': item['text'],
        'reply_to_id': item['comment_id'],
        'access_token': token
    }, timeout=30)
    creation_id = rc.json().get('id')
    if not creation_id:
        print(f"컨테이너 생성 실패 ({item['comment_id']}): {rc.json()}")
        continue
    time.sleep(3)
    rp = requests.post(f'{BASE}/{user_id}/threads_publish',
        params={'creation_id': creation_id, 'access_token': token}, timeout=30)
    print(f"답글 게시 완료: {rp.json().get('id')} (원댓글 {item['comment_id']})")
    time.sleep(2)
