from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
OUT = 'blog_images/2026-11-17_증여세면제한도'
P = '증여세면제한도'
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

cover(f'01_{P}_대표이미지.png', "증여세 면제한도", "직계존속 5천만 원", "혼인·출산 1억 별도", "상속세 및 증여세법 제53조·제53조의2 기준")
cover(f't01_{P}_사례.png', "증여세 면제한도", "사례 5가지로 계산", "과세표준까지", "상속세 및 증여세법 제53조·제53조의2 · 필자 가정")

im, d = canvas(880)
d.text((60, 55), "관계별 증여재산공제", font=big, fill=c(NAVY))
d.text((60, 120), "상속세 및 증여세법 제53조", font=body, fill=c(GRAY))
box(d, 190, 110, NAVY, "배우자", None, "6억 원")
box(d, 320, 110, GOLD, "직계존속 (미성년자는 2천만 원)", None, "5천만 원")
box(d, 450, 110, GREEN, "직계비속", None, "5천만 원")
box(d, 580, 110, RED, "4촌 이내 혈족 · 3촌 이내 인척", None, "1천만 원")
d.text((90, 740), "사위·며느리가 시부모에게 받으면 인척 1천만 원 (필자 해석)", font=small, fill=c(GRAY))
im.save(f'{OUT}/02_{P}_관계별.png')

im, d = canvas(880)
d.text((60, 55), "10년 합산 (필자 가정)", font=big, fill=c(NAVY))
d.text((60, 120), "성년 자녀가 부모에게 두 번 받는 경우", font=body, fill=c(GRAY))
box(d, 200, 120, NAVY, "첫 증여: 아버지 5천만 원", "5천만 원 공제 사용", "공제 5천만")
box(d, 350, 120, GOLD, "7년 뒤: 어머니 3천만 원", "10년 안 합산 8천만 원", "한도 소진")
d.text((90, 540), "공제 한도는 10년 안의 공제액과 합쳐 적용", font=sub, fill=c(NAVY))
d.text((90, 595), "제53조 후단 · 제47조 제2항", font=small, fill=c(GRAY))
d.text((90, 640), "두 번째 3천만 원은 공제할 한도가 남지 않습니다", font=small, fill=c(RED))
im.save(f'{OUT}/03_{P}_합산.png')

def calc(fn, t):
    im, d = canvas(1000)
    d.text((60, 55), t, font=big, fill=c(NAVY))
    d.text((60, 120), "필자 가정 · 다른 증여 합산 없음 · 과세표준까지", font=body, fill=c(GRAY))
    box(d, 190, 120, NAVY, "성년 자녀 3천만 원", "공제 5천만 원", "0원")
    box(d, 330, 120, GOLD, "미성년 자녀 3천만 원", "공제 2천만 원", "1천만 원")
    box(d, 470, 120, GREEN, "결혼 전후 2년 1.5억", "5천만 + 혼인 1억 = 1.5억 공제", "0원")
    box(d, 610, 120, RED, "혼인 1억 + 출산 후 1억", "공제 5천만 + 혼인·출산 한도 1억", "5천만 원")
    box(d, 750, 120, GRAY, "며느리가 시아버지 5천만 원", "인척 공제 1천만 원 (필자 해석)", "4천만 원")
    d.text((90, 930), "과세표준 50만 원 미만이면 증여세 없음 (제55조 제2항)", font=small, fill=c(GRAY))
    im.save(f'{OUT}/{fn}')
calc(f'04_{P}_계산.png', "과세표준 예시"); calc(f't02_{P}_계산.png', "사례별 과세표준")

im, d = canvas(860)
d.text((60, 55), "혼인 공제를 받은 뒤", font=big, fill=c(NAVY))
d.text((60, 120), "상속세 및 증여세법 제53조의2 제5항·제6항", font=body, fill=c(GRAY))
box(d, 200, 150, GREEN, "부득이한 사유로 3개월 안 반환", "처음부터 증여가 없었던 것으로 봄", "제5항")
box(d, 390, 150, RED, "2년 안에 혼인하지 않은 경우", "수정신고·기한 후 신고 시 가산세 감면, 이자상당액 가산", "제6항")
d.text((90, 620), "혼인을 전제로 먼저 받았다면 일정을 확인하세요", font=sub, fill=c(NAVY))
im.save(f'{OUT}/05_{P}_사후.png')

core(f'06_{P}_핵심정리.png', [("1", "공제 한도: 배우자 6억, 직계 5천만, 기타 친족 1천만", NAVY), ("2", "한도는 10년 안에 공제받은 금액과 합쳐 적용", RED), ("3", "혼인·출산 증여는 직계존속에게 받으면 별도 1억", GREEN)])
core(f't03_{P}_핵심.png', [("1", "직계존속 5천만 원, 미성년자는 2천만 원 공제", NAVY), ("2", "혼인·출산 공제는 합쳐서 1억 원 한도", GREEN), ("3", "공제 한도는 10년 안의 공제액과 합산", RED)])
print('ok')
