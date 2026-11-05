import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/shop_2026-11-05_이즈미보풀제거기'; K='이즈미보풀제거기'
import os
if not os.path.exists(f'{OUT}/01_{K}_대표이미지.jpg'): print(search_pexels_photo('knit sweater wool texture close up', output_path=f'{OUT}/01_{K}_대표이미지.jpg', orientation='landscape'))
if not os.path.exists(f'{OUT}/08_{K}_클로징.jpg'): print(search_pexels_photo('folded knit sweaters wardrobe shelf', output_path=f'{OUT}/08_{K}_클로징.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
def title(d,t,s):
    d.text((60,55),t,font=load_font('extrabold',40),fill=c(NAVY)); d.text((60,120),s,font=load_font('regular',26),fill=c(GRAY))
# 02 이즈미 상품별 가격
rows=[("네이버 IKL-610 (3중날 표기)",69000,GOLD),("네이버 IKL-610 (C타입 표기, 정가 89,000원)",79000,GOLD),
      ("쿠팡 다이아몬드 연마 대형날 상품",52060,GREEN),("쿠팡 세탁소용 니트 가디건 코트 상품",70400,GREEN),
      ("쿠팡 IKL-820",75850,GREEN),("쿠팡 IKL-830",79800,GREEN),("쿠팡 IKL-810",89000,GREEN)]
im,d=canvas(1180)
title(d,"이즈미 보풀제거기 가격","네이버는 판매 페이지 · 쿠팡은 검색 목록 표기 · 2026-11-05 조회")
y=200
for n,v,col in rows:
    d.text((60,y),n,font=load_font('bold',26),fill=c(NAVY)); y+=42
    w=int(640*v/90000)
    d.rectangle([60,y,60+w,y+40],fill=c(col))
    d.text((60+w+14,y+20),f"{v:,}원",font=load_font('extrabold',28),fill=c(NAVY),anchor='lm'); y+=66
    y+=28
im.save(f'{OUT}/02_{K}_이즈미가격.png')
# 03 브랜드별 네이버 vs 쿠팡
hdr=["모델","네이버 판매가","쿠팡 목록 표기"]; x=[60,470,830]; y=200
im,d=canvas(1120)
title(d,"네이버와 쿠팡 목록 표기가","쿠팡은 목록 가격이며 배송비와 옵션은 확인하지 못했어요 · 2026-11-05")
for i,h in enumerate(hdr): d.text((x[i],y),h,font=load_font('extrabold',26),fill=c(GOLD))
data=[("이즈미 (모델 혼재)","69,000원 · 79,000원","52,060~89,000원"),("필립스 GCA2100/20","28,000원","17,240원"),
      ("멜리언스 1세대","25,900원","25,900원"),("글리너 수동","35,800원","36,800원"),("아이프리 FX-714","25,000원","23,650원")]
y+=60
for r in data:
    d.rectangle([40,y-12,W-40,y+128],fill=c("#FFFFFF"),outline=c(RED) if r[0].startswith("필립스") else None,width=4 if r[0].startswith("필립스") else 0)
    for i,t in enumerate(r): d.text((x[i],y+58),t,font=load_font('bold',24),fill=c(NAVY),anchor='lm')
    y+=170 if False else 160
im.save(f'{OUT}/03_{K}_채널별가격.png')
# 04 사양
hdr=["상품","전원·형태","표기된 날·기능","인증·제조일"]; x=[60,330,600,900]; y=200
data=[("이즈미 IKL-610 A","핸디형 · 휴대용","특허 3중날 · 3단 높이","표기 없음"),("이즈미 IKL-610 B","C타입 충전","다이아몬드 연마 대형날","적합등록 · 2023.09"),
      ("필립스 GC026/00","건전지식","탈착 보풀함 · 먼지솔","표기 없음"),("필립스 GCA2100/20","USB 충전","표기 없음","표기 없음"),
      ("멜리언스 ML-MJD01","핸디형 (충전식 표기)","6중날 · LED","적합등록 · 2024.06"),("글리너 수동","수동식","칼날 3단 조절","표기 없음"),
      ("아이프리 FX-714","핸디형 · 전기식(쿠팡)","전용 칼날 별도 판매","안전인증 · 2021.01")]
im,d=canvas(1250)
title(d,"판매 페이지에 적힌 사양","같은 보풀제거기여도 전원 방식과 인증 표기가 달랐어요")
for i,h in enumerate(hdr): d.text((x[i],y),h,font=load_font('extrabold',26),fill=c(GOLD))
y+=60
for r in data:
    d.rectangle([40,y-12,W-40,y+80],fill=c("#FFFFFF"))
    for i,t in enumerate(r): d.text((x[i],y+34),t,font=load_font('bold',21),fill=c(NAVY),anchor='lm')
    y+=120 if False else 140
im.save(f'{OUT}/04_{K}_공개사양.png')
# 05 평점
rows=[("이즈미 IKL-610 A",0,"0"),("이즈미 IKL-610 B",0,"0"),("필립스 GC026/00",4.75,"4,787"),("필립스 GCA2100/20",4.81,"266"),
      ("멜리언스 1세대",4.75,"37,518"),("글리너 수동",4.63,"11,810"),("아이프리 FX-714",4.79,"3,602")]
im,d=canvas(1180)
title(d,"네이버 표기 평점(리뷰 수)","리뷰 수는 상품 페이지 전체 기준 · 2026-11-05")
y=200
for k,r,n in rows:
    d.text((60,y+25),k,font=load_font('bold',24),fill=c(NAVY),anchor='lm')
    d.rectangle([420,y+5,420+int(300*r/5),y+45],fill=c(GOLD))
    d.text((750,y+25),f"{r}" if r else "없음",font=load_font('extrabold',30),fill=c(NAVY),anchor='lm')
    d.text((W-60,y+25),f"리뷰 {n}건",font=load_font('bold',26),fill=c(GRAY),anchor='rm'); y+=125
im.save(f'{OUT}/05_{K}_평점리뷰.png')
# 06 체크리스트
im,d=canvas(1000)
title(d,"결제 전 확인할 여섯 가지","모델명과 전원 방식부터 맞춰 보세요")
chk=["모델명(IKL-610 등)이 같은지 확인","전원 방식(건전지·충전·수동) 확인","교체용 칼날을 따로 파는지 확인","인증번호와 제조일자 표기 확인","쿠팡은 배송비와 옵션을 직접 보기","평점은 리뷰 건수와 함께 보기"]
for i,t in enumerate(chk):
    col=i%2; rw=i//2; xx=60+col*570; yy=200+rw*190
    d.rectangle([xx,yy,xx+540,yy+150],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((xx+40,yy+75),"□",font=load_font('extrabold',44),fill=c(GREEN),anchor='lm')
    d.text((xx+110,yy+75),t,font=load_font('bold',22),fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/06_{K}_확인체크리스트.png')
# 07 핵심정리
im,d=canvas(900)
d.rectangle([0,0,W,14],fill=c(GOLD)); d.text((60,70),"핵심 정리",font=load_font('extrabold',52),fill=c(NAVY))
pts=["이즈미 IKL-610은 네이버 두 페이지에서 69,000원과 79,000원으로 표기됨","필립스 GCA2100/20은 네이버 28,000원, 쿠팡 목록 17,240원으로 10,760원 차이","이즈미 두 상품은 네이버 리뷰 0건, 비교한 다른 상품은 266건 이상"]
y=200
for i,t in enumerate(pts,1):
    d.ellipse([60,y,130,y+70],fill=c(GOLD)); d.text((95,y+35),str(i),font=load_font('extrabold',40),fill=c("#FFFFFF"),anchor='mm')
    d.text((160,y+35),t,font=load_font('bold',21),fill=c(NAVY),anchor='lm'); y+=190
im.save(f'{OUT}/07_{K}_핵심정리.png')
