#!/usr/bin/env python3
"""엔드그레인 도마 쿠팡 표기가 낮은 순 Top3(2026-10-20). 순위 기준은 화면에 명시. SHOP_VOICE / SHOP_OUT / SHOP_PREVIEW"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-10-20_도마Top3'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_top3_anim.mp4'
ROWS = [('1위 WHH', 32000, GREEN), ('2위 LOVFIR', 34800, GOLD), ('3위 WHH', 36000, GOLD)]
SCENES = [
    dict(kind='bars', card='A', title='엔드그레인 도마 · 쿠팡 표기가', big='낮은 순 Top3', small='검색 상위 10개 중 · 2026-10-20 조회', col=GOLD,
         say='엔드그레인 도마, 쿠팡 표기가가 낮은 순으로 세 개를 골라봤어요. 검색 상위 열 개 기준이에요.'),
    dict(kind='price', card='C', title='3위 · WHH 아카시아 원목 도마', n=36000, small='무료배송 · 로켓배송 아님', col=GOLD,
         say='3위는 3만 6천 원. 아카시아 원목 도마고, 로켓배송은 아니에요.'),
    dict(kind='price', card='B', title='2위 · LOVFIR 고급나무도마', n=34800, small='로켓배송 표기', col=GOLD,
         say='2위는 3만 4천 8백 원. 로켓배송 표기예요.'),
    dict(kind='price', card='A', title='1위 · WHH 아카시나무 도마', n=32000, small='로켓배송 표기', col=GREEN,
         say='1위는 3만 2천 원. 아카시나무 도마고, 로켓배송 표기예요.'),
    dict(kind='check', card='A', title='순위 기준', big='쿠팡 표기가 낮은 순', small='크기·두께는 목록마다 달라요', col=RED,
         items=['검색 상위 10개 중 가격순', '크기·두께(cm)가 같은지', '접합 방식·세척 안내'],
         say='순위 기준은 쿠팡 표기가 낮은 순이에요. 크기와 두께는 목록마다 다르니, 가격을 먼저 보는 분은 이 세 개부터 비교해 보세요.'),
    dict(kind='cta', title='저장해두세요', big='살 때 꺼내보기', small='직접 써본 후기 아님 · 쿠팡 파트너스 수수료', col=GOLD,
         say='저장해 두고, 살 때 꺼내 보세요. 도마 교체 시기 정리는 블로그에 있어요.'),
]
_bgs = {}


def big_bg(i):
    f = '07_엔드그레인도마_클로징.jpg' if i % 2 == 0 else '01_엔드그레인도마_대표이미지.jpg'
    if f not in _bgs:
        _bgs[f] = A.cover(f'{IMG}/{f}', 0.5)
    return _bgs[f]


def render(sc, i, p, t, t01, work):
    im = A.bg_frame(big_bg(i), t01, 1 if i % 2 == 0 else -1)
    k = sc['kind']
    if k == 'price':
        A.banner(im, sc['title'], '', sc['small'], sc['col'], p, countup=(sc['n'], '원'))
        A.product_card(im, f"{IMG}/prod_{sc['card']}.jpg", max(0.0, (t - 0.15) / 0.7), 610, 440)
        return _foot(im)
    A.banner(im, sc['title'], sc.get('big', ''), sc.get('small', ''), sc['col'], p)
    if k == 'bars':
        A.product_card(im, f"{IMG}/prod_{sc['card']}.jpg", max(0.0, (t - 0.15) / 0.7), 610, 400)
        A.bars(im, ROWS, 1190, max(0.0, (t - 0.45) / 1.2), gap='가격 기준 순위')
    elif k == 'check':
        A.product_card(im, f"{IMG}/prod_{sc['card']}.jpg", max(0.0, (t - 0.15) / 0.7), 610, 360)
        A.checklist(im, sc['items'], 1100, max(0.0, (t - 0.5) / 1.5))
    else:
        A.bookmark(im, max(0.0, (t - 0.2) / 0.8), t)
        if t > 0.8:
            A.panel(im, [90, 1110, A.W - 90, 1230], alpha=225)
            ImageDraw.Draw(im).text((A.W // 2, 1170), '블로그에 정리가 있어요', font=load_font('bold', 42), fill=(255, 255, 255), anchor='mm')
    return _foot(im)


def _foot(im):
    A.foot(im)
    return im


if __name__ == '__main__':
    A.run(SCENES, render, OUT, preview=bool(os.environ.get('SHOP_PREVIEW')))
