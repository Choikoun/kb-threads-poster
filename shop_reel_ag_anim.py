#!/usr/bin/env python3
"""엔드그레인 도마 릴스 애니메이션 버전(shop_anim 엔진). SHOP_VOICE / SHOP_OUT / SHOP_PREVIEW 환경변수 지원"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-10-16_엔드그레인도마'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_ag_anim.mp4'
ROWS = [('쿠팡 로켓 목록 A', 86200, GREEN), ('쿠팡 로켓 목록 B', 107150, GOLD)]
RANGES = [('아카시아', 23400, 71440), ('레인트리', 33750, 120000), ('월넛', 19800, 107150), ('편백', 64000, 99750), ('탄화목', 82100, 135460)]
SCENES = [
    dict(kind='hook', card='A', title='엔드그레인 월넛 도마 · 2026-10-16', big='같은 이름인데' + chr(10) + '20,950원 차이', col=RED,
         say='같은 이름의 월넛 엔드그레인 도마인데, 쿠팡 목록가가 2만 950원 차이 났어요.'),
    dict(kind='price', card='A', title='BOUMBI 북미산 월넛 · 목록 A', n=86200, hi=0, small='쿠팡 로켓배송 표기', col=GREEN,
         say='한 목록은 8만 6천 2백 원.'),
    dict(kind='price', card='B', title='BOUMBI 북미산 월넛 · 목록 B', n=107150, hi=1, small='쿠팡 로켓배송 표기', col=GOLD,
         say='다른 목록은 10만 7천 1백 5십 원이에요.'),
    dict(kind='range', title='소재별 쿠팡 목록 가격대', big='2만 원대~13만 원대', small='아카시아·월넛·편백·탄화목', col=GOLD,
         say='아카시아는 2만 3천 원대부터, 탄화목은 13만 원대까지 있었어요.'),
    dict(kind='check', card='C', title='결제 전 확인', big='크기·두께·옵션', small='목록마다 크기가 달라요', col=RED,
         items=['크기·두께(cm)가 같은지', '옵션·구성이 같은지', '접합 방식·세척 안내'],
         say='크기와 두께, 옵션이 같은지 먼저 맞춰 보세요.'),
    dict(kind='check', card='C', title='관리 안내', big='물 담금 · 식기세척기 X', small='레이디경향 2025-07-28 기사 기준', col=GREEN,
         items=['물에 담가 두지 않기', '식기세척기 피하기', '쓴 뒤 세워서 말리기'],
         say='물에 담그거나 식기세척기에 넣는 건 피하라는 안내가 많아요.'),
    dict(kind='cta', title='저장해두세요', big='살 때 꺼내보기', small='직접 써본 후기 아님 · 쿠팡 파트너스 수수료', col=GOLD,
         say='저장해 두고, 살 때 꺼내 보세요. 자세한 비교는 프로필 블로그에 있어요.'),
]
_bgs = {}


def big_bg(i):
    f = '01_엔드그레인도마_대표이미지.jpg' if i % 2 == 0 else '07_엔드그레인도마_클로징.jpg'
    if f not in _bgs:
        _bgs[f] = A.cover(f'{IMG}/{f}', 0.5 if i % 2 == 0 else 0.45)
    return _bgs[f]


def render(sc, i, p, t, t01, work):
    im = A.bg_frame(big_bg(i), t01, 1 if i % 2 == 0 else -1)
    k = sc['kind']
    if k == 'range':
        A.banner(im, sc['title'], sc['big'], sc['small'], sc['col'], p)
        # 범위 막대는 배너 아래가 아니라 중앙(배너 y=190~560 아래 640~)
        A.range_bars(im, RANGES, 640, max(0.0, (t - 0.3) / 1.8))
    else:
        if k == 'price':
            A.banner(im, sc['title'], '', sc['small'], sc['col'], p, countup=(sc['n'], '원'))
        else:
            A.banner(im, sc['title'], sc.get('big', ''), sc.get('small', ''), sc['col'], p)
        if k in ('hook', 'price'):
            A.product_card(im, f"{IMG}/prod_{sc['card']}.jpg", max(0.0, (t - 0.15) / 0.7), 610, 400 if k == 'hook' else 440)
            A.bars(im, ROWS, 1230 if k == 'hook' else 1250, max(0.0, (t - 0.45) / 1.2), hi=sc.get('hi'),
                   gap='같은 이름 · 목록가 20,950원 차이' if k == 'hook' else None)
        elif k == 'check':
            A.product_card(im, f"{IMG}/prod_{sc['card']}.jpg", max(0.0, (t - 0.15) / 0.7), 610, 360)
            A.checklist(im, sc['items'], 1100, max(0.0, (t - 0.5) / 1.5))
        else:
            A.bookmark(im, max(0.0, (t - 0.2) / 0.8), t)
            if t > 0.8:
                A.panel(im, [90, 1110, A.W - 90, 1230], alpha=225)
                ImageDraw.Draw(im).text((A.W // 2, 1170), '프로필 링크 → 블로그에 전체 비교', font=load_font('bold', 42), fill=(255, 255, 255), anchor='mm')
    A.foot(im)
    return im


if __name__ == '__main__':
    A.run(SCENES, render, OUT, preview=bool(os.environ.get('SHOP_PREVIEW')))
