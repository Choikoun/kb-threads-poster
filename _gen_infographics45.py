from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
import os
OUT = 'blog_images/2026-11-22_육아휴직급여'
P = '육아휴직급여'
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



cover(f'01_{P}_대표이미지.png', "육아휴직급여", "3개월 상한 250만", "시행령 제95조", "고용보험법 · 2026.11.22 확인")
cover('t01_육아휴직급여_부모.png', "부모 모두", "육아휴직 급여", "6개월 상한 450만", "시행령 제95조의3 · 2026.11.22 확인")

im, d = canvas(900)
d.text((60, 55), "월 지급액 (시행령 제95조)", font=big, fill=c(NAVY))
d.text((60, 120), "육아휴직 시작일 기준 월 통상임금", font=body, fill=c(GRAY))
box(d, 190, 150, NAVY, "1~3개월", "통상임금 100% · 하한 70만 원", "상한 250만")
box(d, 370, 150, GOLD, "4~6개월", "통상임금 100% · 하한 70만 원", "상한 200만")
box(d, 550, 150, GREEN, "7개월~종료", "통상임금 80% · 하한 70만 원", "상한 160만")
d.text((90, 770), "1개월 미만은 휴직 일수에 비례해 계산", font=small, fill=c(GRAY))
im.save(f'{OUT}/02_{P}_금액.png')

im, d = canvas(1000)
d.text((60, 55), "부모 모두 사용 시 상한", font=big, fill=c(NAVY))
d.text((60, 120), "출생 후 18개월 이내 · 각각 6개월 사용 · 시행령 제95조의3", font=small, fill=c(GRAY))
rows = [("1~2개월째", "250만"), ("3개월째", "300만"), ("4개월째", "350만"), ("5개월째", "400만"), ("6개월째", "450만")]
for i, (a, b) in enumerate(rows):
    y = 190 + i * 130
    d.rectangle([90, y, W - 90, y + 105], fill=c("#FFFFFF"), outline=c(GOLD), width=3)
    d.text((130, y + 52), a, font=load_font('extrabold', 32), fill=c(NAVY), anchor='lm')
    d.text((W - 130, y + 52), b, font=load_font('extrabold', 40), fill=c(RED), anchor='rm')
d.text((90, 860), "7개월째부터는 통상임금 80%, 상한 160만 원", font=small, fill=c(GRAY))
im.save(f'{OUT}/03_{P}_부모특례.png')

im, d = canvas(900)
d.text((60, 55), "급여가 끊기거나 줄 때", font=big, fill=c(NAVY))
d.text((60, 120), "고용보험법 제73조 · 시행령 제98조", font=body, fill=c(GRAY))
box(d, 190, 120, RED, "휴직 중 이직", "이직한 때부터 지급 안 함", "중단")
box(d, 330, 120, GOLD, "휴직 중 취업", "취업한 기간은 지급 안 함, 신고 필요", "신고")
box(d, 470, 120, NAVY, "사업주 금품", "급여 합산이 통상임금 초과 시 감액", "감액")
box(d, 610, 120, GRAY, "부정 수급", "받은 날부터 지급 제한", "제한")
im.save(f'{OUT}/04_{P}_주의.png')

core(f'05_{P}_핵심정리.png', [("1", "시작일 이전 피보험 단위기간 180일 이상", NAVY), ("2", "3개월 250만 · 4~6개월 200만 · 7개월~ 160만", RED), ("3", "시작 1개월 후~종료 후 12개월 안에 신청", GREEN)])

im, d = canvas(900)
d.text((60, 55), "부모 각 6개월 사용 시 합계", font=big, fill=c(NAVY))
d.text((60, 120), "필자 계산 · 월 통상임금이 각각 같다고 가정", font=body, fill=c(GRAY))
box(d, 190, 150, NAVY, "통상임금 월 300만 원", "250+250+300+300+300+300", "1,700만")
box(d, 370, 150, GREEN, "통상임금 월 500만 원", "250+250+300+350+400+450", "2,000만")
d.text((90, 590), "부모 둘 합계: 3,400만 원 · 4,000만 원 (6개월까지)", font=sub, fill=c(NAVY))
d.text((90, 650), "7개월째부터는 통상임금 80%, 상한 160만 원", font=small, fill=c(GRAY))
im.save(f'{OUT}/t02_육아휴직급여_예시.png')
core('t03_육아휴직급여_핵심.png', [("1", "부모 모두 사용 시 6개월까지 상한이 단계적으로 상승", NAVY), ("2", "출생 후 18개월 이내 자녀가 대상", RED), ("3", "신청은 시작 1개월 후~종료 후 12개월 안에", GREEN)])
print('ok')
