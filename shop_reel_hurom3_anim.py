#!/usr/bin/env python3
"""휴롬 모델 구분 릴스(shop_anim 엔진). SHOP_VOICE=gemini:Kore / SHOP_OUT / SHOP_PREVIEW"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-10-19_휴롬H400'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_hurom3_anim.mp4'
NV, CP = GOLD, GREEN
SCENES = [
    dict(kind='bars', card='A', title='휴롬 착즙기 · 2026-10-19', big='H400 H410 H430', small='이름만 비슷한 3종, 가격 표기는요?', col=RED,
         rows=[('H400 정가', 599000, CP), ('H410 정가', 699000, NV)], gap='정가부터 10만 원 차이',
         say='휴롬 H400, H410, H430. 이름이 비슷해서 검색하면 섞여 나와요.'),
    dict(kind='bars', card='A', title='쿠팡 브랜드샵 표기', big='H400 324,000원', small='정가 599,000원 · 쿠폰 적용 표기', col=GREEN,
         rows=[('H400 정가', 599000, CP), ('H400 표기가', 324000, CP)],
         say='H400은 정가 59만 9천 원에, 32만 4천 원으로 표기됐어요.'),
    dict(kind='bars', card='B', title='쿠팡 브랜드샵 표기', big='H410 351,730원', small='정가 699,000원', col=GOLD,
         rows=[('H410 정가', 699000, NV), ('H410 표기가', 351730, NV)],
         say='H410은 정가 69만 9천 원에, 35만 1천7백 원으로 표기됐어요.'),
    dict(kind='bars', card='B', title='쿠팡 오픈마켓 표기', big='H430 349,000원', small='정가는 적혀 있지 않았어요', col=GOLD,
         rows=[('H430 표기가', 349000, NV), ('H400 표기가', 324000, CP)],
         say='H430은 오픈마켓에서 34만 9천 원이었고, 정가는 적혀 있지 않았어요.'),
    dict(kind='check', card='B', title='가격만 보면 헷갈려요', big='모델명 먼저 확인', small='사양은 상세 페이지 사양표로', col=RED,
         items=['모델명 H400·H410·H430', '색상과 구성품', '판매자와 보증기간'],
         say='가격만 보면 다른 모델을 비교하게 돼요. 모델명부터 확인하세요.'),
    dict(kind='cta', title='저장해두세요', big='살 때 꺼내보기', small='직접 써본 후기 아님 · 쿠팡 파트너스 수수료', col=GOLD,
         say='저장해 두고, 살 때 꺼내 보세요. 전체 가격 비교는 블로그에 있어요.'),
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
