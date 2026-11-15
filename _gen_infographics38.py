from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
OUT = 'blog_images/2026-11-15_부담부증여'
P = '부담부증여'
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
d.text((70, 200), "부담부증여", font=load_font('extrabold', 110), fill=c(NAVY))
d.text((70, 390), "채무 부분은 양도세", font=load_font('extrabold', 72), fill=c(NAVY))
d.text((70, 500), "나머지는 증여세", font=load_font('extrabold', 88), fill=c(GOLD))
d.text((70, 700), "소득세법 제88조 · 상속세 및 증여세법 제47조 기준", font=sub, fill=c(GRAY))
im.save(f'{OUT}/01_{P}_대표이미지.png')

im, d = canvas(900)
d.text((60, 55), "세금이 두 갈래로 나뉩니다", font=big, fill=c(NAVY))
d.text((60, 120), "증여재산에 담보된 채무를 수증자가 인수할 때", font=body, fill=c(GRAY))
box(d, 200, 150, RED, "채무를 넘기는 부분", "양도로 봄 · 소득세법 제88조 제1호", "양도소득세")
box(d, 390, 150, GREEN, "채무를 뺀 나머지", "증여세 과세가액 · 상증세법 제47조 제1항", "증여세")
d.text((90, 620), "증여자가 임대한 재산의 임대보증금도 채무에 포함", font=sub, fill=c(NAVY))
d.text((90, 675), "상속세 및 증여세법 시행령 제36조 제1항", font=small, fill=c(GRAY))
im.save(f'{OUT}/02_{P}_구조.png')

im, d = canvas(1040)
d.text((60, 55), "계산 예시 (필자 가정)", font=big, fill=c(NAVY))
d.text((60, 120), "평가액 10억 · 취득가액 4억 · 채무 3억 인수", font=body, fill=c(GRAY))
box(d, 200, 110, NAVY, "증여세 과세가액", None, "7억 원")
box(d, 330, 110, RED, "양도가액 (10억 × 3/10)", None, "3억 원")
box(d, 460, 110, RED, "취득가액 (4억 × 3/10)", None, "1.2억 원")
box(d, 590, 110, GOLD, "양도차익", None, "1.8억 원")
d.text((90, 760), "시행령 제159조 제1항 계산식 · 필요경비·공제 제외", font=sub, fill=c(NAVY))
d.text((90, 815), "증여세는 직계존속 공제 5천만 원 가정 시 과세표준 6.5억 원", font=small, fill=c(GRAY))
d.text((90, 860), "실제 세액이 아니라 과세 대상이 갈리는 방식입니다", font=small, fill=c(GRAY))
im.save(f'{OUT}/03_{P}_계산.png')

im, d = canvas(940)
d.text((60, 55), "가족 사이 채무 증빙", font=big, fill=c(NAVY))
d.text((60, 120), "배우자·직계존비속 간은 인수 안 된 것으로 추정", font=body, fill=c(RED))
box(d, 200, 130, NAVY, "국가·지자체·금융회사 채무", "해당 기관 채무임을 확인할 수 있는 서류")
box(d, 360, 130, GOLD, "그 밖의 사람에 대한 채무", "채무부담계약서·채권자확인서")
box(d, 520, 130, GREEN, "담보설정과 이자지급 증빙", "사실을 확인할 수 있는 서류")
d.text((90, 720), "상증세법 제47조 제3항 · 시행령 제36조 제2항", font=sub, fill=c(NAVY))
d.text((90, 775), "추정이 깨지지 않으면 채무로 빼지 못합니다", font=small, fill=c(GRAY))
im.save(f'{OUT}/04_{P}_증빙.png')

im, d = canvas(860)
d.text((60, 55), "신고기한이 두 개입니다", font=big, fill=c(NAVY))
d.text((60, 120), "각각 말일부터 3개월", font=body, fill=c(GRAY))
box(d, 200, 150, RED, "양도소득세 예정신고", "양도일이 속하는 달의 말일부터 3개월", "3개월")
box(d, 390, 150, GREEN, "증여세 신고", "증여일이 속하는 달의 말일부터 3개월", "3개월")
d.text((90, 620), "양도차익이 없거나 손실이어도 신고해야 합니다", font=sub, fill=c(NAVY))
d.text((90, 675), "소득세법 제105조 제1항 제3호 · 제3항", font=small, fill=c(GRAY))
im.save(f'{OUT}/05_{P}_신고기한.png')

im, d = canvas(800)
d.text((60, 55), "핵심 정리", font=big, fill=c(NAVY))
for i, (k, v, col) in enumerate([("1", "채무를 넘긴 부분은 양도소득세, 나머지는 증여세", NAVY), ("2", "가족 사이는 채무 증빙이 없으면 인수 안 된 것으로 추정", RED), ("3", "양도소득세·증여세 신고기한 각각 말일부터 3개월", GREEN)]):
    d.rectangle([90, 160 + i * 190, W - 90, 160 + i * 190 + 150], fill=c("#FFFFFF"), outline=c(col), width=4)
    d.text((130, 160 + i * 190 + 75), k, font=load_font('extrabold', 44), fill=c(col), anchor='lm')
    d.text((220, 160 + i * 190 + 75), v, font=load_font('bold', 27), fill=c(NAVY), anchor='lm')
im.save(f'{OUT}/06_{P}_핵심정리.png')
print('ok')
