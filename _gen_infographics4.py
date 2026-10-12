#!/usr/bin/env python3
"""가족간차용증 인포그래픽 2장 (구조도, 원금기준 비교표)"""
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb

OUT = 'blog_images/2026-10-02_가족간차용증'

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

# ── 02: 적정이자율 구조도 ──────────────────────────────
H1 = 900
img, d = new_canvas(H1)

d.text((60, 55), "적정이자율 4.6%, 차액이 기준입니다", font=load_font('extrabold', 38), fill=hex_to_rgb(NAVY))
d.text((60, 115), "실제 이자와 적정이자의 차액이 연 1천만원 넘으면 과세", font=body_font, fill=hex_to_rgb(GRAY))

box_top = 200
box_h = 260
d.rectangle([90, box_top, W - 90, box_top + box_h], fill=hex_to_rgb("#FFFFFF"), outline=hex_to_rgb(GOLD), width=4)
d.text((W//2, box_top + 50), "세법상 적정이자율", font=sub_font, fill=hex_to_rgb(NAVY), anchor='mm')
d.text((W//2, box_top + 150), "연 4.6%", font=load_font('extrabold', 64), fill=hex_to_rgb(GOLD), anchor='mm')
d.text((W//2, box_top + 220), "가족 간 대여에도 동일하게 적용", font=body_font, fill=hex_to_rgb(GRAY), anchor='mm')

sub_title_y = box_top + box_h + 50
d.text((60, sub_title_y), "과세 판단 흐름", font=sub_font, fill=hex_to_rgb(NAVY))

steps = ["적정이자(4.6%) 계산", "실제 받은 이자와 차액 산출", "차액이 연 1천만원 이상이면 과세"]
chip_top = sub_title_y + 60
chip_h = 80
gap = 16
for i, text in enumerate(steps):
    y0 = chip_top + i * (chip_h + gap)
    color = RED if i == 2 else LIGHT
    textcolor = "#FFFFFF" if i == 2 else NAVY
    d.rectangle([90, y0, W - 90, y0 + chip_h], fill=hex_to_rgb(color) if i==2 else hex_to_rgb(LIGHT))
    d.text((120, y0 + chip_h//2), f"{i+1}. {text}", font=body_font, fill=hex_to_rgb(textcolor), anchor='lm')

img.save(f'{OUT}/02_가족간차용증_구조도.png')
print('saved 02')

# ── 03: 원금 2억vs3억 비교 ──────────────────────────────
H2 = 820
img2, d2 = new_canvas(H2)

d2.text((60, 55), "같은 무이자, 원금 따라 결과가 갈립니다", font=load_font('extrabold', 36), fill=hex_to_rgb(NAVY))
d2.text((60, 118), "무이자로 빌려준 경우 기준", font=body_font, fill=hex_to_rgb(GRAY))

box_top = 210
box_h = 380
box_w = 500
gap_h = 60

x0 = 90
d2.rectangle([x0, box_top, x0 + box_w, box_top + box_h], fill=hex_to_rgb("#FFFFFF"), outline=hex_to_rgb(GREEN), width=4)
d2.text((x0 + box_w//2, box_top + 45), "원금 2억원", font=sub_font, fill=hex_to_rgb(NAVY), anchor='mm')
d2.text((x0 + box_w//2, box_top + 100), "적정이자 920만원", font=body_font, fill=hex_to_rgb(GRAY), anchor='mm')
d2.text((x0 + box_w//2, box_top + 190), "1천만원 미만", font=load_font('extrabold', 48), fill=hex_to_rgb(GREEN), anchor='mm')
d2.text((x0 + box_w//2, box_top + 260), "증여세", font=sub_font, fill=hex_to_rgb(GREEN), anchor='mm')
d2.text((x0 + box_w//2, box_top + 335), "과세 안 됨", font=small_font, fill=hex_to_rgb(GREEN), anchor='mm')

x1 = x0 + box_w + gap_h
d2.rectangle([x1, box_top, x1 + box_w, box_top + box_h], fill=hex_to_rgb("#FFFFFF"), outline=hex_to_rgb(RED), width=4)
d2.text((x1 + box_w//2, box_top + 45), "원금 3억원", font=sub_font, fill=hex_to_rgb(NAVY), anchor='mm')
d2.text((x1 + box_w//2, box_top + 100), "적정이자 1,380만원", font=body_font, fill=hex_to_rgb(GRAY), anchor='mm')
d2.text((x1 + box_w//2, box_top + 190), "1천만원 이상", font=load_font('extrabold', 48), fill=hex_to_rgb(RED), anchor='mm')
d2.text((x1 + box_w//2, box_top + 260), "증여세", font=sub_font, fill=hex_to_rgb(RED), anchor='mm')
d2.text((x1 + box_w//2, box_top + 335), "매년 과세 대상", font=small_font, fill=hex_to_rgb(RED), anchor='mm')

note_y = box_top + box_h + 50
d2.rectangle([60, note_y, W - 60, note_y + 120], fill=hex_to_rgb(LIGHT))
d2.text((90, note_y + 25), "기준선(약 2억 1,700만원)을 넘는 순간부터,", font=body_font, fill=hex_to_rgb(NAVY))
d2.text((90, note_y + 75), "무이자 전액이 아니라 차액 전체가 과세 대상이 됩니다.", font=body_font, fill=hex_to_rgb(NAVY))

img2.save(f'{OUT}/03_가족간차용증_비교표.png')
print('saved 03')
