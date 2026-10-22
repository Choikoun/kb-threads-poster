import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/shop_2026-10-22_리브비밀폐용기'; K='리브비밀폐용기'
print(search_pexels_photo('plastic food storage containers stacked kitchen shelf', output_path=f'{OUT}/01_{K}_대표이미지.jpg', orientation='landscape'))
print(search_pexels_photo('meal prep containers freezer organized', output_path=f'{OUT}/08_{K}_클로징.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
body=load_font('regular',28)
def title(d,t,s):
    d.text((60,55),t,font=load_font('extrabold',40),fill=c(NAVY)); d.text((60,120),s,font=body,fill=c(GRAY))
def row(d,y,cells,xs,bold=False,fill=NAVY,size=26):
    for t,x,al in zip(cells,xs,('lm','rm','rm','rm','rm')):
        d.text((x,y),t,font=load_font('extrabold' if bold else 'bold',size),fill=c(fill),anchor=al)
# 02 에코젠 용량·수량별 (네이버 표기)
rows=[("400ml",11800,43800,4.82,11,4.72,69),("650ml",13200,49900,4.63,24,4.75,67),("900ml",15600,57200,4.72,29,4.74,43),("2.4L",23800,86800,4.55,20,4.83,6)]
im,d=canvas(900)
title(d,"에코젠 반찬통 용량·수량별 표기가","네이버쇼핑(브랜드 커넥트 목록) 2026-10-22 조회 · 할인가 기준")
xs=[70,440,640,830,1130]
row(d,215,["용량","1개","4개","4개 개당","평점(4개)"],xs,True,GRAY,24)
y=270
for cap,p1,p4,r1,n1,r4,n4 in rows:
    d.rectangle([50,y-34,W-50,y+46],fill=c("#FFFFFF"),outline=c("#E3DED2"),width=2)
    row(d,y+6,[cap,f"{p1:,}원",f"{p4:,}원",f"{p4//4:,}원",f"{r4} ({n4})"],xs,False,NAVY,27); y+=120
d.text((60,y+20),"개당 가격은 4개 할인가를 4로 나눈 값이에요 · 괄호 안은 리뷰 수",font=load_font('regular',24),fill=c(GRAY))
im.save(f'{OUT}/02_{K}_용량수량별가격.png')
# 03 쿠팡·네이버 같은 금액
im,d=canvas(900)
title(d,"쿠팡 목록에서 같은 금액이 보인 에코젠","쿠팡 리브비 에코젠 상품번호 목록 표기가 · 네이버쇼핑 표기가와 금액이 일치 (2026-10-22)")
lst=[("400ml 4개 (네이버 표기)",43800),("650ml 4개 (네이버 표기)",49900),("900ml 4개 (네이버 표기)",57200),("3종 세트 (네이버 표기)",79800),("4종 세트 (네이버 표기)",119800)]
y=210
for k,v in lst:
    d.rectangle([60,y,W-60,y+110],fill=c("#FFFFFF"),outline=c(NAVY),width=3)
    d.text((100,y+55),k,font=load_font('bold',28),fill=c(NAVY),anchor='lm')
    d.text((W-100,y+55),f"쿠팡도 {v:,}원 표기",font=load_font('extrabold',30),fill=c(GREEN),anchor='rm'); y+=130
d.text((60,y+15),"금액이 같다는 뜻이고, 구성과 옵션이 같은지는 목록만으로 확인하지 못했어요",font=load_font('bold',24),fill=c(RED))
im.save(f'{OUT}/03_{K}_쿠팡네이버금액.png')
# 04 세트 가격
sets=[("에코젠 2종 (400·2, 900·1)",37800),("에코젠 2종 (650·2, 2.4L·1)",49800),("에코젠 3종 (400·650·900)",79800),("에코젠 4종 (400·650·4개씩 등)",119800),("엘라스토머 2종 (300·4, 600·2)",33500),("엘라스토머 4종 (300·600·6개 등)",84900)]
im,d=canvas(1000)
title(d,"세트 구성 네이버 표기가(할인가)","용량 옆 숫자는 개수 · 2026-10-22 조회")
y=210
for k,v in sets:
    d.text((60,y+28),k,font=load_font('bold',26),fill=c(NAVY),anchor='lm')
    w=int(380*v/120000); d.rectangle([590,y+6,590+w,y+50],fill=c(GOLD if '에코젠' in k else GREEN))
    d.text((590+w+12,y+28),f"{v:,}원",font=load_font('extrabold',26),fill=c(NAVY),anchor='lm'); y+=105
im.save(f'{OUT}/04_{K}_세트가격.png')
# 05 엘라스토머 냉동 전용
rows2=[("300ml",6800,21600),("600ml",8900,29700),("1500ml",13800,43800),("2.3L",17200,59800)]
im,d=canvas(800)
title(d,"엘라스토머 냉동 전용 용기 표기가","네이버쇼핑 할인가 · 2026-10-22 조회 · 리뷰는 0~4건으로 적어요")
xs=[70,500,760,1130]
row(d,215,["용량","1개","4개","4개 개당"],[70,500,760,1130],True,GRAY,24)
y=270
for cap,p1,p4 in rows2:
    d.rectangle([50,y-34,W-50,y+46],fill=c("#FFFFFF"),outline=c("#E3DED2"),width=2)
    for t,x,al in ((cap,70,'lm'),(f"{p1:,}원",500,'rm'),(f"{p4:,}원",760,'rm'),(f"{p4//4:,}원",1130,'rm')):
        d.text((x,y+6),t,font=load_font('bold',27),fill=c(NAVY),anchor=al)
    y+=110
im.save(f'{OUT}/05_{K}_엘라스토머가격.png')
# 06 체크리스트
im,d=canvas(1000)
title(d,"결제 전 확인할 여섯 가지","같은 상품번호라도 용량·수량 옵션이 달라요")
chk=["용량(ml·L)과 개수(1개·4개·세트)","에코젠인지 엘라스토머 냉동 전용인지","개당 가격으로 환산해 비교","평점과 함께 리뷰 수 보기","상세 페이지의 사용 가능 범위 안내","최종 결제가와 교환·반품 조건"]
for i,t in enumerate(chk):
    col=i%2; rw=i//2; x=60+col*570; yy=200+rw*190
    d.rectangle([x,yy,x+540,yy+150],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((x+40,yy+75),"□",font=load_font('extrabold',44),fill=c(GREEN),anchor='lm')
    d.text((x+110,yy+75),t,font=load_font('bold',23),fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/06_{K}_확인체크리스트.png')
# 07 핵심 정리
im,d=canvas(900)
d.rectangle([0,0,W,14],fill=c(GOLD)); d.text((60,70),"핵심 정리",font=load_font('extrabold',52),fill=c(NAVY))
pts=["에코젠 400ml는 1개 11,800원, 4개 43,800원(개당 10,950원)","쿠팡 목록 금액이 네이버 4개·세트 가격과 같게 표기됐어요","평점은 4.4~4.8대이고 리뷰는 용량마다 크게 달라요"]
y=200
for i,t in enumerate(pts,1):
    d.ellipse([60,y,130,y+70],fill=c(GOLD)); d.text((95,y+35),str(i),font=load_font('extrabold',40),fill=c("#FFFFFF"),anchor='mm')
    d.text((160,y+35),t,font=load_font('bold',25),fill=c(NAVY),anchor='lm'); y+=190
im.save(f'{OUT}/07_{K}_핵심정리.png')
