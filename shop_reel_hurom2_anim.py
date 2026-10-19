#!/usr/bin/env python3
"""휴롬 H400 릴스(shop_anim 엔진). SHOP_VOICE=gemini:Kore / SHOP_OUT / SHOP_PREVIEW"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-10-19_휴롬H400'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_hurom2_anim.mp4'
NV, CP = GOLD, GREEN
SCENES = [
    dict(kind='bars', card='A', title='휴롬 H400 · 2026-10-19', big='할인율 45% vs 24%', small='어디가 더 쌀까요?', col=RED,
         rows=[('쿠팡 정가', 599000, CP), ('네이버 정가', 499000, NV)], gap='정가 기준부터 달라요',
         say='할인율 45퍼센트와 24퍼센트, 같은 휴롬 H400인데 어디가 더 쌀까요?'),
    dict(kind='bars', card='A', title='쿠팡 브랜드샵', big='599,000 → 324,000원', small='45% 할인 · 쿠폰 적용 표기', col=GREEN,
         rows=[('쿠팡 정가', 599000, CP), ('쿠팡 할인가', 324000, CP)],
         say='쿠팡 브랜드샵은 정가 59만 9천 원에서 32만 4천 원이에요.'),
    dict(kind='bars', card='A', title='네이버쇼핑', big='499,000 → 379,000원', small='24% 할인', col=GOLD,
         rows=[('네이버 정가', 499000, NV), ('네이버 할인가', 379000, NV)],
         say='네이버는 정가 49만 9천 원에서 37만 9천 원이에요.'),
    dict(kind='bars', card='A', title='최종 결제가 비교', big='324,000 vs 379,000원', small='정가가 달라 할인율은 기준이 안 돼요', col=GOLD,
         rows=[('쿠팡 브랜드샵', 324000, CP), ('네이버', 379000, NV)], gap='55,000원 차이',
         say='정가 기준이 달라서 할인율보다 최종 결제가를 비교해야 해요.'),
    dict(kind='check', card='B', title='결제 전 확인', big='쿠폰 전후 가격', small='모델명 · 판매자도 맞춰 보세요', col=RED,
         items=['쿠폰 적용 전·후 가격', '모델명(H400·H410·H430)', '판매자와 보증기간'],
         say='쿠폰 적용 전후 가격과 모델명도 꼭 확인하세요.'),
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
