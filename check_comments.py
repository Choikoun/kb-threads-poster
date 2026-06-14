import sys, os, time, requests
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()

token = os.environ.get('THREADS_ACCESS_TOKEN')
BASE = 'https://graph.threads.net/v1.0'
SELF = 'financial_planner0'
MAX_DEPTH = 6  # 답글 스레드 최대 탐색 깊이 (대화 핑퐁 여러 번까지 추적)


def api_get(url, params, retries=2):
    for attempt in range(retries + 1):
        try:
            return requests.get(url, params=params, timeout=30).json()
        except requests.exceptions.RequestException:
            if attempt == retries:
                raise
            time.sleep(2)


def get_replies(comment_id):
    data = api_get(f'{BASE}/{comment_id}/replies',
        {'fields': 'id,text,username,timestamp', 'access_token': token})
    return data.get('data', [])


def collect_unanswered(comment, depth=0):
    """comment는 외부 사용자의 댓글. 우리가 답글을 안 달았으면 그대로 반환,
    답글을 달았으면 그 답글에 달린 추가 외부 댓글을 재귀로 탐색."""
    if depth >= MAX_DEPTH:
        return [comment]
    own = [c for c in get_replies(comment['id']) if c.get('username') == SELF]
    if not own:
        return [comment]
    unanswered = []
    for o in own:
        for grandchild in get_replies(o['id']):
            if grandchild.get('username') != SELF:
                unanswered.extend(collect_unanswered(grandchild, depth + 1))
    return unanswered


user_id = api_get(f'{BASE}/me', {'access_token': token}).get('id')
resp = api_get(f'{BASE}/{user_id}/threads',
    {'fields': 'id,text,timestamp', 'limit': 50, 'access_token': token})
posts = resp.get('data', [])

found = False
for post in posts:
    pid = post['id']
    ext_top = [r for r in get_replies(pid) if r.get('username') != SELF]

    unanswered = []
    for e in ext_top:
        unanswered.extend(collect_unanswered(e))

    if unanswered:
        found = True
        ts = post.get('timestamp', '')[:10]
        preview = post.get('text', '')[:35].replace('\n', ' ')
        print(f'[{ts}] {preview}')
        for r in unanswered:
            uname = r.get('username', '')
            rts = r.get('timestamp', '')[:10]
            txt = r.get('text', '')[:60].replace('\n', ' ')
            print(f'  id={r.get("id")} @{uname} ({rts}): {txt}')
        print()

if not found:
    print('새 외부 댓글 없음.')
