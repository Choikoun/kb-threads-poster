#!/usr/bin/env python3
"""쇼핑 계정 릴스 제작: 라바제 식기건조대 가격 비교
- 제품 사진이 처음부터 끝까지 배경에 깔리고(블러 확장 배경 + 선명한 중앙 사진), 그 위로 정보 배너가 뜸
- 쿠팡 판매 목록 제품은 시험 대상 제품이 아님을 명시, 후기 표현 없음
python shop_reel_lbz.py  → blog_images/shop_2026-10-14_라바제식기건조대/reel_lbz.mp4
"""
import os, sys, tempfile, shutil
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image, ImageDraw, ImageFilter
from card_generator import load_font, hex_to_rgb
from video_poster import generate_narration_timed, make_subtitle_phrases, get_audio_duration, build_video_multi, pick_bgm

IMG_DIR = 'blog_images/shop_2026-10-14_라바제식기건조대'
OUT = f'{IMG_DIR}/reel_lbz.mp4'
NAVY = '#1B2A4A'; GOLD = '#B8925A'; RED = '#D9534F'; GREEN = '#2F9D6F'
W, H = 1080, 1920
c = hex_to_rgb

# (배경 제품, 라벨, 큰 글자, 작은 글자, 강조색, 음성) — 장면당 음성 길이를 비슷하게 맞춤
SCENES = [
    ('A', '쿠팡 목록 표기 · 2026-10-14', '같은 식기건조대인데' + chr(10) + '가격이 3배?', '', RED,
     '같은 라바제 식기건조대인데, 가격이 거의 세 배나 차이 난다고요? 쿠팡 목록으로 확인한 내용입니다.'),
    ('A', '① 가장 낮은 표기', '88,900원', 'DLM-8690 슬림 세로형 일본직수입', GREEN,
     '하나, 가장 낮은 표기는 8만 8천 9백 원, 슬림 세로형 DLM-8690입니다.'),
    ('B', '② 3종세트 표기', '255,000원', '같은 모델명 DLM-8690 3종세트', RED,
     '둘, 같은 모델명의 3종 세트는 25만 5천 원으로 표기됐습니다.'),
    ('C', '③ 옵션별 표기', '209,860원~', 'DLM-8690 올스텐 슬림 대용량', GOLD,
     '셋, 다른 목록은 옵션에 따라 20만 9천 8백 6십 원부터였습니다.'),
    ('D', '④ 가로형 대형', '168,000원', 'DLM-8563 가로형', GOLD,
     '넷, 대형 가로형 DLM-8563은 16만 8천 원이었습니다.'),
    ('A', '확인 ① 구성', '세트 vs 단품', '건조대·수저통·물받이 트레이', GREEN,
     '결제 전에, 3종 세트인지 건조대 단품인지 확인하세요.'),
    ('B', '확인 ② 크기', '450×300mm', 'DLM-8690 공식 크기(약)', GREEN,
     '공식 크기는 DLM-8690이 가로 450, 세로 300밀리미터입니다.'),
    ('C', '확인 ③ 판매처', '정식 유통?', '일본 직수입 여부와 배송비', GREEN,
     '일본 직수입인지, 최종 결제가와 판매처도 확인하세요. 직접 써본 후기가 아닌 정보 정리이며, 자세한 내용은 프로필 블로그에서 확인하세요.'),
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
        _, bounds = generate_narration_timed(narration, output_path=audio)
        phrases = make_subtitle_phrases(bounds)
        dur = get_audio_duration(audio)
        build_video_multi(frames, audio, output_path=OUT, duration=dur, bgm_path=pick_bgm(), phrases=phrases, work_dir=tmp)
        print('완료:', OUT, f'{dur:.1f}초')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
