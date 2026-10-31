#!/usr/bin/env python3
"""오슬로 텀블러 릴스(2026-10-31): 대비형 훅·약 30초. SHOP_VOICE / SHOP_OUT / SHOP_PREVIEW"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-11-01_스탠리텀블러'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_stan_anim.mp4'
C1 = C2 = '08_스탠리텀블러_클로징.jpg'
SCENES = [
    dict(kind='check', card=C1, title='스탠리 클래식 보틀', big='1.4L가 1.9L보다 비싸요', small='네이버 스마트스토어 · 2026-11-01 조회', col=RED,
         items=['1.4L 106,000원 + 배송비 39,000원', '1.9L 108,000원 · 무료배송', '총액 145,000원과 108,000원'],
         say='스탠리 클래식 보틀, 1.4리터가 1.9리터보다 총액이 더 비싸요. 1.4리터는 배송비가 3만 9천 원 붙어서 14만 5천 원이에요.'),
    dict(kind='bars', card=C2, title='스탠리 GO 473ml', big='쿠팡 목록과 차이가 커요', small='쿠팡은 목록 표기가 · 옵션·배송비는 확인하지 못했어요', col=GOLD,
         rows=[('네이버 총액', 52500, RED), ('쿠팡 목록 낮은 표기', 24430, GREEN), ('쿠팡 목록 높은 표기', 34900, GOLD)], gap='판매자와 옵션은 직접 확인하세요',
         say='GO 473ml는 네이버 총액이 5만 2천 5백 원, 쿠팡 목록은 2만 4천 4백 원과 3만 4천 9백 원으로 보여요.'),
    dict(kind='check', card=C1, title='클래식은 해외직배송', big='받기까지 시간이 걸려요', small='판매 페이지 안내 기준', col=GOLD,
         items=['유럽 발송 · 영업일 7일 안팎', '구매대행으로 유통된다고 표기', '1.9L 페이지 모델명에 1.4리터 표기'],
         say='클래식 두 상품은 해외직배송이고 수령까지 영업일로 7일쯤 걸려요. 1.9리터 페이지는 모델명 칸에 1.4리터가 적혀 있어서 용량을 확인하세요.'),
    dict(kind='check', card=C2, title='결제 전 확인', big='총액과 용량부터', small='판매자마다 금액이 달라요', col=RED,
         items=['용량과 모델명', '배송비 포함 총액', '쿠팡은 옵션·배송비 직접 확인'],
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
