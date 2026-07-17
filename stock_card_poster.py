#!/usr/bin/env python3
"""
실사 이미지 카드 + 캡션 포스팅
AI 일러스트 카드와 같은 슬롯에서 격일 교대로 실행 (Pexels 스톡 사진 사용)
"""
import os, sys, json, re, random
import requests
from google import genai
from dotenv import load_dotenv
import news_auto_poster as nap
from ai_illustration_poster import overlay_headline, RAW_IMAGE_PATH, FINAL_IMAGE_PATH
from card_generator import upload_to_imgbb

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

GEMINI_KEY = os.environ['GEMINI_API_KEY']
PEXELS_KEY = os.environ['PEXELS_API_KEY']


def generate_content(articles, category='business'):
    client = genai.Client(api_key=GEMINI_KEY)
    cat = nap.CATEGORIES.get(category, nap.CATEGORIES['business'])
    news_list = '\n'.join([f"{i+1}. {a['title']}" for i, a in enumerate(articles[:20])])
    trend_headlines = nap.get_trend_headlines()
    trend_block = f"\n[오늘의 핵심 이슈 - 후속/연결 가능하면 활용]\n{trend_headlines}\n" if trend_headlines else ''

    prompt = f"""너는 한국 Threads에서 활동하는 법인·세금·자산 설계 전문가야.
아래 뉴스 중 {cat['name']} 독자에게 가장 임팩트 있는 것 하나 골라서,
실사 이미지 카드(이미지 1장) + 캡션 형태의 포스트를 작성해줘.

[오늘 뉴스]
{news_list}
{trend_block}
[뉴스 선택 우선순위]
다음 유형의 뉴스가 있으면 최우선으로 선택해:
- 정부기관(국세청·대법원·헌재·공정위·금융위 등) 공식 발표, 판결, 표결 결과
- 구체적 숫자(금액·비율·표결수)가 포함된 사실
해당하는 뉴스가 없으면 기존 기준대로 가장 임팩트 있는 걸 선택해.

[작성 각도]
{cat['angle']}

[핵심 원칙 - 반드시 지켜]
- 전부 반말
- 상담/DM/점검 유도 절대 금지. 화두만 던지고 끝낸다.
- 특정 종목·자산의 매수/매도/매매 타이밍을 지시하거나 추천하지 않는다 (미등록 투자자문 리스크). 구조적 인식까지만 다루고 투자행동 지시는 하지 않는다.
- [금지 - 플랫폼이 금융사기로 자동 분류함] 특정 종목명(삼성전자, SK하이닉스 등)·레버리지·빚투와 구체적 금액을 한 포스트에 함께 언급하지 않는다. 단순 제도 뉴스 전달이어도 이 조합만으로 스캠성 콘텐츠로 자동 분류되어 게시물이 삭제된 사례 있음(2026-07-16).
- 완전한 답 주지 말 것. 경각심·인사이트·잘못된 상식을 건드리되 "상황마다 달라", "구조가 먼저야"처럼 열어두어 독자 스스로 "내 상황은 어떻게 되지?" 상담 욕구가 생기도록.
- 세금 계산·법 조항 해설보다 "미리 구조를 설계하느냐 못 하느냐의 차이" 부각이 이 계정의 포지셔닝.
- "이거 누가 알아서 해줄까?", "전문가 도움 필요하지 않을까?" 같이 컨설팅/전문가 필요성을
  은근히 암시하는 질문도 금지. 마지막 질문은 사실/숫자/구조 자체에 대한 궁금증으로 끝낸다.
- 팔로우 유도는 괜찮음 (자연스러울 때만, 강요하지 않기)
- 팔로우 유도 시 "@계정명" 같은 계정 핸들을 절대 만들어내지 않는다. "팔로우해", "팔로우해두면 다음 글도 볼 수 있어"처럼 핸들 없이 담백하게 표현한다.
- [금지 - 플랫폼이 금융사기로 자동 분류함] "놓치다/놓칠/기회/혜택/지금 아니면" 같이 긴급성·손실회피를 자극하는 표현 절대 금지.
- 자극적이되 공격적이지 않게. 독자를 비하하거나 몰아붙이는 표현 금지.
- 모호한 표현 금지: "뭔가 있어", "조심해", "알아봐야 해" → 구체적으로 써

[이미지 검색어 작성 - image_query]
영문 2~4단어. Pexels 스톡 사진 검색에 쓸 키워드.
선택한 뉴스 상황의 감정/분위기를 일반적인 비즈니스 장면으로 표현
(예: "stressed businessman office", "tax documents desk", "worried business owner").
특정 한국 기업·인물은 묘사할 수 없으니 일반적인 인물/사무실/감정 위주로 작성.

[이미지 헤드라인 작성 - headline]
이미지 하단에 들어갈 한글 헤드라인. 2줄 이내, 굵고 강렬한 핵심 사실/숫자 위주.
줄바꿈은 \\n 사용.

[캡션 구조 - caption]
1. 훅 1~2줄 (이미지/헤드라인과 이어지는 맥락, 반전이나 의문 제기)
↵빈줄
2. 📌 으로 시작하는 불릿 3개 - 핵심 사실/원인을 짧게 한 줄씩
↵빈줄
3. 핵심 숫자나 결론을 강조하는 한 줄
↵빈줄
4. (자연스러우면) 팔로우 유도 한 줄. 반말.

[댓글 구조]
1~2개. 추가 맥락이나 반전 포인트. 마지막 댓글은 반말 질문으로 마무리 가능.

JSON만 출력:
{{
  "selected_title": "선택한 뉴스 제목",
  "image_query": "...",
  "headline": "한글 헤드라인 (줄바꿈 \\\\n)",
  "caption": "캡션 텍스트",
  "comments": ["댓글1", "댓글2 (선택)"]
}}"""

    for attempt in range(3):
        try:
            resp = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            raw = resp.text.strip()
            m = re.search(r'\{[\s\S]*\}', raw)
            if m:
                return json.loads(m.group())
        except Exception as e:
            print(f'Gemini 텍스트 생성 오류 (시도 {attempt+1}/3): {e}')
    return None


