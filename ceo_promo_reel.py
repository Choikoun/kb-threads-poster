#!/usr/bin/env python3
"""
1인법인 중임등기 셀프 도구 — 인스타 릴스 홍보 (주 1회)
뉴스 기반이 아닌 고정 주제(중임등기)를 앵글 로테이션으로 릴스화.
video_poster의 멀티컷+훅화면+싱크자막 파이프라인 재사용.
"""
import os, sys, json, re, random, tempfile
from datetime import datetime, timezone, timedelta
from PIL import Image, ImageDraw
import qrcode
from google import genai
from dotenv import load_dotenv
import news_auto_poster as nap
from card_generator import load_font
from video_poster import (
    create_scene_frames, generate_narration_timed, make_subtitle_phrases,
    get_audio_duration, build_video_multi, pick_bgm,
)
from instagram_reels_poster import post_reels, load_ig_log, save_ig_log

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

GEMINI_KEY = os.environ['GEMINI_API_KEY']
KST = timezone(timedelta(hours=9))

TOOL_URL = 'https://web-production-92ec7.up.railway.app/public/ceo-reappoint'

ANGLES = [
    '과태료 경고형 — 임기 만료 놓치면 최대 500만원, 회사는 그대로인데 서류 때문에',
    '비용 비교형 — 법무사 수십만원 vs 셀프 무료, 서류만 있으면 되는 일',
    '깜빡함 공감형 — 1인법인 대표가 제일 많이 까먹는 등기, 바뀐 게 없어서 더 까먹는다',
    '3분 해결형 — 회사 정보 입력하면 서류 zip으로 끝, 어렵게 생각했던 일의 실체',
]

HASHTAGS = '#1인법인 #법인대표 #중임등기 #법인등기 #셀프등기 #법인운영 #사업자 #대표이사'


