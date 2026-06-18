#!/usr/bin/env python3
"""
최근 포스팅 댓글 감지 — 새 댓글 발견 시 GitHub Issue 생성
매일 09:00 KST 실행
"""
import os, sys, json, time, requests
from datetime import datetime, timezone, timedelta
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.environ['THREADS_ACCESS_TOKEN']
BASE = 'https://graph.threads.net/v1.0'
KST = timezone(timedelta(hours=9))
COMMENT_LOG_FILE = 'comment_log.json'


def get_my_info():
    resp = requests.get(f'{BASE}/me', params={'fields': 'id,username', 'access_token': TOKEN}, timeout=30)
    data = resp.json()
    return data.get('id'), data.get('username', '')


def get_my_posts(uid):
    resp = requests.get(f'{BASE}/{uid}/threads',
                        params={'fields': 'id,text,timestamp', 'limit': 30, 'access_token': TOKEN},
                        timeout=30)
    if not resp.ok:
        return []
    return resp.json().get('data', [])


def get_conversation(post_id):
    resp = requests.get(f'{BASE}/{post_id}/conversation',
                        params={'fields': 'id,text,username,timestamp', 'access_token': TOKEN},
                        timeout=30)
    if not resp.ok:
        return []
    return resp.json().get('data', [])


def load_comment_log():
    if os.path.exists(COMMENT_LOG_FILE):
        with open(COMMENT_LOG_FILE, encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_comment_log(data):
    with open(COMMENT_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def create_github_issue(title, body=''):
    gh_token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    repo = os.environ.get('GITHUB_REPOSITORY', 'Choikoun/kb-threads-poster')
    if not gh_token:
        print('GH_TOKEN 없음 — Issue 생성 건너뜀')
        return
    headers = {'Authorization': f'token {gh_token}', 'Accept': 'application/vnd.github+json'}
    r = requests.post(
        f'https://api.github.com/repos/{repo}/issues',
        headers=headers,
        json={'title': title, 'body': body},
        timeout=30
    )
    if r.ok:
        print(f'Issue 생성: {r.json().get("html_url")}')
    else:
        print(f'Issue 생성 실패: {r.status_code} {r.text[:100]}')


def main():
    uid, my_username = get_my_info()
    if not uid:
        print('계정 조회 실패')
        return

    posts = get_my_posts(uid)
    if not posts:
        print('포스팅 조회 실패')
        return

    comment_log = load_comment_log()
    new_comments_found = []

    for post in posts:
        post_id = post['id']
        post_text = post.get('text', '')[:40].replace('\n', ' ')

        conversation = get_conversation(post_id)
        time.sleep(0.3)

        seen = set(comment_log.get(post_id, []))
        new_in_post = []

        for reply in conversation:
            cid = reply.get('id')
            username = reply.get('username', '')
            # 내 답글은 제외
            if not cid or username == my_username:
                continue
            if cid not in seen:
                new_in_post.append(reply)
                seen.add(cid)

        if new_in_post:
            comment_log[post_id] = list(seen)
            for c in new_in_post:
                new_comments_found.append({
                    'post_id': post_id,
                    'post_text': post_text,
                    'comment_id': c.get('id'),
                    'username': c.get('username', '?'),
                    'text': c.get('text', ''),
                    'timestamp': c.get('timestamp', ''),
                })

    if new_comments_found:
        today = datetime.now(KST).strftime('%Y-%m-%d %H:%M')
        title = f'💬 새 댓글 {len(new_comments_found)}개 — {today} KST'
        lines = []
        for c in new_comments_found:
            ts = c['timestamp'][:16].replace('T', ' ') if c['timestamp'] else '?'
            lines.append(f'**@{c["username"]}** ({ts})')
            lines.append(f'> {c["text"][:300]}')
            lines.append(f'원글: {c["post_text"]}...')
            lines.append('')
        body = '\n'.join(lines)
        create_github_issue(title, body)
        print(f'새 댓글 {len(new_comments_found)}개 감지 → Issue 생성')
    else:
        print('새 댓글 없음')

    save_comment_log(comment_log)


if __name__ == '__main__':
    main()
