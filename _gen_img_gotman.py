import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/shop_2026-10-21_고트만밀폐용기'; K='고트만밀폐용기'
print(search_pexels_photo('food storage containers fridge organized meal prep', output_path=f'{OUT}/01_{K}_대표이미지.jpg', orientation='landscape'))
print(search_pexels_photo('kitchen counter glass food containers lunch', output_path=f'{OUT}/07_{K}_클로징.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
body=load_font('regular',28)
def title(d,t,s):
    d.text((60,55),t,font=load_font('extrabold',40),fill=c(NAVY)); d.text((60,120),s,font=body,fill=c(GRAY))
# 02 단품 목록 표기가
rows=[("직3호 블랙 (목록A)",11300),("정사각 3호",21660),("직5호 블랙 (목록A)",26600),("직5-2호 블랙",30400),("모5-1호 블랙",37200),("직5호 블랙 (목록B)",39060),("직3호 블랙 (목록B)",39600),("직3호 화이트",39600),("정3호 블랙",40500)]
im,d=canvas(1180)
title(d,"고트만 밀폐용기 단품 쿠팡 표기가","2026-10-21 조회 · '고트만 밀폐용기', '고트만 네오크리스탈' 검색 목록 기준")
y=200; mx=45000
for k,v in rows:
    d.text((60,y+22),k,font=load_font('bold',26),fill=c(NAVY),anchor='lm')
    w=int(560*v/mx); d.rectangle([420,y,420+w,y+44],fill=c(GOLD if v>=39000 else GREEN))
    d.text((420+w+14,y+22),f"{v:,}원",font=load_font('extrabold',26),fill=c(NAVY),anchor='lm'); y+=100
im.save(f'{OUT}/02_{K}_단품가격.png')
# 03 같은 이름 다른 가격
im,d=canvas(900)
title(d,"같은 이름인데 표기가가 갈렸어요","상품명이 같은 목록이 옵션에 따라 다르게 표기됨 · 2026-10-21")
groups=[("고트만 네오크리스탈 직3호 블랙",[("목록 A",11300,GREEN),("목록 B",39600,GOLD)]),("고트만 네오크리스탈 직5호 블랙",[("목록 A",26600,GREEN),("목록 B",39060,GOLD)])]
y=200
for g,rs in groups:
    d.text((60,y),g,font=load_font('extrabold',32),fill=c(NAVY)); y+=60
    for k,v,col in rs:
        d.text((60,y+24),k,font=load_font('bold',26),fill=c(GRAY),anchor='lm')
        w=int(560*v/45000); d.rectangle([220,y,220+w,y+48],fill=c(col))
        d.text((220+w+14,y+24),f"{v:,}원",font=load_font('extrabold',28),fill=c(NAVY),anchor='lm'); y+=76
    y+=70
d.text((60,y),"옵션·수량 차이로 보이지만 목록만으로는 확인하지 못했어요",font=load_font('bold',26),fill=c(RED))
im.save(f'{OUT}/03_{K}_같은이름가격.png')
# 04 세트 가격
im,d=canvas(800)
title(d,"세트 구성 쿠팡 표기가","2026-10-21 · 구성 용기와 용량은 목록에서 확인하지 못했어요")
sets=[("고트만 네오크리스탈 7종 세트 화이트",91200),("고트만 올트라이탄 네오 8종 세트 블랙",110440)]
y=220
for k,v in sets:
    d.rectangle([60,y,W-60,y+170],fill=c("#FFFFFF"),outline=c(NAVY),width=3)
    d.text((100,y+60),k,font=load_font('bold',30),fill=c(NAVY),anchor='lm')
    d.text((W-100,y+115),f"{v:,}원",font=load_font('extrabold',44),fill=c(RED),anchor='rm'); y+=210
im.save(f'{OUT}/04_{K}_세트가격.png')
# 05 체크리스트
im,d=canvas(1000)
title(d,"결제 전 확인할 여섯 가지","같은 호수 이름이어도 목록·옵션마다 달라요")
chk=["호수(직3·직5·정3 등)와 색상","용량(ml)과 크기(cm)","옵션·수량(낱개인지 세트인지)","소재와 내열 온도 표기","전자레인지·식기세척기 안내","최종 결제가와 교환·반품 조건"]
for i,t in enumerate(chk):
    col=i%2; row=i//2; x=60+col*570; yy=200+row*190
    d.rectangle([x,yy,x+540,yy+150],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((x+40,yy+75),"□",font=load_font('extrabold',44),fill=c(GREEN),anchor='lm')
    d.text((x+110,yy+75),t,font=load_font('bold',24),fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/05_{K}_확인체크리스트.png')
# 06 핵심 정리
im,d=canvas(900)
d.rectangle([0,0,W,14],fill=c(GOLD)); d.text((60,70),"핵심 정리",font=load_font('extrabold',52),fill=c(NAVY))
pts=["단품은 11,300원부터 40,500원, 세트는 91,200원·110,440원 표기","같은 이름 목록이 옵션에 따라 11,300원과 39,600원으로 갈렸어요","호수·용량·옵션부터 맞춘 뒤 최종 결제가를 비교하세요"]
y=200
for i,t in enumerate(pts,1):
    d.ellipse([60,y,130,y+70],fill=c(GOLD)); d.text((95,y+35),str(i),font=load_font('extrabold',40),fill=c("#FFFFFF"),anchor='mm')
    d.text((160,y+35),t,font=load_font('bold',25),fill=c(NAVY),anchor='lm'); y+=190
im.save(f'{OUT}/06_{K}_핵심정리.png')
