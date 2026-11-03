#!/usr/bin/env python3
"""오슬로 텀블러 릴스(2026-10-31): 대비형 훅·약 30초. SHOP_VOICE / SHOP_OUT / SHOP_PREVIEW"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-11-03_써모스보온병'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_therm_anim.mp4'
C1 = C2 = '08_써모스보온병_클로징.jpg'
SCENES = [
    dict(kind='check', card=C1, title='써모스 FFX-751K 750ml', big='판매가는 싸도 총액은 달라요', small='네이버 스마트스토어 · 2026-11-03 조회', col=RED,
         items=['고캠프 45,000원 + 배송비 3,000원', '도심산장 46,750원 · 무료배송', '총액 48,000원과 46,750원'],
         say='써모스 FFX-751K 750ml, 판매가는 고캠프가 낮은데 배송비를 더하면 도심산장이 더 싸요. 총액이 4만 8천 원과 4만 6천 7백 50원이에요.'),
    dict(kind='bars', card=C2, title='트래블킹 1.2L', big='판매처별 가격이 달라요', small='세 곳 모두 무료배송으로 표기', col=GOLD,
         rows=[('도심산장', 45810, RED), ('고캠프', 44100, GREEN), ('에어마운틴', 44100, GOLD)], gap='도심산장 배송 문구는 결제 화면에서 확인',
         say='트래블킹 1.2리터는 고캠프와 에어마운틴이 4만 4천 1백 원, 도심산장이 4만 5천 8백 10원이에요.'),
    dict(kind='check', card=C1, title='같은 트래블킹 1.2L', big='사양 표기가 달라요', small='판매자가 입력한 사양 기준', col=GOLD,
         items=['도심산장·고캠프 지름 9.5cm · 말레이시아산', '에어마운틴 지름 11cm · 중국산', '컵홀더에 넣는다면 직접 확인'],
         say='같은 트래블킹 1.2리터인데 지름이 9.5센티와 11센티, 원산지도 말레이시아와 중국으로 달리 적혀 있어요.'),
    dict(kind='check', card=C2, title='결제 전 확인', big='총액과 용량부터', small='판매처마다 금액이 달라요', col=RED,
         items=['모델명과 용량', '배송비 포함 총액', '쿠팡은 옵션·배송비 직접 확인'],
         say='모델명과 용량, 배송비를 더한 총액을 먼저 보고, 쿠팡은 옵션과 배송비를 직접 확인해 보세요.'),
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
