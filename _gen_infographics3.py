#!/usr/bin/env python3
"""특정법인증여의제 인포그래픽 2장 (요건구조도, 몰아주기vs정상 비교)"""
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb

OUT = 'blog_images/2026-10-01_특정법인증여의제'

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

# ── 02: 특정법인 요건 구조도 ──────────────────────────────
H1 = 1080
img, d = new_canvas(H1)

d.text((60, 55), "특정법인, 지분 30% 기준으로 판단합니다", font=load_font('extrabold', 38), fill=hex_to_rgb(NAVY))
d.text((60, 115), "지배주주와 친족 지분 합계가 30% 이상이면 해당", font=body_font, fill=hex_to_rgb(GRAY))

box_top = 200
box_h = 260
d.rectangle([90, box_top, W - 90, box_top + box_h], fill=hex_to_rgb("#FFFFFF"), outline=hex_to_rgb(GOLD), width=4)
d.text((W//2, box_top + 50), "특정법인 요건", font=sub_font, fill=hex_to_rgb(NAVY), anchor='mm')
d.text((W//2, box_top + 120), "지배주주 + 배우자·자녀 등 특수관계인", font=body_font, fill=hex_to_rgb(NAVY), anchor='mm')
d.text((W//2, box_top + 165), "직·간접 보유 지분 합계", font=body_font, fill=hex_to_rgb(NAVY), anchor='mm')
d.text((W//2, box_top + 220), "30% 이상", font=load_font('extrabold', 56), fill=hex_to_rgb(GOLD), anchor='mm')

sub_title_y = box_top + box_h + 50
d.text((60, sub_title_y), "과세되는 거래 유형", font=sub_font, fill=hex_to_rgb(NAVY))

items = ["무상 제공·용역", "저가 양수·고가 양도", "채무 면제·인수", "불균등 감자", "배당 몰아주기(포기)"]
chip_top = sub_title_y + 60
chip_h = 70
gap = 16
for i, text in enumerate(items):
    y0 = chip_top + i * (chip_h + gap)
    d.rectangle([90, y0, W - 90, y0 + chip_h], fill=hex_to_rgb(LIGHT))
    d.text((120, y0 + chip_h//2), f"• {text}", font=body_font, fill=hex_to_rgb(NAVY), anchor='lm')

img.save(f'{OUT}/02_특정법인증여의제_구조도.png')
print('saved 02')

# ── 03: 몰아주기 vs 정상배당 비교 ──────────────────────────────
H2 = 820
img2, d2 = new_canvas(H2)

d2.text((60, 55), "배당 몰아주기, 세금까지 몰아서 나옵니다", font=load_font('extrabold', 38), fill=hex_to_rgb(NAVY))
d2.text((60, 118), "지분 1% 자녀 법인이 받은 배당 기준 예시", font=body_font, fill=hex_to_rgb(GRAY))

box_top = 210
box_h = 380
box_w = 500
gap_h = 60

x0 = 90
d2.rectangle([x0, box_top, x0 + box_w, box_top + box_h], fill=hex_to_rgb("#FFFFFF"), outline=hex_to_rgb(RED), width=4)
d2.text((x0 + box_w//2, box_top + 45), "배당 몰아주기", font=sub_font, fill=hex_to_rgb(NAVY), anchor='mm')
d2.text((x0 + box_w//2, box_top + 95), "지분 1% → 약 30억원 수령", font=body_font, fill=hex_to_rgb(GRAY), anchor='mm')
d2.text((x0 + box_w//2, box_top + 190), "증여세 약", font=body_font, fill=hex_to_rgb(GRAY), anchor='mm')
d2.text((x0 + box_w//2, box_top + 260), "10억원대", font=load_font('extrabold', 58), fill=hex_to_rgb(RED), anchor='mm')
d2.text((x0 + box_w//2, box_top + 335), "특정법인증여의제 적용", font=small_font, fill=hex_to_rgb(RED), anchor='mm')

x1 = x0 + box_w + gap_h
d2.rectangle([x1, box_top, x1 + box_w, box_top + box_h], fill=hex_to_rgb("#FFFFFF"), outline=hex_to_rgb(GREEN), width=4)
d2.text((x1 + box_w//2, box_top + 45), "정상 배당 + 증여", font=sub_font, fill=hex_to_rgb(NAVY), anchor='mm')
d2.text((x1 + box_w//2, box_top + 95), "지분대로 수령 후 세후 증여", font=body_font, fill=hex_to_rgb(GRAY), anchor='mm')
d2.text((x1 + box_w//2, box_top + 190), "배당소득세 +", font=body_font, fill=hex_to_rgb(GRAY), anchor='mm')
d2.text((x1 + box_w//2, box_top + 260), "일반 증여세", font=load_font('extrabold', 44), fill=hex_to_rgb(GREEN), anchor='mm')
d2.text((x1 + box_w//2, box_top + 335), "사전 시뮬레이션으로 비교 필요", font=small_font, fill=hex_to_rgb(GREEN), anchor='mm')

note_y = box_top + box_h + 50
d2.rectangle([60, note_y, W - 60, note_y + 150], fill=hex_to_rgb(LIGHT))
d2.text((90, note_y + 25), "몇 퍼센트 지분 참여만으로도 과세가액이 크게 불어날 수 있어,", font=body_font, fill=hex_to_rgb(NAVY))
d2.text((90, note_y + 75), "거래 전 실제 세액을 미리 계산해보는 절차가 꼭 필요합니다.", font=body_font, fill=hex_to_rgb(NAVY))

img2.save(f'{OUT}/03_특정법인증여의제_비교표.png')
print('saved 03')
