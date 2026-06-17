#!/usr/bin/env python3
import os, sys, time, requests
sys.stdout.reconfigure(encoding='utf-8')

TOKEN = os.environ['THREADS_ACCESS_TOKEN']
BASE = 'https://graph.threads.net/v1.0'

main_text = """"돌아가시면 그때 가서 알아보면 되지."

이 말이 상속에서 제일 비싸.

상속세는 돌아가신 날 기준으로 계산해.
그날 이후로는 바꿀 수 있는 게 없어.

준비할 시간이 있을 때
구조를 먼저 봐야 해."""

comments = [
    "상속은 사건이 아니야.\n오랫동안 쌓인 구조의 결과야.\n사망 이후에 할 수 있는 건 생각보다 많지 않아.",
    "지금 부모님 자산 구조,\n파악하고 있어, 못 하고 있어?"
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
