#!/usr/bin/env python3
"""쇼핑 계정 릴스 제작: 탄소매트 시험결과 정보형 v3
- 제품 사진이 처음부터 끝까지 배경에 깔리고(블러 확장 배경 + 선명한 중앙 사진), 그 위로 정보 배너가 뜸
- 쿠팡 판매 목록 제품은 시험 대상 제품이 아님을 명시, 후기 표현 없음
python shop_reel_mat.py  → blog_images/shop_2026-10-08_탄소매트/reel_mat.mp4
"""
import os, sys, tempfile, shutil
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image, ImageDraw, ImageFilter
from card_generator import load_font, hex_to_rgb
from video_poster import generate_narration_timed, make_subtitle_phrases, get_audio_duration, build_video_multi, pick_bgm

IMG_DIR = 'blog_images/shop_2026-10-08_탄소매트'
OUT = f'{IMG_DIR}/reel_mat.mp4'
NAVY = '#1B2A4A'; GOLD = '#B8925A'; RED = '#D9534F'; GREEN = '#2F9D6F'
W, H = 1080, 1920
c = hex_to_rgb

# (배경 제품, 라벨, 큰 글자, 작은 글자, 강조색, 음성) — 장면당 음성 길이를 비슷하게 맞춤
SCENES = [
    ('A', '한국소비자원 10개 제품 비교시험', '같은 탄소매트인데\n온도가 25도 차이?', '', RED,
     '같은 탄소매트인데, 온도가 25도나 차이 난다고요? 한국소비자원 시험 결과로 확인할 다섯 가지입니다.'),
    ('B', '① 최대 표면온도', '39 ~ 64도', '제품별 최대 25도 차이', RED,
     '하나, 최대 표면온도는 39도에서 64도까지, 제품마다 25도 차이가 났습니다.'),
    ('C', '② 위치별 온도편차', '0.4 ~ 10.5도', '매트 위 어디냐에 따라 다릅니다', GOLD,
     '둘, 같은 매트 안에서도 위치별 온도 편차가 0.4도에서 10.5도까지 벌어졌습니다.'),
    ('D', '③ 발열속도 (20→35도)', '12 ~ 49분', '저가형 평균 19분 · 중·고가형 34분', RED,
     '셋, 20도에서 35도까지 데워지는 시간은 12분에서 49분이었고, 저가형이 평균 더 빨랐습니다.'),
    ('E', '④ 머리 쪽 열선', '10개 중 4개', '머리부 열선이 없는 제품', GREEN,
     '넷, 열 개 중 네 개 제품은 머리 쪽 열선이 없었습니다.'),
    ('F', '⑤ 전자파·감전 안전성', '10개 모두 적합', '시험 기준 충족', GREEN,
     '다섯, 전자파와 감전 안전성은 열 개 모두 기준에 적합했습니다.'),
]
# 쿠팡 판매 목록(2026-10-07 기준, 블로그 7번과 동일) — 시험 대상 제품이 아님
PRODUCTS = [
    ('A', '한일의료기 지엔베르그', '49,000원', '쿠팡 판매 목록 일부입니다. 시험 대상 제품과는 다른 제품입니다. 한일의료기 지엔베르그, 4만 9천 원.'),
    ('B', '대성 탄소매트 슈퍼싱글', '69,000원', '대성 탄소매트 슈퍼싱글, 6만 9천 원.'),
    ('C', '일신한일 3cm 워셔블', '92,950원', '일신한일 워셔블 탄소매트, 9만 2천 9백 원.'),
    ('D', '한일 프리미엄라인 퀸', '94,900원', '한일 프리미엄라인 퀸 사이즈, 9만 4천 9백 원.'),
    ('E', '한일의료기 해브온', '129,000원', '한일의료기 해브온, 12만 9천 원.'),
    ('F', '곰표한일 IOT 패딩', '159,900원', '곰표한일 아이오티 패딩형, 15만 9천 9백 원. 가격은 10월 7일 기준이고 시험 결과와는 무관합니다. 직접 써본 후기가 아닌 정보 정리이며, 전체 내용은 프로필 블로그에서 확인하세요.'),
]


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
        frames += [product_frame(p, os.path.join(tmp, f'p{i}.png')) for i, p in enumerate(PRODUCTS)]
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
