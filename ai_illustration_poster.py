#!/usr/bin/env python3
"""
AI 일러스트 카드 + 캡션 포스팅
하루 1회, 뉴스 중 가장 임팩트 있는 걸 골라 AI 일러스트 카드로 제작
"""
import os, sys, json, re
from PIL import Image, ImageDraw
from google import genai
from dotenv import load_dotenv
import news_auto_poster as nap
from card_generator import load_font, wrap_text, hex_to_rgb, COLORS

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

GEMINI_KEY = os.environ['GEMINI_API_KEY']
RAW_IMAGE_PATH = 'ai_card_raw.png'
FINAL_IMAGE_PATH = 'ai_card_final.jpg'


def generate_content(articles, category='business'):
    client = genai.Client(api_key=GEMINI_KEY)
    cat = nap.CATEGORIES.get(category, nap.CATEGORIES['business'])
    news_list = '\n'.join([f"{i+1}. {a['title']}" for i, a in enumerate(articles[:20])])
    trend_headlines = nap.get_trend_headlines()
    trend_block = f"\n[오늘의 핵심 이슈 - 후속/연결 가능하면 활용]\n{trend_headlines}\n" if trend_headlines else ''

    prompt = f"""너는 한국 Threads에서 활동하는 법인·세금·자산 설계 전문가야.
아래 뉴스 중 {cat['name']} 독자에게 가장 임팩트 있는 것 하나 골라서,
AI 일러스트 카드(이미지 1장) + 캡션 형태의 포스트를 작성해줘.

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
- 팔로우 유도는 괜찮음 (자연스러울 때만, 강요하지 않기)
- 자극적이되 공격적이지 않게. 독자를 비하하거나 몰아붙이는 표현 금지.
- 모호한 표현 금지: "뭔가 있어", "조심해", "알아봐야 해" → 구체적으로 써

[이미지 생성 프롬프트 작성 - image_prompt]
영문으로 작성. 선택한 뉴스 상황을 한국인 사업주/직장인이 겪는 장면으로 구체적으로 묘사
(표정: 놀람/불안/충격 등, 상황: 사무실/차/책상 등).
다크 네이비 + 골드 톤, 시네마틱 디지털 아트 스타일.
문서·화면·서류·태블릿처럼 텍스트가 들어갈 수 있는 사물은 등장시키지 않는다
(AI가 깨진 텍스트를 그려넣는 문제 방지). 인물의 표정과 분위기, 배경으로만 장면을 구성.
반드시 "no text, no documents, no screens, no readable signage in image" 포함.

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
  "image_prompt": "...",
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


def generate_illustration(prompt, output_path=RAW_IMAGE_PATH):
    client = genai.Client(api_key=GEMINI_KEY)
    for attempt in range(3):
        try:
            resp = client.models.generate_content(model='gemini-2.5-flash-image', contents=prompt)
            for part in resp.candidates[0].content.parts:
                if getattr(part, 'inline_data', None):
                    with open(output_path, 'wb') as f:
                        f.write(part.inline_data.data)
                    return output_path
        except Exception as e:
            print(f'이미지 생성 오류 (시도 {attempt+1}/3): {e}')
    return None


def overlay_headline(image_path, headline, output_path=FINAL_IMAGE_PATH, band_color=COLORS['bg']):
    img = Image.open(image_path).convert('RGB').resize((1080, 1080))
    draw = ImageDraw.Draw(img)
    font = load_font('extrabold', 62)
    lines = wrap_text(headline, font, 1080 - 120, draw)
    line_height = 78
    band_height = 60 + len(lines) * line_height

    draw.rectangle([0, 1080 - band_height, 1080, 1080], fill=hex_to_rgb(band_color))
    y = 1080 - band_height + 30
    for line in lines:
        draw.text((60, y), line, font=font, fill=hex_to_rgb(COLORS['white']))
        y += line_height

    img.save(output_path, 'JPEG', quality=95)
    return output_path


def main():
    category = 'business'
    print(f'=== AI 일러스트 카드 포스팅 ({category}) ===')
    articles = nap.get_hot_news(category)
    content = generate_content(articles, category)
    if not content:
        print('컨텐츠 생성 실패 - 종료')
        sys.exit(1)

    print(f"선택 뉴스: {content['selected_title']}")
    print(f"\n이미지 프롬프트:\n{content['image_prompt']}\n")
    print(f"헤드라인:\n{content['headline']}\n")
    print(f"캡션:\n{content['caption']}\n")
    for i, c in enumerate(content.get('comments', [])):
        print(f'댓글{i+1}:\n{c}\n')

    print('이미지 생성 중...')
    raw = generate_illustration(content['image_prompt'])
    if not raw:
        print('이미지 생성 실패 - 종료')
        sys.exit(1)

    overlay_headline(raw, content['headline'])
    print(f'카드 완성: {FINAL_IMAGE_PATH}')

    with open(FINAL_IMAGE_PATH, 'rb') as f:
        image_url = nap.upload_to_imgbb(f.read())
    if not image_url:
        print('imgbb 업로드 실패 - 종료')
        sys.exit(1)

    main_id = nap.post_to_threads(content['caption'], content.get('comments', []), image_url)
    print(f'완료! 메인 포스트 ID: {main_id}')
    nap.log_content(main_id, category, 'ai_illustration', content['selected_title'])


if __name__ == '__main__':
    main()
