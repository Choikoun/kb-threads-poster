#!/usr/bin/env python3
"""
주간 비디오 포스팅
매주 1회, 뉴스 기반 훅을 짧은 세로형(9:16) 영상으로 제작해 Threads에 VIDEO로 포스팅
이미지(AI 일러스트/Pexels 실사)에 Ken Burns 효과 + 한글 TTS 내레이션
"""
import os, sys, json, re, subprocess, asyncio
from datetime import datetime, timezone, timedelta
from PIL import Image, ImageDraw
from google import genai
import edge_tts
from dotenv import load_dotenv
import news_auto_poster as nap
from card_generator import load_font, wrap_text, hex_to_rgb, COLORS
from ai_illustration_poster import generate_illustration
from stock_card_poster import search_pexels_photo

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

GEMINI_KEY = os.environ['GEMINI_API_KEY']
KST = timezone(timedelta(hours=9))

RAW_IMAGE_PATH = 'video_raw.jpg'
FRAME_PATH = 'video_frame.jpg'
AUDIO_PATH = 'video_narration.mp3'
OUTPUT_VIDEO = 'video_final.mp4'

VOICE = 'ko-KR-SunHiNeural'


def generate_content(articles, category='business'):
    client = genai.Client(api_key=GEMINI_KEY)
    cat = nap.CATEGORIES.get(category, nap.CATEGORIES['business'])
    news_list = '\n'.join([f"{i+1}. {a['title']}" for i, a in enumerate(articles[:20])])
    trend_headlines = nap.get_trend_headlines()
    trend_block = f"\n[오늘의 핵심 이슈 - 후속/연결 가능하면 활용]\n{trend_headlines}\n" if trend_headlines else ''

    prompt = f"""너는 한국 Threads에서 활동하는 법인·세금·자산 설계 전문가야.
아래 뉴스 중 {cat['name']} 독자에게 가장 임팩트 있는 것 하나 골라서,
짧은 세로형 영상(15~25초) + 캡션 형태의 포스트를 작성해줘.
영상은 정지 이미지 1장에 Ken Burns 효과(천천히 줌인)를 주고, 그 위에 음성 내레이션이 깔리는 형식이야.

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
- "이거 누가 알아서 해줄까?", "전문가 도움 필요하지 않을까?" 같이 컨설팅/전문가 필요성을
  은근히 암시하는 질문도 금지. 마지막 질문은 사실/숫자/구조 자체에 대한 궁금증으로 끝낸다.
- 팔로우 유도는 괜찮음 (자연스러울 때만, 강요하지 않기)
- 팔로우 유도 시 "@계정명" 같은 계정 핸들을 절대 만들어내지 않는다. "팔로우해", "팔로우 해두면 놓치지 않아"처럼 핸들 없이 표현한다.
- 자극적이되 공격적이지 않게. 독자를 비하하거나 몰아붙이는 표현 금지.
- 모호한 표현 금지: "뭔가 있어", "조심해", "알아봐야 해" → 구체적으로 써

[이미지 생성 프롬프트 작성 - image_prompt]
영문으로 작성. 9:16 세로형 구도. 선택한 뉴스 상황을 한국인 사업주/직장인이 겪는 장면으로 구체적으로 묘사
(표정: 놀람/불안/충격 등, 상황: 사무실/차/책상 등).
다크 네이비 + 골드 톤, 시네마틱 디지털 아트 스타일.
문서·화면·서류·태블릿처럼 텍스트가 들어갈 수 있는 사물은 등장시키지 않는다
(AI가 깨진 텍스트를 그려넣는 문제 방지). 인물의 표정과 분위기, 배경으로만 장면을 구성.
반드시 "vertical 9:16 portrait composition, no text, no documents, no screens, no readable signage in image" 포함.

[이미지 검색어 작성 - image_query]
영문 2~4단어. Pexels 스톡 사진(인물 portrait 위주) 검색에 쓸 키워드.
선택한 뉴스 상황의 감정/분위기를 일반적인 비즈니스 장면으로 표현
(예: "stressed businessman office", "tax documents desk", "worried business owner").
특정 한국 기업·인물은 묘사할 수 없으니 일반적인 인물/사무실/감정 위주로 작성.

[이미지 헤드라인 작성 - headline]
영상 하단에 들어갈 한글 헤드라인. 2줄 이내, 굵고 강렬한 핵심 사실/숫자 위주.
줄바꿈은 \\n 사용.

[내레이션 작성 - narration]
영상에서 음성(TTS)으로 읽힐 한국어 대본.
- 자연스러운 구어체 반말. 글머리 기호(📌 등)나 이모지 절대 사용 금지 - 음성으로만 들린다.
- 분량: 80~150자 (TTS 기준 초당 5~6자, 15~25초 분량).
- 짧은 훅으로 시작 → 헤드라인의 핵심 사실을 풀어서 설명 → 여운 있는 한 줄로 마무리.
- 숫자나 핵심 사실은 명확하게 말로 풀어 쓴다 (예: "1.8조" → "1조 8천억원").

[캡션 구조 - caption]
1. 훅 1~2줄 (영상/헤드라인과 이어지는 맥락, 반전이나 의문 제기)
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
  "image_query": "...",
  "headline": "한글 헤드라인 (줄바꿈 \\\\n)",
  "narration": "TTS로 읽힐 한국어 대본 (80~150자)",
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


def get_visual_source():
    """ISO 주차 홀짝으로 AI 일러스트 / Pexels 실사 교대"""
    week = datetime.now(KST).isocalendar()[1]
    return 'illustration' if week % 2 == 0 else 'stock'


def compose_frame(image_path, headline, output_path=FRAME_PATH, band_color=COLORS['bg']):
    """원본 이미지를 1080x1920으로 cover-crop 후 하단에 헤드라인 밴드 합성"""
    W, H = 1080, 1920
    img = Image.open(image_path).convert('RGB')

    src_w, src_h = img.size
    src_ratio = src_w / src_h
    target_ratio = W / H
    if src_ratio > target_ratio:
        new_h = H
        new_w = int(src_ratio * new_h)
    else:
        new_w = W
        new_h = int(new_w / src_ratio)
    img = img.resize((new_w, new_h))
    left = (new_w - W) // 2
    top = (new_h - H) // 2
    img = img.crop((left, top, left + W, top + H))

    draw = ImageDraw.Draw(img)
    font = load_font('extrabold', 72)
    lines = wrap_text(headline, font, W - 120, draw)
    line_height = 88
    band_height = 100 + len(lines) * line_height

    draw.rectangle([0, H - band_height, W, H], fill=hex_to_rgb(band_color))
    y = H - band_height + 50
    for line in lines:
        draw.text((60, y), line, font=font, fill=hex_to_rgb(COLORS['white']))
        y += line_height

    img.save(output_path, 'JPEG', quality=95)
    return output_path


async def _tts(text, output_path, voice):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


def generate_narration(text, output_path=AUDIO_PATH, voice=VOICE):
    asyncio.run(_tts(text, output_path, voice))
    return output_path


def get_audio_duration(audio_path):
    result = subprocess.run([
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        audio_path
    ], capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def build_video(frame_path, audio_path, output_path=OUTPUT_VIDEO, duration=20.0):
    fps = 30
    total_frames = int(round(duration * fps))
    vf = (
        f"scale=2160:3840,"
        f"zoompan=z='min(zoom+0.0008,1.15)':d={total_frames}:s=1080x1920:fps={fps},"
        f"format=yuv420p"
    )

    cmd = [
        'ffmpeg', '-y',
        '-loop', '1', '-i', frame_path,
        '-i', audio_path,
        '-vf', vf,
        '-map', '0:v', '-map', '1:a',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        '-r', str(fps),
        '-t', f'{duration:.2f}',
        '-shortest',
        '-movflags', '+faststart',
        output_path,
    ]
    subprocess.run(cmd, check=True)
    return output_path


def main():
    category = 'business'
    print(f'=== 주간 비디오 포스팅 ({category}) ===')
    articles = nap.get_hot_news(category)
    content = generate_content(articles, category)
    if not content:
        print('컨텐츠 생성 실패 - 종료')
        sys.exit(1)

    print(f"선택 뉴스: {content['selected_title']}")
    print(f"헤드라인:\n{content['headline']}\n")
    print(f"내레이션:\n{content['narration']}\n")
    print(f"캡션:\n{content['caption']}\n")
    for i, c in enumerate(content.get('comments', [])):
        print(f'댓글{i+1}:\n{c}\n')

    source = get_visual_source()
    print(f'비주얼 소스: {source}')
    if source == 'illustration':
        raw = generate_illustration(content['image_prompt'], RAW_IMAGE_PATH)
    else:
        raw = search_pexels_photo(content['image_query'], RAW_IMAGE_PATH, orientation='portrait')
    if not raw:
        print('비주얼 생성 실패 - 종료')
        sys.exit(1)

    compose_frame(raw, content['headline'])
    print(f'프레임 합성 완료: {FRAME_PATH}')

    generate_narration(content['narration'])
    print(f'내레이션 생성 완료: {AUDIO_PATH}')

    duration = get_audio_duration(AUDIO_PATH)
    print(f'내레이션 길이: {duration:.2f}초')

    build_video(FRAME_PATH, AUDIO_PATH, OUTPUT_VIDEO, duration)
    print(f'영상 생성 완료: {OUTPUT_VIDEO}')

    video_url = nap.upload_to_github_release(OUTPUT_VIDEO)
    if not video_url:
        print('영상 업로드 실패 - 종료')
        sys.exit(1)

    main_id = nap.post_video_to_threads(
        content['caption'], content.get('comments', []), video_url,
        topic_tag=nap.CATEGORIES[category].get('topic_tag'))
    if not main_id:
        print('포스팅 실패 - 종료')
        sys.exit(1)
    print(f'완료! 메인 포스트 ID: {main_id}')

    nap.log_content(main_id, category, 'video', content['selected_title'])


if __name__ == '__main__':
    main()
