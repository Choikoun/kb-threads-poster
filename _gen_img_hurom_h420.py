import sys, os
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo

OUT = 'blog_images/shop_2026-11-09_휴롬H420'
K = '휴롬H420'
if not os.path.exists(f'{OUT}/01_{K}_대표이미지.jpg'):
    print(search_pexels_photo('slow juicer orange juice kitchen', output_path=f'{OUT}/01_{K}_대표이미지.jpg', orientation='landscape'))
BG = "#F7F5F0"; NAVY = "#1B2A4A"; GOLD = "#B8925A"; GRAY = "#6B7280"; RED = "#B5473A"; GREEN = "#2F7D5D"; W = 1200
c = hex_to_rgb


def canvas(h):
    im = Image.new('RGB', (W, h), c(BG))
    return im, ImageDraw.Draw(im)


def title(d, t, s):
    d.text((60, 55), t, font=load_font('extrabold', 40), fill=c(NAVY))
    d.text((60, 120), s, font=load_font('regular', 26), fill=c(GRAY))


# 02 공식몰 가격: 정가 대비 판매가
rows = [("H400", 499000, 419000, "16% 할인"), ("H410", 499000, 449000, "10% 할인"), ("H420", 499000, 499000, "할인 없음")]
im, d = canvas(900)
title(d, "휴롬 공식몰 정가와 판매가", "휴롬 공식몰 상품 페이지 · 2026-11-08 조회 · 배송비 0원")
y = 210
for n, lp, sp, tag in rows:
    d.text((60, y), n, font=load_font('extrabold', 34), fill=c(NAVY))
    d.text((W - 60, y + 6), tag, font=load_font('bold', 26), fill=c(GREEN if sp < lp else GRAY), anchor='ra')
    y += 56
    d.rectangle([60, y, 60 + 700, y + 34], fill=c("#E5E1D8"))
    d.text((60 + 710, y + 17), f"정가 {lp:,}원", font=load_font('bold', 22), fill=c(GRAY), anchor='lm')
    y += 44
    w = int(700 * sp / lp)
    d.rectangle([60, y, 60 + w, y + 40], fill=c(GOLD))
    d.text((60 + 710, y + 20), f"판매가 {sp:,}원", font=load_font('extrabold', 26), fill=c(NAVY), anchor='lm')
    y += 96
im.save(f'{OUT}/02_{K}_공식몰가격.png')

# 03 공식몰 사양
hdr = ["항목", "H400", "H410", "H420"]
x = [60, 400, 680, 940]
data = [("모델명", "H400", "H71FT", "H72FW"), ("크기(mm)", "169x261x471", "174x216x441", "174x216x441"), ("정격 전압", "150W", "150W", "150W"),
        ("출시년월", "2022.11", "2023.12", "2024.04"), ("제조국", "대한민국", "대한민국", "대한민국")]
im, d = canvas(900)
title(d, "공식몰 상품정보에 적힌 사양", "휴롬 공식몰 상품필수 정보 기준 · 2026-11-08 조회")
y = 200
for i, h in enumerate(hdr):
    d.text((x[i], y), h, font=load_font('extrabold', 26), fill=c(GOLD))
y += 56
for r in data:
    d.rectangle([40, y - 10, W - 40, y + 80], fill=c("#FFFFFF"))
    for i, t in enumerate(r):
        d.text((x[i], y + 35), t, font=load_font('bold', 24), fill=c(NAVY), anchor='lm')
    y += 118
im.save(f'{OUT}/03_{K}_공식몰사양.png')

# 04 쿠팡 목록
hdr = ["상품명(쿠팡 표기)", "쿠팡 목록", "로켓 표기"]
x = [60, 800, 1010]
data = [("휴롬 H420 원액기 주서기", "347,760원", "있음"), ("휴롬 H420 원액기 주서기 H72FW", "366,920원부터", "있음"), ("휴롬 착즙기 (H410)", "389,000원부터", "있음"),
        ("휴롬 착즙기 H400", "349,000원", "없음")]
im, d = canvas(900)
title(d, "휴롬 쿠팡 목록 가격", "쿠팡은 검색 목록 가격이에요 · 배송비와 옵션은 확인하지 못했어요")
y = 200
for i, h in enumerate(hdr):
    d.text((x[i], y), h, font=load_font('extrabold', 24), fill=c(GOLD))
y += 56
for r in data:
    d.rectangle([40, y - 10, W - 40, y + 90], fill=c("#FFFFFF"))
    for i, t in enumerate(r):
        d.text((x[i], y + 40), t, font=load_font('bold', 23), fill=c(NAVY), anchor='lm')
    y += 130
im.save(f'{OUT}/04_{K}_쿠팡목록.png')

# 05 구매 전 확인
im, d = canvas(800)
title(d, "구매 전 직접 확인할 것", "표기만으로는 알 수 없는 부분이에요")
pts = [("모델명 표기", "상품명에 H400 · H410 · H420 중 어느 모델인지 적혀 있는지"),
       ("판매 주체와 A/S", "공식몰은 A/S 책임자 휴롬 고객센터 1544-7011 표기 · 쿠팡 판매처는 직접 확인"),
       ("H410과 H420", "크기와 정격 전압이 같게 적혀 있어 표기만으로는 구분이 어려워요")]
y = 200
for h, t in pts:
    d.rectangle([40, y, W - 40, y + 150], fill=c("#FFFFFF"), outline=c(GOLD), width=3)
    d.text((80, y + 40), h, font=load_font('extrabold', 30), fill=c(NAVY), anchor='lm')
    d.text((80, y + 100), t, font=load_font('bold', 22), fill=c(GRAY), anchor='lm')
    y += 190
im.save(f'{OUT}/05_{K}_구매전확인.png')

# 06 체크리스트
im, d = canvas(1000)
title(d, "결제 전 확인할 다섯 가지", "모델명과 보증부터 보세요")
chk = ["판매가와 쿠폰 적용가 따로 확인", "상품명에 모델명이 있는지 보기", "판매 주체와 보증·A/S 조건 확인", "쿠팡은 옵션·배송비 직접 확인", "로켓 표기보다 모델명 먼저 보기"]
for i, t in enumerate(chk):
    col = i % 2
    rw = i // 2
    xx = 60 + col * 570
    yy = 200 + rw * 190
    d.rectangle([xx, yy, xx + 540, yy + 150], fill=c("#FFFFFF"), outline=c(GOLD), width=3)
    d.text((xx + 40, yy + 75), "□", font=load_font('extrabold', 44), fill=c(GREEN), anchor='lm')
    d.text((xx + 110, yy + 75), t, font=load_font('bold', 21), fill=c(NAVY), anchor='lm')
im.save(f'{OUT}/06_{K}_확인체크리스트.png')
print('ok')
