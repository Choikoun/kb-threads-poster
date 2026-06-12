import sys, requests, os
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()

token = os.environ.get('THREADS_ACCESS_TOKEN')
BASE = 'https://graph.threads.net/v1.0'
user_id = requests.get(f'{BASE}/me', params={'access_token': token}, timeout=15).json().get('id')

resp = requests.get(f'{BASE}/{user_id}/threads',
    params={'fields': 'id,text,timestamp', 'limit': 50, 'access_token': token}, timeout=15)
posts = resp.json().get('data', [])

found = False
for post in posts:
    pid = post['id']
    rr = requests.get(f'{BASE}/{pid}/replies',
        params={'fields': 'id,text,username,timestamp', 'access_token': token}, timeout=15)
    ext = [r for r in rr.json().get('data', []) if r.get('username') != 'financial_planner0']
    if ext:
        found = True
        ts = post.get('timestamp', '')[:10]
        preview = post.get('text', '')[:35].replace('\n', ' ')
        print(f'[{ts}] {preview}')
        for r in ext:
            uname = r.get('username', '')
            rts = r.get('timestamp', '')[:10]
            txt = r.get('text', '')[:60].replace('\n', ' ')
            print(f'  @{uname} ({rts}): {txt}')
        print()

if not found:
    print('새 외부 댓글 없음.')
