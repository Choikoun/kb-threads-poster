#!/usr/bin/env python3
"""프리파라 밀폐용기 릴스(2026-10-25): 같은 이름 세트 네이버 공식몰 vs 쿠팡 가격 차이. SHOP_VOICE / SHOP_OUT / SHOP_PREVIEW"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-10-25_프리파라밀폐용기'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_pre_anim.mp4'
SCENES = [
    dict(kind='bars', card='A', title='프리파라 브루클린 베이지 17P 세트', big='32,600원 차이', small='네이버 공식몰 vs 쿠팡 · 2026-10-25 조회', col=RED,
         rows=[('네이버 공식몰', 211600, GOLD), ('쿠팡 목록', 179000, GREEN)], gap='같은 이름 · 구성 일치는 확인하지 못했어요',
         say='프리파라 브루클린 베이지 17P 세트가 네이버 공식몰은 21만 1천 6백 원, 쿠팡은 17만 9천 원으로 표기됐어요.'),
    dict(kind='bars', card='A', title='브루클린 11P 세트', big='5,300원 차이', small='네이버 공식몰 vs 쿠팡', col=GOLD,
         rows=[('네이버 공식몰', 149000, GOLD), ('쿠팡 목록', 143700, GREEN)], gap='차이가 작았어요',
         say='11P 세트는 공식몰이 14만 9천 원, 쿠팡이 14만 3천 7백 원으로 차이가 작았어요.'),
    dict(kind='bars', card='B', title='밥팩(냉동밥) 460ml 6P', big='색상별로 달라요', small='네이버 공식몰은 블랙·베이지 모두 64,300원', col=GOLD,
         rows=[('공식몰', 64300, GOLD), ('쿠팡 블랙', 60270, GREEN), ('쿠팡 베이지', 63700, GREEN)],
         say='밥팩 6개입은 공식몰이 6만 4천 3백 원이고, 쿠팡은 블랙이 6만 270원, 베이지가 6만 3천 7백 원이에요.'),
    dict(kind='check', card='B', title='네이버쇼핑 공식몰 평점(리뷰 수)', big='4점대 후반', small='구매자 점수이며 제 평가가 아니에요', col=RED,
         items=['5호 2200ml  4.88 (2,400)', '4호 1.5L  4.9 (367)', '11P 세트  4.91 (298)'],
         say='네이버 공식몰 평점은 4점대 후반이고, 5호 2200ml는 리뷰가 2천 4백 개로 가장 많아요.'),
    dict(kind='check', card='A', title='결제 전 확인', big='색상·구성이 같은지', small='같은 이름도 판매처마다 달라요', col=RED,
         items=['세트 구성과 색상', '공식몰인지 다른 판매자인지', '정가보다 최종 결제가'],
         say='색상과 세트 구성이 같은지 먼저 맞추고, 정가보다 최종 결제가를 비교하세요.'),
    dict(kind='cta', title='저장해두세요', big='살 때 꺼내보기', small='직접 써본 후기 아님 · 쿠팡 파트너스 수수료', col=GOLD,
         say='저장해 두고, 살 때 꺼내 보세요. 자세한 가격 정리는 블로그에 있어요.'),
]
_bgs = {}


def big_bg(i):
    f = '07_프리파라밀폐용기_클로징.jpg' if i % 2 == 0 else '01_프리파라밀폐용기_대표이미지.jpg'
    if f not in _bgs:
        _bgs[f] = A.cover(f'{IMG}/{f}', 0.5)
    return _bgs[f]


def render(sc, i, p, t, t01, work):
    im = A.bg_frame(big_bg(i), t01, 1 if i % 2 == 0 else -1)
    k = sc['kind']
    A.banner(im, sc['title'], sc.get('big', ''), sc.get('small', ''), sc['col'], p)
    if k == 'bars':
        n = len(sc['rows'])
        A.product_card(im, f"{IMG}/prod_{sc['card']}.jpg", max(0.0, (t - 0.15) / 0.7), 610, 380 if n > 3 else 400)
        A.bars(im, sc['rows'], 1230 if n <= 2 else (1190 if n == 3 else 1130), max(0.0, (t - 0.45) / 1.2), gap=sc.get('gap'))
    elif k == 'check':
        A.product_card(im, f"{IMG}/prod_{sc['card']}.jpg", max(0.0, (t - 0.15) / 0.7), 610, 360)
        A.checklist(im, sc['items'], 1100, max(0.0, (t - 0.5) / 1.5))
    else:
        A.bookmark(im, max(0.0, (t - 0.2) / 0.8), t)
        if t > 0.8:
            A.panel(im, [90, 1110, A.W - 90, 1230], alpha=225)
            ImageDraw.Draw(im).text((A.W // 2, 1170), '블로그에 가격 정리가 있어요', font=load_font('bold', 42), fill=(255, 255, 255), anchor='mm')
    A.foot(im)
    return im


if __name__ == '__main__':
    A.run(SCENES, render, OUT, preview=bool(os.environ.get('SHOP_PREVIEW')))
