#!/usr/bin/env python3
"""쇼핑 계정 릴스 제작: AMT 사각팬 가격 비교 v2(25초·정확한 훅·저장 유도)
- 제품 사진이 처음부터 끝까지 배경에 깔리고(블러 확장 배경 + 선명한 중앙 사진), 그 위로 정보 배너가 뜸
- 쿠팡 판매 목록 제품은 시험 대상 제품이 아님을 명시, 후기 표현 없음
python shop_reel_amt.py  (SHOP_VOICE=ko-KR-InJoonNeural 으로 남자 음성)
"""
import os, sys, tempfile, shutil
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image, ImageDraw, ImageFilter
from card_generator import load_font, hex_to_rgb
from video_poster import generate_narration_timed, make_subtitle_phrases, get_audio_duration, build_video_multi, pick_bgm

IMG_DIR = 'blog_images/shop_2026-10-15_AMT사각팬'
OUT = os.environ.get('SHOP_OUT') or f'{IMG_DIR}/reel_amt.mp4'
NAVY = '#1B2A4A'; GOLD = '#B8925A'; RED = '#D9534F'; GREEN = '#2F9D6F'
W, H = 1080, 1920
c = hex_to_rgb

# (배경 제품, 라벨, 큰 글자, 작은 글자, 강조색, 음성) — 장면당 음성 길이를 비슷하게 맞춤
SCENES = [
    ('A', 'AMT 프로 사각 컴바인 팬 · 2026-10-15', '같은 모델인데' + chr(10) + '29,240원 차이', '', RED,
     'AMT 컴바인 팬, 네이버와 쿠팡 가격을 비교해 보니 29,240원이 차이 났어요.'),
    ('A', '네이버 AMT 코리아', '152,000원', '정가 185,000원에서 할인', GOLD,
     '네이버 AMT 코리아는 15만 2천 원.'),
    ('A', '네이버 뎀블루', '146,670원', '같은 이름 모델', GOLD,
     '뎀블루는 14만 6천 6백 7십 원.'),
    ('A', '쿠팡 로켓배송', '122,760원', '표기 가격 가장 낮음', GREEN,
     '쿠팡 로켓배송은 12만 2천 7백 6십 원이에요.'),
    ('B', '정사각 베스트 팬 24cm', '22,120원 낮음', '네이버 132,000원 쿠팡 109,880원', GREEN,
     '24센티 정사각 베스트 팬도, 쿠팡이 2만 2천 원 낮았어요.'),
    ('C', '결제 전 확인', '크기·구성', '22cm인지 24cm인지, 뚜껑 포함인지', RED,
     '단, 크기와 구성이 같은지는 꼭 맞춰 보세요.'),
    ('A', '저장해두세요', '살 때 꺼내보기', '직접 써본 후기 아님 · 쿠팡 파트너스 수수료', GOLD,
     '저장해 두고, 살 때 꺼내 보세요. 자세한 비교는 프로필 블로그에 있어요.'),
]
PRODUCTS = []


def cover(path, dim=0.55, blur=0):
    ph = Image.open(path).convert('RGB')
    r = max(W / ph.width, H / ph.height)
    ph = ph.resize((int(ph.width * r) + 1, int(ph.height * r) + 1))
    x, y = (ph.width - W) // 2, (ph.height - H) // 2
    ph = ph.crop((x, y, x + W, y + H))
    if blur:
        ph = ph.filter(ImageFilter.GaussianBlur(blur))
    return Image.blend(ph, Image.new('RGB', (W, H), c('#0F1A33')), dim)


def bg_for(i):
    return cover(f'{IMG_DIR}/' + ('01_AMT사각팬_대표이미지.jpg' if i % 2 == 0 else '07_AMT사각팬_클로징.jpg'), 0.5 if i % 2 == 0 else 0.45)


