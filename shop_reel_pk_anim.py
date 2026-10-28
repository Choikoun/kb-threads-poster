#!/usr/bin/env python3
"""밀폐용기 패킹 교체 시기 정보 릴스(2026-10-28, 제휴 링크 없음): 약 30초·대비형 훅. SHOP_VOICE / SHOP_OUT / SHOP_PREVIEW"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-10-27_밀폐용기패킹'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_pk_anim.mp4'
C1, C2 = '01_밀폐용기패킹_대표이미지.jpg', '07_밀폐용기패킹_클로징.jpg'
SCENES = [
    dict(kind='check', card=C1, title='밀폐용기 뚜껑이 헐거워졌다면', big='패킹부터 확인', small='기사 4건 정리 · 2026-10-27', col=RED,
         items=['패킹만의 교체 주기는 못 찾았어요', '6개월~1년은 용기 전체 기준', '상태 신호로 판단해요'],
         say='뚜껑이 헐거워졌다면 용기보다 패킹이 먼저 지친 걸 수 있어요. 패킹만의 교체 주기는 찾지 못했고, 상태 신호로 판단하라고 해요.'),
    dict(kind='check', card=C2, title='교체 신호', big='이럴 때 바꿔요', small='레이디경향·위키트리 기사', col=GOLD,
         items=['닫아도 헐겁거나 국물이 새요', '갈라짐·늘어남·눌린 자국', '씻어도 냄새가 남아요'],
         say='닫아도 헐겁거나 국물이 새고, 갈라지거나 늘어났거나, 씻어도 냄새가 남으면 바꿀 때예요.'),
    dict(kind='check', card=C1, title='세척 순서', big='분리 · 건조 · 따로 보관', small='패킹 점검 기사 참고', col=GREEN,
         items=['패킹을 빼서 비눗물로 씻기', '완전히 말린 뒤 끼우기', '마른 패킹은 따로 보관'],
         say='패킹은 빼서 씻고, 완전히 말린 뒤에 끼우고, 마르면 뚜껑에 끼우지 말고 따로 보관하세요.'),
    dict(kind='check', card=C2, title='전자레인지 전에', big='뚜껑 닫고 데우지 마세요', small='전자레인지용 표시는 안전 보장이 아니에요', col=RED,
         items=['증기 압력으로 위험해질 수 있어요', 'PP·HDPE는 가능, PET·PS는 불가', '재질과 표시를 먼저 확인'],
         say='뚜껑을 닫은 채 데우면 증기 압력으로 위험할 수 있어요. 재질과 전자레인지 표시를 먼저 확인하세요.'),
    dict(kind='cta', title='저장해두세요', big='뚜껑 헐거울 때 꺼내보기', small='직접 써본 후기 아님 · 기사 정리', col=GOLD,
         say='저장해 두고, 뚜껑이 헐거워질 때 꺼내 보세요. 전체 정리는 블로그에 있어요.'),
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
    if sc['kind'] == 'check':
        A.product_card(im, f"{IMG}/{sc['card']}", max(0.0, (t - 0.15) / 0.7), 610, 360)
        A.checklist(im, sc['items'], 1100, max(0.0, (t - 0.5) / 1.5))
    else:
        A.bookmark(im, max(0.0, (t - 0.2) / 0.8), t)
        if t > 0.8:
            A.panel(im, [90, 1110, A.W - 90, 1230], alpha=225)
            ImageDraw.Draw(im).text((A.W // 2, 1170), '블로그에 전체 정리가 있어요', font=load_font('bold', 42), fill=(255, 255, 255), anchor='mm')
    ImageDraw.Draw(im).text((A.W // 2, 1790), '정보 정리용 · 직접 써본 후기가 아닌 기사 정리 · 제휴 링크 없음', font=load_font('bold', 32), fill=(230, 233, 242), anchor='mm')
    return im


if __name__ == '__main__':
    A.run(SCENES, render, OUT, preview=bool(os.environ.get('SHOP_PREVIEW')))
