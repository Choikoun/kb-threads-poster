from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
import os
OUT = 'blog_images/2026-11-26_출산전후휴가급여'
P = '출산전후휴가급여'
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
    d.text((70, 200), l1, font=load_font('extrabold', 90), fill=c(NAVY))
    d.text((70, 380), l2, font=load_font('extrabold', 66), fill=c(NAVY))
    d.text((70, 490), l3, font=load_font('extrabold', 80), fill=c(GOLD))
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

cover(f'01_{P}_대표이미지.png', "출산전후휴가급여", "대기업은 뒤 30일", "신청은 12개월 이내", "고용보험법 제75조·제76조 · 2026.11.26 확인")
cover('t01_출산전후휴가급여_일수.png', "출산휴가 급여", "회사 규모별", "받는 일수 계산", "고용보험법 제76조 · 필자 계산 · 2026.11.26 확인")

im, d = canvas(900)
d.text((60, 55), "급여 요건 (고용보험법 제75조)", font=big, fill=c(NAVY))
d.text((60, 120), "휴가 종료일 기준", font=body, fill=c(GRAY))
box(d, 190, 130, NAVY, "피보험 단위기간", "휴가가 끝난 날 이전 합산 180일 이상", "180일")
box(d, 350, 130, GOLD, "신청 시작", "휴가 시작 후 1개월부터", "1개월")
box(d, 510, 130, RED, "신청 마감", "휴가가 끝난 날 이후 12개월 이내", "12개월")
d.text((90, 700), "비우선지원대상기업은 휴가 시작 후 60일(둘 이상 자녀 75일) 지난 날 기준", font=small, fill=c(GRAY))
im.save(f'{OUT}/02_{P}_요건.png')

im, d = canvas(900)
d.text((60, 55), "급여 대상 일수 (필자 계산)", font=big, fill=c(NAVY))
d.text((60, 120), "법 제76조 제1항 제1호", font=body, fill=c(GRAY))
box(d, 190, 150, GREEN, "우선지원대상기업 · 90일", "90일 전체", "90일")
box(d, 370, 150, NAVY, "그 외 기업 · 90일", "최초 60일 사업주 유급, 뒤 30일 급여", "30일")
box(d, 550, 150, GOLD, "그 외 기업 · 둘 이상 자녀 120일", "최초 75일 사업주 유급, 뒤 45일 급여", "45일")
d.text((90, 760), "미숙아 100일은 60일 초과분 40일, 한도 40일", font=small, fill=c(GRAY))
im.save(f'{OUT}/03_{P}_일수.png')

im, d = canvas(900)
d.text((60, 55), "급여가 줄거나 제한될 때", font=big, fill=c(NAVY))
d.text((60, 120), "시행령 제102조~제104조", font=body, fill=c(GRAY))
box(d, 190, 120, RED, "사업주 금품 수령", "급여와 합산이 통상임금 초과 시 초과분 감액", "감액")
box(d, 340, 120, GOLD, "휴가 중 취업", "취업 사실 신고 필요", "신고")
box(d, 490, 120, NAVY, "부정 수급", "지급 제한과 반환명령", "제한")
im.save(f'{OUT}/04_{P}_감액.png')

core(f'05_{P}_핵심정리.png', [("1", "휴가 종료일 이전 피보험 단위기간 180일 이상", NAVY), ("2", "비우선지원대상기업은 90일 중 뒤 30일 급여", RED), ("3", "신청은 휴가 종료 후 12개월 이내", GREEN)])

im, d = canvas(900)
d.text((60, 55), "회사 규모별 급여 일수", font=big, fill=c(NAVY))
d.text((60, 120), "필자 계산 · 근로기준법 제74조 + 고용보험법 제76조", font=body, fill=c(GRAY))
box(d, 190, 150, GREEN, "우선지원대상기업", "휴가 90일 전체", "90일")
box(d, 370, 150, NAVY, "그 외 기업", "60일 초과분, 한도 30일", "30일")
d.text((90, 590), "둘 이상 자녀: 휴가 120일 중 75일 초과분, 한도 45일", font=sub, fill=c(NAVY))
d.text((90, 650), "내 회사가 우선지원대상기업인지는 고용센터에 확인", font=small, fill=c(GRAY))
im.save(f'{OUT}/t02_출산전후휴가급여_상담.png')

core('t03_출산전후휴가급여_핵심.png', [("1", "신청은 휴가 종료 후 12개월 이내", NAVY), ("2", "대기업은 90일 중 뒤 30일 급여", RED), ("3", "내 회사 규모는 고용센터에서 확인", GREEN)])
