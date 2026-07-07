#!/usr/bin/env python3
"""
주간 비디오 포스팅
매주 1회, 뉴스 기반 훅을 짧은 세로형(9:16) 영상으로 제작해 Threads에 VIDEO로 포스팅
이미지(AI 일러스트/Pexels 실사)에 Ken Burns 효과 + 한글 TTS 내레이션
"""
import os, sys, json, re, glob, random, subprocess, asyncio
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
# 배경음악(선택): assets/ 폴더의 mp3 중 매번 랜덤으로 하나 골라 낮은 볼륨으로 깔림. 폴더가 비었으면 스킵.
# (API 발행 릴스는 인스타 '트렌딩 오디오'를 붙일 수 없어 자체 BGM 로테이션으로 네이티브 느낌·다양성 보강)
BGM_DIR = 'assets'


def pick_bgm():
    candidates = glob.glob(os.path.join(BGM_DIR, '*.mp3'))
    return random.choice(candidates) if candidates else None


def generate_content(articles, category='business', platform='threads'):
    """platform='threads'|'instagram' — 두 플랫폼의 어조가 달라 톤을 분기한다:
    Threads는 반말(친근한 전문가), Instagram은 존댓말(정중한 정보 전달)이 계정 규칙."""
    client = genai.Client(api_key=GEMINI_KEY)
    cat = nap.CATEGORIES.get(category, nap.CATEGORIES['business'])
    news_list = '\n'.join([f"{i+1}. {a['title']}" for i, a in enumerate(articles[:20])])
    trend_headlines = nap.get_trend_headlines()
    trend_block = f"\n[오늘의 핵심 이슈 - 후속/연결 가능하면 활용]\n{trend_headlines}\n" if trend_headlines else ''

    is_ig = (platform == 'instagram')
    tone_name = '존댓말(합니다체)' if is_ig else '반말'
    tone_rule = '전부 존댓말(합니다체)로 정중하게' if is_ig else '전부 반말'
    narration_tone = (
        '자연스럽고 정중한 존댓말 구어체. "~습니다/~해요" 톤 유지.'
        if is_ig else
        '자연스러운 구어체 반말. "~했습니다" 금지 - "~했대", "~라는 거야" 식.'
    )
    followup_tone = '자연스러우면) 팔로우 유도 한 줄. 존댓말.' if is_ig else '자연스러우면) 팔로우 유도 한 줄. 반말.'
    comment_tone = '마지막 댓글은 존댓말 질문으로 마무리 가능.' if is_ig else '마지막 댓글은 반말 질문으로 마무리 가능.'

    prompt = f"""너는 한국 {'Instagram' if is_ig else 'Threads'}에서 활동하는 법인·세금·자산 설계 전문가야.
아래 뉴스 중 {cat['name']} 독자에게 가장 임팩트 있는 것 하나 골라서,
짧은 세로형 릴스 영상(10~13초) + 캡션 형태의 포스트를 작성해줘.

[영상 형식]
- 총 10~13초. 장면(컷) 3~4개가 내레이션 박자에 맞춰 전환되는 세로형 영상.
- 1번 장면은 "훅 화면": 이미지 위에 큰 텍스트 한 줄이 박혀 스크롤을 멈추게 한다.
- 2번 장면부터는 이미지 하단에 짧은 자막이 붙는다.
- 장면마다 다른 구도·배경·감정으로 시각적 변화를 준다.

[오늘 뉴스]
{news_list}
{trend_block}
[뉴스 선택 우선순위 — 릴스는 "내 얘기"가 아니면 죽는다]
1순위: 보는 사람이 "어? 이거 내 얘기인데"라고 느낄 뉴스 — 내 월급/세금/보험료/전세금/상속·증여, 가족 사이 돈 문제, 누구나 겪는 억울함·놀람
2순위: 충격적인 구체 숫자가 있는 뉴스 (금액·배수·비율)
피해야 할 것: 특정 기업 제재·기관 행정 발표·업계 단신처럼 일반인 삶과 연결고리가 없는 뉴스 — 이런 소재는 릴스에서 반복 검증된 저성과다. 후보에 1순위감이 없으면 그나마 가장 생활에 가까운 걸 골라 "내 삶에 미치는 영향" 각도로 재해석해라.

[작성 각도]
{cat['angle']}

[핵심 원칙 - 반드시 지켜]
- {tone_rule}
- 상담/DM/점검 유도 절대 금지. 화두만 던지고 끝낸다.
- 특정 종목·자산의 매수/매도/매매 타이밍을 지시하거나 추천하지 않는다 (미등록 투자자문 리스크). 구조적 인식까지만 다루고 투자행동 지시는 하지 않는다.
- 완전한 답 주지 말 것. 경각심·인사이트·잘못된 상식을 건드리되 "상황마다 달라", "구조가 먼저야"처럼 열어두어 독자 스스로 "내 상황은 어떻게 되지?" 상담 욕구가 생기도록.
- 세금 계산·법 조항 해설보다 "미리 구조를 설계하느냐 못 하느냐의 차이" 부각이 이 계정의 포지셔닝.
- "이거 누가 알아서 해줄까?", "전문가 도움 필요하지 않을까?" 같이 컨설팅/전문가 필요성을
  은근히 암시하는 질문도 금지. 마지막 질문은 사실/숫자/구조 자체에 대한 궁금증으로 끝낸다.
- 팔로우 유도는 괜찮음 (자연스러울 때만, 강요하지 않기)
- 팔로우 유도 시 "@계정명" 같은 계정 핸들을 절대 만들어내지 않는다. "팔로우해", "팔로우해두면 다음 글도 볼 수 있어"처럼 핸들 없이 담백하게 표현한다.
- [금지 - 플랫폼이 금융사기로 자동 분류함] "놓치다/놓칠/기회/혜택/지금 아니면" 같이 긴급성·손실회피를 자극하는 표현 절대 금지.
- 자극적이되 공격적이지 않게. 독자를 비하하거나 몰아붙이는 표현 금지.
- 모호한 표현 금지: "뭔가 있어", "조심해", "알아봐야 해" → 구체적으로 써
- [정확성 필수] 국회 통과·시행이 확정되지 않은 '개정안/발의/추진/검토/입법예고' 내용을 확정된 사실("~로 바뀌었다")처럼 단정하지 마라. 미확정이면 "추진 중", "통과되면"으로 명시.

[훅 작성 - hook]
1번 장면 이미지 위에 크게 박히는 한 줄. 8~16자. 숫자·반전이 있으면 최고.
(예: "보험료 12배가 수수료?", "상속세 0원인 집 많다")
스크롤 멈추게 하는 게 유일한 목적. 물음표로 끝나면 더 좋다.

[장면 작성 - scenes (3~4개)]
각 장면마다 아래 3개 필드:
- image_prompt: 영문. 9:16 세로형 구도. 그 장면의 상황을 한국인 사업주/직장인이 겪는 모습으로 구체적으로 묘사
  (표정: 놀람/불안/충격 등, 상황: 사무실/차/책상 등). 다크 네이비 + 골드 톤, 시네마틱 디지털 아트 스타일.
  문서·화면·서류·태블릿처럼 텍스트가 들어갈 수 있는 사물은 등장시키지 않는다.
  반드시 "vertical 9:16 portrait composition, no text, no documents, no screens, no readable signage in image" 포함.
- image_query: 영문 2~4단어. Pexels 스톡 사진(인물 portrait 위주) 검색 키워드
  (예: "stressed businessman office", "worried business owner"). 일반적인 인물/사무실/감정 위주.
- text: 그 장면 하단에 깔릴 자막. 14자 이내 한 줄. 내레이션의 해당 구간 핵심을 요약.
  1번 장면은 훅이 대신하므로 text를 빈 문자열로.
장면 순서 = 내레이션 전개 순서. 장면끼리 배경·구도가 겹치지 않게.

[내레이션 작성 - narration]
영상에서 음성(TTS)으로 읽힐 한국어 대본.
- {narration_tone} 글머리 기호(📌 등)나 이모지 절대 사용 금지 - 음성으로만 들린다.
- 분량: 50~80자 (TTS 기준 초당 5~6자, 10~13초 분량). 반드시 이 안에서 끝낸다.
- 첫 문장은 반드시 짧은 질문이나 충격 문장 (2초 안에 발화 끝나는 길이) — 여기서 못 잡으면 스와이프당한다.
- 뉴스 앵커체는 피하되 {tone_name} 유지. 숫자나 핵심 사실은 명확하게 말로 풀어 쓴다 (예: "1.8조" → "1조 8천억원").

[캡션 구조 - caption]
1. 훅 1~2줄 (영상/헤드라인과 이어지는 맥락, 반전이나 의문 제기)
↵빈줄
2. 📌 으로 시작하는 불릿 3개 - 핵심 사실/원인을 짧게 한 줄씩
↵빈줄
3. 핵심 숫자나 결론을 강조하는 한 줄
↵빈줄
4. ({followup_tone}

[댓글 구조]
1~2개. 추가 맥락이나 반전 포인트. {comment_tone}

JSON만 출력:
{{
  "selected_title": "선택한 뉴스 제목",
  "hook": "첫 화면 큰 텍스트 (8~16자)",
  "scenes": [
    {{"image_prompt": "...", "image_query": "...", "text": ""}},
    {{"image_prompt": "...", "image_query": "...", "text": "하단 자막 (14자 이내)"}},
    {{"image_prompt": "...", "image_query": "...", "text": "하단 자막 (14자 이내)"}}
  ],
  "narration": "TTS로 읽힐 한국어 대본 (50~80자)",
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


def _cover_crop(image_path, W=1080, H=1920):
    """원본 이미지를 W x H로 cover-crop"""
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
    return img.crop((left, top, left + W, top + H))


def compose_frame(image_path, headline, output_path=FRAME_PATH, band_color=COLORS['bg']):
    """원본 이미지를 1080x1920으로 cover-crop 후 하단에 헤드라인 밴드 합성 (텍스트 없으면 크롭만)"""
    W, H = 1080, 1920
    img = _cover_crop(image_path, W, H)

    if headline and headline.strip():
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


def compose_hook_frame(image_path, hook_text, output_path):
    """훅 화면: 이미지에 어두운 오버레이 + 화면 중앙 큰 텍스트 (릴스 첫 컷용)"""
    W, H = 1080, 1920
    img = _cover_crop(image_path, W, H).convert('RGBA')
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 115))
    img = Image.alpha_composite(img, overlay).convert('RGB')

    draw = ImageDraw.Draw(img)
    font = load_font('extrabold', 104)
    lines = wrap_text(hook_text, font, W - 160, draw)
    line_height = 130
    total_h = len(lines) * line_height
    y = (H - total_h) // 2
    for line in lines:
        line_w = draw.textlength(line, font=font)
        x = int((W - line_w) // 2)
        # 가독성용 그림자
        draw.text((x + 4, y + 4), line, font=font, fill=(0, 0, 0))
        draw.text((x, y), line, font=font, fill=(255, 255, 255))
        y += line_height

    img.save(output_path, 'JPEG', quality=95)
    return output_path


VOICE_RATE = '+6%'   # 살짝 빠른 발화 = 릴스 네이티브 톤


async def _tts(text, output_path, voice):
    communicate = edge_tts.Communicate(text, voice, rate=VOICE_RATE)
    await communicate.save(output_path)


def generate_narration(text, output_path=AUDIO_PATH, voice=VOICE):
    asyncio.run(_tts(text, output_path, voice))
    return output_path


async def _tts_timed(text, output_path, voice):
    """TTS 저장 + 단어별 타임스탬프(WordBoundary) 수집 — 싱크 자막용
    (edge-tts 7.x는 boundary 기본값이 SentenceBoundary라 명시 필요)"""
    communicate = edge_tts.Communicate(text, voice, rate=VOICE_RATE, boundary='WordBoundary')
    boundaries = []
    with open(output_path, 'wb') as f:
        async for chunk in communicate.stream():
            if chunk['type'] == 'audio':
                f.write(chunk['data'])
            elif chunk['type'] == 'WordBoundary':
                boundaries.append({
                    'start': chunk['offset'] / 1e7,                       # 100ns → sec
                    'end': (chunk['offset'] + chunk['duration']) / 1e7,
                    'text': chunk['text'],
                })
    return boundaries


def generate_narration_timed(text, output_path=AUDIO_PATH, voice=VOICE):
    """내레이션 생성 + 단어 타임스탬프 반환. 타임스탬프 수집 실패 시 (경로, []) 반환."""
    try:
        boundaries = asyncio.run(_tts_timed(text, output_path, voice))
    except Exception as e:
        print(f'  타임스탬프 수집 실패, 일반 TTS로 폴백: {e}')
        asyncio.run(_tts(text, output_path, voice))
        boundaries = []
    return output_path, boundaries


def make_subtitle_phrases(boundaries, max_words=4, max_chars=14, gap_break=0.3):
    """단어 타임스탬프를 자막 구절(2~4단어)로 묶기 — 릴스식 짧은 싱크 자막.
    단어 사이 침묵(gap_break초 이상 = 문장 쉼)에서도 끊어 문장 경계를 존중."""
    phrases = []
    cur_words, cur_start = [], None
    for i, b in enumerate(boundaries):
        if cur_start is None:
            cur_start = b['start']
        cur_words.append(b)
        joined = ' '.join(w['text'] for w in cur_words)
        nxt = boundaries[i + 1] if i + 1 < len(boundaries) else None
        pause_next = nxt is not None and (nxt['start'] - b['end']) >= gap_break
        if len(cur_words) >= max_words or len(joined) >= max_chars or pause_next:
            phrases.append({'start': cur_start, 'end': b['end'], 'text': joined})
            cur_words, cur_start = [], None
    if cur_words:
        phrases.append({'start': cur_start, 'end': cur_words[-1]['end'],
                        'text': ' '.join(w['text'] for w in cur_words)})
    # 구절 사이 공백 없이 이어지도록 end를 다음 start까지 살짝 연장 (자막 깜빡임 방지)
    for i in range(len(phrases) - 1):
        phrases[i]['end'] = max(phrases[i]['end'], phrases[i + 1]['start'])
    if phrases:
        phrases[-1]['end'] += 0.3
    return phrases


def get_audio_duration(audio_path):
    result = subprocess.run([
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        audio_path
    ], capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def create_scene_frames(content, out_dir='.', raw_prefix='scene', use_scene_text=True):
    """scenes 각 장면의 이미지 생성 + 프레임 합성 → 프레임 경로 리스트 (1번 장면은 훅 화면).
    use_scene_text=False면 하단 자막 밴드 생략 — 싱크 자막(drawtext)과 겹치지 않게."""
    scenes = content.get('scenes') or []
    if not scenes:
        return None
    source = get_visual_source()
    print(f'  비주얼 소스: {source} (단, 1번 장면=썸네일은 항상 실사)')
    frames = []
    prev_raw = None
    for idx, scene in enumerate(scenes):
        raw_path = os.path.join(out_dir, f'{raw_prefix}_{idx}_raw.jpg')
        raw = None
        # 썸네일로 쓰이는 1번 장면(훅 화면)은 AI 티가 나면 클릭률이 떨어지므로 항상 실사 우선
        use_ai = (source == 'illustration') and (idx != 0)
        if use_ai:
            png = os.path.join(out_dir, f'{raw_prefix}_{idx}_ai.png')
            result = generate_illustration(scene['image_prompt'], output_path=png)
            if result:
                Image.open(result).convert('RGB').save(raw_path, 'JPEG', quality=95)
                raw = raw_path
        if not raw:
            raw = search_pexels_photo(scene.get('image_query', ''), output_path=raw_path, orientation='portrait')
        if not raw and prev_raw:
            raw = prev_raw  # 장면 이미지 실패 시 직전 장면 이미지 재사용
        if not raw:
            return None
        prev_raw = raw

        frame_path = os.path.join(out_dir, f'{raw_prefix}_{idx}_frame.jpg')
        if idx == 0:
            compose_hook_frame(raw, content.get('hook', ''), output_path=frame_path)
        else:
            compose_frame(raw, scene.get('text', '') if use_scene_text else '', output_path=frame_path)
        frames.append(frame_path)
        print(f'  장면 {idx+1}/{len(scenes)} 완료')
    return frames


SUB_FONT = os.path.join('fonts', 'NanumGothicExtraBold.ttf')


def build_video_multi(frame_paths, audio_path, output_path=OUTPUT_VIDEO, duration=12.0,
                      bgm_path=None, phrases=None, work_dir=None,
                      end_card=None, end_card_seconds=2.8):
    """장면 컷 전환 + 줌(홀짝 교차) + 선택적 BGM + 선택적 싱크 자막(phrases) 번인.
    phrases: [{'start','end','text'}] — generate_narration_timed + make_subtitle_phrases 결과.
    end_card: 내레이션 끝난 뒤 end_card_seconds 동안 붙는 마지막 화면(QR 등). BGM은 끊기지 않고 이어짐."""
    fps = 30
    n = len(frame_paths)
    seg_frames = int(round(duration * fps / n))

    all_frames = list(frame_paths)
    use_endcard = bool(end_card) and os.path.exists(end_card)
    if use_endcard:
        all_frames.append(end_card)
    m = len(all_frames)                      # 오디오 입력 인덱스
    end_frames = int(round(end_card_seconds * fps))
    total_duration = duration + (end_card_seconds if use_endcard else 0)

    cmd = ['ffmpeg', '-y']
    for p in all_frames:
        cmd += ['-i', p]
    cmd += ['-i', audio_path]
    use_bgm = bool(bgm_path) and os.path.exists(bgm_path)
    if use_bgm:
        cmd += ['-stream_loop', '-1', '-i', bgm_path]

    parts = []
    for k in range(m):
        if k % 2 == 0:
            zexpr = "min(zoom+0.0012,1.12)"          # 줌인
        else:
            zexpr = "if(lte(on,1),1.12,max(1.0,zoom-0.0012))"  # 줌아웃
        d = end_frames if (use_endcard and k == m - 1) else seg_frames
        parts.append(
            f"[{k}:v]scale=2160:3840,"
            f"zoompan=z='{zexpr}':d={d}:s=1080x1920:fps={fps},"
            f"format=yuv420p,setsar=1[v{k}]"
        )
    concat_in = ''.join(f'[v{k}]' for k in range(m))
    parts.append(f"{concat_in}concat=n={m}:v=1:a=0[vc]")

    # 싱크 자막: 구절마다 drawtext + enable 구간. 텍스트는 textfile로 전달(특수문자 이스케이프 회피)
    cur = 'vc'
    if phrases:
        sub_dir = work_dir or os.path.dirname(os.path.abspath(output_path))
        fontfile = SUB_FONT.replace('\\', '/')
        for i, ph in enumerate(phrases):
            tf = os.path.join(sub_dir, f'sub_{i}.txt')
            with open(tf, 'w', encoding='utf-8') as f:
                f.write(ph['text'].strip())
            tf_ff = tf.replace('\\', '/')
            nxt = f'vs{i}'
            parts.append(
                f"[{cur}]drawtext=fontfile='{fontfile}':textfile='{tf_ff}'"
                f":fontsize=62:fontcolor=white:borderw=6:bordercolor=black@0.85"
                f":x=(w-text_w)/2:y=h*0.68"
                f":enable='between(t,{ph['start']:.2f},{ph['end']:.2f})'[{nxt}]"
            )
            cur = nxt
    parts.append(f"[{cur}]null[vout]")

    # 내레이션 오디오: 엔드카드가 있으면 그 길이만큼 무음 패딩(BGM이 duration=first로 이어지게)
    pad = f"apad=pad_dur={end_card_seconds:.2f}," if use_endcard else ""
    parts.append(f"[{m}:a]{pad}volume=1.0[nar]")
    if use_bgm:
        parts.append(f"[{m+1}:a]volume=0.12[bgm]")
        parts.append("[nar][bgm]amix=inputs=2:duration=first:dropout_transition=0[aout]")
        audio_map = '[aout]'
    else:
        audio_map = '[nar]'

    cmd += [
        '-filter_complex', ';'.join(parts),
        '-map', '[vout]', '-map', audio_map,
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        '-r', str(fps),
        '-t', f'{total_duration:.2f}',
        '-movflags', '+faststart',
        output_path,
    ]
    subprocess.run(cmd, check=True)
    return output_path


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
    print(f"훅: {content.get('hook', '')}")
    print(f"내레이션:\n{content['narration']}\n")
    print(f"캡션:\n{content['caption']}\n")
    for i, c in enumerate(content.get('comments', [])):
        print(f'댓글{i+1}:\n{c}\n')

    print('장면 프레임 생성 중...')
    frames = create_scene_frames(content, out_dir='.', use_scene_text=False)
    if not frames:
        print('비주얼 생성 실패 - 종료')
        sys.exit(1)

    _, boundaries = generate_narration_timed(content['narration'])
    phrases = make_subtitle_phrases(boundaries)
    print(f'내레이션 생성 완료: {AUDIO_PATH} (자막 구절 {len(phrases)}개)')

    duration = get_audio_duration(AUDIO_PATH)
    print(f'내레이션 길이: {duration:.2f}초')

    build_video_multi(frames, AUDIO_PATH, OUTPUT_VIDEO, duration,
                      bgm_path=pick_bgm(), phrases=phrases, work_dir='.')
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
