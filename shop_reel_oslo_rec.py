#!/usr/bin/env python3
"""오슬로 텀블러 릴스 — 스톡 사진 대신 실제 판매 페이지 화면(2026-10-31 캡처)을 보여 주는 화면기록형. 틱톡 0조회 대조 실험"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import shop_anim as A
from shop_anim import *

IMG = 'blog_images/shop_2026-10-31_오슬로텀블러'
OUT = os.environ.get('SHOP_OUT') or f'{IMG}/reel_oslo_rec.mp4'
SCENES = [
    dict(img='cap/outback_kim_0.png', y0=300, y1=860, hl=(640, 735), title='오슬로 아웃백 500ml', sub='네이버 스마트스토어 · 실제 판매 페이지',
         say='오슬로 아웃백 500ml, 같은 모델인데 판매자마다 총액이 달라요.'),
    dict(img='cap/outback_kim_1.png', y0=50, y1=610, hl=(105, 235), title='김씨하우스', sub='판매가 11,900원 + 배송비 3,000원 = 14,900원',
         say='김씨하우스는 판매가 만 천 9백 원에 배송비 3천 원, 합쳐서 만 4천 9백 원이에요.'),
    dict(img='cap/outback_ana_1.png', y0=50, y1=610, hl=(95, 175), title='ANA스토어', sub='판매가 12,800원 + 배송비 3,000원 = 15,800원',
         say='ANA스토어는 만 2천 8백 원에 배송비 3천 원, 합치면 만 5천 8백 원이에요.'),
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
        if a > 0:
            h0, h1 = sc['hl']
            hy0, hy1 = Y0 + int((h0 - y0) * sc_), Y0 + int((h1 - y0) * sc_)
            hy0, hy1 = max(Y0, hy0), min(Y0 + ph, hy1)
            d.rounded_rectangle([X0 + 10, hy0, X0 + PW - 10, hy1], radius=14, outline=(217, 83, 79), width=int(4 + 4 * a))
        d.text((A.W // 2, 170), sc['sub'], font=load_font('bold', 34), fill=(255, 213, 74), anchor='mm')
    d.text((A.W // 2, 1790), '광고 · 판매 페이지 화면 정리 · 제휴 수수료를 받을 수 있음', font=load_font('bold', 32), fill=(230, 233, 242), anchor='mm')
    return im


if __name__ == '__main__':
    A.run(SCENES, render, OUT, preview=bool(os.environ.get('SHOP_PREVIEW')))
