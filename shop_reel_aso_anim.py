#!/usr/bin/env python3
"""아소부 텀블러 릴스(2026-10-30): 대비형 훅·약 30초. SHOP_VOICE / SHOP_OUT / SHOP_PREVIEW"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-10-30_아소부텀블러'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_aso_anim.mp4'
C1, C2 = '01_아소부텀블러_대표이미지.jpg', '08_아소부텀블러_클로징.jpg'
SCENES = [
    dict(kind='check', card=C1, title='아소부 퓨라믹 커피 익스프레스 360ml', big='같은 모델명인데 가격이 둘', small='네이버·쿠팡 목록 · 2026-10-30 조회', col=RED,
         items=['네이버 판매가 25,900원', '쿠팡 목록 22,310원', '쿠팡 목록 38,140원'],
         say='아소부 커피 익스프레스 360ml, 쿠팡 목록에는 같은 이름으로 2만 2천 원과 3만 8천 원이 함께 보여요.'),
    dict(kind='bars', card=C2, title='아소부 베스티 460ml', big='채널마다 가격이 달라요', small='쿠팡은 목록 표기가 · 옵션은 확인하지 못했어요', col=GOLD,
         rows=[('정가', 59900, '#8C92A0'), ('네이버', 40900, GOLD), ('쿠팡 목록', 35810, GREEN)], gap='쿠팡에는 50,900원 표기도 있었어요',
         say='베스티 460ml는 정가 5만 9천 9백 원, 네이버 4만 9백 원, 쿠팡 목록 3만 5천 8백 원으로 표기됐어요.'),
    dict(kind='check', card=C1, title='아소부 익스플로러 1L', big='여기는 네이버가 더 낮아요', small='쿠팡은 1L로 표기된 상품 기준', col=GOLD,
         items=['네이버 33,900원', '쿠팡 1L 표기 35,900원', '쿠폰 적용 시 네이버 32,900원'],
         say='익스플로러 1리터는 네이버가 3만 3천 9백 원으로, 쿠팡 1리터 표기 3만 5천 9백 원보다 낮았어요.'),
    dict(kind='check', card=C2, title='결제 전 확인', big='용량과 옵션부터', small='모델마다 금액이 달라요', col=RED,
         items=['모델명과 용량(ml)', '색상별 판매가와 재고', '쿠팡은 옵션 가격 직접 확인'],
         say='모델명과 용량, 색상별 재고를 먼저 보고, 쿠팡은 옵션 가격을 직접 확인해 보세요.'),
    dict(kind='cta', title='저장해두세요', big='살 때 꺼내보기', small='직접 써본 후기 아님 · 제휴 수수료', col=GOLD,
         say='저장해 두고, 살 때 꺼내 보세요. 모델별 가격 정리와 링크는 블로그에 있어요.'),
]
_bgs = {}


def big_bg(i):
    f = C2 if i % 2 == 0 else C1
    if f not in _bgs:
        _bgs[f] = A.cover(f'{IMG}/{f}', 0.5)
    return _bgs[f]


def render(sc, i, p, t, t01, work):
    im = A.bg_frame(big_bg(i), t01, 1 if i % 2 == 0 else -1)
    A.banner(im, sc['title'], sc.get('big', ''), sc.get('small', ''), sc['col'], p)
    k = sc['kind']
    if k == 'bars':
        A.product_card(im, f"{IMG}/{sc['card']}", max(0.0, (t - 0.15) / 0.7), 610, 400)
        A.bars(im, sc['rows'], 1230, max(0.0, (t - 0.45) / 1.2), gap=sc.get('gap'))
    elif k == 'check':
        A.product_card(im, f"{IMG}/{sc['card']}", max(0.0, (t - 0.15) / 0.7), 610, 360)
        A.checklist(im, sc['items'], 1100, max(0.0, (t - 0.5) / 1.5))
    else:
        A.bookmark(im, max(0.0, (t - 0.2) / 0.8), t)
        if t > 0.8:
            A.panel(im, [90, 1110, A.W - 90, 1230], alpha=225)
            ImageDraw.Draw(im).text((A.W // 2, 1170), '블로그에 모델별 가격 정리가 있어요', font=load_font('bold', 40), fill=(255, 255, 255), anchor='mm')
    ImageDraw.Draw(im).text((A.W // 2, 1790), '광고 · 가격 정보 정리용 · 제휴 수수료를 받을 수 있음', font=load_font('bold', 32), fill=(230, 233, 242), anchor='mm')
    return im


if __name__ == '__main__':
    A.run(SCENES, render, OUT, preview=bool(os.environ.get('SHOP_PREVIEW')))
