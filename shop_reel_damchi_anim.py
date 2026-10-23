#!/usr/bin/env python3
"""담치락 밀폐용기 릴스(2026-10-23): 한 상품 옵션 11개, 28,400~299,800원. SHOP_VOICE / SHOP_OUT / SHOP_PREVIEW"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-10-23_담치락밀폐용기'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_damchi_anim.mp4'
SCENES = [
    dict(kind='bars', card='A', title='담치락 밀폐용기 · 쿠팡 옵션 11개', big='28,400 ~ 299,800원', small='같은 상품번호 · 2026-10-23 조회', col=RED,
         rows=[('시그니처 세트', 99800, GREEN), ('프라임 세트', 164800, GOLD), ('메가 세트', 299800, GOLD)], gap='단품 1호는 28,400원부터',
         say='담치락 밀폐용기는 쿠팡 한 상품번호 아래 옵션이 열한 개고, 가격이 2만 8천 4백 원부터 29만 9천 8백 원까지 갈렸어요.'),
    dict(kind='bars', card='A', title='담치락 호수별 단품', big='1호~4호', small='배송비 포함 표기 · 호수별 용량은 확인하지 못했어요', col=GOLD,
         rows=[('1호', 28400, GREEN), ('2호', 33400, GREEN), ('3호', 38400, GOLD), ('4호', 43300, GOLD)],
         say='단품은 1호가 2만 8천 4백 원, 4호가 4만 3천 3백 원이에요. 호수마다 5천 원 안팎씩 올라가요.'),
    dict(kind='bars', card='A', title='담치락 세트 옵션', big='99,800 ~ 299,800원', small='무료배송 표기 · 세트별 구성은 확인하지 못했어요', col=GOLD,
         rows=[('시그니처', 99800, GREEN), ('프라임', 164800, GOLD), ('메가', 299800, GOLD)],
         say='세트는 시그니처가 9만 9천 8백 원, 프라임이 16만 4천 8백 원, 메가가 29만 9천 8백 원이에요.'),
    dict(kind='check', card='A', title='결제 전 확인', big='펌프는 별도 옵션', small='반영구 펌프 15,400원', col=RED,
         items=['세트에 어떤 호수가 몇 개인지', '펌프 포함 옵션인지', '배송비 포함인지 무료배송인지'],
         say='펌프는 만 5천 4백 원짜리 별도 옵션이 있어요. 펌프 포함 여부와 세트 구성을 먼저 확인하세요.'),
    dict(kind='cta', title='저장해두세요', big='살 때 꺼내보기', small='직접 써본 후기 아님 · 쿠팡 파트너스 수수료', col=GOLD,
         say='저장해 두고, 살 때 꺼내 보세요. 자세한 가격 정리는 블로그에 있어요.'),
]
_bgs = {}


def big_bg(i):
    f = '06_담치락밀폐용기_클로징.jpg' if i % 2 == 0 else '01_담치락밀폐용기_대표이미지.jpg'
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
