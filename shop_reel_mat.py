#!/usr/bin/env python3
"""쇼핑 계정 릴스 제작: 탄소매트 시험결과 정보형 (직접 만든 인포그래픽 장면, 사진·후기 표현 없음)
python shop_reel_mat.py  → blog_images/shop_2026-10-08_탄소매트/reel_mat.mp4
"""
import os, sys, tempfile, shutil
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from video_poster import generate_narration_timed, make_subtitle_phrases, get_audio_duration, build_video_multi, pick_bgm

OUT = 'blog_images/shop_2026-10-08_탄소매트/reel_mat.mp4'
BG = '#F7F5F0'; NAVY = '#1B2A4A'; GOLD = '#B8925A'; GRAY = '#6B7280'; RED = '#B5473A'; GREEN = '#2F7D5D'
W, H = 1080, 1920
c = hex_to_rgb

# (상단 큰 제목, 큰 숫자, 보조설명, 강조색)  — 자막은 y≈1306 부근이라 그 아래는 비워둠
SCENES = [
    ('탄소매트 고르기 전', '확인할 5가지', '한국소비자원 10개 제품 비교시험', NAVY),
    ('① 최대 표면온도', '39 ~ 64℃', '같은 탄소매트인데 제품별 최대 25℃ 차이', RED),
    ('② 위치별 온도편차', '0.4 ~ 10.5℃', '매트 위 어디냐에 따라 따뜻함이 다릅니다', GOLD),
    ('③ 발열속도 (20→35℃)', '12 ~ 49분', '저가형 평균 19분 · 중·고가형 평균 34분', RED),
    ('④ 머리 쪽 열선', '10개 중 4개', '머리부 열선이 없는 제품이었습니다', GREEN),
    ('⑤ 안전성은 모두 적합', '10개 모두', '전자파·감전 안전성 시험 기준', GREEN),
]

NARRATION = (
    '탄소매트 고르기 전에, 한국소비자원 시험 결과로 확인할 다섯 가지입니다. '
    '하나, 최대 표면온도는 39도에서 64도까지, 제품마다 25도 차이가 났습니다. '
    '둘, 위치별 온도 편차는 0.4도에서 10.5도까지 벌어졌습니다. '
    '셋, 20도에서 35도까지 데워지는 시간은 12분에서 49분이었고, 저가형이 평균 더 빨랐습니다. '
    '넷, 열 개 중 네 개 제품은 머리 쪽 열선이 없었습니다. '
    '다섯, 전자파와 감전 안전성은 열 개 모두 기준에 적합했습니다. '
    '직접 써본 후기가 아니라 시험 결과를 정리한 내용입니다. 전체 정리는 프로필의 블로그에서 확인하세요.'
)


def frame(title, big, sub, col, path):
    im = Image.new('RGB', (W, H), c(BG))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 14], fill=c(col))
    d.text((W // 2, 330), title, font=load_font('extrabold', 66), fill=c(NAVY), anchor='mm')
    d.rounded_rectangle([80, 460, W - 80, 880], radius=28, fill=c('#FFFFFF'), outline=c(col), width=6)
    size = 120 if len(big) <= 7 else 96
    d.text((W // 2, 650), big, font=load_font('extrabold', size), fill=c(col), anchor='mm')
    d.text((W // 2, 800), sub, font=load_font('regular', 34), fill=c(GRAY), anchor='mm')
    d.text((W // 2, 1760), '정보 정리용 · 쿠팡 파트너스 활동으로 수수료를 받을 수 있음', font=load_font('regular', 26), fill=c(GRAY), anchor='mm')
    im.save(path)
    return path


def main():
    tmp = tempfile.mkdtemp()
    try:
        frames = [frame(*s, os.path.join(tmp, f'f{i}.png')) for i, s in enumerate(SCENES)]
        audio = os.path.join(tmp, 'nar.mp3')
        _, bounds = generate_narration_timed(NARRATION, output_path=audio)
        phrases = make_subtitle_phrases(bounds)
        dur = get_audio_duration(audio)
        build_video_multi(frames, audio, output_path=OUT, duration=dur, bgm_path=pick_bgm(), phrases=phrases, work_dir=tmp)
        print('완료:', OUT, f'{dur:.1f}초')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
