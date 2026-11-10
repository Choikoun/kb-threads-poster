#!/usr/bin/env python3
"""말코닉 옴니아 릴스 분할비교형(2026-11-10): 첫 화면부터 가격, 좌우 분할 비교, 장면 약 3초.
참고: 조회수 높은 가격비교 쇼츠의 구조(첫 화면 가격·분할 비교·짧은 컷·댓글 유도)만 반영.
SHOP_VOICE / SHOP_OUT / SHOP_PREVIEW"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
os.environ.setdefault('SHOP_TEMPO', '1.5')   # 장면 3초 안팎(참고 영상 컷 속도)
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-11-10_말코닉옴니아'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_omnia_split.mp4'
BG = '01_말코닉옴니아_대표이미지.jpg'
SCENES = [
    dict(kind='split', title='말코닉 옴니아', head='쿠팡 목록 가격 차이', note='쿠팡 검색 목록 · 2026-11-10 조회',
         L=dict(name='가장 낮은 표기', price='4,350,000원', sub='로켓 표기 없음', win=True), R=dict(name='가장 높은 표기', price='4,950,000원', sub='로켓 표기 없음', bad=True),
         say='말코닉 옴니아는 쿠팡 목록에서 435만 원부터 495만 원까지 표기됐어요.'),
    dict(kind='split', title='같은 이름', head='60만 원 차이', note='옵션과 판매처는 상품 페이지에서 확인',
         L=dict(name='최저 표기', price='4,350,000원', sub='업소용 전자동 표기', win=True), R=dict(name='최고 표기', price='4,950,000원', sub='전자동 커피그라인더 표기', bad=True),
         say='같은 이름인데 차이는 60만 원이에요.'),
    dict(kind='big', title='공식 사이트 사양', head='98mm 날 · 호퍼 250g', note='mahlkoenig.com 기술 사양 기준', lines=['분쇄 날 지름 98mm 주강', '호퍼 용량 약 250g', '최대 정격 전력 750W'],
         say='공식 사양은 98밀리 날, 호퍼 250그램, 최대 750와트예요.'),
    dict(kind='split', title='가격 표기', head='단위가 달라 바로 비교 불가', note='환산하지 않고 표기 그대로',
         L=dict(name='공식 독일 상점', price='4,050유로', sub='부가세 포함'), R=dict(name='쿠팡 목록', price='435만원~', sub='원화 표기'),
         say='공식 독일 상점은 4,050유로, 쿠팡은 원화라서 바로 비교할 수 없어요.'),
    dict(kind='big', title='결제 전 확인', head='전압과 보증부터', note='고가 수입 제품이에요', lines=['상품명에 EK OMNIA', '전압과 플러그 규격', '보증과 A/S 주체'],
         say='모델명, 전압, 보증 주체를 먼저 확인하세요.'),
    dict(kind='cta', title='모델별 정리와 링크는 블로그에', head='댓글에 \'비교\'', note='직접 써본 후기 아님 · 쿠팡 파트너스 수수료',
         say='링크는 블로그에 있어요. 궁금하면 댓글에 비교라고 남겨 주세요.'),
]
_bg = {}


def big_bg():
    if 'b' not in _bg:
        _bg['b'] = A.cover(f'{IMG}/{BG}', 0.62)
    return _bg['b']


def side(im, box, d, e):
    """분할 카드 한 쪽. d: name/price/sub/win/bad/small. e: 등장 진행도"""
    x0, y0, x1, y1 = box
    s = max(0.01, pop(e))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    w, h = int((x1 - x0) * s), int((y1 - y0) * s)
    dr = ImageDraw.Draw(im)
    win = d.get('win')
    dr.rounded_rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], radius=34, fill=c('#FFFFFF'),
                         outline=c(GREEN) if win else None, width=10 if win else 0)
    if s < 0.9:
        return
    dr.text((cx, y0 + 70), d['name'], font=load_font('bold', 38 if len(d['name']) > 6 else 46), fill=c('#1B2A4A'), anchor='mm')
    size = 58 if d.get('small') else (70 if len(d['price']) <= 7 else 62)
    dr.text((cx, cy - 10), d['price'], font=load_font('extrabold', size), fill=c(GREEN) if win else c('#1B2A4A'), anchor='mm')
    dr.text((cx, cy + 90), d['sub'], font=load_font('bold', 36), fill=c(RED) if d.get('bad') else c('#5B6577'), anchor='mm')
    if win:
        dr.rounded_rectangle([cx - 90, y1 - 120, cx + 90, y1 - 50], radius=30, fill=c(GREEN))
        dr.text((cx, y1 - 85), '더 낮음', font=load_font('extrabold', 36), fill=c('#FFFFFF'), anchor='mm')


def render(sc, i, p, t, t01, work):
    im = A.bg_frame(big_bg(), t01, 1 if i % 2 == 0 else -1)
    pp = 1.0 if i == 0 else p   # 첫 장면은 처음부터 완전히 보이게(첫 화면에 가격)
    A.banner(im, sc['title'], sc['head'], sc.get('note', ''), GOLD if sc['kind'] != 'cta' else RED, pp)
    k = sc['kind']
    if k == 'split':
        e = 1.0 if i == 0 else max(0.0, (t - 0.05) / 0.45)
        side(im, [50, 610, 525, 1180], sc['L'], e)
        side(im, [555, 610, 1030, 1180], sc['R'], e if i == 0 else max(0.0, (t - 0.2) / 0.45))
    elif k == 'big':
        A.panel(im, [90, 700, A.W - 90, 1100], alpha=225, a=min(1.0, ease(p * 1.5)))
        d = ImageDraw.Draw(im)
        for n, line in enumerate(sc.get('lines', ['배송비를 더한 총액', '용량·지름·원산지', '쿠폰 기한'])):
            ee = ease(p * 1.6 - n * 0.35)
            if ee > 0:
                d.text((A.W // 2, 800 + n * 120), line, font=load_font('extrabold', 58), fill=tuple(int(v * ee + 25 * (1 - ee)) for v in c('#FFFFFF')), anchor='mm')
    else:
        A.bookmark(im, max(0.0, (t - 0.2) / 0.8), t)
        if t > 0.6:
            A.panel(im, [90, 1110, A.W - 90, 1230], alpha=225)
            ImageDraw.Draw(im).text((A.W // 2, 1170), '댓글에 \'비교\' 남기기', font=load_font('bold', 44), fill=(255, 255, 255), anchor='mm')
    ImageDraw.Draw(im).text((A.W // 2, 1790), '광고 · 가격 정보 정리용 · 제휴 수수료를 받을 수 있음', font=load_font('bold', 32), fill=(230, 233, 242), anchor='mm')
    return im


if __name__ == '__main__':
    A.run(SCENES, render, OUT, preview=bool(os.environ.get('SHOP_PREVIEW')))
