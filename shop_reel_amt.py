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


def background(L):
    ph = Image.open(f'{IMG_DIR}/prod_{L}.jpg').convert('RGB')
    bg = ph.resize((H, H)).crop(((H - W) // 2, 0, (H - W) // 2 + W, H)).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new('RGB', (W, H), c('#0F1A33')), 0.55)
    s = ph.resize((W, W))
    bg.paste(s, (0, 150))
    return bg


def banner(im, title, big, small, col):
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rounded_rectangle([50, 190, W - 50, 560], radius=28, fill=(15, 26, 51, 215))
    im.paste(Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB'))
    d = ImageDraw.Draw(im)
    d.text((W // 2, 250), title, font=load_font('bold', 40), fill=c('#FFFFFF'), anchor='mm')
    lines = big.split('\n')
    size = 110 if max(len(x) for x in lines) <= 7 else (92 if len(lines) == 1 else 82)
    y0 = 400 - (len(lines) - 1) * size * 0.55
    for i, ln in enumerate(lines):
        d.text((W // 2, y0 + i * size * 1.15), ln, font=load_font('extrabold', size), fill=c(col if len(lines) == 1 else '#FFFFFF'), anchor='mm')
    if small:
        d.text((W // 2, 505), small, font=load_font('regular', 32), fill=c('#D8DCE6'), anchor='mm')


def foot(im):
    d = ImageDraw.Draw(im)
    d.text((W // 2, 1790), '정보 정리용 · 쿠팡 파트너스 활동으로 수수료를 받을 수 있음', font=load_font('regular', 26), fill=c('#B8BECC'), anchor='mm')


def info_frame(sc, path):
    L, title, big, small, col, _ = sc
    im = background(L)
    banner(im, title, big, small, col)
    foot(im)
    im.save(path)
    return path


def product_frame(pr, path):
    L, name, price, _ = pr
    im = background(L)
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle([50, 190, W - 50, 470], radius=28, fill=(15, 26, 51, 215))
    im.paste(Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB'))
    d = ImageDraw.Draw(im)
    d.text((W // 2, 245), '쿠팡 판매 목록 · 시험 대상 제품 아님', font=load_font('bold', 34), fill=c('#FFB4A8'), anchor='mm')
    d.text((W // 2, 335), name, font=load_font('extrabold', 54), fill=c('#FFFFFF'), anchor='mm')
    d.text((W // 2, 420), price, font=load_font('extrabold', 66), fill=c('#FFD27A'), anchor='mm')
    foot(im)
    im.save(path)
    return path


def main():
    tmp = tempfile.mkdtemp()
    try:
        frames = [info_frame(s, os.path.join(tmp, f'f{i}.png')) for i, s in enumerate(SCENES)]
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
