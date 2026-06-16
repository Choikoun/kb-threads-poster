#!/usr/bin/env python3
"""
증여·상속 구조 설계 전문가 포지셔닝 자동 포스팅
뉴스 없이 구조 설계 각도 글을 AI로 생성해서 올림
매주 화요일·목요일 오후 8시 KST 실행
"""
import os, sys, json, re, random, time, requests
from google import genai
from dotenv import load_dotenv
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

TOKEN = os.environ['THREADS_ACCESS_TOKEN']
GEMINI_KEY = os.environ['GEMINI_API_KEY']
BASE = 'https://graph.threads.net/v1.0'
SERIES_FILE = 'series_log.json'


def get_series_number():
    if os.path.exists(SERIES_FILE):
        try:
            with open(SERIES_FILE, encoding='utf-8') as f:
                return json.load(f).get('inheritance_count', 0) + 1
        except Exception:
            pass
    return 1


def increment_series(n):
    data = {}
    if os.path.exists(SERIES_FILE):
        try:
            with open(SERIES_FILE, encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            pass
    data['inheritance_count'] = n
    with open(SERIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

TOPICS = [
    "자녀에게 현금 줄 때 증여냐 차용이냐 — 목적이 뭐냐에 따라 구조가 달라진다",
    "배우자 증여 6억 공제 — 조건을 알고 쓰는 것과 모르고 쓰는 건 다르다",
    "상속 준비는 사망 후가 아니라 생전에 — 그날 이후엔 바꿀 수 있는 게 없다",
    "법인 지분 자녀에게 넘기기 — 방법보다 타이밍과 구조가 먼저다",
    "부동산 증여 vs 상속 — 어느 쪽이 유리한지는 상황마다 다르다",
    "10년 주기 증여 공제 — 알고는 있지만 제대로 쓰는 사람은 드물다",
    "가족 간 돈 거래 — 국세청이 실제로 보는 것은 서류가 아니라 흐름이다",
    "유언장 vs 생전 증여 — 재산을 넘기는 방식이 세금 구조를 결정한다",
    "법인 대표의 은퇴 설계 — 퇴직금·배당·지분 매각 중 무엇을 먼저 써야 하나",
    "부모 사망 후 형제 간 재산 분쟁 — 생전에 설계하지 않으면 법대로 나뉜다",
]

PROMPT_TEMPLATE = """너는 한국 Threads에서 활동하는 증여·상속 구조 설계 전문가야.
이 글은 "증여 설계 이야기" 시리즈의 #{series_num}번째 편이야.
세무사가 아니야. 세금 계산보다 "가족 자산이 누구한테, 언제, 어떻게 가야 하는가"를 미리 설계하는 것이 전문 영역이야.

오늘 주제: {topic}

[핵심 원칙 - 반드시 지켜]
- 전부 반말
- 완전한 답 주지 말 것. 경각심·인사이트·잘못된 상식을 건드리되 "상황마다 달라", "구조가 먼저야"처럼 열어두어 독자 스스로 "내 상황은 어떻게 되지?" 상담 욕구가 생기도록.
- 세금 계산·법 조항 해설보다 "미리 구조를 설계하느냐 못 하느냐의 차이" 부각이 이 계정의 포지셔닝.
- 상담/DM/점검 유도 절대 금지. 화두만 던지고 끝낸다.
- 훅을 첫 줄에 — 반전 사례, 펀치라인, 경각심 중 하나로 시작. 질문이나 흔한 전제로 시작하지 않는다.
- 메인 포스트: 6~10줄. 짧고 강하게.
- 한 줄 15~25자 수준

[포맷 — 아래 중 하나 선택]
반전형: 충격 사실/사례 → 반전 포인트 → 구조 관점 → 묵직한 마무리
감정인용형: 1인칭 공감 인용구 시작 → 현실 반전 → 구체 사실 → 마무리

[댓글]
- 댓글 1: 추가 맥락 (2~3줄)
- 댓글 2: 양자택일형 질문으로 마무리 (예: "A야, B야?") — 2줄, 반말

메인 포스트 마지막 줄 다음에 빈 줄 하나 추가 후 `#증여 #상속` 해시태그 붙여.
메인 포스트 어딘가에 자연스럽게 "증여 설계 이야기 #{series_num}" 을 한 줄로 넣어. 강요하는 느낌 없이 자연스럽게.

JSON만 출력:
{{
  "main": "메인 포스트 텍스트\n\n#증여 #상속",
  "comments": ["댓글1", "댓글2"]
}}"""

def generate(topic, series_num):
    client = genai.Client(api_key=GEMINI_KEY)
    prompt = PROMPT_TEMPLATE.format(topic=topic, series_num=series_num)
    for attempt in range(3):
        try:
            resp = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            m = re.search(r'\{[\s\S]*\}', resp.text.strip())
            if m:
                return json.loads(m.group())
        except Exception as e:
            print(f'생성 오류 (시도 {attempt+1}/3): {e}')
    return None

def post(content):
    r = requests.get(f'{BASE}/me', params={'fields': 'id', 'access_token': TOKEN}, timeout=30)
    uid = r.json()['id']

    r1 = requests.post(f'{BASE}/{uid}/threads',
                       params={'media_type': 'TEXT', 'text': content['main'], 'access_token': TOKEN},
                       timeout=30)
    time.sleep(4)
    r2 = requests.post(f'{BASE}/{uid}/threads_publish',
                       params={'creation_id': r1.json()['id'], 'access_token': TOKEN},
                       timeout=30)
    main_id = r2.json()['id']
    print(f'메인 발행: {main_id}')
    time.sleep(3)

    for i, c in enumerate(content.get('comments', [])):
        rc = requests.post(f'{BASE}/{uid}/threads',
                           params={'media_type': 'TEXT', 'text': c, 'reply_to_id': main_id, 'access_token': TOKEN},
                           timeout=30)
        time.sleep(3)
        rp = requests.post(f'{BASE}/{uid}/threads_publish',
                           params={'creation_id': rc.json()['id'], 'access_token': TOKEN},
                           timeout=30)
        print(f'댓글{i+1} 발행: {rp.json().get("id")}')
        time.sleep(2)

    return main_id

def main():
    topic = random.choice(TOPICS)
    series_num = get_series_number()
    print(f'주제: {topic} (시리즈 #{series_num})')
    content = generate(topic, series_num)
    if not content:
        print('생성 실패')
        return
    print(f'\n메인:\n{content["main"]}\n')
    for i, c in enumerate(content.get('comments', [])):
        print(f'댓글{i+1}:\n{c}\n')
    post(content)
    increment_series(series_num)
    print('완료!')

if __name__ == '__main__':
    main()
