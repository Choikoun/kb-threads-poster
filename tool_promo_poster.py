#!/usr/bin/env python3
"""
1인법인 대표이사 중임등기 셀프 도구 - 주간 홍보 포스팅
매주 1회, 각도를 랜덤하게 바꿔서 도구를 소개하고 링크를 노출
"""
import os, sys, json, re, random
import requests
from google import genai
from dotenv import load_dotenv
import news_auto_poster as nap  # post_to_threads 재사용

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

GEMINI_KEY = os.getenv('GEMINI_API_KEY')

TOOL_URL = 'https://web-production-92ec7.up.railway.app/public/ceo-reappoint'

ANGLES = [
    '물어보는 사람이 너무 많아서 만들었다는 톤 - 수요에 응해서 무료로 공개한다는 느낌',
    '1인법인 대표 중에 본인 임기 끝난 줄도 모르고 그냥 운영하는 경우가 많다는 반전',
    '법인 등기는 한 번 하면 끝나는 게 아니라 임기마다 다시 해야 하고, 안 하면 과태료 대상이라는 사실로 시작',
    '법인을 운영하는 이유가 세율 때문이라면, 법인 돈을 개인 통장으로 가져올 때 세금이 또 붙는다는 반전 - 제대로 활용 안 하면 오히려 손해이고 더 큰 문제로 커질 수 있다는 본질적인 이야기',
    '셀프로 중임등기 끝낸 사람들이 점점 늘고 있다는 사회적 증거형',
]


def generate_content():
    client = genai.Client(api_key=GEMINI_KEY)
    angle = random.choice(ANGLES)

    prompt = f"""너는 한국 Threads에서 활동하는 법인 컨설팅 전문가야.
1인법인 대표이사 중임등기 셀프 서류 생성 도구를 홍보하는 포스팅을 작성해줘.

[도구 정보]
- 1인법인 대표이사 중임등기에 필요한 서류를 자동 생성해주는 무료 웹페이지
- 회사 정보(회사명, 등기번호, 발행주식수, 사업자등록번호 등)와 대표이사 정보만 입력하면 필요한 서류를 zip으로 다운로드
- 무료, 하루 5회까지 사용 가능
- 링크: {TOOL_URL}

[이번 포스팅 각도]
{angle}

[핵심 원칙 - 반드시 지켜]
- 전부 반말. 마지막 문장도 반말 (예외 없음)
- 한 줄 15~25자 수준. 자연스러운 문장 단위로 끊는다.
- 아이디어 바뀔 때 빈 줄 삽입 (가독성)
- 자극적이되 공격적이지 않게. 독자를 비하하거나 몰아붙이지 않는다.
- "상담받으세요", "DM 주세요", "점검해보세요" 같은 직접적 상담 유도 문구는 쓰지 않는다.
  다만 이 포스팅은 무료 도구를 공유하는 게 목적이므로, 메인 포스트 마지막에 링크를 자연스럽게 포함시킨다.
- 특정 종목·자산의 매수/매도/매매 타이밍을 지시하거나 추천하지 않는다 (미등록 투자자문 리스크)

[메인 포스트 구조]
1. 훅 (이번 포스팅 각도를 반영, 1~3줄)
↵빈줄
2. 도구 소개 - 무료, 사용법 한 줄 (입력 정보 + zip 다운로드)
↵빈줄
3. 링크: {TOOL_URL}

[댓글 구조 - 1~2개]
- 댓글1: 사용법 보충 또는 "이미 써본 사람들 있다" 류 사회적 증거
- 마지막 댓글: 법인을 운영하는 진짜 이유나 법인 구조 전반에 대한 본질적인 질문을 던지며 마무리.
  설명하지 말고 질문만. 반말. (예: "이 법인, 지금 제대로 쓰이고 있는 걸까." 톤)

JSON만 출력:
{{
  "main": "메인 포스트 텍스트 (링크 포함)",
  "comments": ["댓글1", "댓글2 (선택)"]
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
    print('=== 중임등기 도구 주간 홍보 포스팅 ===')
    content = generate_content()
    if not content:
        print('컨텐츠 생성 실패 - 종료')
        sys.exit(1)

    print(f"메인:\n{content['main']}\n")
    for i, c in enumerate(content.get('comments', [])):
        print(f'댓글{i+1}:\n{c}\n')

    # 발판(topic_tag) + 민감미디어 경고 제거(맨텍스트 홍보글에 경고 붙으면 도달 저하) + 성과 추적
    main_id = nap.post_to_threads(content['main'], content.get('comments', []), image_url=None,
                                  topic_tag='법인', content_warning=False)
    print(f'완료! 메인 포스트 ID: {main_id}')

    nap.log_content(main_id, 'business', '도구홍보', '1인법인 중임등기 셀프 도구 주간 홍보', source='자체기획')


if __name__ == '__main__':
    main()
