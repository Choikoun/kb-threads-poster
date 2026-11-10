from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
OUT = 'blog_images/2026-11-10_과세전적부심사'
P = '과세전적부심사'
BG = "#F7F5F0"; NAVY = "#1B2A4A"; GOLD = "#B8925A"; GRAY = "#6B7280"; RED = "#B5473A"; GREEN = "#2F7D5D"
W = 1200; c = hex_to_rgb
def canvas(h):
    im = Image.new('RGB', (W, h), c(BG)); return im, ImageDraw.Draw(im)
sub = load_font('bold', 32); body = load_font('regular', 28); small = load_font('regular', 24); big = load_font('extrabold', 40)
def box(d, y, h, col, left, right=None, lsize=36):
    d.rectangle([90, y, W - 90, y + h], fill=c("#FFFFFF"), outline=c(col), width=4)
    d.text((130, y + h // 2), left, font=load_font('extrabold', lsize), fill=c(col), anchor='lm')
    if right: d.text((W - 130, y + h // 2), right, font=body, fill=c(NAVY), anchor='rm')
def arrow(d, y):
    d.polygon([(600, y), (570, y - 24), (630, y - 24)], fill=c(GRAY))

im, d = canvas(900)
d.rectangle([0, 0, W,14], fill=c(GOLD))
d.text((70, 200), "과세전적부심사", font=load_font('extrabold', 100), fill=c(NAVY))
d.text((70, 380), "통지받은 날부터", font=load_font('extrabold', 76), fill=c(NAVY))
d.text((70, 490), "30일 이내 청구", font=load_font('extrabold', 96), fill=c(GOLD))
d.text((70, 690), "국세기본법 제81조의15 · 법제처 현행 조문 기준", font=sub, fill=c(GRAY))
im.save(f'{OUT}/01_{P}_대표이미지.png')

im, d = canvas(1000)
d.text((60, 55), "통지부터 결과까지", font=big, fill=c(NAVY))
d.text((60, 120), "고지서가 나오기 전 단계입니다", font=body, fill=c(GRAY))
box(d, 190, 100, NAVY, "세무조사 종료", "조사를 마친 날부터 20일 이내 결과 통지", 28)
arrow(d, 325)
box(d, 335, 100, GOLD, "통지서 수령", "세무조사 결과통지 또는 과세예고통지", 28)
arrow(d, 470)
box(d, 480, 100, RED, "청구서 제출", "통지받은 날부터 30일 이내", 28)
arrow(d, 615)
box(d, 625, 100, GREEN, "결과 통지", "청구받은 날부터 30일 이내", 28)
d.text((90, 790), "청구한 부분은 결정이 날 때까지 결정·경정이 보류됩니다", font=sub, fill=c(NAVY))
d.text((90, 845), "세무조사 결과통지 기간은 일부 경우 40일입니다", font=small, fill=c(GRAY))
im.save(f'{OUT}/02_{P}_통지와기한.png')

im, d = canvas(940)
d.text((60, 55), "어디에 청구하나", font=big, fill=c(NAVY))
d.text((60, 120), "국세기본법 시행령 제63조의15 · 국세청 안내", font=body, fill=c(GRAY))
box(d, 200, 110, NAVY, "원칙", "통지한 세무서장·지방국세청장", 30)
box(d, 340, 150, GOLD, "국세청장", None, 30)
d.text((330, 395), "법령 해석 변경·새 해석, 업무감사 결과 통지,", font=body, fill=c(NAVY), anchor='lm')
d.text((330, 440), "청구금액 5억 원 이상 등", font=body, fill=c(NAVY), anchor='lm')
box(d, 520, 110, GREEN, "제출", "관할 세무서에 직접 또는 우편", 30)
d.text((90, 700), "청구서에 적을 것: 주소·성명, 통지 받은 날짜, 청구 세액, 내용과 이유", font=small, fill=c(NAVY))
d.text((90, 750), "증거서류가 있으면 함께 붙입니다", font=small, fill=c(GRAY))
im.save(f'{OUT}/03_{P}_청구처.png')

im, d = canvas(900)
d.text((60, 55), "심사 결과는 세 갈래", font=big, fill=c(NAVY))
d.text((60, 120), "국세심사위원회 심사를 거쳐 결정합니다", font=body, fill=c(GRAY))
box(d, 200, 110, GREEN, "채택 · 일부 채택", "추가 조사가 필요하면 재조사 결정", 30)
box(d, 340, 110, RED, "채택하지 않음", "청구가 이유 없다고 인정", 30)
box(d, 480, 110, GOLD, "심사하지 않음", "청구기간 경과 · 보정 미이행 등", 30)
d.text((90, 650), "국세청 안내: 보완요구는 접수 뒤 20일 이내", font=sub, fill=c(NAVY))
d.text((90, 705), "불채택 뒤 이어지는 불복 절차는 이 글에서 다루지 않았습니다", font=small, fill=c(GRAY))
im.save(f'{OUT}/04_{P}_결과.png')

im, d = canvas(1000)
d.text((60, 55), "청구할 수 없는 경우", font=big, fill=c(NAVY))
d.text((60, 120), "국세기본법 제81조의15 제3항", font=body, fill=c(GRAY))
box(d, 190, 90, RED, "납부기한 전 징수 · 수시부과 사유", None, 28)
box(d, 300, 90, RED, "고발 · 통고처분 (관련 없는 세목 제외)", None, 28)
box(d, 410, 90, RED, "제척기간 만료까지 3개월 이하", None, 28)
box(d, 520, 90, RED, "상호합의 요청 · 재조사 결정 조사", None, 28)
box(d, 680, 110, GREEN, "대안", "청구 대신 조기 결정·경정 신청", 30)
d.text((90, 840), "제8항: 신청받은 내용대로 즉시 결정·경정해야 합니다", font=small, fill=c(GRAY))
im.save(f'{OUT}/05_{P}_제외와조기결정.png')

im, d = canvas(780)
d.text((60, 55), "핵심 정리", font=big, fill=c(NAVY))
for i, (k, v, col) in enumerate([("1", "통지받은 날부터 30일 이내 통지한 세무서·지방청에 청구", NAVY), ("2", "청구하면 고지 보류, 청구받은 날부터 30일 이내 결과 통지", GREEN), ("3", "제외 사유가 있고 청구 대신 조기 결정 신청도 가능", RED)]):
    box(d, 160 + i * 190, 150, col, k, None, 44); d.text((220, 160 + i * 190 + 75), v, font=load_font('bold', 28), fill=c(NAVY), anchor='lm')
im.save(f'{OUT}/06_{P}_핵심정리.png')
print('ok')
