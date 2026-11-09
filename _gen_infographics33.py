from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
OUT = 'blog_images/2026-11-09_대습상속'
P = '대습상속'
BG = "#F7F5F0"; NAVY = "#1B2A4A"; GOLD = "#B8925A"; GRAY = "#6B7280"; RED = "#B5473A"; GREEN = "#2F7D5D"
W = 1200; c = hex_to_rgb
def canvas(h):
    im = Image.new('RGB', (W, h), c(BG)); return im, ImageDraw.Draw(im)
sub = load_font('bold', 32); body = load_font('regular', 28); small = load_font('regular', 24); big = load_font('extrabold', 40)
def box(d, y, h, col, left, right=None, lsize=36):
    d.rectangle([90, y, W - 90, y + h], fill=c("#FFFFFF"), outline=c(col), width=4)
    d.text((130, y + h // 2), left, font=load_font('extrabold', lsize), fill=c(col), anchor='lm')
    if right: d.text((W - 130, y + h // 2), right, font=body, fill=c(NAVY), anchor='rm')
def node(d, cx, y, w, h, col, t1, t2=None, fill="#FFFFFF", dash=False):
    d.rectangle([cx - w // 2, y, cx + w // 2, y + h], fill=c(fill), outline=c(col), width=4)
    if t2:
        d.text((cx, y + h // 2 - 20), t1, font=load_font('extrabold', 28), fill=c(col), anchor='mm')
        d.text((cx, y + h // 2 + 22), t2, font=small, fill=c(GRAY), anchor='mm')
    else:
        d.text((cx, y + h // 2), t1, font=load_font('extrabold', 28), fill=c(col), anchor='mm')
def line(d, x1, y1, x2, y2, col=NAVY):
    d.line([x1, y1, x2, y2], fill=c(col), width=4)

# 01 대표
im, d = canvas(900)
d.rectangle([0, 0, W, 14], fill=c(GOLD))
d.text((70, 200), "대습상속", font=load_font('extrabold', 110), fill=c(NAVY))
d.text((70, 380), "자녀가 먼저 사망하면", font=load_font('extrabold', 76), fill=c(NAVY))
d.text((70, 490), "손자녀가 순위를 잇는다", font=load_font('extrabold', 76), fill=c(GOLD))
d.text((70, 690), "민법 제1001조 · 법제처 현행 조문 기준", font=sub, fill=c(GRAY))
im.save(f'{OUT}/01_{P}_대표이미지.png')

# 02 상속관계도
im, d = canvas(980)
d.text((60, 50), "누가 상속인이 되나", font=big, fill=c(NAVY))
d.text((60, 115), "국세청 예시: 아들 E가 상속개시일 전에 사망한 경우", font=body, fill=c(GRAY))
node(d, 600, 180, 300, 90, NAVY, "피상속인", "아버지 사망")
line(d, 600, 270, 600, 310); line(d, 300, 310, 900, 310)
line(d, 300, 310, 300, 350); line(d, 900, 310, 900, 350)
node(d, 300, 350, 300, 100, RED, "큰아들 E", "먼저 사망", fill="#F6E4E0")
node(d, 900, 350, 300, 100, GREEN, "둘째 아들", "상속인")
node(d, 600, 355, 240, 90, GOLD, "E의 배우자", "대습상속인")
line(d, 450, 400, 480, 400)
line(d, 300, 450, 300, 560); line(d, 180, 560, 420, 560); line(d, 180, 560, 180, 620); line(d, 420, 560, 420, 620)
node(d, 180, 620, 220, 90, GOLD, "자녀 F", "대습상속인")
node(d, 420, 620, 220, 90, GOLD, "자녀 G", "대습상속인")
d.text((600, 840), "큰아들 몫은 E의 배우자와 자녀가 이어받습니다", font=sub, fill=c(NAVY), anchor='mm')
d.text((600, 895), "자녀 F·G는 피상속인의 손자녀입니다", font=small, fill=c(GRAY), anchor='mm')
im.save(f'{OUT}/02_{P}_상속관계도.png')

# 03 사유
im, d = canvas(900)
d.text((60, 55), "대습상속이 생기는 사유", font=big, fill=c(NAVY))
d.text((60, 120), "2026년 3월 17일 시행 민법 제1001조 기준", font=body, fill=c(GRAY))
box(d, 200, 110, NAVY, "① 상속개시 전 사망", "피상속인보다 먼저 사망", 30)
box(d, 340, 110, RED, "② 결격사유", "민법 제1004조", 30)
box(d, 480, 110, GOLD, "③ 상속권 상실 선고", "민법 제1004조의2 · 가정법원", 30)
d.text((90, 650), "조문은 직계비속과 형제자매만 적고 있습니다", font=sub, fill=c(NAVY))
d.text((90, 705), "상속이 시작된 뒤에 사망한 경우는 이 조문의 대상이 아닙니다", font=small, fill=c(GRAY))
im.save(f'{OUT}/03_{P}_사유.png')

# 04 상속분 가정 계산
im, d = canvas(940)
d.text((60, 55), "대습상속분 가정 계산", font=big, fill=c(NAVY))
d.text((60, 120), "재산 12억 원, 어머니 사망, 유언 없음, 큰아들 先死", font=body, fill=c(GRAY))
box(d, 200, 110, GREEN, "둘째 아들", "6억 원", 32)
box(d, 340, 110, GOLD, "큰아들의 배우자", "약 2억 5,700만 원", 30)
box(d, 480, 110, NAVY, "큰아들의 자녀 각각", "약 1억 7,100만 원", 30)
d.text((90, 650), "큰아들 몫 6억 원을 배우자 1.5 : 자녀 1 : 자녀 1 로 나눔", font=sub, fill=c(NAVY))
d.text((90, 705), "가정 계산입니다 · 기여분, 생전 증여, 유류분은 반영하지 않음", font=small, fill=c(GRAY))
d.text((90, 750), "민법 제1009조 제2항, 제1010조 기준", font=small, fill=c(GRAY))
im.save(f'{OUT}/04_{P}_상속분.png')

# 05 할증 비교
im, d = canvas(900)
d.text((60, 55), "세대생략 할증 비교", font=big, fill=c(NAVY))
d.text((60, 120), "가정: 산출세액 1억 원, 손자가 상속재산의 절반을 받음", font=body, fill=c(GRAY))
box(d, 200, 110, RED, "유언으로 손자에게", "가산액 1,500만 원", 30)
box(d, 340, 110, GREEN, "대습상속으로 손자가", "가산액 없음", 30)
d.text((90, 500), "상속세 및 증여세법 제27조", font=sub, fill=c(NAVY))
d.text((90, 555), "자녀를 제외한 직계비속이 받으면 30% 가산 (미성년자 20억 원 초과 40%)", font=small, fill=c(GRAY))
d.text((90, 600), "단서: 민법 제1001조에 따른 대습상속은 할증하지 않음", font=small, fill=c(GRAY))
d.text((90, 700), "가산액 = 산출세액 × 받은 재산 비율 × 30% (제가 조문 산식으로 계산)", font=small, fill=c(GRAY))
im.save(f'{OUT}/05_{P}_상속세할증.png')

# 06 핵심 정리
im, d = canvas(780)
d.text((60, 55), "핵심 정리", font=big, fill=c(NAVY))
for i, (k, v, col) in enumerate([("1", "먼저 사망·결격·상속권 상실 시 직계비속이 순위를 잇는다", NAVY), ("2", "먼저 사망한 사람의 몫 안에서 배우자 5할 가산해 나눈다", GREEN), ("3", "대습상속은 세대생략 할증 30%가 붙지 않는다", RED)]):
    box(d, 160 + i * 190, 150, col, k, None, 44); d.text((220, 160 + i * 190 + 75), v, font=load_font('bold', 28), fill=c(NAVY), anchor='lm')
im.save(f'{OUT}/06_{P}_핵심정리.png')
print('ok')
