#!/usr/bin/env python3
"""
법인 절세 구조 설계 포스팅 시리즈
매주 월요일 19:00 KST 실행
"""
import os, sys, json, re, random, time, requests
from datetime import datetime, timezone, timedelta
from google import genai
from dotenv import load_dotenv
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

TOKEN = os.environ['THREADS_ACCESS_TOKEN']
GEMINI_KEY = os.environ['GEMINI_API_KEY']
BASE = 'https://graph.threads.net/v1.0'
SERIES_FILE = 'series_log.json'
CONTENT_LOG_FILE = 'content_log.json'
KST = timezone(timedelta(hours=9))


def log_content(post_id, category, format_variant, selected_title):
    log = []
    if os.path.exists(CONTENT_LOG_FILE):
        with open(CONTENT_LOG_FILE, encoding='utf-8') as f:
            log = json.load(f)
    now = datetime.now(KST)
    log.append({
        'post_id': post_id,
        'category': category,
        'format_variant': format_variant,
        'date': now.strftime('%Y-%m-%d'),
        'hour': now.hour,
        'selected_title': selected_title,
    })
    with open(CONTENT_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def get_series_number():
    if os.path.exists(SERIES_FILE):
        try:
            with open(SERIES_FILE, encoding='utf-8') as f:
                return json.load(f).get('corporate_count', 0) + 1
        except Exception:
            pass
    return 1


def get_recent_topics():
    if os.path.exists(SERIES_FILE):
        try:
            with open(SERIES_FILE, encoding='utf-8') as f:
                return json.load(f).get('corporate_recent_topics', [])
        except Exception:
            pass
    return []


def increment_series(n, topic):
    data = {}
    if os.path.exists(SERIES_FILE):
        try:
            with open(SERIES_FILE, encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            pass
    data['corporate_count'] = n
    recent = data.get('corporate_recent_topics', [])
    if topic in recent:
        recent.remove(topic)
    recent.append(topic)
    data['corporate_recent_topics'] = recent[-5:]
    all_topics = data.get('corporate_all_topics', [])
    all_topics.append(topic)
    data['corporate_all_topics'] = all_topics
    with open(SERIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


TOPICS = [
    "가지급금 — 없애는 방법보다 왜 생겼는지부터 봐야 한다",
    "법인 대표 퇴직금 — 아무 때나 쓰는 게 아니라 구조를 잡고 써야 한다",
    "배당 vs 급여 — 어느 쪽이 유리한지는 세율 표가 아니라 내 구조가 결정한다",
    "법인 보험 — 비용 처리되는 구조와 그냥 드는 구조는 다르다",
    "차명주식 — 해결하려다 더 큰 문제 만드는 경우가 있다",
    "지분 분산 설계 — 자녀에게 언제 어떻게 넘기느냐가 세금을 가른다",
    "법인 부동산 — 법인 명의로 사는 게 항상 유리한 건 아니다",
    "법인 청산 vs 폐업 — 대표가 모르면 세금 폭탄으로 끝난다",
    "개인사업자 법인 전환 — 타이밍을 놓치면 절세 효과가 반감된다",
    "법인 대출 — 사업 자금과 투자 자금을 섞으면 나중에 문제가 생긴다",
    "임원 보수 설계 — 너무 많아도, 너무 적어도 리스크가 있다",
    "법인 이익잉여금 — 쌓아두기만 하면 결국 세금으로 나간다",
    "정관 변경, 대표이사 혼자 하던 시대는 끝났다 — 임원보수규정엔 의결권이 없다",
    "가업승계, 방법이 네 가지인데 어떤 걸 쓰느냐가 결과를 가른다",
]

PROMPT_TEMPLATE = """너는 한국 Threads에서 활동하는 법인 절세 구조 설계 전문가야.
이 글은 "법인 절세 이야기" 시리즈의 #{series_num}번째 편이야.
세무사가 아니야. 세금 신고보다 "법인 구조를 어떻게 설계하느냐가 절세를 결정한다"가 이 계정의 각도야.
세금을 줄이는 것조차 목적이 아니라 도구야. 진짜 목적은 사업주가 원하는 결과(승계, 매각, 동업 정리, 은퇴 후 정리 등)를 이루는 것 — 법인·지분·급여 구조는 그 결과를 만드는 수단일 뿐이라는 관점이 이 계정의 핵심 차별점.

오늘 주제: {topic}

[핵심 원칙 - 반드시 지켜]
- 전부 반말
- 완전한 답 주지 말 것. 경각심·인사이트를 건드리되 "상황마다 달라", "구조가 먼저야"처럼 열어두어 독자 스스로 "내 법인은 어떻게 되지?" 상담 욕구가 생기도록. (단, 디테일풀이형을 선택했을 때는 예외 — 아래 참고)
- 상담/DM/점검 유도 절대 금지. 화두만 던지고 끝낸다.
- 훅을 첫 줄에 — 반전 사례, 펀치라인, 경각심 중 하나로 시작. 질문이나 흔한 전제로 시작하지 않는다.
- 한 줄 = 한 문장 or 핵심 단어구. 절대로 한 줄에 두 문장 붙이지 않는다.
- 연속 2줄 이상이면 무조건 빈 줄 하나 삽입.
- 숫자·핵심 사실은 단독 줄에 배치.
- 이모지: 전체 1~2개. 핵심 줄 앞이나 단락 구분용으로만.
- 메인 포스트: 6~10줄. (디테일풀이형은 예외 — 최대 18줄까지 허용)

[포맷 — 아래 중 하나 선택]
반전형: 충격 사실/사례 → 반전 포인트 → 구조 관점 → 묵직한 마무리
사례형: 구체적 상황·사례 → 반전 → 구조 관점 → 묵직한 마무리
디테일풀이형: 오늘 주제와 관련된 구체적 숫자 시나리오를 직접 만들어서(예: "지분 60:20:20으로 나뉜 법인의 임원보수 의결권은") 끝까지 계산·전개해서 정확한 답을 준다. 지분 구조나 금액 같은 표 형태 정보는 줄글로 풀어서 표현한다. 필요하면 법조항을 인용해도 좋다. 이 포맷에서는 "완전한 답 주지 말 것" 원칙을 적용하지 않음 — 오히려 정확한 숫자·계산 과정으로 전문성을 보여주는 게 목적. 다만 마지막 한 줄에 "조건이 달라지면 결과도 달라진다"는 취지를 자연스럽게 넣어 이 사례가 모든 상황에 적용되는 건 아님을 알린다. 주제가 구체적 계산에 안 맞으면 이 포맷을 선택하지 않는다 — 전체 편 중 20~30% 정도 빈도로만 사용.

[댓글]
- 댓글 1: 추가 맥락 (2~3줄, 반말)
- 댓글 2: 양자택일형 질문으로 마무리 — 2줄, 반말 (예: "지금 이 구조야, 아직 안 잡았어?")
{cross_promo_block}
메인 포스트 마지막 줄 다음에 빈 줄 하나 추가 후 `#법인 #절세` 해시태그 붙여.
메인 포스트 어딘가에 자연스럽게 "법인 절세 이야기 #{series_num}" 을 한 줄로 넣어. 강요하는 느낌 없이.

JSON만 출력:
{{
  "main": "메인 포스트 텍스트\n\n#법인 #절세",
  "comments": ["댓글1", "댓글2"]
}}"""


CROSS_PROMO_BLOCK = '''
[추가 댓글 - 인스타 크로스 프로모션]
위 댓글들 다음에 댓글을 1개 더 추가해.
인스타그램에도 카드뉴스·릴스로 콘텐츠를 올리고 있다는 걸 자연스럽게 언급하는 한 줄.
반말. "인스타에도 카드뉴스로 정리해서 올려. 거기서도 보고 싶으면 팔로우해놔" 같은 식으로 자연스럽게 변형. 매번 같은 문구 반복하지 않는다.
"@계정명" 같은 핸들은 만들어내지 않는다.
'''


def generate(topic, series_num):
    client = genai.Client(api_key=GEMINI_KEY)
    cross_promo_block = CROSS_PROMO_BLOCK if random.random() < 0.12 else ''
    prompt = PROMPT_TEMPLATE.format(topic=topic, series_num=series_num, cross_promo_block=cross_promo_block)
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


def post(content):
    r = requests.get(f'{BASE}/me', params={'fields': 'id', 'access_token': TOKEN}, timeout=30)
    uid = r.json()['id']

    r1 = requests.post(f'{BASE}/{uid}/threads',
                       params={'media_type': 'TEXT', 'text': content['main'],
                               'content_warning_type': 'SENSITIVE_MEDIA', 'access_token': TOKEN},
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
    recent_topics = get_recent_topics()
    weights = [1 if t in recent_topics else 5 for t in TOPICS]
    topic = random.choices(TOPICS, weights=weights, k=1)[0]
    series_num = get_series_number()
    print(f'주제: {topic} (시리즈 #{series_num})')
    content = generate(topic, series_num)
    if not content:
        print('생성 실패')
        return
    print(f'\n메인:\n{content["main"]}\n')
    for i, c in enumerate(content.get('comments', [])):
        print(f'댓글{i+1}:\n{c}\n')
    main_id = post(content)
    log_content(main_id, 'corporate', 'series', topic)
    increment_series(series_num, topic)
    print('완료!')


if __name__ == '__main__':
    main()
