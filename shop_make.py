#!/usr/bin/env python3
"""쇼핑 글 자산 일괄 생성(이미지·릴스 모듈·캡션). 매일 반복 작업의 토큰을 줄이기 위해 만든 도구(2026-11-13).
사용: python shop_make.py <글폴더>      (글폴더/spec.json 필요, naver.txt 는 따로 작성)
spec.json 예시는 shop_spec_example.json 참고.
만드는 것: 글폴더/01_*.jpg(펙셀 대표) + spec.images 의 PNG + shop_reel_<key>_split_anim.py + _cap_<key>_ig/th/th_reply/tt.txt
"""
import sys, os, re, json, ast
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb

BG = "#F7F5F0"; NAVY = "#1B2A4A"; GOLD = "#B8925A"; GRAY = "#6B7280"; RED = "#B5473A"; GREEN = "#2F7D5D"; W = 1200
c = hex_to_rgb


def canvas(h):
    im = Image.new('RGB', (W, h), c(BG))
    return im, ImageDraw.Draw(im)


def head(d, t, s):
    d.text((60, 55), t, font=load_font('extrabold', 40), fill=c(NAVY))
    d.text((60, 120), s, font=load_font('regular', 26), fill=c(GRAY))


def img_bars(o):
    """rows: [[라벨, 숫자]], footer: 하단 강조 문구, unit: 단위(기본 '원')"""
    rows, unit = o['rows'], o.get('unit', '원')
    mx = max(v for _, v in rows) * 1.08
    im, d = canvas(200 + 135 * len(rows) + 110)
    head(d, o['title'], o['sub'])
    y = 190
    for n, v in rows:
        d.text((60, y), n, font=load_font('bold', 26), fill=c(GRAY))
        w = int(880 * v / mx)
        d.rectangle([60, y + 44, 60 + w, y + 100], fill=c(GOLD))
        d.text((60 + w + 14, y + 72), f"{v:,}{unit}", font=load_font('extrabold', 30), fill=c(NAVY), anchor='lm')
        y += 135
    if o.get('footer'):
        d.text((60, y), o['footer'], font=load_font('extrabold', 32), fill=c(RED))
    return im


def img_kv(o):
    """rows: [[항목, 값]]"""
    rows = o['rows']
    im, d = canvas(190 + 108 * len(rows) + 60)
    head(d, o['title'], o['sub'])
    y = 190
    for a, b in rows:
        d.rectangle([40, y, W - 40, y + 92], fill=c("#FFFFFF"))
        d.text((80, y + 46), a, font=load_font('bold', 26), fill=c(GRAY), anchor='lm')
        d.text((W - 80, y + 46), b, font=load_font('extrabold', 28), fill=c(NAVY), anchor='rm')
        y += 108
    return im


def img_table(o):
    """hdr: [열 제목...], rows: [[...]] (첫 열은 넓게)"""
    hdr, rows = o['hdr'], o['rows']
    n = len(hdr)
    xs = [50] + [330 + int((W - 380) * i / (n - 1)) for i in range(n - 1)]
    im, d = canvas(190 + 52 + 112 * len(rows) + 60)
    head(d, o['title'], o['sub'])
    y = 190
    for i, h in enumerate(hdr):
        d.text((xs[i], y), h, font=load_font('extrabold', 24), fill=c(GOLD))
    y += 52
    for r in rows:
        d.rectangle([30, y - 8, W - 30, y + 84], fill=c("#FFFFFF"))
        for i, t in enumerate(r):
            d.text((xs[i], y + 38), t, font=load_font('bold', 21), fill=c(NAVY), anchor='lm')
        y += 112
    return im


def img_cards(o):
    """rows: [[라벨, 값]] 큰 카드"""
    rows = o['rows']
    im, d = canvas(200 + 145 * len(rows) + 40)
    head(d, o['title'], o['sub'])
    y = 200
    for a, b in rows:
        d.rectangle([40, y, W - 40, y + 120], fill=c("#FFFFFF"), outline=c(GOLD), width=3)
        d.text((80, y + 60), a, font=load_font('bold', 28), fill=c(GRAY), anchor='lm')
        d.text((W - 80, y + 60), b, font=load_font('extrabold', 34), fill=c(NAVY), anchor='rm')
        y += 145
    return im


