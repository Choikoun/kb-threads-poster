from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
import os
OUT = 'blog_images/2026-11-27_실업급여소정급여일수'
P = '실업급여소정급여일수'
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

cover(f'01_{P}_대표이미지.png', "실업급여", "소정급여일수", "1년 4개월 근무 = 150일", "고용보험법 제50조 · 고용노동부 FAQ · 2026.11.27 확인")
cover('t01_실업급여소정급여일수_일수.png', "실업급여 몇 개월", "근무 기간별", "120일~270일", "고용보험법 제50조 · 2026.11.27 확인")

im, d = canvas(1000)
d.text((60, 55), "소정급여일수 (2019.10.1. 이후 이직자)", font=big, fill=c(NAVY))
d.text((60, 120), "고용노동부 FAQ 게시 기준", font=body, fill=c(GRAY))
rows = [("1년 미만", "120일", "120일"), ("1년~3년", "150일", "180일"), ("3년~5년", "180일", "210일"), ("5년~10년", "210일", "240일"), ("10년 이상", "240일", "270일")]
d.rectangle([90, 190, W - 90, 260], fill=c(NAVY))
d.text((130, 225), "피보험기간", font=sub, fill=c("#FFFFFF"), anchor='lm')
d.text((620, 225), "50세 미만", font=sub, fill=c("#FFFFFF"), anchor='mm')
d.text((930, 225), "50세 이상·장애인", font=load_font('bold', 26), fill=c("#FFFFFF"), anchor='mm')
for i, (a, b, e) in enumerate(rows):
    y = 270 + i * 100
    col = GOLD if i == 1 else NAVY
    d.rectangle([90, y, W - 90, y + 85], fill=c("#FFFFFF"), outline=c(col), width=4 if i == 1 else 2)
    d.text((130, y + 42), a, font=load_font('extrabold', 30), fill=c(col), anchor='lm')
    d.text((620, y + 42), b, font=load_font('extrabold', 34), fill=c(col), anchor='mm')
    d.text((930, y + 42), e, font=load_font('extrabold', 34), fill=c(col), anchor='mm')
d.text((90, 800), "1년 4개월 근무는 1년~3년 구간(금색 표시)", font=sub, fill=c(NAVY))
d.text((90, 860), "경계에 걸리면 고용센터에서 확인", font=small, fill=c(GRAY))
im.save(f'{OUT}/02_{P}_일수표.png')

im, d = canvas(900)
d.text((60, 55), "피보험기간 계산 (제50조)", font=big, fill=c(NAVY))
d.text((60, 120), "수급 요건 180일(피보험 단위기간)과는 다른 개념", font=body, fill=c(GRAY))
box(d, 190, 130, NAVY, "기본", "이직 당시 적용 사업에서 고용된 기간", "제3항")
box(d, 350, 130, GREEN, "합산", "이전 직장 자격 상실일부터 3년 이내 재취득", "합산")
box(d, 510, 130, RED, "제외", "이전 직장 퇴사로 구직급여를 받은 기간", "제외")
im.save(f'{OUT}/03_{P}_피보험기간.png')

im, d = canvas(900)
d.text((60, 55), "받는 기간과 기한", font=big, fill=c(NAVY))
d.text((60, 120), "고용보험법 제48조 · 제49조", font=body, fill=c(GRAY))
box(d, 190, 130, GOLD, "대기기간", "신고일부터 7일은 지급하지 않음", "7일")
box(d, 350, 130, NAVY, "수급기간", "이직 다음 날부터 12개월 안에 일수 한도로 지급", "12개월")
box(d, 510, 130, GREEN, "연장 사유", "임신·출산·육아 신고 시 최대 4년", "4년")
d.text((90, 710), "훈련·개별·특별연장급여는 제51~53조에 별도 요건", font=small, fill=c(GRAY))
im.save(f'{OUT}/04_{P}_수급기간.png')

core(f'05_{P}_핵심정리.png', [("1", "소정급여일수는 근무 기간·나이로 120~270일", NAVY), ("2", "1~3년 근무: 50세 미만 150일, 이상 180일", GOLD), ("3", "이직 다음 날부터 12개월 안에 신청", GREEN)])

im, d = canvas(900)
d.text((60, 55), "1년 4개월 근무 예시", font=big, fill=c(NAVY))
d.text((60, 120), "1년 이상 3년 미만 구간 · 필자 계산", font=body, fill=c(GRAY))
box(d, 190, 150, NAVY, "50세 미만", "150일 (30일 기준 약 5개월)", "150일")
box(d, 370, 150, GOLD, "50세 이상·장애인", "180일 (30일 기준 약 6개월)", "180일")
d.text((90, 590), "먼저 이직 전 18개월 중 180일 요건을 충족해야 함", font=sub, fill=c(NAVY))
d.text((90, 650), "퇴사 사유가 제한 사유가 아니어야 함", font=small, fill=c(GRAY))
im.save(f'{OUT}/t02_{P}_상담.png')

core(f't03_{P}_핵심.png', [("1", "일수는 근무 기간과 나이로 정해집니다", NAVY), ("2", "1년 4개월 근무: 150일 또는 180일", GOLD), ("3", "12개월 안에 신청해야 다 쓸 수 있음", GREEN)])
print('ok')
