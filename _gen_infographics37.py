from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
OUT = 'blog_images/2026-11-14_달러종신보험'
P = '달러종신보험'
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
d.text((70, 200), "달러종신보험", font=load_font('extrabold', 100), fill=c(NAVY))
d.text((70, 380), "일시납 예시 32,778달러에", font=load_font('extrabold', 64), fill=c(NAVY))
d.text((70, 490), "가입금액 200,000달러", font=load_font('extrabold', 76), fill=c(GOLD))
d.text((70, 690), "상품요약서 2026.7.1 적용 · 40세 남성 예시", font=sub, fill=c(GRAY))
im.save(f'{OUT}/01_{P}_대표이미지.png')

im, d = canvas(980)
d.text((60, 55), "일시납 달러종신 구조", font=big, fill=c(NAVY))
d.text((60, 120), "가입금액 200,000달러 · 40세 남성 · 일시납 예시", font=body, fill=c(GRAY))
box(d, 200, 130, NAVY, "일반심사형 표준체", "가입금액 ÷ 보험료 약 6.1배(필자 계산)", "32,778달러")
box(d, 360, 130, GOLD, "간편심사형", "가입금액 ÷ 보험료 약 5.4배(필자 계산)", "37,314달러")
box(d, 520, 130, GREEN, "비흡연자 우량체 할인특약", "일반심사형에 부가 시", "31,206달러")
d.text((90, 720), "납입·지급·대출·인출이 모두 미국 달러입니다", font=sub, fill=c(NAVY))
d.text((90, 775), "원화환산납입·지급서비스 특약 가입이 필요합니다", font=small, fill=c(GRAY))
im.save(f'{OUT}/02_{P}_구조.png')

im, d = canvas(960)
d.text((60, 55), "사망보험금 기준", font=big, fill=c(NAVY))
d.text((60, 120), "세 금액 중 가장 큰 금액 + 보너스", font=body, fill=c(GRAY))
box(d, 200, 100, NAVY, "기본보험금 (20년 전 100%, 이후 30%)")
box(d, 320, 100, NAVY, "직전 월계약해당일 적립액의 103%")
box(d, 440, 100, NAVY, "이미 낸 보험료")
d.text((90, 590), "20년이 되는 날 유효하면 보너스 추가", font=sub, fill=c(GOLD))
box(d, 650, 100, GREEN, "사망보너스", None, "보험료의 80%", 30)
box(d, 770, 100, GREEN, "미국채 연동 사망보너스", None, "가입금액 70%까지", 30)
im.save(f'{OUT}/03_{P}_사망보험금.png')

im, d = canvas(980)
d.text((60, 55), "해약환급률 예시", font=big, fill=c(NAVY))
d.text((60, 120), "공시이율 연복리 5.18% 가정 · 달러 기준 · 세전", font=body, fill=c(GRAY))
rows = [("1년", "79.19%", RED), ("5년", "87.10%", RED), ("10년", "109.13%", GOLD), ("20년", "170.68%", GREEN)]
for i, (k, v, col) in enumerate(rows):
    box(d, 200 + i * 125, 105, col, k, None, v)
d.text((90, 730), "공시이율 1.5%p 상승 가정: 10년 94.80%", font=sub, fill=c(RED))
d.text((90, 785), "최저환급금 가정: 10년 89.99%, 15년 98.37%", font=sub, fill=c(RED))
d.text((90, 850), "미래 수익을 보장하는 숫자가 아닙니다", font=small, fill=c(GRAY))
im.save(f'{OUT}/04_{P}_환급률.png')

im, d = canvas(900)
d.text((60, 55), "가입 전 확인할 위험", font=big, fill=c(NAVY))
d.text((60, 120), "상품요약서 유의사항 기준", font=body, fill=c(GRAY))
box(d, 200, 110, RED, "환율", "달러 보험료와 원화 수령액이 환율에 따라 달라집니다")
box(d, 340, 110, RED, "중도해지", "10년 안에는 낸 보험료보다 적을 수 있습니다")
box(d, 480, 110, RED, "20년 이후", "기본보험금 30%, 보너스에 따라 크기가 달라집니다")
box(d, 620, 110, RED, "예시 숫자", "공시이율은 가입 시점마다 다릅니다")
im.save(f'{OUT}/05_{P}_유의점.png')

im, d = canvas(800)
d.text((60, 55), "핵심 정리", font=big, fill=c(NAVY))
for i, (k, v, col) in enumerate([("1", "예시: 32,778달러로 가입금액 200,000달러, 약 6.1배(필자 계산)", NAVY), ("2", "사망보험금은 세 금액 중 최대, 20년 뒤 기본보험금은 30%", GREEN), ("3", "환급률 1년 79%, 10년 109%, 10년 안 해지는 손실 가능", RED)]):
    d.rectangle([90, 160 + i * 190, W - 90, 160 + i * 190 + 150], fill=c("#FFFFFF"), outline=c(col), width=4)
    d.text((130, 160 + i * 190 + 75), k, font=load_font('extrabold', 44), fill=c(col), anchor='lm')
    d.text((220, 160 + i * 190 + 75), v, font=load_font('bold', 27), fill=c(NAVY), anchor='lm')
im.save(f'{OUT}/06_{P}_핵심정리.png')
print('ok')
