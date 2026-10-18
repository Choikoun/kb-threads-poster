#!/usr/bin/env python3
"""카이 손톱깎이 릴스(shop_anim 엔진). SHOP_VOICE=gemini:Kore / SHOP_OUT / SHOP_PREVIEW"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-10-16_카이손톱깎이'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_kai_anim.mp4'
NV, CP = GOLD, GREEN
SCENES = [
    dict(kind='bars', card='M', title='카이 손톱깎이 중(M) · 2026-10-16', big='중(M) 사이즈' + chr(10) + '1,000원 차이', col=RED,
         rows=[('네이버 N펀키보이', 4800, NV), ('쿠팡 로켓 · 중', 5800, CP)], gap='표기가 기준 · 모델번호 확인 필요',
         say='카이 손톱깎이 중 사이즈, 네이버는 4천 8백 원, 쿠팡은 5천 8백 원으로 표기됐어요.'),
    dict(kind='bars', card='S', title='소(S) 사이즈', big='4,000~5,100원', small='네이버 · 쿠팡 로켓 5,000원', col=GOLD,
         rows=[('네이버 N펀키보이', 4000, NV), ('네이버 일상라이프', 5100, NV), ('쿠팡 로켓 · 소', 5000, CP)],
         say='소 사이즈는 4천 원에서 5천 1백 원 사이였어요.'),
    dict(kind='bars', card='L', title='대(L) 사이즈', big='6,500 / 6,900원', small='네이버 119 일자 L · 쿠팡 로켓 세트 L', col=GOLD,
         rows=[('네이버 119 일자 L', 6500, NV), ('쿠팡 로켓 세트 L', 6900, CP)],
         say='대 사이즈는 6천 5백 원과 6천 9백 원이에요.'),
    dict(kind='check', card='M', title='결제 전 확인', big='품번이 먼저', small='001 · 003 · 119 / 소·중·대', col=RED,
         items=['품번(KF 번호)이 같은지', '사이즈 S·M·L이 같은지', '곡선날·직선날이 같은지'],
         say='소중대 표기만으론 모델을 알 수 없어요. 품번과 날 모양을 먼저 확인하세요.'),
    dict(kind='cta', title='저장해두세요', big='살 때 꺼내보기', small='직접 써본 후기 아님 · 쿠팡 파트너스 수수료', col=GOLD,
         say='저장해 두고, 살 때 꺼내 보세요. 자세한 비교는 블로그에 있어요.'),
]
_bgs = {}


def big_bg(i):
    f = '01_카이손톱깎이_대표이미지.jpg' if i % 2 == 0 else '07_카이손톱깎이_클로징.jpg'
    if f not in _bgs:
        _bgs[f] = A.cover(f'{IMG}/{f}', 0.55)
    return _bgs[f]


def render(sc, i, p, t, t01, work):
    im = A.bg_frame(big_bg(i), t01, 1 if i % 2 == 0 else -1)
    k = sc['kind']
    A.banner(im, sc['title'], sc['big'], sc.get('small', ''), sc['col'], p)
    if k == 'bars':
        A.product_card(im, f"{IMG}/prod_{sc['card']}.jpg", max(0.0, (t - 0.15) / 0.7), 610, 400)
        A.bars(im, sc['rows'], 1230, max(0.0, (t - 0.45) / 1.2), gap=sc.get('gap'))
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
