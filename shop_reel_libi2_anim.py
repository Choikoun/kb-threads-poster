#!/usr/bin/env python3
"""리브비 밀폐용기 릴스 2(2026-10-22): 세트 구성별 가격 격차 + 냉동 전용 라인. SHOP_VOICE / SHOP_OUT / SHOP_PREVIEW"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import shop_anim as A
from shop_anim import *
import shop_reel_libi_anim as B

IMG = B.IMG
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_libi2_anim.mp4'
SCENES = [
    dict(kind='bars', card='C', title='리브비 에코젠 세트 · 네이버 표기', big='37,800 ~ 177,800원', small='세트 구성에 따라 4배 넘게 갈려요 · 2026-10-22 조회', col=RED,
         rows=[('3종 세트', 79800, GREEN), ('4종 세트', 119800, GOLD), ('4종 세트', 177800, GOLD)], gap='2종 세트는 37,800원부터',
         say='리브비 에코젠 세트는 네이버쇼핑 표기로 3만 7천 8백 원부터 17만 7천 8백 원까지 갈렸어요.'),
    dict(kind='check', card='C', title='세트마다 구성이 달라요', big='이름은 같은 4종', small='개수와 용량 조합이 달라서 단순 비교는 어려워요', col=GOLD,
         items=['4종 세트 119,800원', '4종 세트 126,800원', '4종 세트 177,800원'],
         say='같은 4종 세트도 119,800원, 126,800원, 177,800원으로 나뉘어요. 개수와 용량 조합이 달라서예요.'),
    dict(kind='bars', card='A', title='냉동 전용 용기(엘라스토머) · 4개', big='용량별 표기가', small='에코젠과는 별개 라인이에요', col=GOLD,
         rows=[('300ml', 21600, GREEN), ('600ml', 29700, GOLD), ('1500ml', 43800, GOLD)],
         say='냉동 전용 용기는 따로 있어요. 4개 가격이 300ml는 2만 1천 6백 원, 600ml는 2만 9천 7백 원, 1500ml는 4만 3천 8백 원이에요.'),
    dict(kind='check', card='C', title='결제 전 확인', big='구성·용량·라인', small='필요한 용량부터 정하세요', col=RED,
         items=['세트의 개수와 용량 조합', '에코젠인지 냉동 전용인지', '개당 가격으로 환산'],
         say='세트는 개수와 용량 조합부터 확인하고, 에코젠인지 냉동 전용 라인인지도 맞춰 보세요.'),
    dict(kind='cta', title='저장해두세요', big='살 때 꺼내보기', small='직접 써본 후기 아님 · 쿠팡 파트너스 수수료', col=GOLD,
         say='저장해 두고, 살 때 꺼내 보세요. 자세한 가격 정리는 블로그에 있어요.'),
]
_bgs = {}


def big_bg(i):
    f = '01_리브비밀폐용기_대표이미지.jpg' if i % 2 == 0 else '08_리브비밀폐용기_클로징.jpg'
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
            ImageDraw.Draw(im).text((A.W // 2, 1170), '블로그에 가격 정리가 있어요', font=load_font('bold', 42), fill=(255, 255, 255), anchor='mm')
    A.foot(im)
    return im


if __name__ == '__main__':
    A.run(SCENES, render, OUT, preview=bool(os.environ.get('SHOP_PREVIEW')))
