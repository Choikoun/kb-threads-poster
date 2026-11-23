from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
import os
OUT = 'blog_images/2026-11-23_소상공인정책자금'
P = '소상공인정책자금'
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

cover(f'01_{P}_대표이미지.png', "소상공인", "정책자금 한도·금리", "연 7천만 · +0.6%p", "소진공 2026 융자계획 · 2026.11.23 확인")
cover('t01_소상공인정책자금_제한.png', "정책자금", "신청 전 막히는", "융자제한 8가지", "2026 융자계획 공고 · 2026.11.23 확인")

im, d = canvas(900)
d.text((60, 55), "일반경영안정자금 (대리대출)", font=big, fill=c(NAVY))
d.text((60, 120), "소상공인 · 업력 무관 · 운전자금", font=body, fill=c(GRAY))
box(d, 190, 120, NAVY, "대출금리", "정책자금 기준금리 + 0.6%p 변동", "+0.6%p")
box(d, 340, 120, GOLD, "대출기간", "5년 이내 (거치 2년 포함)", "5년")
box(d, 490, 120, RED, "대출한도", "연간", "7천만")
box(d, 640, 120, GREEN, "융자방식", "금융기관 통한 대리대출", "대리")
im.save(f'{OUT}/02_{P}_일반경영.png')

im, d = canvas(1000)
d.text((60, 55), "우대금리 (최대 0.8%p)", font=big, fill=c(NAVY))
d.text((60, 120), "동일 유형 중복 불가 · 고정금리 상품 제외", font=small, fill=c(GRAY))
rows = [("정책 우대", "컨설팅·제로페이·온누리 가맹", "0.1%p"), ("정책 배려", "여성·장애인기업 등", "0.1%p"),
        ("사회안전망", "고용보험·노란우산·풍수해보험 등", "0.1%p"), ("성실상환", "직접대출 성실상환", "0.3%p"),
        ("지역 격차해소", "비수도권 소재", "0.2%p")]
for i, (a, b, r) in enumerate(rows):
    y = 190 + i * 150
    box(d, y, 120, GOLD, a, b, r)
im.save(f'{OUT}/03_{P}_우대금리.png')

im, d = canvas(900)
d.text((60, 55), "융자제한 대표 사유", font=big, fill=c(NAVY))
d.text((60, 120), "2026 소상공인 정책자금 융자계획 공통사항", font=body, fill=c(GRAY))
box(d, 190, 120, RED, "세금 체납", "유예 등은 직접대출에 한해 가능", "체납")
box(d, 330, 120, RED, "신용정보 등록", "신용도판단정보·공공정보 등", "등록")
box(d, 470, 120, GOLD, "휴·폐업 / 제외업종", "별표 1 업종 해당 시 제외", "제외")
box(d, 610, 120, NAVY, "5년 3회 이상 지원", "특별경영안정자금은 횟수 제외", "3회")
im.save(f'{OUT}/04_{P}_제한.png')

core(f'05_{P}_핵심정리.png', [("1", "공통 한도 운전 5억 · 시설 포함 10억", NAVY), ("2", "일반경영 연 7천만 · 기준금리+0.6%p · 5년", RED), ("3", "우대 최대 0.8%p · 체납·신용정보 등록은 제한", GREEN)])

im, d = canvas(1000)
d.text((60, 55), "신청 전 체크리스트", font=big, fill=c(NAVY))
d.text((60, 120), "공고 융자제한 8가지 중 앞 4가지", font=body, fill=c(GRAY))
for i, (a, b) in enumerate([("1", "세금 체납 없음"), ("2", "신용도판단정보 등 미등록"), ("3", "휴·폐업 아님 / 제외업종 아님"), ("4", "최근 5년 정책자금 3회 미만")]):
    y = 190 + i * 160
    box(d, y, 130, NAVY, f"{a}. {b}")
im.save(f'{OUT}/t02_{P}_체크.png')

core(f't03_{P}_핵심.png', [("1", "체납·신용정보 등록은 한도 이전 관문", RED), ("2", "5년 3회·휴폐업·제외업종도 제한", NAVY), ("3", "최신 공고·접수는 소진공에서 확인", GREEN)])