def img_checklist(o):
    items = o['items']
    rows = (len(items) + 1) // 2
    im, d = canvas(200 + 190 * rows + 40)
    head(d, o.get('title', '결제 전 확인할 6가지'), o['sub'])
    for i, t in enumerate(items):
        col, row = i % 2, i // 2
        x0, y0 = 60 + col * 570, 200 + row * 190
        d.rectangle([x0, y0, x0 + 540, y0 + 150], fill=c("#FFFFFF"), outline=c(GOLD), width=3)
        d.text((x0 + 40, y0 + 75), "□", font=load_font('extrabold', 44), fill=c(GREEN), anchor='lm')
        d.text((x0 + 100, y0 + 75), t, font=load_font('bold', 22), fill=c(NAVY), anchor='lm')
    return im


KINDS = dict(bars=img_bars, kv=img_kv, table=img_table, cards=img_cards, checklist=img_checklist)


def make_images(spec, folder):
    hero = spec['hero_file']
    if not os.path.exists(f'{folder}/{hero}'):
        from stock_card_poster import search_pexels_photo
        print('대표이미지', search_pexels_photo(spec['hero_query'], output_path=f'{folder}/{hero}', orientation='landscape'))
    for o in spec['images']:
        KINDS[o['kind']](o).save(f"{folder}/{o['file']}")
        print('이미지', o['file'])


def make_reel_module(spec, folder):
    key = spec['key']
    src = open('shop_reel_c3_split_anim.py', encoding='utf-8').read()
    h = src[:src.index('SCENES = [')]
    tail = src[src.index('_bg = {}'):]
    doc = f"{spec['keyword']} 릴스 분할비교형({spec['date']}): shop_make.py 가 spec.json 으로 생성.\nSHOP_VOICE / SHOP_OUT / SHOP_PREVIEW"
    h = re.sub(r'""".*?"""', '"""' + doc + '"""', h, count=1, flags=re.S)
    h = h.replace("IMG = 'blog_images/shop_2026-11-06_타임모어C3'", "IMG = '" + folder.replace('\\', '/') + "'")
    h = h.replace("reel_c3_split.mp4", f"reel_{key}_split.mp4").replace("BG = '01_타임모어C3_대표이미지.jpg'", "BG = '" + spec['hero_file'] + "'")
    cta = dict(kind='cta', title='모델별 정리와 링크는 블로그에', head="댓글에 '비교'", note='직접 써본 후기 아님 · 쿠팡 파트너스 수수료',
               say='링크는 블로그에 있어요. 궁금하면 댓글에 비교라고 남겨 주세요.')
    scenes = spec['reel']['scenes'] + [cta]
    code = h + 'SCENES = [\n' + ''.join('    ' + repr(s) + ',\n' for s in scenes) + ']\n' + tail
    ast.parse(code)
    name = f'shop_reel_{key}_split_anim.py'
    open(name, 'w', encoding='utf-8').write(code)
    print('릴스 모듈', name)


def make_captions(spec):
    key, cap = spec['key'], spec['caption']
    ask = "궁금한 상품이 있으면 댓글에 '비교'라고 남겨 주세요."
    ig = (f"[광고] 쿠팡 파트너스 수수료 포함\n{cap['headline']}\n{cap['detail']}\n{ask} 전체 정리는 블로그에 있어요.\n"
          f"※ 직접 써본 후기가 아닌 가격 정보 정리예요. 이 포스팅은 쿠팡 파트너스 활동의 일환으로, 수수료를 제공받습니다.\n\n{cap['tags']} #광고\n")
    th = f"{cap['headline']}\n{cap['detail_short']} {ask}\n전체 정리는 블로그에 있어요. 직접 써본 후기가 아닌 가격 정보 정리예요.\n"
    files = {f'_cap_{key}_ig.txt': ig, f'_cap_{key}_tt.txt': ig, f'_cap_{key}_th.txt': th,
             f'_cap_{key}_th_reply.txt': f"쿠팡 {cap['reply_name']} 보기 → {spec['reply_link']}\n"}
    for n, t in files.items():
        open(n, 'w', encoding='utf-8').write(t)
    print('캡션', ', '.join(files))


if __name__ == '__main__':
    folder = sys.argv[1].rstrip('/\\')
    spec = json.load(open(f'{folder}/spec.json', encoding='utf-8'))
    make_images(spec, folder)
    make_reel_module(spec, folder)
    make_captions(spec)
