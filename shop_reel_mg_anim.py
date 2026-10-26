#!/usr/bin/env python3
"""태안 물결카라반 릴스(2026-10-26): 요일별 요금 격차. SHOP_VOICE / SHOP_OUT / SHOP_PREVIEW"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-10-26_태안물결카라반'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_mg_anim.mp4'
SCENES = [
    dict(kind='bars', card='A', title='태안 물결카라반 · 오션뷰 카라반', big='토요일은 평일의 3.5배', small='쿠팡 여행 표기 · 12월 첫째 주 · 판매처 제공 이미지', col=RED,
         rows=[('월~목', 99000, GREEN), ('금', 179000, GOLD), ('토', 349000, RED)],
         say='태안 물결카라반 오션뷰 카라반은 평일 9만 9천 원인데, 토요일은 34만 9천 원으로 표기됐어요.'),
    dict(kind='bars', card='A', title='감성 커플카라반 (기준 2인·최대 3인)', big='평일 49,000원부터', small='쿠팡 여행 표기 · 12월 첫째 주', col=GOLD,
         rows=[('월~목', 49000, GREEN), ('일', 69000, GREEN), ('금', 99000, GOLD), ('토', 149000, GOLD)],
         say='커플 카라반은 월요일부터 목요일까지 4만 9천 원, 금요일 9만 9천 원, 토요일 14만 9천 원이에요.'),
    dict(kind='bars', card='A', title='현장 추가 요금', big='바비큐 30,000원', small='숙소 공지 기준', col=GOLD,
         rows=[('바비큐(4인)', 30000, GOLD), ('불멍', 20000, GREEN), ('노천탕 냉수', 20000, GREEN), ('노천탕 온수', 50000, RED)],
         say='바비큐는 4인 기준 3만 원, 불멍은 2만 원, 노천탕은 냉수 2만 원, 온수 5만 원이 현장에서 추가돼요.'),
    dict(kind='check', card='A', title='쿠팡 여행 상품평 10개', big='의견이 엇갈려요', small='글쓴이 추천은 개인 의견이에요', col=RED,
         items=['서비스·접근성은 보통 수준', '시설·청결은 별로~나쁨 표시', '사진과 다르다는 의견도 있어요'],
         say='쿠팡 상품평은 시설과 청결 점수가 낮은 편이고, 서비스와 접근성은 보통이었어요. 의견이 엇갈리니 기대치를 정하고 예약하세요.'),
    dict(kind='check', card='A', title='예약 전 확인', big='요일·인원·추가 요금', small='아기 포함 인원은 예약처 확인', col=RED,
         items=['가는 날 요일(금·토가 비싸요)', '객실 최대 인원과 아기 포함 여부', '체크인 15시, 입실은 20시까지'],
         say='가는 날 요일과 최대 인원, 아기가 인원에 들어가는지 먼저 확인하세요. 입실은 저녁 8시까지예요.'),
    dict(kind='cta', title='저장해두세요', big='갈 때 꺼내보기', small='직접 이용 후기 아님 · 쿠팡 파트너스 수수료', col=GOLD,
         say='저장해 두고, 예약할 때 꺼내 보세요. 자세한 요금 정리는 블로그에 있어요.'),
]
_bgs = {}


def big_bg(i):
    f = '08_태안물결카라반_클로징.jpg' if i % 2 == 0 else '01_태안물결카라반_대표이미지.jpg'
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
            ImageDraw.Draw(im).text((A.W // 2, 1170), '블로그에 요금 정리가 있어요', font=load_font('bold', 42), fill=(255, 255, 255), anchor='mm')
    A.foot(im)
    return im


if __name__ == '__main__':
    A.run(SCENES, render, OUT, preview=bool(os.environ.get('SHOP_PREVIEW')))
