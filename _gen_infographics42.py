from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
import os
OUT = 'blog_images/2026-11-19_건강보험임의계속가입'
P = '건강보험임의계속가입'
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


cover(f'01_{P}_대표이미지.png', "건강보험임의계속", "퇴직 후 최대 36개월", "2개월 안에 신청", "국민건강보험법 제110조 기준")
cover(f't01_{P}_질문.png', "건강보험임의계속", "이런 경우 어떻게", "질문 7가지", "국민건강보험법 제110조 · 필자 가정")

im, d = canvas(800)
d.text((60, 55), "신청 자격", font=big, fill=c(NAVY))
d.text((60, 120), "국민건강보험법 제110조 제1항 · 시행규칙 제62조", font=body, fill=c(GRAY))
box(d, 200, 160, NAVY, "퇴직 전 18개월 안", "직장가입자로 지낸 기간을 합산", "18개월")
box(d, 400, 160, GREEN, "합쳐서 1년 이상", "통산 기준 (개별 판단은 공단 확인)", "1년")
d.text((90, 640), "직장을 옮겨 다닌 기간도 합쳐 보는 구조 (필자 해석)", font=small, fill=c(GRAY))
im.save(f'{OUT}/02_{P}_자격.png')

im, d = canvas(900)
d.text((60, 55), "신청 기한 순서", font=big, fill=c(NAVY))
d.text((60, 120), "기산점은 퇴직일이 아니라 첫 지역보험료 고지", font=body, fill=c(GRAY))
box(d, 190, 120, NAVY, "1 퇴직 (사용관계 종료)", "지역가입자로 바뀜 (필자 정리)", "")
box(d, 330, 120, GOLD, "2 첫 지역보험료 고지서 수령", "이날부터 신청 가능", "")
box(d, 470, 120, RED, "3 납부기한에서 2개월 경과 전", "이 안에 신청", "마감")
d.text((90, 660), "제110조 제1항 · 일정은 개인마다 다릅니다", font=small, fill=c(GRAY))
im.save(f'{OUT}/03_{P}_기한.png')

im, d = canvas(800)
d.text((60, 55), "유지 기간 (필자 가정)", font=big, fill=c(NAVY))
d.text((60, 120), "시행령 제77조 제1항", font=body, fill=c(GRAY))
box(d, 200, 140, NAVY, "2026.11.30 퇴사", "사용관계가 끝난 날", "")
box(d, 370, 140, GOLD, "2026.12.1부터 시작", "다음 날부터 기산", "")
box(d, 540, 140, GREEN, "상한 2029.11.30", "36개월이 되는 날을 넘지 않는 범위 (필자 계산)", "36개월")
im.save(f'{OUT}/04_{P}_36개월.png')

im, d = canvas(900)
d.text((60, 55), "보험료 구조", font=big, fill=c(NAVY))
d.text((60, 120), "국민건강보험법 제110조 제3항·제4항·제5항", font=body, fill=c(GRAY))
box(d, 200, 130, NAVY, "보수월액 = 최근 12개월 평균", "필자 가정 300만 x 6 + 260만 x 6", "280만")
box(d, 360, 130, RED, "보수월액보험료 전액 본인 부담", "재직 때처럼 회사가 내 주지 않음", "전액")
box(d, 520, 130, GREEN, "고시에 따라 일부 경감 가능", "경감 비율은 확인하지 못했습니다", "경감")
im.save(f'{OUT}/05_{P}_보험료.png')

im, d = canvas(1000)
d.text((60, 55), "상황별 정리", font=big, fill=c(NAVY))
d.text((60, 120), "국민건강보험법 제110조 · 시행규칙 제63조", font=body, fill=c(GRAY))
rows = [("직장 2곳 합산", "퇴직 전 18개월 안이면 통산", NAVY), ("기한 경과", "문구상 신청 불가", RED),
        ("첫 보험료 미납", "자격 유지 불가", RED), ("재취업", "자격 변동 (제63조 제3항)", GOLD),
        ("36개월 종료", "다음 날 자격 변동", GREEN), ("중도 탈퇴", "접수 다음 날 자격 변동", GRAY)]
for i, (a, b, col) in enumerate(rows):
    y = 180 + i * 130
    d.rectangle([90, y, W - 90, y + 105], fill=c("#FFFFFF"), outline=c(col), width=4)
    d.text((130, y + 52), a, font=load_font('extrabold', 30), fill=c(col), anchor='lm')
    d.text((W - 130, y + 52), b, font=body, fill=c(NAVY), anchor='rm')
im.save(f'{OUT}/t02_{P}_상황.png')

core(f'06_{P}_핵심정리.png', [("1", "퇴직 전 18개월 중 직장가입 통산 1년 이상", NAVY), ("2", "첫 지역보험료 납부기한 2개월 안에 신청, 최대 36개월", RED), ("3", "최근 12개월 평균 보수월액 기준, 전액 본인 부담", GREEN)])
core(f't03_{P}_핵심.png', [("1", "신청 기한은 첫 지역보험료 고지가 기준", NAVY), ("2", "신청 뒤 첫 보험료도 제때 납부", RED), ("3", "취업하거나 36개월이 지나면 자격 변동", GREEN)])
core(f't04_{P}_정리.png', [("1", "자격: 퇴직 전 18개월 중 통산 1년", NAVY), ("2", "기간: 퇴직 다음 날부터 최대 36개월", GOLD), ("3", "보험료: 전액 본인, 12개월 평균 기준", GREEN)])
print('ok')
