#!/usr/bin/env python3
"""라바제 식기건조대 릴스(2026-10-27, 10-14 글 기준 데이터): 같은 모델명 DLM-8690 쿠팡 표기가 차이. SHOP_VOICE / SHOP_OUT / SHOP_PREVIEW"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-10-14_라바제식기건조대'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_lbz_anim.mp4'
SCENES = [
    dict(kind='bars', card='A', title='라바제 식기건조대 DLM-8690', big='거의 3배 차이', small='쿠팡 목록 표기가 · 2026-10-14 조회', col=RED,
         rows=[('슬림 세로형', 88900, GREEN), ('옵션 목록', 116000, GOLD), ('올스텐 대용량', 209860, GOLD), ('3종세트', 255000, RED)], gap='같은 모델명 · 구성 일치는 확인하지 못했어요',
         say='라바제 식기건조대 DLM-8690이 쿠팡에서 8만 8천 9백 원부터 25만 5천 원까지 다르게 표기됐어요.'),
    dict(kind='check', card='B', title='가격이 갈리는 이유 후보', big='구성이 달라요', small='확정은 못 했어요', col=GOLD,
         items=['3종세트: 건조대·수저통·트레이', '단품: 건조대만 판매', '일본 직수입 · 판매처 차이'],
         say='공식 페이지에서 3종 세트는 건조대, 수저통, 물받이 트레이로 구성돼요. 단품이면 구성이 다를 수 있어요.'),
    dict(kind='check', card='D', title='공식 크기(약)', big='450×300mm', small='세로형 DLM-8690 · 가로형은 538×312mm', col=GOLD,
         items=['세로형 DLM-8690  450×300mm', '가로형 DLM-8563  538×312mm', '가로형 쿠팡 표기 168,000원'],
         say='공식 크기는 세로형이 가로 450, 세로 300밀리미터, 가로형 DLM-8563은 538에 312밀리미터예요.'),
    dict(kind='bars', card='C', title='네이버쇼핑 라바제 목록 3개', big='리뷰 모두 0건', small='모델명이 없어 공식 모델과 같은지는 확인 못 했어요', col=RED,
         rows=[('홈바 싱크용', 48510, GOLD), ('가로형 선반', 98800, GOLD), ('올스텐 세로형', 351800, GOLD)],
         say='네이버쇼핑에는 라바제 목록이 세 개 있었고 가격은 4만 8천 원부터 35만 원대, 리뷰는 모두 0건이었어요.'),
    dict(kind='check', card='A', title='결제 전 확인', big='모델명·구성·판매처', small='같은 이름도 판매처마다 달라요', col=RED,
         items=['DLM-8690인지 8563인지', '3종세트인지 단품인지', '최종 결제가와 배송비'],
         say='모델명과 세트인지 단품인지 먼저 확인하고, 놓을 자리 크기를 재 보세요.'),
    dict(kind='cta', title='저장해두세요', big='살 때 꺼내보기', small='직접 써본 후기 아님 · 쿠팡 파트너스 수수료', col=GOLD,
         say='저장해 두고, 살 때 꺼내 보세요. 자세한 가격 정리는 블로그에 있어요.'),
]
_bgs = {}


def big_bg(i):
    f = '07_라바제식기건조대_클로징.jpg' if i % 2 == 0 else '01_라바제식기건조대_대표이미지.jpg'
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