def product_card(im, L, y0=610, size=520):
    from PIL import ImageChops
    d = ImageDraw.Draw(im)
    ph = Image.open(f'{IMG_DIR}/prod_{L}.jpg').convert('RGB')
    bb = ImageChops.difference(ph, Image.new('RGB', ph.size, (255, 255, 255))).point(lambda v: 255 if v > 24 else 0).getbbox()
    if bb:
        ph = ph.crop(bb)
    cw, ch = W - 260, size
    r = min(cw / ph.width, ch / ph.height)
    ph = ph.resize((int(ph.width * r), int(ph.height * r)))
    d.rounded_rectangle([110, y0, W - 110, y0 + size + 60], radius=36, fill=c('#FFFFFF'))
    im.paste(ph, ((W - ph.width) // 2, y0 + 30 + (size - ph.height) // 2))


def bars(im, rows, y0, hi=None, dim_others=True, gap=None):
    """rows: [(라벨, 값, 색)], 0원 기준 가로 막대"""
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle([50, y0 - 30, W - 50, y0 + 100 * len(rows) + 50], radius=28, fill=(15, 26, 51, 215))
    im.paste(Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB'))
    d = ImageDraw.Draw(im)
    mx = max(v for _, v, _ in rows)
    x0, wmax = 330, 600
    for k, (lab, v, col) in enumerate(rows):
        y = y0 + k * 100 + 30
        on = hi is None or hi == k
        col_ = c(col) if on else tuple(int(t * 0.45 + 28) for t in c(col))
        d.text((70, y), lab, font=load_font('bold', 30), fill=c('#FFFFFF') if on else c('#8A91A3'), anchor='lm')
        d.rounded_rectangle([x0, y - 24, x0 + int(wmax * v / mx), y + 24], radius=12, fill=col_)
        d.text((x0 + int(wmax * v / mx) - 14, y), f'{v:,}', font=load_font('extrabold', 30), fill=c('#FFFFFF'), anchor='rm')
    if gap:
        d.text((W // 2, y0 + 100 * len(rows) + 5), gap, font=load_font('extrabold', 36), fill=c('#FFD27A'), anchor='mm')


def checklist(im, y0):
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle([50, y0, W - 50, y0 + 380], radius=28, fill=(15, 26, 51, 225))
    im.paste(Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB'))
    d = ImageDraw.Draw(im)
    for k, t in enumerate(['크기: 22cm · 24cm 중 어떤 것?', '구성: 뚜껑이 포함인지', '모델명이 같은지']):
        y = y0 + 80 + k * 110
        d.ellipse([90, y - 28, 146, y + 28], outline=c('#FFD27A'), width=5)
        d.line([103, y, 115, y + 12, 135, y - 12], fill=c('#FFD27A'), width=6)
        d.text((175, y), t, font=load_font('bold', 40), fill=c('#FFFFFF'), anchor='lm')


def bookmark(im, cx, cy):
    d = ImageDraw.Draw(im)
    w, h = 190, 280
    d.polygon([(cx - w // 2, cy - h // 2), (cx + w // 2, cy - h // 2), (cx + w // 2, cy + h // 2),
               (cx, cy + h // 2 - 70), (cx - w // 2, cy + h // 2)], fill=c('#FFD27A'))


def banner(im, title, big, small, col):
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rounded_rectangle([50, 190, W - 50, 560], radius=28, fill=(15, 26, 51, 215))
    im.paste(Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB'))
    d = ImageDraw.Draw(im)
    d.text((W // 2, 250), title, font=load_font('bold', 40), fill=c('#FFFFFF'), anchor='mm')
    lines = big.split(chr(10))
    size = 110 if max(len(x) for x in lines) <= 7 else (92 if len(lines) == 1 else 82)
    y0 = 400 - (len(lines) - 1) * size * 0.55
    for i, ln in enumerate(lines):
        d.text((W // 2, y0 + i * size * 1.15), ln, font=load_font('extrabold', size), fill=c(col if len(lines) == 1 else '#FFFFFF'), anchor='mm')
    if small:
        d.text((W // 2, 505), small, font=load_font('regular', 32), fill=c('#D8DCE6'), anchor='mm')


def foot(im):
    d = ImageDraw.Draw(im)
    d.text((W // 2, 1790), '정보 정리용 · 쿠팡 파트너스 활동으로 수수료를 받을 수 있음', font=load_font('regular', 26), fill=c('#B8BECC'), anchor='mm')


NAVER_A = ('네이버 AMT코리아', 152000, '#B8925A')
NAVER_B = ('네이버 뎀블루', 146670, '#B8925A')
CP_A = ('쿠팡 로켓배송', 122760, '#2F9D6F')


def info_frame(i, sc, path):
    L, title, big, small, col, _ = sc
    im = bg_for(i)
    banner(im, title, big, small, col)
    rows = [NAVER_A, NAVER_B, CP_A]
    if i == 0:
        product_card(im, 'A', 610, 400)
        bars(im, rows, 1180, None, gap='최저 ↔ 최고 29,240원 차이')
    elif i in (1, 2, 3):
        product_card(im, 'A', 610, 440)
        bars(im, rows, 1200, hi=i - 1)
    elif i == 4:
        product_card(im, 'B', 610, 400)
        bars(im, [('네이버 24cm', 132000, '#B8925A'), ('쿠팡 24cm', 109880, '#2F9D6F')], 1230, gap='쿠팡이 22,120원 낮음')
    elif i == 5:
        product_card(im, 'C', 610, 360)
        checklist(im, 1100)
    else:
        bookmark(im, W // 2, 900)
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(ov).rounded_rectangle([90, 1110, W - 90, 1230], radius=28, fill=(15, 26, 51, 225))
        im.paste(Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB'))
        ImageDraw.Draw(im).text((W // 2, 1170), '프로필 링크 → 블로그에 전체 비교', font=load_font('bold', 42), fill=c('#FFFFFF'), anchor='mm')
    foot(im)
    im.save(path)
    return path


def main():
    tmp = tempfile.mkdtemp()
    try:
        frames = [info_frame(i, s, os.path.join(tmp, f'f{i}.png')) for i, s in enumerate(SCENES)]
        if os.environ.get('SHOP_PREVIEW'):
            [shutil.copy(f, f'_tmp_vid/prev{i}.png') for i, f in enumerate(frames)]; return
        narration = ' '.join([s[5] for s in SCENES] + [p[3] for p in PRODUCTS])
        audio = os.path.join(tmp, 'nar.mp3')
        _, bounds = generate_narration_timed(narration, output_path=audio, voice=(os.environ.get('SHOP_VOICE') or 'ko-KR-SunHiNeural'))
        phrases = make_subtitle_phrases(bounds)
        dur = get_audio_duration(audio)
        build_video_multi(frames, audio, output_path=OUT, duration=dur, bgm_path=pick_bgm(), phrases=phrases, work_dir=tmp)
        print('완료:', OUT, f'{dur:.1f}초')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
