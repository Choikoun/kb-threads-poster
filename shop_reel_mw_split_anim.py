#!/usr/bin/env python3
"""MWJ25E 릴스 분할비교형(2026-11-19): shop_make.py 가 spec.json 으로 생성.
SHOP_VOICE / SHOP_OUT / SHOP_PREVIEW"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
os.environ.setdefault('SHOP_TEMPO', '1.5')   # 장면 3초 안팎(참고 영상 컷 속도)
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-11-19_LG전자레인지MWJ25E'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_mw_split.mp4'
BG = '01_MWJ25E_대표이미지.jpg'
SCENES = [
    {'kind': 'split', 'title': 'LG 전자레인지 MWJ20EDN', 'head': '공식몰과 쿠팡 표기 차이', 'note': 'LG전자 공식몰·쿠팡 검색 목록 · 2026-11-19 조회', 'L': {'name': 'LG 공식몰', 'price': '152,000원', 'sub': '20L', 'win': True}, 'R': {'name': '쿠팡 목록', 'price': '237,500원', 'sub': '85,500원 높음', 'bad': True}, 'say': 'LG 전자레인지 MWJ20EDN은 공식몰 152,000원, 쿠팡 목록은 237,500원으로 표기됐어요.'},
    {'kind': 'split', 'title': 'LG 전자레인지 MWJ25E', 'head': '쿠팡 같은 모델명 가격 차이', 'note': '쿠팡 검색 목록 · 구성은 확인하지 못했어요', 'L': {'name': '쿠팡 최저', 'price': '216,340원', 'sub': '25L', 'win': True}, 'R': {'name': '쿠팡 최고', 'price': '485,100원', 'sub': '같은 모델명', 'bad': True}, 'say': 'MWJ25E는 쿠팡에서 21만 원대부터 48만 원대까지 표기됐어요.'},
    {'kind': 'big', 'title': '결제 전 확인', 'head': '모델명과 구성품', 'note': '공식몰 MWJ25E는 260,000원이에요', 'lines': ['모델명 MWJ25E', '본품 한 대인지', '설치비와 배송 조건'], 'say': '모델명과 구성품, 설치 조건을 먼저 확인하세요.'},
    {'kind': 'cta', 'title': '쿠팡 링크는 설명란에', 'head': '설명란과 댓글 링크', 'note': '직접 써본 후기 아님 · 쿠팡 파트너스 수수료', 'say': '쿠팡 링크는 설명란과 댓글에 있어요. 옵션과 가격은 페이지에서 확인하세요.'},
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
