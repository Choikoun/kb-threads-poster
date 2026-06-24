#!/usr/bin/env python3
"""
매일 21:00 KST — 팔로워 수 기록 + 이탈 감지 알림
follower_history.json 공유 (weekly_analysis.py와 동일 파일)
"""
import os, sys, json, requests
from datetime import datetime, timezone, timedelta
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.environ['THREADS_ACCESS_TOKEN']
BASE = 'https://graph.threads.net/v1.0'
KST = timezone(timedelta(hours=9))
HISTORY_FILE = 'follower_history.json'


def get_follower_count(user_id):
    resp = requests.get(f'{BASE}/{user_id}/threads_insights',
                        params={'metric': 'followers_count', 'access_token': TOKEN}, timeout=15)
    if not resp.ok:
        return None
    data = resp.json().get('data', [])
    if not data:
        return None
    return data[0].get('total_value', {}).get('value')


def get_profile_views(user_id):
    """일일 프로필 방문 수 — 상담 링크 유입 간접 측정용"""
    resp = requests.get(f'{BASE}/{user_id}/threads_insights',
                        params={'metric': 'profile_views', 'access_token': TOKEN}, timeout=15)
    if not resp.ok:
        return None
    data = resp.json().get('data', [])
    if not data:
        return None
    return data[0].get('total_value', {}).get('value')


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def create_github_issue(title, body=''):
    gh_token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    repo = os.environ.get('GITHUB_REPOSITORY', 'Choikoun/kb-threads-poster')
    if not gh_token:
        return
    headers = {'Authorization': f'token {gh_token}', 'Accept': 'application/vnd.github+json'}
    requests.post(
        f'https://api.github.com/repos/{repo}/issues',
        headers=headers,
        json={'title': title, 'body': body},
        timeout=30
    )


def main():
    uid = requests.get(f'{BASE}/me', params={'fields': 'id', 'access_token': TOKEN}, timeout=30).json()['id']
    count = get_follower_count(uid)
    if count is None:
        print('팔로워 수 조회 실패')
        return

    today = datetime.now(KST).strftime('%Y-%m-%d')
    history = load_history()

    profile_views = get_profile_views(uid)

    if history and history[-1]['date'] == today:
        prev = history[-1]['followers']
        history[-1]['followers'] = count
        if profile_views is not None:
            history[-1]['profile_views'] = profile_views
    else:
        prev = history[-1]['followers'] if history else count
        entry = {'date': today, 'followers': count}
        if profile_views is not None:
            entry['profile_views'] = profile_views
        history.append(entry)

    if profile_views is not None:
        print(f'프로필 방문: {profile_views}회')

    save_history(history)
    diff = count - prev
    sign = '+' if diff >= 0 else ''
    print(f'팔로워: {count:,}명 ({sign}{diff}명)')

    # 이탈 감지 알림
    if diff <= -2:
        cl_path = 'content_log.json'
        today_date = datetime.now(KST).strftime('%Y-%m-%d')
        today_posts = []
        if os.path.exists(cl_path):
            with open(cl_path, encoding='utf-8-sig') as f:
                cl = json.load(f)
            today_posts = [e for e in cl if e.get('date') == today_date]
        lines = [f'팔로워가 {diff}명 감소했습니다 (현재 {count}명).', '']
        if today_posts:
            lines.append(f'오늘 포스팅 {len(today_posts)}개:')
            for p in today_posts:
                lines.append(f'- [{p.get("category","?")}] {(p.get("selected_title") or "")[:50]}')
        else:
            lines.append('오늘 포스팅 없음')
        create_github_issue(
            f'📉 팔로워 이탈 {abs(diff)}명 — {datetime.now(KST).strftime("%Y-%m-%d %H:%M")} KST',
            '\n'.join(lines)
        )


if __name__ == '__main__':
    main()
