from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
import os
OUT = 'blog_images/2026-11-24_종부세납부기간'
P = '종부세납부기간'
os.makedirs(OUT, exist_ok=True)
BG = "#F7F5F0"; NAVY = "#1B2A4A"; GOLD = "#B8925A"; GRAY = "#6B7280"; RED = "#B5473A"; GREEN = "#2F7D5D"
W = 1200; c = hex_to_rgb
def canvas(h):
    im = Image.new('RGB', (W, h), c(BG)); return im, ImageDraw.Draw(im)
sub = load_font('bold', 32); body = load_font('regular', 28); small = load_font('regular', 24); big = load_font('extrabold', 40)
def box(d, y, h, col, t1, t2=None, r=None, s=30):
    d.rectangle([90, y, W - 90, y + h], fill=c("#FFFFFF"), outline=c(col), width=4)
    if t2:
        d.text((130, y + h * 0.33), t1, font=load_font('extrabold', s), fill=c(col), anchor='lm')
        d.text((130, y + h * 0.7), t2, font=body, fill=c(NAVY), anchor='lm')
    else:
        d.text((130, y + h // 2), t1, font=load_font('extrabold', s), fill=c(col), anchor='lm')
    if r: d.text((W - 130, y + h // 2), r, font=load_font('extrabold', 38), fill=c(col), anchor='rm')
def cover(fn, l1, l2, l3, foot):
    im, d = canvas(900)
    d.rectangle([0, 0, W, 14], fill=c(GOLD))
    d.text((70, 200), l1, font=load_font('extrabold', 100), fill=c(NAVY))
    d.text((70, 380), l2, font=load_font('extrabold', 66), fill=c(NAVY))
    d.text((70, 490), l3, font=load_font('extrabold', 88), fill=c(GOLD))
    d.text((70, 700), foot, font=sub, fill=c(GRAY))
    im.save(f'{OUT}/{fn}')
def core(fn, items):
    im, d = canvas(800)
    d.text((60, 55), "핵심 정리", font=big, fill=c(NAVY))
    for i, (k, v, col) in enumerate(items):
        d.rectangle([90, 160 + i * 190, W - 90, 160 + i * 190 + 150], fill=c("#FFFFFF"), outline=c(col), width=4)
        d.text((130, 160 + i * 190 + 75), k, font=load_font('extrabold', 44), fill=c(col), anchor='lm')
        d.text((220, 160 + i * 190 + 75), v, font=load_font('bold', 27), fill=c(NAVY), anchor='lm')
    im.save(f'{OUT}/{fn}')

cover(f'01_{P}_대표이미지.png', "종부세 납부", "12월 1일~15일", "250만 원 넘으면 분납", "종합부동산세법 제16조·제20조 · 2026.11.24 확인")
cover('t01_종부세납부기간_분납.png', "종부세 분납", "세액별로 계산", "400만→150만", "시행령 제16조 · 필자 계산 · 2026.11.24 확인")

im, d = canvas(900)
d.text((60, 55), "납부 일정 (법 제16조)", font=big, fill=c(NAVY))
d.text((60, 120), "해당 연도 기준", font=body, fill=c(GRAY))
box(d, 190, 120, GOLD, "납부고지서 발급", "납부기간 시작 5일 전까지", "11/26")
box(d, 340, 120, NAVY, "납부기간 시작", "12월 1일", "12/1")
box(d, 490, 120, RED, "납부기간 마감", "12월 15일", "12/15")
box(d, 640, 120, GREEN, "신고납부 선택 시", "12월 1일~15일 신고·납부", "신고")
im.save(f'{OUT}/02_{P}_일정.png')

im, d = canvas(900)
d.text((60, 55), "분납 기준 (법 제20조·시행령 제16조)", font=big, fill=c(NAVY))
d.text((60, 120), "납부기한이 지난 날부터 6개월 이내", font=body, fill=c(GRAY))
box(d, 190, 130, GRAY, "세액 250만 원 이하", "분납 대상 아님", "불가")
box(d, 350, 130, NAVY, "250만 초과 ~ 500만 이하", "세액에서 250만 원을 뺀 금액", "초과분")
box(d, 510, 130, GOLD, "500만 원 초과", "세액의 50% 이하 금액", "50%")
d.text((90, 700), "신청서는 납부기한까지 관할 세무서장에게 제출", font=small, fill=c(GRAY))
im.save(f'{OUT}/03_{P}_분납.png')

im, d = canvas(1000)
d.text((60, 55), "납부유예 요건 (법 제20조의2)", font=big, fill=c(NAVY))
d.text((60, 120), "모두 충족 · 납부기한 3일 전까지 신청 · 담보 제공", font=small, fill=c(GRAY))
rows = [("1세대 1주택자", "공동명의 1주택자 포함"), ("60세 이상 또는 5년 이상 보유", "과세기준일 현재"),
        ("소득 기준", "총급여 7천만 원 이하 또는 종합소득 6천만 원 이하"), ("주택분 세액", "100만 원 초과")]
for i, (a, b) in enumerate(rows):
    box(d, 190 + i * 170, 140, GOLD, a, b)
im.save(f'{OUT}/04_{P}_유예.png')

core(f'05_{P}_핵심정리.png', [("1", "납부기간 12월 1일~15일 · 고지서는 5일 전까지", NAVY), ("2", "250만 원 초과 시 6개월 이내 분납 가능", RED), ("3", "납부유예는 1주택자 요건+담보, 3일 전 신청", GREEN)])

im, d = canvas(900)
d.text((60, 55), "분납 금액 계산 (필자 계산)", font=big, fill=c(NAVY))
d.text((60, 120), "시행령 제16조 제1항", font=body, fill=c(GRAY))
box(d, 190, 150, GRAY, "세액 200만 원", "250만 원 이하", "불가")
box(d, 370, 150, NAVY, "세액 400만 원", "400 - 250 = 150만 원까지", "150만")
box(d, 550, 150, GOLD, "세액 800만 원", "800의 50% 이하 = 400만 원까지", "400만")
d.text((90, 760), "분납할 금액은 한도 기준이며 실제 신청은 세무서에서 확인", font=small, fill=c(GRAY))
im.save(f'{OUT}/t01x.png'); os.replace(f'{OUT}/t01x.png', f'{OUT}/t02_종부세납부기간_상담.png')

core('t03_종부세납부기간_핵심.png', [("1", "납부기간 12월 1일~15일", NAVY), ("2", "400만→150만 · 800만→400만 분납 한도", RED), ("3", "분납·유예는 납부기한 전 신청", GREEN)])
