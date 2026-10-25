import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/shop_2026-10-25_프리파라밀폐용기'; K='프리파라밀폐용기'
print(search_pexels_photo('clear plastic food containers stacked kitchen refrigerator', output_path=f'{OUT}/01_{K}_대표이미지.jpg', orientation='landscape'))
print(search_pexels_photo('meal prep containers frozen rice kitchen', output_path=f'{OUT}/07_{K}_클로징.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
def title(d,t,s):
    d.text((60,55),t,font=load_font('extrabold',40),fill=c(NAVY)); d.text((60,120),s,font=load_font('regular',28),fill=c(GRAY))
# 02 같은 이름 세트 네이버 공식몰 vs 쿠팡
groups=[("브루클린 베이지 17P 세트",211600,179000),("브루클린 11P 세트",149000,143700),("밥팩(냉동밥) 460ml 6P 블랙",64300,60270),("밥팩(냉동밥) 460ml 6P 베이지",64300,63700)]
im,d=canvas(1100)
title(d,"같은 이름 세트, 판매처별 표기가","네이버 프리파라 공식몰 vs 쿠팡 로켓배송 목록 · 2026-10-25 조회")
y=200
for g,a,b in groups:
    d.text((60,y),g,font=load_font('extrabold',30),fill=c(NAVY)); y+=50
    for k,v,col in (("네이버 공식몰",a,GOLD),("쿠팡 목록",b,GREEN)):
        d.text((60,y+22),k,font=load_font('bold',24),fill=c(GRAY),anchor='lm')
        w=int(560*v/215000); d.rectangle([260,y,260+w,y+44],fill=c(col))
        d.text((260+w+14,y+22),f"{v:,}원",font=load_font('extrabold',26),fill=c(NAVY),anchor='lm'); y+=56
    d.text((1140,y-30),f"차이 {a-b:,}원",font=load_font('extrabold',26),fill=c(RED),anchor='rm'); y+=36
im.save(f'{OUT}/02_{K}_세트판매처가격.png')
# 03 단품
im,d=canvas(800)
title(d,"브루클린 단품 표기가","네이버 공식몰(정가→할인가) · 쿠팡 로켓배송 · 호수와 색상이 달라 직접 비교는 어려워요")
rows=[("공식몰 4호 1.5L 베이지","41,800 → 20,900원 (50%)"),("공식몰 5호 2200ml 블랙","39,900 → 23,900원 (40%)"),("쿠팡 3호 1L 블랙","27,600원 · 30,600원 (옵션별)"),("쿠팡 4호 1.5L 블랙","33,850원")]
y=210
for k,v in rows:
    d.rectangle([60,y,W-60,y+110],fill=c("#FFFFFF"),outline=c(NAVY),width=3)
    d.text((100,y+55),k,font=load_font('bold',28),fill=c(NAVY),anchor='lm')
    d.text((W-100,y+55),v,font=load_font('extrabold',28),fill=c(RED),anchor='rm'); y+=135
im.save(f'{OUT}/03_{K}_단품가격.png')
# 04 평점
rows=[("5호 2200ml 블랙",4.88,"2,400"),("4호 1.5L 베이지",4.9,"367"),("냉동밥 6P 블랙",4.83,"332"),("11P 세트 블랙",4.91,"298"),("7P 세트",4.91,"123"),("17P 세트 베이지",4.88,"74")]
im,d=canvas(950)
title(d,"네이버쇼핑 공식몰 평점(리뷰 수)","표기된 숫자를 옮긴 것이며 구매자 점수예요 · 2026-10-25")
y=215
for k,r,n in rows:
    d.text((60,y+25),k,font=load_font('bold',27),fill=c(NAVY),anchor='lm')
    d.rectangle([420,y+5,420+int(300*r/5),y+45],fill=c(GOLD))
    d.text((740,y+25),f"{r}",font=load_font('extrabold',30),fill=c(NAVY),anchor='lm')
    d.text((W-60,y+25),f"리뷰 {n}개",font=load_font('bold',26),fill=c(GRAY),anchor='rm'); y+=115
im.save(f'{OUT}/04_{K}_평점리뷰.png')
# 05 체크리스트
im,d=canvas(1000)
title(d,"결제 전 확인할 여섯 가지","같은 이름이어도 색상·구성·판매처가 달라요")
chk=["세트 이름의 구성(P 개수·호수)","색상(블랙·베이지)이 같은지","공식몰인지 다른 판매자인지","정가보다 최종 결제가와 배송 방식","전자레인지·식기세척기·냉동 안내(모델별)","평점과 리뷰 수 함께 보기"]
for i,t in enumerate(chk):
    col=i%2; rw=i//2; x=60+col*570; yy=200+rw*190
    d.rectangle([x,yy,x+540,yy+150],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((x+40,yy+75),"□",font=load_font('extrabold',44),fill=c(GREEN),anchor='lm')
    d.text((x+110,yy+75),t,font=load_font('bold',23),fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/05_{K}_확인체크리스트.png')
# 06 핵심 정리
im,d=canvas(900)
d.rectangle([0,0,W,14],fill=c(GOLD)); d.text((60,70),"핵심 정리",font=load_font('extrabold',52),fill=c(NAVY))
pts=["베이지 17P 세트는 공식몰 211,600원, 쿠팡 179,000원으로 32,600원 차이","11P 세트와 밥팩은 차이가 600원~5,300원으로 작았어요","색상·구성이 같은지 확인한 뒤 최종 결제가를 비교하세요"]
y=200
for i,t in enumerate(pts,1):
    d.ellipse([60,y,130,y+70],fill=c(GOLD)); d.text((95,y+35),str(i),font=load_font('extrabold',40),fill=c("#FFFFFF"),anchor='mm')
    d.text((160,y+35),t,font=load_font('bold',24),fill=c(NAVY),anchor='lm'); y+=190
im.save(f'{OUT}/06_{K}_핵심정리.png')
