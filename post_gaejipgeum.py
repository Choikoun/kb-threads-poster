#!/usr/bin/env python3
import os, sys, time, requests
sys.stdout.reconfigure(encoding='utf-8')

TOKEN = os.environ['THREADS_ACCESS_TOKEN']
BASE = 'https://graph.threads.net/v1.0'

main_text = """가지급금 없애는 방법만 찾다가
더 큰 문제 만든 거 봤어.

방법은 여러 개야.
근데 어떤 방법이 맞는지는
왜 생겼는지부터 봐야 해.

가지급금은 증상이야.
원인이 뭔지 먼저야."""

comments = [
    "가지급금 많은 법인,\n세무조사에서 집중적으로 보는 항목 중 하나야.\n방치하면 이자 계산에 상여 처리까지 붙어.",
    "지금 법인에 가지급금 있어?\n오래된 거야, 최근에 생긴 거야?"
]

me = requests.get(f'{BASE}/me', params={'fields': 'id', 'access_token': TOKEN}, timeout=30)
UID = me.json()['id']

r1 = requests.post(f'{BASE}/{UID}/threads', params={'media_type': 'TEXT', 'text': main_text, 'access_token': TOKEN}, timeout=30)
time.sleep(4)
r2 = requests.post(f'{BASE}/{UID}/threads_publish', params={'creation_id': r1.json()['id'], 'access_token': TOKEN}, timeout=30)
main_id = r2.json()['id']
print(f'메인 발행: {main_id}')
time.sleep(3)

for i, c in enumerate(comments):
    rc = requests.post(f'{BASE}/{UID}/threads', params={'media_type': 'TEXT', 'text': c, 'reply_to_id': main_id, 'access_token': TOKEN}, timeout=30)
    time.sleep(3)
    rp = requests.post(f'{BASE}/{UID}/threads_publish', params={'creation_id': rc.json()['id'], 'access_token': TOKEN}, timeout=30)
    print(f'댓글{i+1} 발행: {rp.json().get("id")}')
    time.sleep(2)

print('완료!')
