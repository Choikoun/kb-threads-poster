#!/usr/bin/env python3
"""휴롬 H400 릴스(shop_anim 엔진). SHOP_VOICE=gemini:Kore / SHOP_OUT / SHOP_PREVIEW"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-10-19_휴롬H400'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_hurom_anim.mp4'
NV, CP = GOLD, GREEN
SCENES = [
    dict(kind='bars', card='A', title='휴롬 H400 · 2026-10-19', big='같은 H400인데' + chr(10) + '55,000원 차이', col=RED,
         rows=[('쿠팡 브랜드샵(쿠폰)', 324000, CP), ('쿠팡 오픈마켓', 349000, CP), ('쿠팡 로켓 기본표기', 361620, CP), ('네이버', 379000, NV)],
         say='휴롬 H400이 쿠팡 브랜드샵에서는 32만 4천 원, 네이버에서는 37만 9천 원으로 표기됐어요.', y0=1150),
    dict(kind='bars', card='A', title='정가 표기도 달랐어요', big='599,000 / 499,000원', small='쿠팡 브랜드샵 · 네이버 H400', col=GOLD,
         rows=[('쿠팡 정가', 599000, CP), ('네이버 정가', 499000, NV)],
         say='정가 표기도 59만 9천 원과 49만 9천 원으로 달랐어요.'),
    dict(kind='bars', card='B', title='모델별 표기가', big='H400 · H410 · H430', small='쿠팡 목록 기준', col=GOLD,
         rows=[('H400 (브랜드샵)', 324000, CP), ('H410 (브랜드샵)', 351730, CP), ('H430 (오픈마켓)', 349000, CP)],
         say='H410과 H430도 같이 나오니 모델명부터 확인하세요.'),
    dict(kind='check', card='A', title='결제 전 확인', big='쿠폰 전후 가격', small='모델명 · 색상 · 판매자도 맞춰 보세요', col=RED,
         items=['모델명(H400·H410·H430)', '쿠폰 적용 전·후 가격', '판매자와 보증기간'],
         say='쿠폰 적용 전과 후 가격도 꼭 비교해 보세요.'),
    dict(kind='cta', title='저장해두세요', big='살 때 꺼내보기', small='직접 써본 후기 아님 · 쿠팡 파트너스 수수료', col=GOLD,
         say='저장해 두고, 살 때 꺼내 보세요. 자세한 비교는 블로그에 있어요.'),
]
_bgs = {}


def big_bg(i):
    f = '01_휴롬H400_대표이미지.jpg' if i % 2 == 0 else '07_휴롬H400_클로징.jpg'
    if f not in _bgs:
        _bgs[f] = A.cover(f'{IMG}/{f}', 0.55)
    return _bgs[f]


def render(sc, i, p, t, t01, work):
    im = A.bg_frame(big_bg(i), t01, 1 if i % 2 == 0 else -1)
    k = sc['kind']
    A.banner(im, sc['title'], sc['big'], sc.get('small', ''), sc['col'], p)
    if k == 'bars':
        A.product_card(im, f"{IMG}/prod_{sc['card']}.jpg", max(0.0, (t - 0.15) / 0.7), 610, 400)
        A.bars(im, sc['rows'], sc.get('y0', 1230), max(0.0, (t - 0.45) / 1.2), gap=sc.get('gap'))
    elif k == 'check':
        A.product_card(im, f"{IMG}/prod_{sc['card']}.jpg", max(0.0, (t - 0.15) / 0.7), 610, 360)
        A.checklist(im, sc['items'], 1100, max(0.0, (t - 0.5) / 1.5))
    else:
        A.bookmark(im, max(0.0, (t - 0.2) / 0.8), t)
        if t > 0.8:
            A.panel(im, [90, 1110, A.W - 90, 1230], alpha=225)
            ImageDraw.Draw(im).text((A.W // 2, 1170), '블로그에 전체 비교가 있어요', font=load_font('bold', 42), fill=(255, 255, 255), anchor='mm')
    A.foot(im)
    return im


if __name__ == '__main__':
    A.run(SCENES, render, OUT, preview=bool(os.environ.get('SHOP_PREVIEW')))
