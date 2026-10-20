#!/usr/bin/env python3
"""엔드그레인 도마 릴스 2(교체 신호 + 소재별 표기가, 2026-10-20). SHOP_VOICE / SHOP_OUT / SHOP_PREVIEW"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-10-16_엔드그레인도마'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_ag2_anim.mp4'
SCENES = [
    dict(kind='check', card='A', title='도마 교체 신호 · 기사 정리', big='칼자국에 손톱이 걸리면', small='위키트리 2026-07-07 · 레이디경향 기사 기준', col=RED,
         items=['손톱이 걸리는 깊은 칼자국', '씻어도 안 빠지는 냄새·얼룩', '뒤틀림이나 갈라짐'],
         say='도마 칼자국에 손톱이 걸릴 정도면 교체를 고려하라는 기사가 있어요. 냄새나 얼룩이 안 빠지거나 뒤틀려도 교체 신호로 봐요.'),
    dict(kind='bars', card='B', title='새로 산다면 · 쿠팡 표기가', big='엔드그레인 도마', small='2026-10-20 조회 · 상위 목록 기준', col=GOLD,
         rows=[('아카시아', 36000, GREEN), ('월넛', 59000, GOLD), ('편백', 91000, GOLD)], gap='소재별로 달랐어요',
         say='같은 엔드그레인 도마도 소재별로 쿠팡 표기가가 달랐어요. 아카시아 3만 6천 원, 월넛 5만 9천 원, 편백 9만 1천 원이에요.'),
    dict(kind='bars', card='B', title='같은 이름 월넛 도마', big='59,000 vs 64,000원', small='옵션 차이일 수 있어요', col=RED,
         rows=[('목록 A', 59000, GREEN), ('목록 B', 64000, GOLD)], gap='5,000원 차이',
         say='같은 이름의 월넛 도마인데 목록가가 5천 원 차이였어요. 옵션이 달라서일 수 있으니 상세 페이지를 확인하세요.'),
    dict(kind='check', card='C', title='결제 전 확인', big='크기·두께·세척 안내', small='목록마다 크기가 달라요', col=RED,
         items=['수종과 크기·두께(cm)', '접합 방식', '식기세척기 가능 여부'],
         say='수종과 크기, 접합 방식, 식기세척기 가능 여부를 먼저 확인하세요.'),
    dict(kind='cta', title='저장해두세요', big='살 때 꺼내보기', small='직접 써본 후기 아님 · 쿠팡 파트너스 수수료', col=GOLD,
         say='저장해 두고, 살 때 꺼내 보세요. 도마 교체 시기 정리는 블로그에 있어요.'),
]
_bgs = {}


def big_bg(i):
    f = '07_엔드그레인도마_클로징.jpg' if i % 2 == 0 else '01_엔드그레인도마_대표이미지.jpg'
    if f not in _bgs:
        _bgs[f] = A.cover(f'{IMG}/{f}', 0.5)
    return _bgs[f]


def render(sc, i, p, t, t01, work):
    im = A.bg_frame(big_bg(i), t01, 1 if i % 2 == 0 else -1)
    k = sc['kind']
    A.banner(im, sc['title'], sc.get('big', ''), sc.get('small', ''), sc['col'], p)
    if k == 'bars':
        A.product_card(im, f"{IMG}/prod_{sc['card']}.jpg", max(0.0, (t - 0.15) / 0.7), 610, 400)
        A.bars(im, sc['rows'], 1190 if len(sc['rows']) > 2 else 1230, max(0.0, (t - 0.45) / 1.2), gap=sc.get('gap'))
    elif k == 'check':
        A.product_card(im, f"{IMG}/prod_{sc['card']}.jpg", max(0.0, (t - 0.15) / 0.7), 610, 360)
        A.checklist(im, sc['items'], 1100, max(0.0, (t - 0.5) / 1.5))
    else:
        A.bookmark(im, max(0.0, (t - 0.2) / 0.8), t)
        if t > 0.8:
            A.panel(im, [90, 1110, A.W - 90, 1230], alpha=225)
            ImageDraw.Draw(im).text((A.W // 2, 1170), '블로그에 정리가 있어요', font=load_font('bold', 42), fill=(255, 255, 255), anchor='mm')
    A.foot(im)
    return im


if __name__ == '__main__':
    A.run(SCENES, render, OUT, preview=bool(os.environ.get('SHOP_PREVIEW')))
