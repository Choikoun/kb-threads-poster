#!/usr/bin/env python3
"""
주간 시리즈: "이번 주 사업주들이 물어본 것"
매주 금요일 저녁 게시 - 구독할 이유를 만드는 고정 시리즈 포맷
"""
import os, sys, json, re
from google import genai
from dotenv import load_dotenv
import news_auto_poster as nap  # post_to_threads, get_trend_headlines 재사용

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

GEMINI_KEY = os.getenv('GEMINI_API_KEY')


def generate_content():
    client = genai.Client(api_key=GEMINI_KEY)
    trends = nap.get_trend_headlines(limit=8)

    prompt = f"""너는 한국 Threads에서 활동하는 법인·세금·자산 설계 전문가야.
매주 올리는 시리즈 포스팅을 작성해줘. 시리즈 제목은 "이번 주 사업주들이 물어본 것"이야.

[이번 주 핵심 이슈 - 참고만, 아래 타겟에 안 맞으면 무시하고 일반적인 사업주 FAQ로 대체]
{trends}

[질문 소재 타겟 - 반드시 이 범위 안에서만]
법인 운영, 법인세·종합소득세 등 세금, 가지급금/배당/임원보수,
정책·세법 개정이 사업과 자산에 미치는 영향, 자산 운용·증여·상속 구조.
"AI주 급등락", "특정 종목 단타" 같은 일반 투자 얘기는 다루지 않는다.

[핵심 원칙 - 반드시 지켜]
- 전부 반말. 마지막 문장도 반말 (예외 없음)
- 한 줄 15~25자 수준. 자연스러운 문장 단위로 끊는다.
- 아이디어 바뀔 때 빈 줄 삽입 (가독성)
- 자극적이되 공격적이지 않게. "도박꾼", "쪽박", "~하면 끝장" 같은 독자를 비하하거나
  몰아붙이는 표현은 절대 쓰지 않는다. 담담하게, 사실과 구조로 설득한다.
- "상담받으세요", "DM 주세요", "점검해보세요" 같은 직접적 유도 표현 금지

[메인 포스트 구조]
1. 시리즈 인트로 1줄 - "이번 주 사업주들이 많이 물어본 거 정리해봤어" 같은 톤으로,
   매주 거의 동일한 인사말로 시작해서 시리즈처럼 느껴지게
↵빈줄
2. 질문 1개 - "OOO 하더라고요" / "OOO 이러더라" 식으로 실제 사업주가 한 말처럼 인용
↵빈줄
3. 그 질문에 대한 반전 또는 핵심 포인트 1~2줄
↵빈줄
4. 마지막 줄: 팔로우 유도 한 줄. "이런 거 매주 정리해서 올릴 거야. 팔로우해두면 놓치지 않아" 같은
   톤으로, 반말. 매주 비슷한 문구 반복해도 됨 (시리즈 시그니처처럼).

[댓글 구조 - 2개]
- 댓글1: 질문 2 (위와 같은 인용형) + 반전/핵심 포인트
- 댓글2 (마지막): 질문 3 (위와 같은 인용형) + 반전/핵심 포인트.
  마지막 문장은 반말 질문으로 마무리해서 호기심 자극

JSON만 출력:
{{
  "main": "메인 포스트 텍스트",
  "comments": ["댓글1", "댓글2"]
}}"""

    for attempt in range(3):
        try:
            resp = client.models.generate_content(
                model='gemini-2.5-flash',
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
    print('=== 주간 시리즈: 이번 주 사업주들이 물어본 것 ===')
    content = generate_content()
    if not content:
        print('컨텐츠 생성 실패 - 종료')
        sys.exit(1)

    print(f"메인:\n{content['main']}\n")
    for i, c in enumerate(content.get('comments', [])):
        print(f'댓글{i+1}:\n{c}\n')

    main_id = nap.post_to_threads(content['main'], content.get('comments', []), image_url=None)
    print(f'완료! 메인 포스트 ID: {main_id}')


if __name__ == '__main__':
    main()
