#!/usr/bin/env python3
"""퇴직연금세액공제 인포그래픽 2장 (세율비교, 중도인출불이익)"""
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb

OUT = 'blog_images/2026-10-01_퇴직연금세액공제'

BG = "#F7F5F0"
NAVY = "#1B2A4A"
GOLD = "#B8925A"
GRAY = "#6B7280"
LIGHT = "#E8E4DC"
RED = "#B5473A"
GREEN = "#2F7D5D"

W = 1200

def new_canvas(h):
    img = Image.new('RGB', (W, h), hex_to_rgb(BG))
    return img, ImageDraw.Draw(img)

title_font = load_font('extrabold', 46)
sub_font = load_font('bold', 32)
body_font = load_font('regular', 28)
small_font = load_font('regular', 24)

# ── 02: 세율 비교 ──────────────────────────────
H1 = 900
img, d = new_canvas(H1)

d.text((60, 55), "퇴직연금세액공제, 소득 기준으로 세율이 갈립니다", font=load_font('extrabold', 38), fill=hex_to_rgb(NAVY))
d.text((60, 115), "연 900만원 전액 납입 시 환급액 비교", font=body_font, fill=hex_to_rgb(GRAY))

# 두 박스: 16.5% vs 13.2%
box_top = 200
box_h = 340
box_w = 500
gap = 60

# 왼쪽 박스 (16.5%)
x0 = 90
d.rectangle([x0, box_top, x0 + box_w, box_top + box_h], fill=hex_to_rgb("#FFFFFF"), outline=hex_to_rgb(GREEN), width=4)
d.text((x0 + box_w//2, box_top + 40), "종합소득금액", font=body_font, fill=hex_to_rgb(GRAY), anchor='mm')
d.text((x0 + box_w//2, box_top + 80), "4,500만원 이하", font=sub_font, fill=hex_to_rgb(NAVY), anchor='mm')
d.text((x0 + box_w//2, box_top + 160), "16.5%", font=load_font('extrabold', 64), fill=hex_to_rgb(GREEN), anchor='mm')
d.text((x0 + box_w//2, box_top + 240), "900만원 납입 시", font=small_font, fill=hex_to_rgb(GRAY), anchor='mm')
d.text((x0 + box_w//2, box_top + 285), "148만 5천원 환급", font=sub_font, fill=hex_to_rgb(GREEN), anchor='mm')

# 오른쪽 박스 (13.2%)
x1 = x0 + box_w + gap
d.rectangle([x1, box_top, x1 + box_w, box_top + box_h], fill=hex_to_rgb("#FFFFFF"), outline=hex_to_rgb(GOLD), width=4)
d.text((x1 + box_w//2, box_top + 40), "종합소득금액", font=body_font, fill=hex_to_rgb(GRAY), anchor='mm')
d.text((x1 + box_w//2, box_top + 80), "4,500만원 초과", font=sub_font, fill=hex_to_rgb(NAVY), anchor='mm')
d.text((x1 + box_w//2, box_top + 160), "13.2%", font=load_font('extrabold', 64), fill=hex_to_rgb(GOLD), anchor='mm')
d.text((x1 + box_w//2, box_top + 240), "900만원 납입 시", font=small_font, fill=hex_to_rgb(GRAY), anchor='mm')
d.text((x1 + box_w//2, box_top + 285), "118만 8천원 환급", font=sub_font, fill=hex_to_rgb(GOLD), anchor='mm')

note_y = box_top + box_h + 60
d.rectangle([60, note_y, W - 60, note_y + 170], fill=hex_to_rgb(LIGHT))
d.text((90, note_y + 25), "근로자는 총급여 5,500만원, 사업소득자는", font=body_font, fill=hex_to_rgb(NAVY))
d.text((90, note_y + 70), "종합소득금액 4,500만원이 기준선입니다.", font=body_font, fill=hex_to_rgb(NAVY))
d.text((90, note_y + 115), "버는 돈이 많을수록 오히려 공제율은 낮아집니다.", font=small_font, fill=hex_to_rgb(GRAY))

img.save(f'{OUT}/02_퇴직연금세액공제_세율비교.png')
print('saved 02')

# ── 03: 중도인출 불이익 ──────────────────────────────
H2 = 900
img2, d2 = new_canvas(H2)

d2.text((60, 55), "중도 인출, 세액공제 받은 만큼 뱉어냅니다", font=load_font('extrabold', 40), fill=hex_to_rgb(NAVY))
d2.text((60, 120), "연금으로 받을 때와 중도에 뺄 때, 세금이 정반대입니다", font=body_font, fill=hex_to_rgb(GRAY))

rows = [
    ("연금으로 수령", "만 55세 이후, 10년 이상 분할", "연금소득세 3.3~5.5%", GREEN),
    ("중도 인출/해지", "만 55세 이전 or 일시 인출", "기타소득세 16.5%", RED),
]

card_top = 220
card_h = 220
gap_v = 40
for i, (title, cond, tax, color) in enumerate(rows):
    y0 = card_top + i * (card_h + gap_v)
    y1 = y0 + card_h
    d2.rectangle([60, y0, W - 60, y1], fill=hex_to_rgb("#FFFFFF"), outline=hex_to_rgb(color), width=4)
    d2.text((100, y0 + 35), title, font=load_font('extrabold', 40), fill=hex_to_rgb(NAVY))
    d2.text((100, y0 + 100), cond, font=body_font, fill=hex_to_rgb(GRAY))
    d2.text((100, y0 + 150), tax, font=sub_font, fill=hex_to_rgb(color))

note_y2 = card_top + 2 * (card_h + gap_v) + 20
d2.rectangle([60, note_y2, W - 60, note_y2 + 170], fill=hex_to_rgb(LIGHT))
d2.text((90, note_y2 + 25), "세액공제와 낮은 연금소득세, 두 혜택을 다 누리려면", font=body_font, fill=hex_to_rgb(NAVY))
d2.text((90, note_y2 + 70), "결국 55세 이후 연금 형태로 받아야 합니다.", font=body_font, fill=hex_to_rgb(NAVY))
d2.text((90, note_y2 + 115), "사업자금이 급해 해지하면 몇 년치 공제를 한번에 반납합니다.", font=small_font, fill=hex_to_rgb(GRAY))

img2.save(f'{OUT}/03_퇴직연금세액공제_중도인출불이익.png')
print('saved 03')
