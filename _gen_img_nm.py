import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/shop_2026-10-29_나이몰리탄소매트'; K='나이몰리탄소매트'
print(search_pexels_photo('cozy bed warm blanket bedroom winter', output_path=f'{OUT}/01_{K}_대표이미지.jpg', orientation='landscape'))
print(search_pexels_photo('winter bedroom warm lamp blanket', output_path=f'{OUT}/08_{K}_클로징.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
def title(d,t,s):
    d.text((60,55),t,font=load_font('extrabold',40),fill=c(NAVY)); d.text((60,120),s,font=load_font('regular',28),fill=c(GRAY))
# 02 모델별 정가→할인가
rows=[("소노세레노 싱글·퀸",398000,199000),("돌체클래식 DCS01",378000,188000),("캠핑 전기요 1인용 싱글",378000,188000),("캠핑 전기요 2인용 퀸",478000,293000)]
im,d=canvas(1000)
title(d,"나이몰리 탄소매트 정가와 할인가","네이버 스마트스토어·쇼핑 커넥트 목록 · 2026-10-29 조회")
y=200
for n,a,b in rows:
    d.text((60,y),n,font=load_font('extrabold',30),fill=c(NAVY)); y+=48
    for k,v,col in (("정가",a,GRAY),("할인가",b,GOLD)):
        d.text((60,y+22),k,font=load_font('bold',24),fill=c(GRAY),anchor='lm')
        w=int(560*v/480000); d.rectangle([220,y,220+w,y+40],fill=c(col))
        d.text((220+w+14,y+20),f"{v:,}원",font=load_font('extrabold',26),fill=c(NAVY),anchor='lm'); y+=50
    y+=28
im.save(f'{OUT}/02_{K}_모델별가격.png')
# 03 옵션 가격
im,d=canvas(900)
title(d,"옵션에 따라 달라지는 금액","돌체클래식 스마트스토어 옵션 목록 · 2026-10-29")
rows=[("돌체도르미르 베이지 퀸","+110,000원 (품절 표시)"),("돌체도르미르 블랙 퀸(1세대 컨트롤러)","+105,000원"),("돌체도르미르 베이지 퀸(1세대 컨트롤러)","+105,000원"),("소노세레노 블루 싱글","추가금 표기 없음")]
y=200
for k,v in rows:
    d.rectangle([60,y,W-60,y+120],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((90,y+60),k,font=load_font('bold',26),fill=c(NAVY),anchor='lm')
    d.text((W-90,y+60),v,font=load_font('extrabold',28),fill=c(RED),anchor='rm'); y+=145
im.save(f'{OUT}/03_{K}_옵션가격.png')
# 04 공개 사양
im,d=canvas(950)
title(d,"판매 페이지에 적힌 사양","스마트스토어 상품정보 · 소비전력·크기는 확인하지 못했어요")
hdr=["항목","소노세레노","돌체클래식"]; data=[("온도 조절","5단계","4단계"),("모드","취침·저온·급속가열·숙면","취침·고온·저온"),("제조일자","2025.10.01","2025.09.01"),("원산지","이탈리아산(에어로코리아)","이탈리아산(에어로코리아)"),("용도","침대용","침대용")]
x=[60,330,760]; y=200
for i,h in enumerate(hdr): d.text((x[i],y),h,font=load_font('extrabold',28),fill=c(GOLD))
y+=60
for r in data:
    d.rectangle([40,y-12,W-40,y+78],fill=c("#FFFFFF"))
    for i,t in enumerate(r): d.text((x[i],y+33),t,font=load_font('bold',24),fill=c(NAVY),anchor='lm')
    y+=110
im.save(f'{OUT}/04_{K}_공개사양.png')
# 05 평점
rows=[("소노세레노 싱글·퀸",4.75,"802"),("돌체클래식 DCS01",4.83,"200"),("캠핑 전기요 싱글",4.79,"863"),("캠핑 전기요 퀸",4.91,"81")]
im,d=canvas(800)
title(d,"네이버 표기 평점(리뷰 수)","구매자 점수이며 리뷰 수가 적을수록 신뢰도가 낮아요 · 2026-10-29")
y=215
for k,r,n in rows:
    d.text((60,y+25),k,font=load_font('bold',27),fill=c(NAVY),anchor='lm')
    d.rectangle([420,y+5,420+int(300*r/5),y+45],fill=c(GOLD))
    d.text((740,y+25),f"{r}",font=load_font('extrabold',30),fill=c(NAVY),anchor='lm')
    d.text((W-60,y+25),f"리뷰 {n}건",font=load_font('bold',26),fill=c(GRAY),anchor='rm'); y+=125
im.save(f'{OUT}/05_{K}_평점리뷰.png')
# 06 체크리스트
im,d=canvas(1000)
title(d,"결제 전 확인할 여섯 가지","모델과 옵션에 따라 금액이 달라요")
chk=["모델명(소노세레노·돌체·캠핑)","사이즈와 옵션 추가금","쿠폰 적용가와 기한","소비전력·크기·세탁 안내","인증번호 직접 조회","평점과 리뷰 건수 함께 보기"]
for i,t in enumerate(chk):
    col=i%2; rw=i//2; xx=60+col*570; yy=200+rw*190
    d.rectangle([xx,yy,xx+540,yy+150],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((xx+40,yy+75),"□",font=load_font('extrabold',44),fill=c(GREEN),anchor='lm')
    d.text((xx+110,yy+75),t,font=load_font('bold',23),fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/06_{K}_확인체크리스트.png')
# 07 핵심정리
im,d=canvas(900)
d.rectangle([0,0,W,14],fill=c(GOLD)); d.text((60,70),"핵심 정리",font=load_font('extrabold',52),fill=c(NAVY))
pts=["소노세레노 199,000원(쿠폰가 189,000원), 돌체클래식 188,000원","돌체클래식 퀸 옵션은 +105,000~110,000원","소비전력·크기·세탁 안내는 상세 이미지로 직접 확인"]
y=200
for i,t in enumerate(pts,1):
    d.ellipse([60,y,130,y+70],fill=c(GOLD)); d.text((95,y+35),str(i),font=load_font('extrabold',40),fill=c("#FFFFFF"),anchor='mm')
    d.text((160,y+35),t,font=load_font('bold',24),fill=c(NAVY),anchor='lm'); y+=190
im.save(f'{OUT}/07_{K}_핵심정리.png')
