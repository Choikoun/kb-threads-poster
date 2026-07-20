#!/usr/bin/env python3
"""
주간 시리즈: "이번 주 사업주들이 물어본 것"
매주 금요일 저녁 게시 - 구독할 이유를 만드는 고정 시리즈 포맷
회차 번호로 누적 (김진숙 "금요일의 보상" 196회차 스타일 참고, 2026-06-20) — 질문 1개로 단순화
"""
import os, sys, json, re, random
from google import genai
from dotenv import load_dotenv
import news_auto_poster as nap  # post_to_threads, get_trend_headlines 재사용

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

GEMINI_KEY = os.getenv('GEMINI_API_KEY')
QA_LOG = 'qa_series_log.json'

SERIES_CROSS_REF_BLOCK = '''
[추가 댓글 - 다른 시리즈 교차 언급]
위 댓글 다음에 댓글을 1개 더 추가해.
"증여 설계 이야기"나 "법인 절세 이야기" 시리즈도 따로 올리고 있다는 걸 자연스럽게 한 줄로 언급
(이번 회차 주제와 더 어울리는 쪽 하나만 골라서). 반말. 구체적 회차 번호는 언급하지 않는다.
'''


def get_episode_number():
    if os.path.exists(QA_LOG):
        try:
            with open(QA_LOG, encoding='utf-8') as f:
                return json.load(f).get('qa_count', 0) + 1
        except Exception:
            pass
    return 1


def save_episode_number(n):
    with open(QA_LOG, 'w', encoding='utf-8') as f:
        json.dump({'qa_count': n}, f, ensure_ascii=False, indent=2)


def generate_content(episode_num):
    client = genai.Client(api_key=GEMINI_KEY)
    trends = nap.get_trend_headlines(limit=8)
    series_cross_ref_block = SERIES_CROSS_REF_BLOCK if random.random() < 0.15 else ''

    prompt = f"""너는 한국 Threads에서 활동하는 법인·세금·자산 설계 전문가야.
매주 올리는 시리즈 포스팅을 작성해줘. 시리즈 제목은 "이번 주 사업주들이 물어본 것"이고 이번이 {episode_num}회차야.

[이번 주 핵심 이슈 - 참고만, 아래 타겟에 안 맞으면 무시하고 일반적인 사업주 FAQ로 대체]
{trends}

[질문 소재 타겟 - 반드시 이 범위 안에서만]
법인 운영, 법인세·종합소득세 등 세금, 가지급금/배당/임원보수,
정책·세법 개정이 사업과 자산에 미치는 영향, 자산 운용·증여·상속 구조.
"AI주 급등락", "특정 종목 단타" 같은 일반 투자 얘기는 다루지 않는다.

[참고 - 가능하면 이런 결의 질문도 환영]
이 계정의 역대 최고 성과들은 "당연시되는 헌신과 실제 보상의 불일치"를 건드린 질문이었다 —
가족 쪽으로는 효도·간병 vs 상속 분배, 사업 쪽으로는 동업자 관계(친구라서 시작했는데 친구라서
못 끝내는 딜레마, 신의성실 의무 위반) 같은 것. 이번 주 질문 소재에 이런 결이 자연스럽게
있다면 적극적으로 살려라(억지로 끌어오지는 말 것).

[핵심 원칙 - 반드시 지켜]
- 전부 반말. 마지막 문장도 반말 (예외 없음)
- 한 줄 15~25자 수준. 자연스러운 문장 단위로 끊는다.
- 아이디어 바뀔 때 빈 줄 삽입 (가독성)
- 자극적이되 공격적이지 않게. "도박꾼", "쪽박", "~하면 끝장" 같은 독자를 비하하거나
  몰아붙이는 표현은 절대 쓰지 않는다. 담담하게, 사실과 구조로 설득한다.
- "상담받으세요", "DM 주세요", "점검해보세요" 같은 직접적 유도 표현 금지
- 특정 종목·자산의 매수/매도/매매 타이밍을 지시하거나 추천하지 않는다 (미등록 투자자문 리스크). 구조적 인식까지만 다루고 투자행동 지시는 하지 않는다.
- 완전한 답 주지 말 것. 경각심·인사이트·잘못된 상식을 건드리되 "상황마다 달라", "구조가 먼저야"처럼 열어두어 독자 스스로 "내 상황은 어떻게 되지?" 상담 욕구가 생기도록.
- 세금 계산·법 조항 해설보다 "미리 구조를 설계하느냐 못 하느냐의 차이" 부각이 이 계정의 포지셔닝.
- 팔로우 유도 시 "@계정명" 같은 계정 핸들을 절대 만들어내지 않는다. "팔로우해두면 놓치지 않아"처럼 핸들 없이 표현한다.
- 본문에 실명·서명 절대 사용 금지. 신원 특정 가능한 정보 노출 불가.

[메인 포스트 구조 - 질문 1개로 단순하게]
1. 시리즈 인트로 1줄 - "이번 주 사업주들이 많이 물어본 거 #{episode_num}" 같은 톤으로,
   매주 거의 동일한 인사말 + 회차 번호로 시작해서 시리즈처럼 느껴지게
↵빈줄
2. 질문 1개 - "OOO 하더라고요" / "OOO 이러더라" 식으로 실제 사업주가 한 말처럼 인용
↵빈줄
3. 그 질문에 대한 반전 또는 핵심 포인트 2~3줄
↵빈줄
4. 마지막 줄: 팔로우 유도 한 줄. "이런 거 매주 정리해서 올릴 거야. 팔로우해두면 놓치지 않아" 같은
   톤으로, 반말. 매주 비슷한 문구 반복해도 됨 (시리즈 시그니처처럼).

[댓글 구조 - 1개]
- 댓글1 (마지막): 위 질문과 이어지는 양자택일형 질문으로 마무리 (예: "지금 이 구조야, 아직 안 잡았어?") — 2줄, 반말
{series_cross_ref_block}
JSON만 출력:
{{
  "main": "메인 포스트 텍스트",
  "comments": ["댓글1"]
}}"""

    for attempt in range(3):
        try:
            resp = client.models.generate_content(
                model='gemini-flash-latest',
                contents=prompt
            )
            raw = resp.text.strip()
            m = re.search(r'\{[\s\S]*\}', raw)
            if m:
                return json.loads(m.group())
        except Exception as e:
            print(f'Gemini 오류 (시도 {attempt+1}/3): {e}')
    return None


def main():
    episode_num = get_episode_number()
    print(f'=== 주간 시리즈: 이번 주 사업주들이 물어본 것 #{episode_num} ===')
    content = generate_content(episode_num)
    if not content:
        print('컨텐츠 생성 실패 - 종료')
        sys.exit(1)

    print(f"메인:\n{content['main']}\n")
    for i, c in enumerate(content.get('comments', [])):
        print(f'댓글{i+1}:\n{c}\n')

    main_id = nap.post_to_threads(content['main'], content.get('comments', []), image_url=None,
                                   topic_tag=nap.CATEGORIES['business'].get('topic_tag'))
    print(f'완료! 메인 포스트 ID: {main_id}')
    save_episode_number(episode_num)


if __name__ == '__main__':
    main()
