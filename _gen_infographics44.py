from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
import os
OUT = 'blog_images/2026-11-21_실업급여조건'
P = '실업급여조건'
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


cover(f'01_{P}_대표이미지.png', "실업급여조건", "18개월 중 180일", "퇴사 사유도 확인", "고용보험법 제40조 · 2026.11.21 확인")
cover('t01_실업급여개편_변경점.png', "실업급여", "2027 주6일 지급", "보도된 개편안", "YTN·세계일보 2026.9.2 · 확정 아님")

im, d = canvas(900)
d.text((60, 55), "수급 요건 (제40조)", font=big, fill=c(NAVY))
d.text((60, 120), "모두 갖춰야 지급", font=body, fill=c(GRAY))
box(d, 190, 120, NAVY, "피보험 단위기간", "이직 전 18개월 중 합산 180일 이상", "1")
box(d, 330, 120, GOLD, "근로 의사·능력", "있는데도 취업하지 못한 상태", "2")
box(d, 470, 120, RED, "퇴사 사유", "제58조 제한 사유가 아닐 것", "3")
box(d, 610, 120, GREEN, "재취업 노력", "적극적으로 노력할 것", "4")
d.text((90, 800), "보수를 받은 날의 합이 기준 (근무 개월 수 아님)", font=small, fill=c(GRAY))
im.save(f'{OUT}/02_{P}_요건.png')

im, d = canvas(900)
d.text((60, 55), "제한되는 퇴사 사유", font=big, fill=c(NAVY))
d.text((60, 120), "고용보험법 제58조", font=body, fill=c(GRAY))
box(d, 190, 170, RED, "중대한 귀책사유 해고", "금고 이상 형 · 막대한 손해 · 장기 무단결근", "해고")
box(d, 400, 170, GOLD, "자기 사정 이직", "전직·자영업 이직 등, 정당한 사유가 아닌 경우", "자진")
d.text((90, 640), "정당한 사유는 고용노동부령(시행규칙)이 정함", font=sub, fill=c(NAVY))
d.text((90, 695), "직업안정기관의 장이 인정하면 수급자격 없음", font=small, fill=c(GRAY))
im.save(f'{OUT}/03_{P}_퇴사사유.png')

im, d = canvas(1000)
d.text((60, 55), "소정급여일수", font=big, fill=c(NAVY))
d.text((60, 120), "고용노동부 FAQ · 2019.10.1 이후 이직자", font=body, fill=c(GRAY))
rows = [("1년 미만", "120일", "120일"), ("1~3년", "150일", "180일"), ("3~5년", "180일", "210일"), ("5~10년", "210일", "240일"), ("10년 이상", "240일", "270일")]
d.text((300, 200), "50세 미만", font=sub, fill=c(NAVY), anchor='mm'); d.text((700, 200), "50세 이상·장애인", font=sub, fill=c(RED), anchor='mm')
for i, (a, b, cc) in enumerate(rows):
    y = 240 + i * 125
    d.rectangle([90, y, W - 90, y + 100], fill=c("#FFFFFF"), outline=c(GOLD), width=3)
    d.text((130, y + 50), a, font=load_font('extrabold', 30), fill=c(NAVY), anchor='lm')
    d.text((540, y + 50), b, font=load_font('extrabold', 36), fill=c(NAVY), anchor='mm')
    d.text((900, y + 50), cc, font=load_font('extrabold', 36), fill=c(RED), anchor='mm')
im.save(f'{OUT}/04_{P}_소정급여일수.png')

im, d = canvas(900)
d.text((60, 55), "하루 지급액 한도", font=big, fill=c(NAVY))
d.text((60, 120), "기초일액의 60% · 필자 계산", font=body, fill=c(GRAY))
box(d, 200, 160, NAVY, "상한", "기초일액 상한 11만3,500원 × 60%", "68,100원")
box(d, 400, 160, GREEN, "하한", "최저임금 10,320원 × 8시간 × 80%", "66,048원")
d.text((90, 620), "시행령 제68조 · 고용노동부 보도자료(최저임금)", font=small, fill=c(GRAY))
d.text((90, 670), "소정근로시간이 8시간보다 짧으면 하한이 달라집니다", font=small, fill=c(RED))
im.save(f'{OUT}/05_{P}_금액.png')

im, d = canvas(900)
d.text((60, 55), "2027 개편안 (보도)", font=big, fill=c(NAVY))
d.text((60, 120), "YTN · 세계일보 2026.9.2 · 확정 아님", font=body, fill=c(GRAY))
box(d, 190, 140, NAVY, "지급 방식", "주7일 → 무급휴일 제외 주6일", "주6일")
box(d, 350, 140, GREEN, "총 지급액", "120~270일 소정급여일수 유지", "유지")
box(d, 510, 140, GOLD, "상한액", "정액 → 하한액의 103% 연동", "103%")
box(d, 670, 140, RED, "조기재취업수당", "제외 기준 월 574만 → 300만 원", "300만")
im.save(f'{OUT}/t02_실업급여개편_수령액.png')
core('t03_실업급여개편_핵심.png', [("1", "주6일 지급은 보도된 개편안, 아직 확정 아님", NAVY), ("2", "총액은 유지, 월 수령액은 줄 수 있다는 추정", RED), ("3", "이직 시점의 법령이 기준, 시행 소식 확인", GREEN)])
core(f'06_{P}_핵심정리.png', [("1", "18개월 중 보수 받은 날 180일 이상", NAVY), ("2", "퇴사 사유가 제58조 제한에 해당하지 않을 것", RED), ("3", "이직 다음 날부터 12개월 안에 신고", GREEN)])
print('ok')