def make_qr_endcard(url, out_path):
    """릴스 마지막 화면: QR + 안내 텍스트 (인스타 캡션 링크 클릭 불가 우회).
    스토리/릴스 UI(상단 진행바·프로필, 하단 답장창)가 화면 상하단을 가리므로
    핵심 콘텐츠를 세로 중앙 50%(대략 y 460~1570) 안에 넣는 세이프존 레이아웃."""
    W, H = 1080, 1920
    img = Image.new('RGB', (W, H), (26, 26, 46))  # 다크 네이비 (#1a1a2e)
    draw = ImageDraw.Draw(img)

    title_font = load_font('extrabold', 72)
    sub_font = load_font('bold', 46)
    small_font = load_font('regular', 36)

    def center_text(y, text, font, fill=(255, 255, 255)):
        w = draw.textlength(text, font=font)
        draw.text(((W - w) // 2, y), text, font=font, fill=fill)

    center_text(480, '중임등기 서류', title_font)
    center_text(585, '무료로 받아보세요', title_font, fill=(240, 200, 100))  # 골드

    qr = qrcode.QRCode(box_size=13, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    qsize = 500
    qimg = qr.make_image(fill_color='black', back_color='white').convert('RGB').resize((qsize, qsize))
    qr_top = 800
    pad = 28
    draw.rectangle([(W - qsize) // 2 - pad, qr_top - pad, (W + qsize) // 2 + pad, qr_top + qsize + pad],
                  fill=(255, 255, 255))
    img.paste(qimg, ((W - qsize) // 2, qr_top))

    center_text(qr_top + qsize + pad + 60, 'QR을 스캔하면 바로 열립니다', sub_font)
    center_text(qr_top + qsize + pad + 130, '프로필 링크로도 이동하실 수 있어요', small_font, fill=(180, 180, 200))

    img.save(out_path, 'JPEG', quality=95)
    return out_path


def generate_content():
    client = genai.Client(api_key=GEMINI_KEY)
    angle = random.choice(ANGLES)
    prompt = f"""너는 한국 인스타그램에서 활동하는 법인·세금·자산 설계 전문가야.
"1인법인 대표이사 중임등기 셀프 서류 생성 도구"(무료 웹 도구)를 홍보하는 짧은 릴스(10~13초) 콘텐츠를 만들어줘.

[도구 정보 — 이 사실만 사용, 지어내지 말 것]
- 1인법인 대표이사 중임등기에 필요한 서류를 자동 생성해주는 무료 웹페이지
- 회사 정보 입력 → 필요 서류가 zip 파일로 다운로드
- 법인 이사 임기는 최대 3년(상법), 임기 만료 후 2주 내 중임(변경)등기 의무
- 등기 게을리하면 과태료 최대 500만원(상법상 상한)
- 법무사 의뢰 시 통상 수십만원 비용

[오늘의 앵글]
{angle}

[영상 형식]
- 장면(컷) 3개. 1번 장면은 훅 화면(이미지 위 큰 텍스트), 2~3번은 상황 이미지.
- 내레이션 50~80자(10~13초). 첫 문장은 2초 안에 끝나는 질문/충격.
- 정중한 존댓말 구어체("~습니다/~해요"). 딱딱한 뉴스 앵커체는 피하되 존댓말은 유지.

[핵심 원칙]
- 전부 존댓말(합니다체)로 정중하게. 과장·허위 금지 — 위 [도구 정보]의 사실 범위 안에서만.
- 겁주되 비하하지 않기. "몰라서 내는 돈"의 구조를 짚는 톤.
- 마지막은 "프로필 링크에서 무료로 만들어보세요" 류로 자연스럽게 유도.
- 훅(첫 화면 텍스트)은 앵글의 경각심보다 "무료로 서류를 받을 수 있다"는 사실을 우선 노출할 것.
  스크롤 중 시선을 끄는 건 위기감이 아니라 "이거 무료임"이라는 정보다. 예시 톤: "이거 무료로 드려요", "서류 무료 배포 중", "무료로 다 만들어드립니다".

[장면 작성 - scenes 3개]
각 장면: image_prompt(영문, 9:16 세로, 한국인 1인법인 대표의 상황 묘사, 다크 네이비+골드 시네마틱,
반드시 "vertical 9:16 portrait composition, no text, no documents, no screens, no readable signage in image" 포함),
image_query(영문 2~4단어 Pexels 검색어), text(빈 문자열 — 자막은 싱크 자막이 대체).

[캡션 - caption]
전부 존댓말로 작성.
1. 훅 1~2줄 (영상과 이어지는 반전/경각심)
2. 도구 핵심 한 줄 (무료, 입력→zip)
3. "링크는 프로필에 있어요 🔗" 한 줄
4. "링크가 필요하시면 댓글에 '등기'라고 남겨주세요. DM으로 보내드릴게요." 한 줄 (댓글 유도 — 인스타는 댓글이 도달을 키움)
5. 해시태그는 내가 따로 붙이니 쓰지 마.

JSON만 출력:
{{
  "hook": "첫 화면 큰 텍스트 (8~16자, '무료' 단어 포함해서 무료 제공을 직접 드러낼 것)",
  "scenes": [
    {{"image_prompt": "...", "image_query": "...", "text": ""}},
    {{"image_prompt": "...", "image_query": "...", "text": ""}},
    {{"image_prompt": "...", "image_query": "...", "text": ""}}
  ],
  "narration": "TTS 대본 (50~80자)",
  "caption": "캡션 텍스트"
}}"""
    for attempt in range(3):
        try:
            resp = client.models.generate_content(model='gemini-flash-latest', contents=prompt)
            m = re.search(r'\{[\s\S]*\}', resp.text.strip())
            if m:
                return json.loads(m.group())
        except Exception as e:
            print(f'Gemini 오류 (시도 {attempt+1}/3): {e}')
    return None


def main():
    print('=== 중임등기 도구 인스타 릴스 홍보 ===')
    content = generate_content()
    if not content:
        print('콘텐츠 생성 실패 - 종료')
        sys.exit(1)

    print(f"훅: {content.get('hook','')}")
    print(f"내레이션: {content['narration']}")

    caption = f"{content['caption']}\n\n{TOOL_URL}\n\n{HASHTAGS}"

    tmp_dir = tempfile.mkdtemp()
    audio_path = os.path.join(tmp_dir, 'narration.mp3')
    video_path = os.path.join(tmp_dir, 'reels.mp4')

    print('장면 프레임 생성 중...')
    frames = create_scene_frames(content, out_dir=tmp_dir, use_scene_text=False)
    if not frames:
        print('비주얼 생성 실패 - 종료')
        sys.exit(1)

    print('TTS 생성 중 (타임스탬프 수집)...')
    _, boundaries = generate_narration_timed(content['narration'], output_path=audio_path)
    phrases = make_subtitle_phrases(boundaries)
    duration = get_audio_duration(audio_path)
    print(f'  {duration:.1f}초, 자막 구절 {len(phrases)}개')

    print('QR 엔드카드 생성 중...')
    endcard = make_qr_endcard(TOOL_URL, os.path.join(tmp_dir, 'endcard.jpg'))

    print('영상 빌드 중...')
    bgm = pick_bgm()
    build_video_multi(frames, audio_path, output_path=video_path, duration=duration,
                      bgm_path=bgm, phrases=phrases, work_dir=tmp_dir,
                      end_card=endcard, end_card_seconds=2.8)

    print('GitHub Release 업로드 중...')
    video_url = nap.upload_to_github_release(video_path)
    if not video_url:
        print('업로드 실패 - 종료')
        sys.exit(1)

    print('Instagram 릴스 발행 중...')
    ig_id = post_reels(video_url, caption)
    if not ig_id:
        print('릴스 발행 실패 - 종료')
        sys.exit(1)

    print(f'완료! Instagram Reels ID: {ig_id}')
    ig_log = load_ig_log()
    ig_log.append({
        'ig_post_id': ig_id,
        'type': 'reels',
        'selected_title': '[홍보] 중임등기 셀프 도구 릴스',
        'date': datetime.now(KST).strftime('%Y-%m-%d %H:%M'),
    })
    save_ig_log(ig_log)


if __name__ == '__main__':
    main()
