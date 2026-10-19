#!/usr/bin/env python3
"""쇼핑 릴스 애니메이션 엔진 — 정지 프레임+줌 대신, 장면마다 30fps로 직접 그려서 움직임을 만든다.
- 배경 사진이 천천히 줌, 배너가 위에서 내려오며 나타남, 가격 숫자는 0에서 올라가고(카운트업), 막대는 늘어남
- 장면마다 내레이션을 따로 만들어 그 길이만큼 장면을 유지(말과 화면이 맞음)
- 제품 카드는 통통 튀며 등장, 체크리스트는 한 줄씩 나타남
사용: 장면 목록(SCENES)과 draw 함수를 가진 모듈에서 run(SCENES, bg_for, draw_content, out, voice) 호출.
ffmpeg는 GitHub Actions에서만 있음(로컬 실행 불가) — SHOP_PREVIEW=1이면 장면별 마지막 프레임 PNG만 저장.
"""
import os, sys, math, shutil, tempfile, subprocess
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from card_generator import load_font, hex_to_rgb
from video_poster import generate_narration_timed, get_audio_duration, pick_bgm, SUB_FONT, make_subtitle_phrases

W, H, FPS = 1080, 1920, 30
TEMPO = float(os.environ.get('SHOP_TEMPO') or 1.12)   # Gemini TTS는 느린 편이라 약간 빠르게
c = hex_to_rgb
NAVY, GOLD, RED, GREEN = '#1B2A4A', '#B8925A', '#D9534F', '#2F9D6F'


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def pop(x):
    """살짝 튀어 오르는 등장(1.0을 넘었다가 돌아옴)"""
    x = max(0.0, min(1.0, x))
    return 1 + 2.7 * (x - 1) ** 3 + 1.7 * (x - 1) ** 2 if x < 1 else 1.0


def cover(path, dim=0.5, extra=1.12):
    """화면보다 extra배 큰 배경을 만들어 둔다(줌 크롭용)"""
    ph = Image.open(path).convert('RGB')
    bw, bh = int(W * extra), int(H * extra)
    r = max(bw / ph.width, bh / ph.height)
    ph = ph.resize((int(ph.width * r) + 1, int(ph.height * r) + 1))
    x, y = (ph.width - bw) // 2, (ph.height - bh) // 2
    ph = ph.crop((x, y, x + bw, y + bh))
    return Image.blend(ph, Image.new('RGB', (bw, bh), c('#0F1A33')), dim)


def bg_frame(big, t01, direction=1, extra=1.12):
    """t01: 0~1 장면 진행도. direction 1=줌인, -1=줌아웃"""
    z = (1.0 + (extra - 1.0) * (t01 if direction > 0 else 1 - t01)) / extra   # 크롭 크기 비율(1/extra~1)
    cw, ch = int(big.width * z), int(big.height * z)
    x, y = (big.width - cw) // 2, (big.height - ch) // 2
    return big.crop((x, y, x + cw, y + ch)).resize((W, H), Image.BILINEAR)


