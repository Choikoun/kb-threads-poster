#!/usr/bin/env python3
"""오슬로 텀블러 릴스(2026-10-31): 대비형 훅·약 30초. SHOP_VOICE / SHOP_OUT / SHOP_PREVIEW"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-10-31_오슬로텀블러'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_oslo_anim.mp4'
C1, C2 = '01_오슬로텀블러_대표이미지.jpg', '08_오슬로텀블러_클로징.jpg'
SCENES = [
    dict(kind='check', card=C1, title='오슬로 아웃백 500ml', big='같은 모델인데 총액이 달라요', small='네이버 스마트스토어 · 2026-10-31 조회', col=RED,
         items=['ANA스토어 12,800원 + 배송비 3,000원', '김씨하우스 11,900원 + 배송비 3,000원', '총액 15,800원과 14,900원'],
         say='오슬로 아웃백 500ml, 판매자에 따라 배송비까지 더한 총액이 만 5천 8백 원과 만 4천 9백 원으로 갈려요.'),
    dict(kind='bars', card=C2, title='오슬로 밀크 450ml', big='배송비를 더해 비교하세요', small='쿠팡은 목록 표기가 · 옵션·배송비는 확인하지 못했어요', col=GOLD,
         rows=[('네이버 판매가', 15500, GOLD), ('네이버 총액', 18500, RED), ('쿠팡 목록', 17000, GREEN)], gap='네이버는 배송비 3,000원이 별도예요',
         say='밀크 450ml는 네이버 판매가 만 5천 5백 원에 배송비 3천 원이 붙어 1만 8천 5백 원, 쿠팡 목록은 1만 7천 원이에요.'),
    dict(kind='check', card=C1, title='같은 아웃백 500ml', big='지름 표기가 달라요', small='판매자가 입력한 사양 기준', col=GOLD,
         items=['ANA스토어 지름 7.4cm', '김씨하우스 지름 5cm', '컵홀더에 넣는다면 직접 확인'],
         say='같은 아웃백 500ml인데 지름이 7.4센티와 5센티로 달리 적혀 있어요. 컵홀더에 넣는다면 직접 확인하세요.'),
    dict(kind='check', card=C2, title='결제 전 확인', big='총액과 용량부터', small='판매자마다 금액이 달라요', col=RED,
         items=['용량(ml)과 모델명', '배송비 포함 총액', '쿠팡은 옵션·배송비 직접 확인'],
         say='용량과 모델명, 배송비를 더한 총액을 먼저 보고, 쿠팡은 옵션과 배송비를 직접 확인해 보세요.'),
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
