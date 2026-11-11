from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
OUT = 'blog_images/2026-11-11_동거주택상속공제'
P = '동거주택상속공제'
BG = "#F7F5F0"; NAVY = "#1B2A4A"; GOLD = "#B8925A"; GRAY = "#6B7280"; RED = "#B5473A"; GREEN = "#2F7D5D"
W = 1200; c = hex_to_rgb
def canvas(h):
    im = Image.new('RGB', (W, h), c(BG)); return im, ImageDraw.Draw(im)
sub = load_font('bold', 32); body = load_font('regular', 28); small = load_font('regular', 24); big = load_font('extrabold', 40)
def box(d, y, h, col, left, right=None, lsize=36):
    d.rectangle([90, y, W - 90, y + h], fill=c("#FFFFFF"), outline=c(col), width=4)
    d.text((130, y + h // 2), left, font=load_font('extrabold', lsize), fill=c(col), anchor='lm')
    if right: d.text((W - 130, y + h // 2), right, font=body, fill=c(NAVY), anchor='rm')

im, d = canvas(900)
d.rectangle([0, 0, W, 14], fill=c(GOLD))
d.text((70, 200), "동거주택 상속공제", font=load_font('extrabold', 100), fill=c(NAVY))
d.text((70, 380), "10년 이상 동거하면", font=load_font('extrabold', 76), fill=c(NAVY))
d.text((70, 490), "최대 6억 원 공제", font=load_font('extrabold', 96), fill=c(GOLD))
d.text((70, 690), "상속세 및 증여세법 제23조의2 · 법제처 현행 조문 기준", font=sub, fill=c(GRAY))
im.save(f'{OUT}/01_{P}_대표이미지.png')

im, d = canvas(940)
d.text((60, 55), "공제액 계산", font=big, fill=c(NAVY))
d.text((60, 120), "상속주택가액의 100%, 한도 6억 원 (가정 예시)", font=body, fill=c(GRAY))
for y, col, t1, t2, r in [(200, NAVY, "주택 9억 · 채무 없음", "9억 원이지만 한도가 있어", "공제 6억 원"), (370, GREEN, "주택 5억 · 담보채무 1억", "4억 원 전액 공제", "공제 4억 원")]:
    d.rectangle([90, y, W - 90, y + 130], fill=c("#FFFFFF"), outline=c(col), width=4)
    d.text((130, y + 42), t1, font=load_font('extrabold', 30), fill=c(col), anchor='lm')
    d.text((130, y + 92), t2, font=body, fill=c(NAVY), anchor='lm')
    d.text((W - 130, y + 65), r, font=load_font('extrabold', 40), fill=c(col), anchor='rm')
d.text((90, 590), "상속주택가액 = 주택 + 부수토지 가액 - 담보된 피상속인 채무", font=sub, fill=c(NAVY))
d.text((90, 650), "조문 산식을 적용한 예시이고, 실제 신고는 사실관계에 따라 달라집니다", font=small, fill=c(GRAY))
im.save(f'{OUT}/02_{P}_공제액.png')

im, d = canvas(980)
d.text((60, 55), "요건 세 가지", font=big, fill=c(NAVY))
d.text((60, 120), "모두 갖춰야 합니다 · 법 제23조의2 제1항", font=body, fill=c(GRAY))
box(d, 200, 150, NAVY, "1", None, 44)
d.text((220, 250), "상속개시일부터 소급해 10년 이상", font=load_font('bold', 30), fill=c(NAVY), anchor='lm')
d.text((220, 305), "계속 하나의 주택에서 동거 (미성년 기간 제외)", font=body, fill=c(NAVY), anchor='lm')
box(d, 380, 150, GOLD, "2", None, 44)
d.text((220, 430), "10년 이상 계속 1세대 1주택", font=load_font('bold', 30), fill=c(NAVY), anchor='lm')
d.text((220, 485), "무주택 기간은 1세대 1주택 기간에 포함", font=body, fill=c(NAVY), anchor='lm')
box(d, 560, 150, GREEN, "3", None, 44)
d.text((220, 610), "상속개시일 현재 무주택 상속인", font=load_font('bold', 30), fill=c(NAVY), anchor='lm')
d.text((220, 665), "또는 피상속인과 공동 1세대 1주택 보유·동거 상속인", font=body, fill=c(NAVY), anchor='lm')
d.text((90, 800), "상속인은 직계비속과, 민법 제1003조 제2항에 따라", font=sub, fill=c(NAVY))
d.text((90, 850), "상속인이 된 그 직계비속의 배우자로 한정됩니다", font=sub, fill=c(NAVY))
im.save(f'{OUT}/03_{P}_요건.png')

im, d = canvas(940)
d.text((60, 55), "떨어져 산 기간은?", font=big, fill=c(NAVY))
d.text((60, 120), "시행령 제20조의2 제2항 · 시행규칙 제9조의2", font=body, fill=c(GRAY))
box(d, 190, 80, GREEN, "징집", None, 30)
box(d, 285, 80, GREEN, "초·중학교 제외 학교에의 취학", None, 28)
box(d, 380, 80, GREEN, "직장 변경·전근 등 근무상 형편", None, 28)
box(d, 475, 80, GREEN, "1년 이상 치료·요양이 필요한 질병", None, 28)
d.text((90, 640), "동거가 이어진 것으로 보지만", font=sub, fill=c(NAVY))
d.text((90, 695), "그 기간은 10년의 동거 기간에 넣지 않습니다", font=load_font('extrabold', 34), fill=c(RED))
d.text((90, 790), "동거 기간 계산의 세부는 이 글에서 다루지 않았습니다", font=small, fill=c(GRAY))
im.save(f'{OUT}/04_{P}_동거인정.png')

im, d = canvas(1060)
d.text((60, 55), "2주택이어도 1주택으로 보는 경우", font=big, fill=c(NAVY))
d.text((60, 120), "시행령 제20조의2 제1항 · 대부분 기한 안에 양도해야 합니다", font=body, fill=c(GRAY))
box(d, 190, 100, NAVY, "일시적 2주택", "새 주택 취득일부터 2년 이내 종전 주택 양도", 28)
box(d, 310, 100, GOLD, "상속인 혼인", "혼인일부터 5년 이내 배우자 주택 양도", 28)
box(d, 430, 100, GREEN, "동거봉양 합가", "60세 이상 직계존속, 합친 날부터 5년 이내", 28)
box(d, 550, 100, RED, "특정 주택", "국가등록문화유산·이농·귀농주택", 28)
d.text((90, 730), "그 밖에 피상속인의 혼인, 제3자 상속 공동소유 주택도 있습니다", font=sub, fill=c(NAVY))
d.text((90, 790), "해당 여부는 조문 전체를 보고 판단해야 합니다", font=small, fill=c(GRAY))
im.save(f'{OUT}/05_{P}_1주택예외.png')

im, d = canvas(780)
d.text((60, 55), "핵심 정리", font=big, fill=c(NAVY))
for i, (k, v, col) in enumerate([("1", "주택가액(담보채무 제외)의 100%, 6억 원 한도 공제", NAVY), ("2", "10년 동거 · 10년 1세대 1주택 · 무주택 상속인", GREEN), ("3", "떨어져 산 기간은 햇수 불산입, 공제 합계 한도도 있음", RED)]):
    box(d, 160 + i * 190, 150, col, k, None, 44); d.text((220, 160 + i * 190 + 75), v, font=load_font('bold', 28), fill=c(NAVY), anchor='lm')
im.save(f'{OUT}/06_{P}_핵심정리.png')
print('ok')
