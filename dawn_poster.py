#!/usr/bin/env python3
"""
새벽 슬롯 06:00 KST — 3~4줄 짧은 구조 설계 인사이트 포스팅
07:30 뉴스 슬롯과 다르게 시사가 아닌 '타임리스 원칙' 각도
"""
import os, sys, json, re, random, time, requests
sys.stdout.reconfigure(encoding='utf-8')
from google import genai
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.environ['THREADS_ACCESS_TOKEN']
GEMINI_KEY = os.environ['GEMINI_API_KEY']
BASE = 'https://graph.threads.net/v1.0'

TOPICS = [
    '증여는 금액이 아니라 시점이 핵심이다',
    '법인 대표가 돈을 꺼내는 방법은 세 가지인데 세금이 전부 다르다',
    '상속은 죽은 뒤의 일이 아니라 살아있을 때 결정된다',
    '차용증보다 중요한 건 왜 빌리는지다',
    '배우자 증여 6억은 조건을 알아야 쓸 수 있다',
    '10년 주기 증여 공제는 시작이 빠를수록 유리하다',
    '가족 간 돈 거래에서 국세청이 보는 건 서류가 아니라 흐름이다',
    '부동산을 증여할지 상속할지는 지금 상황이 결정한다',
    '유언장이 없으면 법대로 나뉜다는 말의 진짜 의미',
    '법인 지분을 자녀에게 넘길 때 방법보다 타이밍이 먼저다',
    '퇴직금 설계는 대표가 재직 중일 때만 가능하다',
    '상속세는 사망일 기준으로 계산된다 — 그날 이후엔 바꿀 수 없다',
]

PROMPT = """너는 한국 Threads에서 활동하는 증여·상속 구조 설계 전문가야.

오늘 새벽 주제: {topic}

아주 짧은 인사이트 포스팅을 써줘.

[원칙]
- 전부 반말
- 3~4줄, 군더더기 없이
- 뉴스·사례 없이 원칙 하나를 선명하게
- 첫 줄이 훅 — 반전이나 경각심
- 완전한 답 주지 말 것. 독자 스스로 "내 상황은 어때?" 생각하게 열어두기
- 상담/링크 유도 금지
- 마지막에 빈 줄 + `#증여 #상속`

JSON만 출력:
{{"main": "포스트 텍스트\\n\\n#증여 #상속"}}"""


def generate(topic):
    client = genai.Client(api_key=GEMINI_KEY)
    prompt = PROMPT.format(topic=topic)
    for attempt in range(3):
        try:
            resp = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            m = re.search(r'\{[\s\S]*\}', resp.text.strip())
            if m:
                return json.loads(m.group())
        except Exception as e:
            print(f'생성 오류 (시도 {attempt+1}/3): {e}')
            time.sleep(3)
    return None


def main():
    topic = random.choice(TOPICS)
    print(f'주제: {topic}')
    content = generate(topic)
    if not content:
        print('생성 실패')
        return

    print(f'\n{content["main"]}\n')

    uid = requests.get(f'{BASE}/me', params={'fields': 'id', 'access_token': TOKEN}, timeout=30).json()['id']
    r1 = requests.post(f'{BASE}/{uid}/threads',
                       params={'media_type': 'TEXT', 'text': content['main'], 'content_warning_type': 'SENSITIVE_MEDIA', 'access_token': TOKEN}, timeout=30)
    time.sleep(4)
    r2 = requests.post(f'{BASE}/{uid}/threads_publish',
                       params={'creation_id': r1.json()['id'], 'access_token': TOKEN}, timeout=30)
    print(f'새벽 포스팅 완료: {r2.json().get("id")}')


if __name__ == '__main__':
    main()