def panel(im, box, alpha=215, dy=0, a=1.0):
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0))
    x0, y0, x1, y1 = box
    ImageDraw.Draw(ov).rounded_rectangle([x0, y0 + dy, x1, y1 + dy], radius=28, fill=(15, 26, 51, int(alpha * a)))
    im.paste(Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB'))


def banner(im, title, big, small, col, p, countup=None):
    """p: 등장 진행도 0~1(위에서 내려오며 나타남). countup=(목표값, 접미사) 이면 big 대신 숫자가 올라감"""
    e = ease(p)
    dy = int(-70 * (1 - e))
    panel(im, [50, 190, W - 50, 560], dy=dy, a=e)
    d = ImageDraw.Draw(im)
    if e < 0.05:
        return
    fade = lambda rgb: tuple(int(v * e + 25 * (1 - e)) for v in rgb)
    d.text((W // 2, 250 + dy), title, font=load_font('bold', 40), fill=fade(c('#FFFFFF')), anchor='mm')
    if countup:
        target, suf = countup
        big = f'{int(target * ease(min(1.0, p * 1.15))):,}{suf}'
    lines = big.split(chr(10))
    size = 110 if max(len(x) for x in lines) <= 7 else (92 if len(lines) == 1 else 82)
    y0 = 400 - (len(lines) - 1) * size * 0.55 + dy
    for i, ln in enumerate(lines):
        d.text((W // 2, y0 + i * size * 1.15), ln, font=load_font('extrabold', size),
               fill=fade(c(col if len(lines) == 1 else '#FFFFFF')), anchor='mm')
    if small:
        d.text((W // 2, 505 + dy), small, font=load_font('regular', 32), fill=fade(c('#D8DCE6')), anchor='mm')


def product_card(im, path, p, y0=610, size=440):
    ph = Image.open(path).convert('RGB')
    bb = ImageChops.difference(ph, Image.new('RGB', ph.size, (255, 255, 255))).point(lambda v: 255 if v > 24 else 0).getbbox()
    if bb:
        ph = ph.crop(bb)
    s = max(0.01, pop(p))
    cw, ch = W - 260, size
    r = min(cw / ph.width, ch / ph.height)
    ph = ph.resize((int(ph.width * r), int(ph.height * r)))
    cw2, chh = int((W - 220) * s), int((size + 60) * s)
    cx, cy = W // 2, y0 + (size + 60) // 2
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([cx - cw2 // 2, cy - chh // 2, cx + cw2 // 2, cy + chh // 2], radius=36, fill=c('#FFFFFF'))
    if s > 0.3:
        pw, phh = int(ph.width * s), int(ph.height * s)
        im.paste(ph.resize((max(1, pw), max(1, phh))), (cx - pw // 2, cy - phh // 2))


def bars(im, rows, y0, p, hi=None, gap=None):
    """rows: [(라벨, 값, 색)] 0원 기준 가로 막대. p: 막대가 늘어나는 진행도"""
    e = ease(p)
    panel(im, [50, y0 - 30, W - 50, y0 + 100 * len(rows) + 50], a=min(1.0, e * 2))
    d = ImageDraw.Draw(im)
    mx = max(v for _, v, _ in rows)
    x0, wmax = 330, 600
    for k, (lab, v, col) in enumerate(rows):
        y = y0 + k * 100 + 30
        on = hi is None or hi == k
        col_ = c(col) if on else tuple(int(t * 0.45 + 28) for t in c(col))
        d.text((70, y), lab, font=load_font('bold', 30), fill=c('#FFFFFF') if on else c('#8A91A3'), anchor='lm')
        w = int(wmax * v / mx * ease(p * 1.1 - k * 0.12))
        if w > 6:
            d.rounded_rectangle([x0, y - 24, x0 + w, y + 24], radius=12, fill=col_)
            if w > 150:
                d.text((x0 + w - 14, y), f'{int(v * ease(p * 1.1 - k * 0.12)):,}', font=load_font('extrabold', 30), fill=c('#FFFFFF'), anchor='rm')
    if gap and p > 0.7:
        d.text((W // 2, y0 + 100 * len(rows) + 5), gap, font=load_font('extrabold', 36), fill=c('#FFD27A'), anchor='mm')


def range_bars(im, ranges, y0, p, mx=140000):
    panel(im, [50, y0 - 30, W - 50, y0 + 100 * len(ranges) + 20], a=min(1.0, ease(p) * 2))
    d = ImageDraw.Draw(im)
    x0, wm = 250, 760
    for k, (lab, lo, hi) in enumerate(ranges):
        y = y0 + 25 + k * 100
        e = ease(p * 1.2 - k * 0.15)
        d.text((70, y), lab, font=load_font('bold', 30), fill=c('#FFFFFF'), anchor='lm')
        d.rounded_rectangle([x0, y - 16, x0 + wm, y + 16], radius=10, fill=(60, 72, 100))
        if e > 0.02:
            a, b = x0 + int(wm * lo / mx), x0 + int(wm * (lo + (hi - lo) * e) / mx)
            d.rounded_rectangle([a, y - 22, max(a + 8, b), y + 22], radius=12, fill=c(GOLD))
            if e > 0.9:
                d.text((a, y + 40), f'{lo:,}', font=load_font('bold', 24), fill=c('#D8DCE6'), anchor='rm')
                d.text((b, y + 40), f'{hi:,}', font=load_font('bold', 24), fill=c('#FFD27A'), anchor='lm')


def checklist(im, items, y0, p):
    panel(im, [50, y0, W - 50, y0 + 380], alpha=225, a=min(1.0, ease(p) * 2))
    d = ImageDraw.Draw(im)
    for k, t in enumerate(items):
        e = ease(p * 1.6 - k * 0.35)
        if e <= 0:
            continue
        y = y0 + 80 + k * 110
        d.ellipse([90, y - 28, 146, y + 28], outline=c('#FFD27A'), width=5)
        if e > 0.6:
            d.line([103, y, 115, y + 12, 135, y - 12], fill=c('#FFD27A'), width=6)
        d.text((175 + int(30 * (1 - e)), y), t, font=load_font('bold', 40), fill=tuple(int(v * e + 25 * (1 - e)) for v in c('#FFFFFF')), anchor='lm')


def bookmark(im, p, t):
    """저장 유도: 북마크가 통통 튀며 등장 후 살짝 흔들림"""
    s = max(0.01, pop(p))
    cx, cy = W // 2, 900 + int(math.sin(t * 5) * 10 * ease(p))
    w, h = int(190 * s), int(280 * s)
    ImageDraw.Draw(im).polygon([(cx - w // 2, cy - h // 2), (cx + w // 2, cy - h // 2), (cx + w // 2, cy + h // 2),
                                (cx, cy + h // 2 - int(70 * s)), (cx - w // 2, cy + h // 2)], fill=c('#FFD27A'))


def foot(im):
    ImageDraw.Draw(im).text((W // 2, 1790), '정보 정리용 · 쿠팡 파트너스 활동으로 수수료를 받을 수 있음',
                            font=load_font('bold', 32), fill=c('#E6E9F2'), anchor='mm')


_TTS_MODELS = (os.environ.get('SHOP_TTS_MODELS') or 'gemini-3.8-flash-tts,gemini-3.1-flash-tts-preview,gemini-3.8-flash-lite-tts').split(',')
_tts_dead = set()   # 오늘 한도(무료 등급 모델별 일 10회)를 다 쓴 모델


def gemini_tts(text, wav_path, voice='Kore', style=''):
    """Gemini TTS(무료 등급은 모델별 하루 10회·분당 제한). 한도 소진 모델은 건너뛰고 다음 모델로.
    24kHz 16bit PCM을 wav로 저장하고 길이(초)를 반환. 단어 타임스탬프는 없음."""
    import base64, wave, requests, time, re
    key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    body = {'contents': [{'parts': [{'text': style + text}]}],
            'generationConfig': {'responseModalities': ['AUDIO'],
                                 'speechConfig': {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': voice}}}}}
    pcm = None
    for attempt in range(12):
        models = [m for m in _TTS_MODELS if m not in _tts_dead]
        if not models:
            raise RuntimeError('Gemini TTS 모델 한도 모두 소진')
        m = models[0]
        r = requests.post(f'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent',
                          params={'key': key}, json=body, timeout=120)
        if r.status_code == 200:
            try:
                pcm = base64.b64decode(r.json()['candidates'][0]['content']['parts'][0]['inlineData']['data'])
                print('  TTS 모델:', m)
                break
            except (KeyError, IndexError):
                pass
        print('  Gemini TTS 재시도', attempt + 1, m, r.status_code, r.text[:140].replace(chr(10), ' '))
        wait = 8 * (attempt + 1)
        if r.status_code == 429:
            h = re.search(r'retry in (?:(\d+)h)?(?:(\d+)m)?([0-9.]+)s', r.text)
            secs = (int(h.group(1) or 0) * 3600 + int(h.group(2) or 0) * 60 + float(h.group(3))) if h else 30
            if secs > 120:          # 일일 한도 소진 → 이 모델은 오늘 포기
                _tts_dead.add(m); continue
            wait = secs + 2
        time.sleep(wait)
    if pcm is None:
        raise RuntimeError('Gemini TTS 실패')
    with wave.open(wav_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
    return len(pcm) / 2 / 24000


def split_phrases(text, start, end, max_chars=14):
    """타임스탬프가 없을 때: 문장을 짧은 구절로 나누고 글자 수 비례로 시간 배분"""
    import re
    words, phrases, cur = re.split(r'\s+', text.strip()), [], ''
    for w in words:
        if cur and len(cur) + 1 + len(w) > max_chars:
            phrases.append(cur); cur = w
        else:
            cur = (cur + ' ' + w).strip()
    if cur:
        phrases.append(cur)
    total = sum(len(p) for p in phrases) or 1
    t, out = start, []
    for p in phrases:
        d = (end - start) * len(p) / total
        out.append({'start': t, 'end': t + d, 'text': p}); t += d
    return out


def run(scenes, render, out, voice=None, preview=False):
    """scenes: [{'say': 내레이션, ...임의 필드}]  render(scene, i, p, t, t01, work) -> PIL.Image (p: 장면 시작 0.8초 진행도)"""
    voice = voice or os.environ.get('SHOP_VOICE') or 'ko-KR-SunHiNeural'
    tmp = tempfile.mkdtemp()
    try:
        auds, durs, phrases, t0 = [], [], [], 0.0
        for i, sc in enumerate(scenes):
            if voice.startswith('gemini:'):
                ap = os.path.join(tmp, f'a{i}.wav')
                ad = gemini_tts(sc['say'], ap, voice=voice.split(':', 1)[1]) / TEMPO   # 재생 때 TEMPO배속(ffmpeg atempo)
                D = round(ad + 0.35, 2)
                phrases += split_phrases(sc['say'], t0, t0 + ad)
            else:
                ap = os.path.join(tmp, f'a{i}.mp3')
                _, bounds = generate_narration_timed(sc['say'], output_path=ap, voice=voice)
                ad = get_audio_duration(ap)
                D = round(ad + 0.35, 2)
                for ph in make_subtitle_phrases(bounds):
                    phrases.append({'start': ph['start'] + t0, 'end': ph['end'] + t0, 'text': ph['text']})
            auds.append(ap); durs.append(D); t0 += D
            print(f'장면{i} {D}초')
        if preview:
            os.makedirs('_tmp_vid', exist_ok=True)
            for i, sc in enumerate(scenes):
                render(sc, i, 1.0, durs[i], 1.0, tmp).save(f'_tmp_vid/prev{i}.png')
            return
        cmd = ['ffmpeg', '-y']
        for i, sc in enumerate(scenes):
            n = int(round(durs[i] * FPS))
            d = os.path.join(tmp, f's{i}'); os.makedirs(d)
            for f in range(n):
                t = f / FPS
                render(sc, i, min(1.0, t / 0.8), t, f / max(1, n - 1), tmp).save(os.path.join(d, f'f_{f:05d}.jpg'), quality=92)
            cmd += ['-framerate', str(FPS), '-i', os.path.join(d, 'f_%05d.jpg')]
            print(f'  장면{i} 프레임 {n}장')
        for ap in auds:
            cmd += ['-i', ap]
        ns = len(scenes)
        bgm = pick_bgm()
        if bgm and os.path.exists(bgm):
            cmd += ['-stream_loop', '-1', '-i', bgm]
        parts = [''.join(f'[{k}:v]' for k in range(ns)) + f'concat=n={ns}:v=1:a=0,format=yuv420p,setsar=1[vc]']
        cur = 'vc'
        fontfile = SUB_FONT.replace('\\', '/')
        import re
        for i, ph in enumerate(phrases):
            tf = os.path.join(tmp, f'sub_{i}.txt')
            open(tf, 'w', encoding='utf-8').write(ph['text'].strip())
            has_num = bool(re.search(r'[0-9]', ph['text']))
            fs, fc = (78, '0xFFD54A') if has_num else (62, 'white')
            nxt = f'vs{i}'
            parts.append(f"[{cur}]drawtext=fontfile='{fontfile}':textfile='{tf.replace(chr(92), '/')}':fontsize={fs}:fontcolor={fc}"
                         f":borderw=6:bordercolor=black@0.85:x=(w-text_w)/2:y=h*0.68:enable='between(t,{ph['start']:.2f},{ph['end']:.2f})'[{nxt}]")
            cur = nxt
        parts.append(f'[{cur}]null[vout]')
        for i, D in enumerate(durs):
            parts.append(f'[{ns + i}:a]' + (f'atempo={TEMPO},' if voice.startswith('gemini:') else '') + f'apad=whole_dur={D},atrim=0:{D}[x{i}]')
        parts.append(''.join(f'[x{i}]' for i in range(ns)) + f'concat=n={ns}:v=0:a=1[nar]')
        if bgm and os.path.exists(bgm):
            parts.append(f'[{2 * ns}:a]volume=0.12[bg]')
            parts.append('[nar][bg]amix=inputs=2:duration=first:dropout_transition=0[aout]')
            amap = '[aout]'
        else:
            amap = '[nar]'
        total = sum(durs)
        cmd += ['-filter_complex', ';'.join(parts), '-map', '[vout]', '-map', amap, '-c:v', 'libx264', '-preset', 'medium',
                '-crf', '22', '-c:a', 'aac', '-b:a', '128k', '-r', str(FPS), '-t', f'{total:.2f}', '-map_metadata', '-1', '-fflags', '+bitexact', '-movflags', '+faststart', out]
        subprocess.run(cmd, check=True)
        print('완료:', out, f'{total:.1f}초')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
