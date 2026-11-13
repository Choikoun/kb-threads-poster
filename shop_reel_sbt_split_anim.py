#!/usr/bin/env python3
"""삼바텍 온수매트 릴스 분할비교형(2026-11-13): shop_make.py 가 spec.json 으로 생성.
SHOP_VOICE / SHOP_OUT / SHOP_PREVIEW"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
os.environ.setdefault('SHOP_TEMPO', '1.5')   # 장면 3초 안팎(참고 영상 컷 속도)
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-11-13_삼바텍온수매트'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_sbt_split.mp4'
BG = '01_삼바텍온수매트_대표이미지.jpg'
SCENES = [
    {'kind': 'split', 'title': '삼바텍 침대용 온수매트', 'head': '공식몰과 쿠팡 목록 가격 차이', 'note': '공식몰·쿠팡 검색 목록 · 2026-11-13 조회', 'L': {'name': '공식몰', 'price': '368,000원', 'sub': '스퀘어 블루'}, 'R': {'name': '쿠팡 목록', 'price': '268,000원', 'sub': '로켓 표기 없음', 'win': True}, 'say': '삼바텍 침대용 온수매트는 공식몰 368,000원, 쿠팡 목록에서는 268,000원으로 표기됐어요.'},
    {'kind': 'split', 'title': '같은 모델 표기', 'head': '10만 원 차이', 'note': '쿠팡 판매자와 구성은 확인하지 못했어요', 'L': {'name': '공식몰', 'price': '368,000원', 'sub': '판매가', 'bad': True}, 'R': {'name': '쿠팡 목록', 'price': '268,000원', 'sub': '100,000원 낮음', 'win': True}, 'say': '차이는 10만 원이에요.'},
    {'kind': 'big', 'title': '공식몰 보일러 사양', 'head': 'SBC300과 SBC400', 'note': '공식몰 상세 이미지 기준', 'lines': ['SBC300 단일난방 251W', 'SBC400 분리난방 500W', 'AC220V 60Hz'], 'say': '싱글 단일난방 보일러는 251와트, 더블 분리난방 보일러는 500와트예요.'},
    {'kind': 'big', 'title': '결제 전 확인', 'head': '보일러 구성과 판매자', 'note': '구성에 따라 가격이 달라요', 'lines': ['단일난방 또는 분리난방', '싱글 더블 사이즈', '보증과 A/S 주체'], 'say': '보일러 구성과 사이즈, 보증 주체를 먼저 확인하세요.'},
    {'kind': 'cta', 'title': '모델별 정리와 링크는 블로그에', 'head': "댓글에 '비교'", 'note': '직접 써본 후기 아님 · 쿠팡 파트너스 수수료', 'say': '링크는 블로그에 있어요. 궁금하면 댓글에 비교라고 남겨 주세요.'},
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
