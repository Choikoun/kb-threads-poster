#!/usr/bin/env python3
"""타파웨어 반찬통 릴스(2026-10-24): 공식몰 세트 표기가·할인율·개당 가격. SHOP_VOICE / SHOP_OUT / SHOP_PREVIEW"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-10-24_타파웨어반찬통'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_tw_anim.mp4'
SCENES = [
    dict(kind='bars', card='B', title='타파웨어 공식몰 세트 · 네이버 표기', big='29,900 ~ 179,000원', small='할인율 23~54% 표기 · 2026-10-24 조회', col=RED,
         rows=[('선물세트', 56000, GREEN), ('보울 패키지', 106700, GOLD), ('실속 24개', 179000, GOLD)], gap='원형 5개세트는 29,900원',
         say='타파웨어 반찬통 공식몰 세트는 네이버쇼핑 표기로 2만 9천 9백 원부터 17만 9천 원까지 갈렸어요.'),
    dict(kind='bars', card='B', title='모듈러 보울 패키지세트', big='정가 237,000원', small='54% 할인 표기 · 정가가 높게 잡혀 있어요', col=GOLD,
         rows=[('정가 표기', 237000, GOLD), ('할인가', 106700, GREEN)], gap='할인율보다 최종가와 구성을 보세요',
         say='모듈러 보울 패키지세트는 정가 23만 7천 원에서 54퍼센트 할인한 10만 6천 7백 원이에요. 할인율보다 최종가와 구성을 보세요.'),
    dict(kind='bars', card='B', title='소분 용기 개당 가격', big='같은 29,900원', small='네이버 공식몰 표기 ÷ 개수', col=RED,
         rows=[('원형 5개세트', 5980, GREEN), ('싱싱블록 미니 4개', 7475, GOLD)], gap='개수와 용량이 달라요',
         say='같은 2만 9천 9백 원이어도 원형 5개세트는 개당 5천 9백 8십 원, 싱싱블록 미니 4개는 개당 7천 4백 7십 5원이에요.'),
    dict(kind='check', card='B', title='네이버쇼핑 평점(리뷰 수)', big='4점대 후반', small='구매자 점수이며 제 평가가 아니에요', col=GOLD,
         items=['원형 5개세트  4.7 (368)', '원터치 선물세트  4.8 (204)', '실속구성 24개  4.88 (346)'],
         say='네이버쇼핑 평점은 4점대 후반이고, 리뷰는 원형 5개세트가 368개로 가장 많았어요.'),
    dict(kind='check', card='B', title='결제 전 확인', big='사용 범위는 모델별', small='같은 타파웨어도 사용 범위가 달라요', col=RED,
         items=['공식몰 표기인지 확인', '세트 개수와 용량 구성', '냉동·전자레인지 사용 범위'],
         say='타파웨어는 모델마다 냉동과 전자레인지 사용 범위가 달라요. 상세 안내를 꼭 확인하세요.'),
    dict(kind='cta', title='저장해두세요', big='살 때 꺼내보기', small='직접 써본 후기 아님 · 쿠팡 파트너스 수수료', col=GOLD,
         say='저장해 두고, 살 때 꺼내 보세요. 자세한 가격 정리는 블로그에 있어요.'),
]
_bgs = {}


def big_bg(i):
    f = '07_타파웨어반찬통_클로징.jpg' if i % 2 == 0 else '01_타파웨어반찬통_대표이미지.jpg'
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
