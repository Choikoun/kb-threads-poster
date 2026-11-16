from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
OUT = 'blog_images/2026-11-16_퇴직금중간정산'
P = '퇴직금중간정산'
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
    d.text((70, 380), l2, font=load_font('extrabold', 70), fill=c(NAVY))
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
def calc(fn, t1):
    im, d = canvas(940)
    d.text((60, 55), t1, font=big, fill=c(NAVY))
    d.text((60, 120), "필자 가정: 평균임금 하루 10만 원 · 1년당 300만 원", font=body, fill=c(GRAY))
    box(d, 200, 110, NAVY, "5년째 중간정산", None, "1,500만 원")
    box(d, 330, 110, GOLD, "정산 시점부터 근속 새로 계산", None, "0년부터")
    box(d, 460, 110, GREEN, "이후 3년 근무 후 퇴직", None, "900만 원")
    d.text((90, 640), "임금이 오르면 금액은 달라집니다", font=sub, fill=c(RED))
    d.text((90, 695), "평균임금 산정 방법은 확인하지 못했습니다", font=small, fill=c(GRAY))
    d.text((90, 740), "근로자퇴직급여 보장법 제8조 제1항·제2항", font=small, fill=c(GRAY))
    im.save(f'{OUT}/{fn}')

cover(f'01_{P}_대표이미지.png', "퇴직금 중간정산", "시행령이 정한 사유만", "가능합니다", "근로자퇴직급여 보장법 제8조 · 시행령 제3조 기준")
cover(f't01_{P}_사업주.png', "퇴직금 중간정산", "직원이 요구하면", "사업주는 무엇을?", "근로자퇴직급여 보장법 제8조 · 시행령 제3조 기준")

im, d = canvas(1240)
d.text((60, 55), "중간정산 사유 (시행령 제3조)", font=big, fill=c(NAVY))
d.text((60, 120), "아홉 가지를 다섯 갈래로 묶었습니다", font=body, fill=c(GRAY))
box(d, 190, 120, NAVY, "주거", "무주택 주택 구입 · 전세금·보증금(1회)")
box(d, 330, 120, RED, "의료", "요양 6개월 이상 · 연간 임금총액 12.5% 초과")
box(d, 470, 120, GOLD, "채무", "5년 이내 파산선고·개인회생 결정")
box(d, 610, 120, GREEN, "근로조건", "임금피크제 · 근로시간 단축")
box(d, 750, 120, GRAY, "재난", "고용노동부장관 고시 사유")
d.text((90, 930), "사유 없이 요구한다고 정산되는 구조가 아닙니다", font=sub, fill=c(NAVY))
d.text((90, 985), "제8조 제2항: 대통령령으로 정하는 사유로 근로자가 요구하는 경우", font=small, fill=c(GRAY))
im.save(f'{OUT}/02_{P}_사유.png'); im.save(f'{OUT}/t02_{P}_사유표.png')

calc(f'03_{P}_계산.png', "정산 전후 계산 (필자 가정)")
calc(f't03_{P}_전후.png', "정산 후 퇴직금 계산 (필자 가정)")

im, d = canvas(860)
d.text((60, 55), "증빙 보존", font=big, fill=c(NAVY))
d.text((60, 120), "시행령 제3조 제2항", font=body, fill=c(GRAY))
box(d, 200, 150, GREEN, "사용자 의무", "사유에 따라 정산해 지급했다면 관련 증명 서류 보존", "5년")
box(d, 390, 150, GOLD, "보존 기한", "근로자가 퇴직한 후 5년이 되는 날까지", "퇴직 후")
d.text((90, 620), "퇴직금을 받을 권리는 3년간 행사하지 않으면 소멸", font=sub, fill=c(NAVY))
d.text((90, 675), "근로자퇴직급여 보장법 제10조", font=small, fill=c(GRAY))
im.save(f'{OUT}/04_{P}_증빙.png')

im, d = canvas(940)
d.text((60, 55), "퇴직 때 받는 방식", font=big, fill=c(NAVY))
d.text((60, 120), "근로자퇴직급여 보장법 제9조 · 시행령 제3조의2", font=body, fill=c(GRAY))
box(d, 200, 130, NAVY, "지급 기한", "지급 사유가 발생한 날부터 14일 이내", "14일")
box(d, 360, 130, GOLD, "지급 방법", "근로자가 지정한 개인형퇴직연금 계정으로 이전", "IRP")
box(d, 520, 130, GREEN, "예외", "55세 이후 퇴직 · 고시 금액 이하 · 사망 등")
d.text((90, 730), "퇴직금을 받을 권리는 3년 시효 (제10조)", font=sub, fill=c(RED))
im.save(f'{OUT}/05_{P}_수령방식.png')

core(f'06_{P}_핵심정리.png', [("1", "시행령 제3조 사유에 해당해야 정산할 수 있습니다", NAVY), ("2", "정산 뒤 계속근로기간은 정산 시점부터 새로 계산", GREEN), ("3", "사용자는 증빙을 퇴직 후 5년 되는 날까지 보존", RED)])
core(f't04_{P}_핵심.png', [("1", "사유와 근로자의 요구가 있을 때 사용자가 지급할 수 있음", NAVY), ("2", "정산 뒤 계속근로기간은 정산 시점부터 새로 계산", GREEN), ("3", "증빙은 근로자 퇴직 후 5년 되는 날까지 보존", RED)])
print('ok')
