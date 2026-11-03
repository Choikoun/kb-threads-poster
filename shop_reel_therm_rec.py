#!/usr/bin/env python3
"""스탠리 릴스 — 스톡 사진 대신 실제 판매 페이지 화면(2026-10-31 캡처)을 보여 주는 화면기록형. 틱톡 0조회 대조 실험"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-11-03_써모스보온병'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_therm_rec.mp4'
SCENES = [
    dict(img='cap/ffx751_gocamp_0.png', y0=0, y1=520, hl=None, title='써모스 FFX-751K 750ml', sub='네이버 스마트스토어 · 실제 판매 페이지',
         say='써모스 FFX-751K 750ml, 판매가만 보면 고캠프가 더 싸 보여요.'),
    dict(img='cap/ffx751_gocamp_0.png', y0=370, y1=870, hl=(610, 665), title='고캠프', sub='45,000원 + 배송비 3,000원 = 48,000원',
         say='고캠프는 4만 5천 원에 배송비 3천 원이 붙어 합치면 4만 8천 원이에요.'),
    dict(img='cap/ffx751_dosim_0.png', y0=370, y1=870, hl=(435, 510), title='도심산장', sub='46,750원 · 무료배송',
         say='도심산장은 4만 6천 7백 50원에 무료배송이라 총액이 더 낮아요.'),
    dict(kind='cta', title='저장해두세요', say='배송비까지 더해서 비교하세요. 모델별 가격 정리와 링크는 블로그에 있어요.'),
]
_im = {}
X0, Y0, PW = 70, 230, 940


def shot(name):
    if name not in _im:
        _im[name] = Image.open(f'{IMG}/{name}').convert('RGB')
    return _im[name]


def render(sc, i, p, t, t01, work):
    im = Image.new('RGB', (A.W, A.H), c('#0F1A33'))
    d = ImageDraw.Draw(im)
    d.text((A.W // 2, 105), sc['title'], font=load_font('bold', 54), fill=(255, 255, 255), anchor='mm')
    if sc.get('kind') == 'cta':
        A.bookmark(im, max(0.0, (t - 0.2) / 0.8), t)
    else:
        s = shot(sc['img'])
        sc_ = PW / s.width
        ph = int((sc['y1'] - sc['y0']) * sc_)
        sh = int(30 * t01)   # 천천히 아래로 훑기
        y0 = sc['y0'] + sh
        crop = s.crop((0, y0, s.width, y0 + (sc['y1'] - sc['y0']))).resize((PW, ph), Image.LANCZOS)
        im.paste(crop, (X0, Y0))
        d.rounded_rectangle([X0 - 4, Y0 - 4, X0 + PW + 4, Y0 + ph + 4], radius=10, outline=(184, 146, 90), width=5)
        a = A.ease((t - 0.5) / 0.5)
        if a > 0 and sc['hl']:
            h0, h1 = sc['hl']
            hy0, hy1 = Y0 + int((h0 - y0) * sc_), Y0 + int((h1 - y0) * sc_)
            hy0, hy1 = max(Y0, hy0), min(Y0 + ph, hy1)
            d.rounded_rectangle([X0 + 10, hy0, X0 + PW - 10, hy1], radius=14, outline=(217, 83, 79), width=int(4 + 4 * a))
        d.text((A.W // 2, 170), sc['sub'], font=load_font('bold', 34), fill=(255, 213, 74), anchor='mm')
    d.text((A.W // 2, 1790), '광고 · 판매 페이지 화면 정리 · 제휴 수수료를 받을 수 있음', font=load_font('bold', 32), fill=(230, 233, 242), anchor='mm')
    return im


if __name__ == '__main__':
    A.run(SCENES, render, OUT, preview=bool(os.environ.get('SHOP_PREVIEW')))
