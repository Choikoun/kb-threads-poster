#!/usr/bin/env python3
"""타임모어 C3 릴스 분할비교형(2026-11-06): 첫 화면부터 가격, 좌우 분할 비교, 장면 약 3초.
참고: 조회수 높은 가격비교 쇼츠의 구조(첫 화면 가격·분할 비교·짧은 컷·댓글 유도)만 반영. SHOP_VOICE / SHOP_OUT / SHOP_PREVIEW"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
os.environ.setdefault('SHOP_TEMPO', '1.5')   # 장면 3초 안팎(참고 영상 컷 속도)
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-11-06_타임모어C3'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_c3_split.mp4'
BG = '01_타임모어C3_대표이미지.jpg'
SCENES = [
    dict(kind='split', title='타임모어 C3S PRO', head='같은 모델, 판매처마다 달라요', note='네이버 스마트스토어 · 2026-11-06 조회',
         L=dict(name='셀렉트온', price='85,000원', sub='무료배송', win=True), R=dict(name='모던피크', price='92,500원', sub='국내정식 표기'),
         say='타임모어 C3S PRO, 같은 모델인데 판매처마다 가격이 달라요.'),
    dict(kind='split', title='타임모어 C3S PRO', head='네이버 네 곳 7,500원 차이', note='네 곳 모두 무료배송 표기',
         L=dict(name='네이버 최저', price='85,000원', sub='셀렉트온·미래스토', win=True), R=dict(name='네이버 최고', price='92,500원', sub='모던피크'),
         say='네이버 네 곳에서 7천 5백 원 차이가 나요.'),
    dict(kind='split', title='쿠팡 목록 C3S PRO', head='목록 가격이 크게 달라요', note='쿠팡은 옵션·배송비를 확인하지 못했어요',
         L=dict(name='쿠팡 목록 A', price='97,400원', sub='목록 표기'), R=dict(name='쿠팡 목록 B', price='191,800원', sub='목록 표기', bad=True),
         say='쿠팡 목록은 9만 7천 4백 원과 19만 1천 8백 원이에요.'),
    dict(kind='split', title='타임모어 C3S', head='배송비를 더해 보세요', note='N펀키보이 판매 페이지 기준',
         L=dict(name='판매가', price='77,000원', sub='배송비 3,000원 별도'), R=dict(name='배송비 포함', price='80,000원', sub='합계', bad=True),
         say='C3S는 7만 7천 원이지만 배송비를 더하면 8만 원이에요.'),
    dict(kind='big', title='결제 전 확인', head='모델명 뒤 글자부터', note='페이지마다 표기가 달라요', lines=['C3 · C3S · PRO 구분', '국내정식 표기와 판매자', '구매대행 교환·반품 기준'],
         say='모델명 뒤 글자와 국내정식 표기, 배송비를 확인하세요.'),
    dict(kind='cta', title='모델별 정리와 링크는 블로그에', head='댓글에 \'비교\'', note='직접 써본 후기 아님 · 제휴 수수료',
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
