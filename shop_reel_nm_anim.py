#!/usr/bin/env python3
"""나이몰리 탄소매트 릴스(2026-10-29): 대비형 훅·약 30초. SHOP_VOICE / SHOP_OUT / SHOP_PREVIEW"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-10-29_나이몰리탄소매트'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_nm_anim.mp4'
C1, C2 = '01_나이몰리탄소매트_대표이미지.jpg', '08_나이몰리탄소매트_클로징.jpg'
SCENES = [
    dict(kind='check', card=C1, title='나이몰리 돌체클래식 탄소매트', big='기본가 188,000원인데', small='네이버 스마트스토어 · 2026-10-29 조회', col=RED,
         items=['기본 표기 188,000원', '퀸 옵션은 +105,000~110,000원', '일부 옵션은 품절 표시'],
         say='나이몰리 돌체클래식 기본가는 18만 8천 원인데, 퀸 옵션은 10만 원 넘게 더 붙어요.'),
    dict(kind='bars', card=C2, title='나이몰리 소노세레노', big='정가 절반 표기', small='쿠폰 적용 시 189,000원으로 표기', col=GOLD,
         rows=[('정가', 398000, GOLD), ('표기 판매가', 199000, GREEN)], gap='쿠폰 기한은 이틀 남은 것으로 표시됐어요',
         say='소노세레노는 정가 39만 8천 원을 19만 9천 원으로 표기했고, 쿠폰을 쓰면 18만 9천 원이에요.'),
    dict(kind='check', card=C1, title='판매 페이지에 적힌 사양', big='단계와 모드가 달라요', small='소비전력·크기는 확인하지 못했어요', col=GOLD,
         items=['소노세레노 온도 5단계', '돌체클래식 온도 4단계', '원산지 이탈리아산(에어로코리아)'],
         say='온도 조절은 소노세레노가 5단계, 돌체클래식이 4단계예요. 소비전력과 크기는 확인하지 못했어요.'),
    dict(kind='check', card=C2, title='결제 전 확인', big='옵션 추가금부터', small='모델마다 금액이 달라요', col=RED,
         items=['모델명과 사이즈 옵션 추가금', '쿠폰 적용가와 기한', '인증번호 직접 조회'],
         say='모델명과 옵션 추가금, 쿠폰 기한을 먼저 확인하고, 인증번호도 직접 조회해 보세요.'),
    dict(kind='cta', title='저장해두세요', big='살 때 꺼내보기', small='직접 써본 후기 아님 · 네이버 쇼핑 커넥트 수수료', col=GOLD,
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
            ImageDraw.Draw(im).text((A.W // 2, 1170), '블로그에 가격 정리와 링크가 있어요', font=load_font('bold', 40), fill=(255, 255, 255), anchor='mm')
    ImageDraw.Draw(im).text((A.W // 2, 1790), '광고 · 정보 정리용 · 네이버 쇼핑 커넥트 활동으로 수수료를 받을 수 있음', font=load_font('bold', 32), fill=(230, 233, 242), anchor='mm')
    return im


if __name__ == '__main__':
    A.run(SCENES, render, OUT, preview=bool(os.environ.get('SHOP_PREVIEW')))
