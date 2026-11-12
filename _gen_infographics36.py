from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
OUT = 'blog_images/2026-11-12_증여세연부연납'
P = '증여세연부연납'
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

im, d = canvas(900)
d.rectangle([0, 0, W, 14], fill=c(GOLD))
d.text((70, 200), "증여세 연부연납", font=load_font('extrabold', 100), fill=c(NAVY))
d.text((70, 380), "2천만 원 넘으면", font=load_font('extrabold', 76), fill=c(NAVY))
d.text((70, 490), "최대 5년 분할", font=load_font('extrabold', 96), fill=c(GOLD))
d.text((70, 690), "상속세 및 증여세법 제71조 · 법제처·국세청 기준", font=sub, fill=c(GRAY))
im.save(f'{OUT}/01_{P}_대표이미지.png')

im, d = canvas(1000)
d.text((60, 55), "신청 요건 세 가지", font=big, fill=c(NAVY))
d.text((60, 120), "모두 갖춰야 합니다 · 수증자 주소지 관할 세무서장 허가", font=body, fill=c(GRAY))
box(d, 200, 140, NAVY, "납부세액 2천만 원 초과", "각 회분 분할납부세액은 1천만 원 초과")
box(d, 370, 140, GOLD, "납세담보 제공", "납세보증보험증권 등 확실하면 신청일 허가 간주")
box(d, 540, 140, GREEN, "신청기한 안에 신청서 제출", "신고 시 신고기한까지 · 고지 시 납부기한까지")
d.text((90, 760), "분납과 선택 관계", font=sub, fill=c(NAVY))
d.text((90, 815), "연부연납을 허가받으면 분납은 할 수 없습니다", font=load_font('extrabold', 34), fill=c(RED))
im.save(f'{OUT}/02_{P}_요건.png')

im, d = canvas(860)
d.text((60, 55), "기간은 재산별로 다릅니다", font=big, fill=c(NAVY))
d.text((60, 120), "상속세 및 증여세법 제71조 제2항 제2호", font=body, fill=c(GRAY))
box(d, 200, 130, NAVY, "일반 증여재산", "허가일부터", "5년")
box(d, 360, 130, GOLD, "가업승계 증여세 과세특례 재산", "조세특례제한법 제30조의6 · 2024.1.1. 이후 신청분", "15년", 28)
d.text((90, 570), "참고: 상속세는 일반 재산 10년입니다", font=sub, fill=c(NAVY))
d.text((90, 625), "증여세는 상속세와 기간이 다릅니다", font=small, fill=c(GRAY))
im.save(f'{OUT}/03_{P}_기간.png')

im, d = canvas(900)
d.text((60, 55), "가산금 이자율", font=big, fill=c(NAVY))
d.text((60, 120), "국세청 증여세 납부 안내 · 연 이율", font=body, fill=c(GRAY))
box(d, 200, 110, RED, "2024.3.22.부터", None, "연 3.5%")
box(d, 340, 110, GOLD, "2023.3.20.~2024.3.21.", None, "연 2.9%")
box(d, 480, 110, GREEN, "2021.3.16.~2023.3.19.", None, "연 1.2%")
d.text((90, 680), "2020.2.11. 이후 신청분은 납부일 현재 이자율을 적용합니다", font=sub, fill=c(NAVY))
d.text((90, 740), "가산금 정확한 산식은 이 글에서 확인하지 못했습니다", font=small, fill=c(GRAY))
im.save(f'{OUT}/04_{P}_가산금.png')

im, d = canvas(800)
d.text((60, 55), "허가 취소·변경 사유", font=big, fill=c(NAVY))
d.text((60, 120), "제71조 제4항 중 증여세에 해당하는 것", font=body, fill=c(GRAY))
box(d, 200, 100, RED, "지정된 납부기한까지 미납")
box(d, 320, 100, RED, "담보 변경·보전 명령 불이행")
box(d, 440, 100, RED, "국세징수법 제9조 사유로 전액 징수 곤란", None, None, 28)
d.text((90, 600), "허가 취소 시 연부연납과 관계된 세액을 징수할 수 있습니다", font=sub, fill=c(NAVY))
d.text((90, 655), "매년 납부 일정을 따로 관리해야 합니다", font=small, fill=c(GRAY))
im.save(f'{OUT}/05_{P}_취소사유.png')

im, d = canvas(780)
d.text((60, 55), "핵심 정리", font=big, fill=c(NAVY))
for i, (k, v, col) in enumerate([("1", "2천만 원 초과 · 담보 · 신고기한까지 신청, 분납과 택일", NAVY), ("2", "일반 최대 5년, 가업승계 특례 15년, 각 회분 1천만 원 초과", GREEN), ("3", "가산금 연 3.5%(2024.3.22.~), 납부기한 어기면 취소 가능", RED)]):
    d.rectangle([90, 160 + i * 190, W - 90, 160 + i * 190 + 150], fill=c("#FFFFFF"), outline=c(col), width=4)
    d.text((130, 160 + i * 190 + 75), k, font=load_font('extrabold', 44), fill=c(col), anchor='lm')
    d.text((220, 160 + i * 190 + 75), v, font=load_font('bold', 28), fill=c(NAVY), anchor='lm')
im.save(f'{OUT}/06_{P}_핵심정리.png')
print('ok')
