#!/usr/bin/env python3
"""태안 물결카라반 릴스 2(2026-10-26): 비품·준비물·규정(아기와 갈 때 확인). SHOP_VOICE / SHOP_OUT / SHOP_PREVIEW"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-10-26_태안물결카라반'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_mg2_anim.mp4'
SCENES = [
    dict(kind='check', card='A', title='태안 물결카라반 · 카라반 비품 목록', big='냉장고·밥솥 있어요', small='숙소 공지 기준 · 판매처 제공 이미지', col=GOLD,
         items=['냉장고·전자레인지·전기밥솥', '쿡탑·냄비·프라이팬·도마', '에어컨·온풍기·침구·퀸 침대'],
         say='태안 물결카라반 카라반에는 냉장고, 전자레인지, 전기밥솥, 쿡탑이 비품으로 있다고 안내돼 있어요.'),
    dict(kind='check', card='A', title='직접 챙길 것', big='음식·식수는 직접', small='조미료와 식용유도 포함이에요', col=RED,
         items=['음식물·식수·조미료·식용유', '그릴·숯 개인 반입은 금지', '아기용품 대여는 확인하지 못했어요'],
         say='음식물과 식수, 조미료는 직접 준비해야 하고, 그릴과 숯은 개인 반입이 금지예요. 아기용품 대여는 확인하지 못했어요.'),
    dict(kind='bars', card='A', title='객실별 월~목 1박 요금', big='인원에 따라 달라요', small='쿠팡 여행 표기 · 12월 첫째 주 · 기준 2인', col=GOLD,
         rows=[('커플 최대 3인', 49000, GREEN), ('11호 최대 4인', 69000, GOLD), ('오션뷰 최대 6인', 99000, GOLD)],
         say='평일 요금은 최대 3인 커플 카라반이 4만 9천 원, 최대 4인이 6만 9천 원, 최대 6인 오션뷰가 9만 9천 원이에요.'),
    dict(kind='check', card='A', title='이용 규정', big='어린이 안전 유의', small='숙소 공지 기준', col=RED,
         items=['창문·유리·스위치 파손 유의', '카라반 키 분실 시 3만원', '반려동물 금지·카라반 안 금연'],
         say='숙소 공지에는 어린이가 창문과 유리, 스위치를 파손하지 않도록 유의해 달라는 안내가 있고, 키를 잃어버리면 3만 원이에요.'),
    dict(kind='check', card='A', title='체크인 안내', big='입실은 20시까지', small='늦으면 미리 연락하세요', col=GOLD,
         items=['체크인 15:00 · 체크아웃 11:00', '퇴실 연장 12시까지 시간당 1만원', '성수기·공휴일은 연장 불가'],
         say='체크인은 오후 3시, 체크아웃은 오전 11시이고, 입실은 저녁 8시까지예요. 늦으면 미리 연락하세요.'),
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
