#!/usr/bin/env python3
"""
월간 하이라이트 — 매월 1일에 전달 TOP3 포스트 자동 발행
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
    now = datetime.now(KST)
    first_this_month = now.replace(day=1)
    last_month_end = first_this_month - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    start_str = last_month_start.strftime('%Y-%m-%d')
    end_str = last_month_end.strftime('%Y-%m-%d')
    month_label = last_month_start.strftime('%m월')

    if not os.path.exists(CONTENT_LOG):
        print('content_log.json 없음')
        return

    with open(CONTENT_LOG, encoding='utf-8') as f:
        logs = json.load(f)

    monthly = [p for p in logs
               if start_str <= p.get('date', '') <= end_str and p.get('post_id')]

    if len(monthly) < 3:
        print(f'{month_label} 포스트 {len(monthly)}개 — TOP3 미충족, 건너뜀')
        return

    print(f'{month_label} 후보 {len(monthly)}개 — 조회수 조회 중...')
    scored = []
    for p in monthly:
        v = get_views(p['post_id'])
        print(f"  {p['date']} | {v:,}회 | {p.get('selected_title', '')[:30]}")
        scored.append((v, p))
        time.sleep(0.5)

    top3 = sorted(scored, key=lambda x: x[0], reverse=True)[:3]

    previews = []
    for rank, (views, p) in enumerate(top3, 1):
        title = p.get('selected_title', '')
        if not title:
            text = get_post_text(p['post_id'])
            title = text.split('\n')[0][:25] if text else ''
        previews.append(f'{rank}위.  {title[:25]}')
        time.sleep(0.3)

    post_text = (
        f"{month_label} 반응 제일 좋았던 글이야.\n\n"
        + '\n'.join(previews)
        + '\n\n읽었던 거 있어?\n\n#증여 #상속'
    )

    uid = requests.get(
        f'{BASE}/me', params={'fields': 'id', 'access_token': TOKEN}, timeout=30
    ).json()['id']

    r1 = requests.post(f'{BASE}/{uid}/threads',
                       params={'media_type': 'TEXT', 'text': post_text, 'access_token': TOKEN},
                       timeout=30)
    time.sleep(4)
    r2 = requests.post(f'{BASE}/{uid}/threads_publish',
                       params={'creation_id': r1.json()['id'], 'access_token': TOKEN},
                       timeout=30)
    print(f'{month_label} 하이라이트 발행 완료: {r2.json().get("id")}')


if __name__ == '__main__':
    main()
