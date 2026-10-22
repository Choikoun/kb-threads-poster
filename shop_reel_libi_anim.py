#!/usr/bin/env python3
"""리브비 밀폐용기 릴스(2026-10-22): 4개입 개당 가격 + 평점·리뷰 수(네이버쇼핑 표기). SHOP_VOICE / SHOP_OUT / SHOP_PREVIEW"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-10-22_리브비밀폐용기'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_libi_anim.mp4'
SCENES = [
    dict(kind='bars', card='C', title='리브비 밀폐용기 에코젠 400ml · 네이버', big='개당 7% 낮아요', small='2026-10-22 조회 · 할인가 기준', col=RED,
         rows=[('1개', 11800, GOLD), ('4개 개당', 10950, GREEN)], gap='개당 850원 차이',
         say='리브비 밀폐용기 에코젠 400ml는 1개에 1만 1천 8백 원, 4개로 사면 개당 1만 9백 5십 원으로 표기됐어요.'),
    dict(kind='bars', card='C', title='에코젠 4개입 개당 가격', big='용량별로 달라요', small='네이버쇼핑 표기 · 4개 가격÷4', col=GOLD,
         rows=[('400ml', 10950, GREEN), ('650ml', 12475, GOLD), ('900ml', 14300, GOLD)],
         say='4개입을 개당으로 나누면 400ml는 1만 9백 원대, 650ml는 1만 2천 원대, 900ml는 1만 4천 원대예요.'),
    dict(kind='bars', card='C', title='쿠팡 목록 · 같은 금액', big='43,800원 표기', small='네이버 400ml 4개와 금액이 같아요', col=GOLD,
         rows=[('네이버 400ml 4개', 43800, GREEN), ('쿠팡 에코젠 목록', 43800, GOLD)], gap='구성 일치는 확인하지 못했어요',
         say='쿠팡 에코젠 목록에도 4만 3천 8백 원 표기가 있어요. 금액만 같고 구성이 같은지는 확인하지 못했어요.'),
    dict(kind='check', card='C', title='네이버쇼핑 평점·리뷰 수 (표기)', big='4.7대 평점', small='구매자 점수이며 제 평가가 아니에요', col=RED,
         items=['400ml 4개  4.72 (리뷰 69)', '650ml 4개  4.75 (리뷰 67)', '900ml 4개  4.74 (리뷰 43)'],
         say='네이버쇼핑에는 평점이 4점대 중반 이상으로 표기돼 있고, 리뷰는 400ml 4개가 69개로 가장 많아요.'),
    dict(kind='check', card='A', title='결제 전 확인', big='용량·개수·라인', small='에코젠과 냉동 전용은 별개예요', col=RED,
         items=['용량과 1개·4개 옵션', '에코젠인지 냉동 전용인지', '개당 가격으로 환산'],
         say='용량과 개수 옵션, 에코젠인지 냉동 전용 라인인지 먼저 확인하고, 개당 가격으로 비교하세요.'),
    dict(kind='cta', title='저장해두세요', big='살 때 꺼내보기', small='직접 써본 후기 아님 · 쿠팡 파트너스 수수료', col=GOLD,
         say='저장해 두고, 살 때 꺼내 보세요. 자세한 가격 정리는 블로그에 있어요.'),
]
_bgs = {}


def big_bg(i):
    f = '08_리브비밀폐용기_클로징.jpg' if i % 2 == 0 else '01_리브비밀폐용기_대표이미지.jpg'
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