def search_pexels_photo(query, output_path=RAW_IMAGE_PATH, orientation='square'):
    for attempt in range(3):
        try:
            resp = requests.get('https://api.pexels.com/v1/search',
                                 headers={'Authorization': PEXELS_KEY},
                                 params={'query': query, 'per_page': 10, 'orientation': orientation},
                                 timeout=15)
            if not resp.ok:
                print(f'Pexels 검색 오류 (시도 {attempt+1}/3): {resp.status_code}')
                continue
            photos = resp.json().get('photos', [])
            if not photos:
                print(f'Pexels 검색 결과 없음: "{query}"')
                if query != 'business office':
                    query = 'business office'
                    continue
                return None
            photo = random.choice(photos[:5])
            img_resp = requests.get(photo['src']['large2x'], timeout=30)
            if not img_resp.ok:
                continue
            with open(output_path, 'wb') as f:
                f.write(img_resp.content)
            return output_path
        except Exception as e:
            print(f'Pexels 이미지 다운로드 오류 (시도 {attempt+1}/3): {e}')
    return None


def main():
    category = 'business'
    print(f'=== 실사 이미지 카드 포스팅 ({category}) ===')
    articles = nap.get_hot_news(category)
    content = generate_content(articles, category)
    if not content:
        print('컨텐츠 생성 실패 - 종료')
        sys.exit(1)

    print(f"선택 뉴스: {content['selected_title']}")
    print(f"\n이미지 검색어:\n{content['image_query']}\n")
    print(f"헤드라인:\n{content['headline']}\n")
    print(f"캡션:\n{content['caption']}\n")
    for i, c in enumerate(content.get('comments', [])):
        print(f'댓글{i+1}:\n{c}\n')

    print('이미지 검색 중...')
    raw = search_pexels_photo(content['image_query'])
    if not raw:
        print('이미지 검색 실패 - 종료')
        sys.exit(1)

    overlay_headline(raw, content['headline'])
    print(f'카드 완성: {FINAL_IMAGE_PATH}')

    image_url = upload_to_imgbb(FINAL_IMAGE_PATH)
    if not image_url:
        print('imgbb 업로드 실패 - 종료')
        sys.exit(1)

    main_id = nap.post_to_threads(content['caption'], content.get('comments', []), image_url,
                                   topic_tag=nap.CATEGORIES['business'].get('topic_tag'))
    print(f'완료! 메인 포스트 ID: {main_id}')
    nap.log_content(main_id, category, 'stock_image', content['selected_title'])


if __name__ == '__main__':
    main()
