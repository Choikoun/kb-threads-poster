#!/usr/bin/env python3
"""
지난 30일 포스트 중 조회수 1위를 자동 재발행
매주 수요일 오후 8시 KST 실행
"""
import os, sys, json, time, requests
from datetime import datetime, timezone, timedelta
sys.stdout.reconfigure(encoding='utf-8')

TOKEN = os.environ['THREADS_ACCESS_TOKEN']
BASE = 'https://graph.threads.net/v1.0'
KST = timezone(timedelta(hours=9))
CONTENT_LOG = 'content_log.json'

def get_uid():
    r = requests.get(f'{BASE}/me', params={'fields': 'id', 'access_token': TOKEN}, timeout=30)
    return r.json()['id']

def get_views(post_id):
    try:
        r = requests.get(f'{BASE}/{post_id}/insights',
                         params={'metric': 'views', 'access_token': TOKEN}, timeout=15)
        data = r.json().get('data', [])
        if data:
            return data[0].get('values', [{}])[0].get('value', 0)
    except Exception:
        pass
    return 0

def get_post_text(post_id):
    try:
        r = requests.get(f'{BASE}/{post_id}',
                         params={'fields': 'text', 'access_token': TOKEN}, timeout=15)
        return r.json().get('text', '')
    except Exception:
        return ''

def main():
    with open(CONTENT_LOG, encoding='utf-8') as f:
        logs = json.load(f)

    cutoff = (datetime.now(KST) - timedelta(days=30)).strftime('%Y-%m-%d')
    recent = [p for p in logs if p.get('date', '') >= cutoff and p.get('post_id')]

    if not recent:
        print('재발행 후보 없음')
        return

    print(f'후보 {len(recent)}개 — 조회수 조회 중...')
    best, best_views = None, 0
    for p in recent:
        v = get_views(p['post_id'])
        print(f"  {p['date']} | {v:,}회 | {p.get('selected_title', '')[:30]}")
        if v > best_views:
            best_views, best = v, p
        time.sleep(0.5)

    if not best:
        print('조회수 데이터 없음')
        return

    print(f'\n1위: {best["date"]} | {best_views:,}회 | {best.get("selected_title", "")}')

    original_text = get_post_text(best['post_id'])
    if not original_text:
        print('원문 조회 실패')
        return

    repost_text = f"지난달 반응 좋았던 글 다시 공유해.\n\n{original_text}"

    uid = get_uid()
    r1 = requests.post(f'{BASE}/{uid}/threads',
                       params={'media_type': 'TEXT', 'text': repost_text, 'access_token': TOKEN},
                       timeout=30)
    time.sleep(4)
    r2 = requests.post(f'{BASE}/{uid}/threads_publish',
                       params={'creation_id': r1.json()['id'], 'access_token': TOKEN},
                       timeout=30)
    print(f'재발행 완료: {r2.json().get("id")}')

if __name__ == '__main__':
    main()
