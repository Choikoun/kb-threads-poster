from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
import os
OUT = 'blog_images/2026-11-20_케어네이션가족간병'
P = '케어네이션가족간병'
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

cover(f'01_{P}_대표이미지.png', "케어네이션", "가족간병 이용증명서", "지급은 약관 먼저", "공식 페이지 · 금융감독원 2025.4.9 기준")
cover(f't01_가족간병_사례.png', "가족 간병", "보험금 청구", "수수료 사례", "KPI뉴스 2026.10.2 기준")

im, d = canvas(800)
d.text((60, 55), "이용증명서 발급 흐름", font=big, fill=c(NAVY))
d.text((60, 120), "케어네이션 공식 가족간병 페이지 안내", font=body, fill=c(GRAY))
box(d, 200, 120, NAVY, "1  앱에 정보 입력", "간병 기간 · 환자 정보 · 보험사 정보")
box(d, 350, 120, GOLD, "2  이용증명서 발급", "당일 발급 · PDF 또는 출력")
box(d, 500, 120, GREEN, "3  보험사에 청구", "지급 여부는 약관과 보험사 심사")
d.text((90, 690), "요금 · 수수료는 공식 페이지에서 확인되지 않음", font=small, fill=c(RED))
im.save(f'{OUT}/02_{P}_흐름.png')

im, d = canvas(900)
d.text((60, 55), "약관에서 볼 조건", font=big, fill=c(NAVY))
d.text((60, 120), "금융감독원 2025.4.9 보도자료", font=body, fill=c(GRAY))
box(d, 200, 130, NAVY, "간병인의 정의", "유상 제공 + 비용 지불 사실 확인", "1")
box(d, 360, 130, GOLD, "추가 증빙 요청", "실제 사용 여부가 불분명하면 서류 요구", "2")
box(d, 520, 130, RED, "간호·간병통합서비스", "사용일당 지급 제외 조항 가능", "3")
d.text((90, 720), "가족 간병 인정 여부는 보험사·약관마다 확인", font=sub, fill=c(NAVY))
im.save(f'{OUT}/03_{P}_약관확인.png')

im, d = canvas(1000)
d.text((60, 55), "청구 전 보험사에 물어볼 것", font=big, fill=c(NAVY))
box(d, 160, 130, NAVY, "내 특약", "사용일당인가, 지원일당인가", "1")
box(d, 320, 130, GOLD, "가족 간병", "지급 대상인지, 필요 서류는 무엇인지", "2")
box(d, 480, 130, GREEN, "업체 등록", "등록 필수인지, 지정 업체가 있는지", "3")
box(d, 640, 130, RED, "증빙 범위", "이용증명서만 되는지, 일지·비용 증빙 추가?", "4")
d.text((90, 840), "수수료는 이용 전에 부과 방식과 총액 확인", font=small, fill=c(GRAY))
im.save(f'{OUT}/04_{P}_체크.png')

im, d = canvas(900)
d.text((60, 55), "기사 사례 구조", font=big, fill=c(NAVY))
d.text((60, 120), "KPI뉴스 2026.10.2 · 업체는 케어온, 케어네이션 언급 없음", font=body, fill=c(GRAY))
box(d, 200, 130, NAVY, "간병인 사용일당 5만 원", "어머니를 직접 간병한 아들이 청구", "청구")
box(d, 360, 130, GOLD, "보험사가 업체 등록 요구", "가족 작성 서류는 신뢰성 부족이라는 설명", "요구")
box(d, 520, 130, RED, "업체 안내 하루 5,000원", "30일 15만 원은 기자 계산값", "수수료")
im.save(f'{OUT}/t02_가족간병_확인5가지.png')
core('t03_가족간병_핵심.png', [("1", "가족 간병 지급은 약관의 간병인 조건에 달림", NAVY), ("2", "업체 등록과 수수료는 총액까지 사전 확인", RED), ("3", "보험사에 필요한 서류를 먼저 문의", GREEN)])
core(f'06_{P}_핵심정리.png', [("1", "이용증명서는 지급 확정이 아님", NAVY), ("2", "약관의 간병인 정의와 추가 증빙 확인", RED), ("3", "가족 간병 인정 여부·수수료 총액 문의", GREEN)])
print('ok')
