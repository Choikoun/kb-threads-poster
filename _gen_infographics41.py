from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
import os
OUT = 'blog_images/2026-11-18_간병인보험'
P = '간병인보험'
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

cover(f'01_{P}_대표이미지.png', "간병인보험", "사용일당 청구", "증빙이 먼저", "금융감독원 보도자료 2025.4.9 기준")
cover(f't01_{P}_사례.png', "간병인보험", "청구 거절 사례", "6가지", "금융감독원 민원 사례 · 2025.4.9")

im, d = canvas(800)
d.text((60, 55), "특약 이름부터 구분", font=big, fill=c(NAVY))
d.text((60, 120), "금융감독원 소비자 유의사항", font=body, fill=c(GRAY))
box(d, 200, 160, NAVY, "간병인 사용 입원일당", "내가 간병인을 쓰고 비용을 낸 뒤 청구", "사용일당")
box(d, 400, 160, GREEN, "간병인 지원 입원일당", "보험사가 간병인을 지원하는 특약", "지원일당")
d.text((90, 640), "증권에 어느 쪽인지 먼저 확인하세요", font=sub, fill=c(NAVY))
im.save(f'{OUT}/02_{P}_특약구분.png')

im, d = canvas(1000)
d.text((60, 55), "청구 전 확인 네 가지", font=big, fill=c(NAVY))
d.text((60, 120), "금융감독원 2025.4.9 보도자료", font=body, fill=c(GRAY))
box(d, 190, 120, NAVY, "비용 지불 확인", "간병 서비스 이용 비용을 낸 사실", "1")
box(d, 330, 120, GOLD, "추가 증빙 요청", "실제 간병인 사용 여부 확인", "2")
box(d, 470, 120, GREEN, "간호·간병통합서비스", "사용일당 지급 제한 가능", "3")
box(d, 610, 120, RED, "치매 간병비", "약관의 치매상태 기준 충족", "4")
d.text((90, 800), "실제 지급 여부는 약관과 구체적 사실관계에 따라 달라집니다", font=small, fill=c(GRAY))
im.save(f'{OUT}/03_{P}_네가지.png')

im, d = canvas(900)
d.text((60, 55), "영수증 요건 (약관 예시)", font=big, fill=c(NAVY))
d.text((60, 120), "금융감독원이 소개한 약관 기준", font=body, fill=c(GRAY))
box(d, 190, 130, GREEN, "인정: 카드전표 · 국세청 통보 현금영수증", "간병 기간·금액·사업자등록번호 포함", "OK")
box(d, 350, 130, RED, "간이영수증", "단독으로는 부족, 계좌이체내역 등 추가", "추가")
d.text((90, 540), "추가 서류 예", font=sub, fill=c(NAVY))
d.text((90, 595), "간병인사용계약서 · 간병인사용확인서", font=body, fill=c(NAVY))
d.text((90, 645), "간병근무일지 · 계좌이체내역", font=body, fill=c(NAVY))
im.save(f'{OUT}/04_{P}_증빙.png')

im, d = canvas(920)
d.text((60, 55), "병동별 하루 본인부담", font=big, fill=c(NAVY))
d.text((60, 120), "종합병원 6인실 · 2023년 · 건강보험 웹진", font=body, fill=c(GRAY))
box(d, 200, 160, RED, "일반병동", "입원료 10,990원 + 사적 간병비 101,207원", "112,197원")
box(d, 400, 160, GREEN, "간호·간병통합병동", "입원료 본인부담 (보호자·간병인 상주 없음)", "22,340원")
d.text((90, 620), "필자 계산: 하루 차이 89,857원, 30일 약 270만 원", font=sub, fill=c(NAVY))
d.text((90, 675), "입원료와 간병비만 본 가정, 검사·치료비 제외", font=small, fill=c(GRAY))
d.text((90, 725), "이 병동에서는 사용일당이 지급되지 않을 수 있습니다", font=small, fill=c(RED))
im.save(f'{OUT}/05_{P}_통합서비스.png')

im, d = canvas(1000)
d.text((60, 55), "사례 6가지 요약", font=big, fill=c(NAVY))
d.text((60, 120), "금융감독원 민원 사례 · 보험사 이름은 비공개", font=body, fill=c(GRAY))
rows = [("A 골절 입원, 업체 간병", "비용 지급 내역 없음", NAVY), ("B 병원 등록 지인 간병", "실사용 불분명, 추가 서류", GOLD),
        ("C 영수증 승인번호 없음", "현금영수증 아님, 추가 서류", GREEN), ("D 간호·간병통합병동", "약관 제외 조항, 부지급", RED),
        ("E 치매 진단, 일상생활 가능", "상태 기준 불충족, 보류", NAVY), ("F 평가지표 점수 미달", "진단확정 조건 미달, 거절", GRAY)]
for i, (a, b, col) in enumerate(rows):
    y = 180 + i * 130
    d.rectangle([90, y, W - 90, y + 105], fill=c("#FFFFFF"), outline=c(col), width=4)
    d.text((130, y + 52), a, font=load_font('extrabold', 30), fill=c(col), anchor='lm')
    d.text((W - 130, y + 52), b, font=body, fill=c(NAVY), anchor='rm')
im.save(f'{OUT}/t02_{P}_사례요약.png')

core(f'06_{P}_핵심정리.png', [("1", "사용일당은 간병 비용을 낸 증빙이 있어야 지급", NAVY), ("2", "간호·간병통합병동은 약관 제외 조항 확인", RED), ("3", "특약 이름(사용·지원)은 증권으로 구분", GREEN)])
core(f't03_{P}_핵심.png', [("1", "비용 지급 증빙과 실사용 서류를 함께 보관", NAVY), ("2", "통합병동 입원은 제외 조항부터 확인", RED), ("3", "치매 간병비는 약관의 진단·상태 기준 확인", GREEN)])
print('ok')
