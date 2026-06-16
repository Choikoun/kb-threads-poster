#!/usr/bin/env python3
"""
일요일 슬롯 — 이번 주 조회수 1위 글을 짧게 재소개
매주 일요일 10:00 KST 실행
수요일 repost_top.py(전체 재발행)와 다르게, 첫 2줄 미리보기만 보여줌
"""
import os, sys, json, time, requests
from datetime import datetime, timezone, timedelta
sys.stdout.reconfigure(encoding='utf-8')

TOKEN = os.environ['THREADS_ACCESS_TOKEN']
BASE = 'https://graph.threads.net/v1.0'
KST = timezone(timedelta(hours=9))
CONTENT_LOG = 'content_log.json'


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
    if not os.path.exists(CONTENT_LOG):
        print('content_log.json 없음')
        return

    with open(CONTENT_LOG, encoding='utf-8') as f:
        logs = json.load(f)

    cutoff = (datetime.now(KST) - timedelta(days=7)).strftime('%Y-%m-%d')
    recent = [p for p in logs if p.get('date', '') >= cutoff and p.get('post_id')]

    if not recent:
        print('이번 주 포스트 없음')
        return

    print(f'이번 주 후보 {len(recent)}개 — 조회수 조회 중...')
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

    print(f'\n이번 주 1위: {best["date"]} | {best_views:,}회')

    original = get_post_text(best['post_id'])
    if not original:
        print('원문 조회 실패')
        return

    # 첫 2줄만 미리보기 (해시태그 줄 제외)
    lines = [l for l in original.split('\n') if l.strip() and not l.startswith('#')]
    preview = '\n'.join(lines[:2])

    recap_text = f'이번 주 제일 많이 본 글이야.\n\n{preview}\n\n#증여 #상속'

    uid = requests.get(f'{BASE}/me', params={'fields': 'id', 'access_token': TOKEN}, timeout=30).json()['id']
    r1 = requests.post(f'{BASE}/{uid}/threads',
                       params={'media_type': 'TEXT', 'text': recap_text, 'access_token': TOKEN}, timeout=30)
    time.sleep(4)
    r2 = requests.post(f'{BASE}/{uid}/threads_publish',
                       params={'creation_id': r1.json()['id'], 'access_token': TOKEN}, timeout=30)
    print(f'일요일 요약 발행 완료: {r2.json().get("id")}')


if __name__ == '__main__':
    main()
