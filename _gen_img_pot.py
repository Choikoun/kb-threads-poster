import sys,os
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/shop_2026-11-07_온도조절전기포트'; K='온도조절전기포트'
if not os.path.exists(f'{OUT}/01_{K}_대표이미지.jpg'): print(search_pexels_photo('electric kettle pouring hot water kitchen', output_path=f'{OUT}/01_{K}_대표이미지.jpg', orientation='landscape'))
if not os.path.exists(f'{OUT}/08_{K}_클로징.jpg'): print(search_pexels_photo('cup of tea steam winter morning window', output_path=f'{OUT}/08_{K}_클로징.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
def title(d,t,s):
    d.text((60,55),t,font=load_font('extrabold',40),fill=c(NAVY)); d.text((60,120),s,font=load_font('regular',26),fill=c(GRAY))
# 02 네이버 가격
rows=[("한경희 HEP-2010TW 1.7L",38000),("자일렉 1.7L",39900),("다룸 멜로우 1L",51700),("보아르 다이닝온 1.5L",53800),("모즈스웨덴 1.7L",59000),("테팔 테이스티 BJ551 1.5L",70900)]
im,d=canvas(1000)
title(d,"온도조절 전기포트 네이버 판매가","여섯 곳 모두 무료배송 표기 · 판매 페이지 직접 확인 · 2026-11-06 조회")
y=200
for n,v in rows:
    col=RED if n.startswith("모즈") else GOLD
    d.text((60,y),n,font=load_font('bold',26),fill=c(NAVY)); y+=42
    w=int(640*v/100000)
    d.rectangle([60,y,60+w,y+40],fill=c(col))
    d.text((60+w+14,y+20),f"{v:,}원",font=load_font('extrabold',28),fill=c(NAVY),anchor='lm'); y+=66
    y+=26
im.save(f'{OUT}/02_{K}_네이버가격.png')
# 03 쿠팡 목록 vs 네이버
hdr=["상품","쿠팡 목록","로켓 표기","네이버"]; x=[60,520,740,960]; y=200
data=[("모즈스웨덴 1L MC-1500","69,000원","없음","1.7L 59,000원"),("모즈스웨덴 1.9L","49,000원","있음","1.7L 59,000원"),("다룸 멜로우 1L","47,410원","있음","51,700원"),("보아르 다이닝온 1.5L","53,800원","있음","53,800원"),("테팔 BJ551BKR 1.5L","75,000원","없음","70,900원"),("자일렉 ZL-242DK","39,900원","없음","39,900원"),("한경희 무선 스마트 포트","32,900원","있음","38,000원")]
im,d=canvas(1250)
title(d,"쿠팡 목록 표기와 네이버 가격","쿠팡은 검색 목록 가격 · 다룸·자일렉·한경희는 같은 상품인지 확인하지 못했어요")
for i,h in enumerate(hdr): d.text((x[i],y),h,font=load_font('extrabold',24),fill=c(GOLD))
y+=56
for r in data:
    d.rectangle([40,y-10,W-40,y+90],fill=c("#FFFFFF"),outline=c(RED) if r[0].startswith("모즈") else None,width=4 if r[0].startswith("모즈") else 0)
    for i,t in enumerate(r): d.text((x[i],y+40),t,font=load_font('bold',22),fill=c(NAVY),anchor='lm')
    y+=125
im.save(f'{OUT}/03_{K}_쿠팡목록.png')
# 04 사양
hdr=["상품","용량","조작","제조일자"]; x=[60,470,640,900]; y=200
data=[("모즈스웨덴","1.7L","터치식","2025.02.01"),("다룸 멜로우","1L","표기 확인 못함","2024.07.15"),("보아르 다이닝온","1.5L","LED 디스플레이","2026.03.10"),("테팔 BJ551","1.5L","디스플레이 터치식","표기 없음"),("자일렉","1.7L","LED 디스플레이","표기 없음"),("한경희 HEP-2010TW","1.7L","버튼식","표기 없음")]
im,d=canvas(1100)
title(d,"판매 페이지에 적힌 사양","여섯 상품 모두 안전인증·안전확인 표기가 있었어요")
for i,h in enumerate(hdr): d.text((x[i],y),h,font=load_font('extrabold',26),fill=c(GOLD))
y+=56
for r in data:
    d.rectangle([40,y-10,W-40,y+80],fill=c("#FFFFFF"))
    for i,t in enumerate(r): d.text((x[i],y+35),t,font=load_font('bold',22),fill=c(NAVY),anchor='lm')
    y+=125
im.save(f'{OUT}/04_{K}_사양.png')
# 05 평점
rows=[("다룸 멜로우",4.8,"6,837"),("한경희 HEP-2010TW",4.68,"642"),("보아르 다이닝온",4.76,"517"),("자일렉",4.82,"483"),("테팔 BJ551",4.75,"332"),("모즈스웨덴",4.79,"82")]
im,d=canvas(1060)
title(d,"네이버 표기 평점(리뷰 수)","리뷰 수는 상품 페이지별 기준 · 2026-11-06")
y=200
for k,r,n in rows:
    d.text((60,y+25),k,font=load_font('bold',24),fill=c(NAVY),anchor='lm')
    d.rectangle([440,y+5,440+int(300*r/5),y+45],fill=c(GOLD))
    d.text((770,y+25),f"{r}",font=load_font('extrabold',30),fill=c(NAVY),anchor='lm')
    d.text((W-60,y+25),f"리뷰 {n}건",font=load_font('bold',26),fill=c(GRAY),anchor='rm'); y+=125
im.save(f'{OUT}/05_{K}_평점리뷰.png')
# 06 체크
im,d=canvas(1000)
title(d,"결제 전 확인할 여섯 가지","용량과 쿠폰 적용가부터 보세요")
chk=["용량 1L·1.5L·1.7L 확인","쿠팡·네이버 모델명 같은지 확인","쿠폰 적용가와 할인율 따로 보기","조작 방식과 분리형 여부 확인","인증번호와 제조일자 확인","평점은 리뷰 건수와 함께 보기"]
for i,t in enumerate(chk):
    col=i%2; rw=i//2; xx=60+col*570; yy=200+rw*190
    d.rectangle([xx,yy,xx+540,yy+150],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((xx+40,yy+75),"□",font=load_font('extrabold',44),fill=c(GREEN),anchor='lm')
    d.text((xx+110,yy+75),t,font=load_font('bold',21),fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/06_{K}_확인체크리스트.png')
# 07 핵심
im,d=canvas(900)
d.rectangle([0,0,W,14],fill=c(GOLD)); d.text((60,70),"핵심 정리",font=load_font('extrabold',52),fill=c(NAVY))
pts=["네이버 판매가는 한경희 38,000원부터 테팔 70,900원까지","같은 1.7L인 모즈스웨덴 59,000원과 한경희 38,000원은 21,000원 차이","쿠팡 목록의 모즈스웨덴은 1L 69,000원, 1.9L 49,000원"]
y=200
for i,t in enumerate(pts,1):
    d.ellipse([60,y,130,y+70],fill=c(GOLD)); d.text((95,y+35),str(i),font=load_font('extrabold',40),fill=c("#FFFFFF"),anchor='mm')
    d.text((160,y+35),t,font=load_font('bold',21),fill=c(NAVY),anchor='lm'); y+=190
im.save(f'{OUT}/07_{K}_핵심정리.png')
print('ok')
