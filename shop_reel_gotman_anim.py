#!/usr/bin/env python3
"""고트만 밀폐용기 릴스(2026-10-21): 같은 이름 가격 격차 훅. SHOP_VOICE / SHOP_OUT / SHOP_PREVIEW"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-10-21_고트만밀폐용기'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_gotman_anim.mp4'
SCENES = [
    dict(kind='bars', card='A', title='고트만 밀폐용기 직3호 블랙 · 쿠팡', big='11,300 vs 39,600원', small='같은 이름 · 2026-10-21 조회', col=RED,
         rows=[('목록 A', 11300, GREEN), ('목록 B', 39600, GOLD)], gap='28,300원 차이',
         say='고트만 밀폐용기 직3호 블랙이 쿠팡 목록에서 1만 1천 3백 원과 3만 9천 6백 원으로 표기됐어요.'),
    dict(kind='bars', card='B', title='고트만 밀폐용기 직5호 블랙 · 쿠팡', big='26,600 vs 39,060원', small='같은 이름 · 옵션 차이일 수 있어요', col=GOLD,
         rows=[('목록 A', 26600, GREEN), ('목록 B', 39060, GOLD)], gap='12,460원 차이',
         say='직5호 블랙도 2만 6천 6백 원과 3만 9천 6십 원으로 갈렸어요. 옵션이나 수량 차이일 수 있어요.'),
    dict(kind='bars', card='C', title='단품 쿠팡 표기가 일부', big='호수마다 달라요', small='직3호 · 정사각3호 · 정3호', col=GOLD,
         rows=[('직3호 블랙 A', 11300, GREEN), ('정사각 3호', 21660, GREEN), ('정3호 블랙', 40500, GOLD)],
         say='단품은 1만 원대부터 4만 원대까지 표기됐어요.'),
    dict(kind='bars', card='D', title='세트 쿠팡 표기가', big='7종 vs 8종', small='구성 용기와 용량은 확인하지 못했어요', col=GOLD,
         rows=[('7종 세트 화이트', 91200, GREEN), ('8종 세트 블랙', 110440, GOLD)], gap='구성이 달라 단순 비교는 어려워요',
         say='세트는 7종이 9만 1천 2백 원, 8종이 11만 4백 4십 원이에요. 구성이 달라 단순 비교는 어려워요.'),
    dict(kind='check', card='A', title='결제 전 확인', big='호수·용량·옵션', small='같은 이름도 목록마다 달라요', col=RED,
         items=['호수와 색상', '용량(ml)·크기(cm)', '낱개인지 묶음인지'],
         say='호수와 색상, 용량, 낱개인지 묶음인지 먼저 맞춰 보세요.'),
    dict(kind='cta', title='저장해두세요', big='살 때 꺼내보기', small='직접 써본 후기 아님 · 쿠팡 파트너스 수수료', col=GOLD,
         say='저장해 두고, 살 때 꺼내 보세요. 자세한 가격 정리는 블로그에 있어요.'),
]
_bgs = {}


def big_bg(i):
    f = '07_고트만밀폐용기_클로징.jpg' if i % 2 == 0 else '01_고트만밀폐용기_대표이미지.jpg'
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
