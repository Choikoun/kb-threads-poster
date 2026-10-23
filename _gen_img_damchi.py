import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/shop_2026-10-23_담치락밀폐용기'; K='담치락밀폐용기'
print(search_pexels_photo('glass food storage container stainless lid kitchen', output_path=f'{OUT}/01_{K}_대표이미지.jpg', orientation='landscape'))
print(search_pexels_photo('glass containers kitchen fridge vegetables fresh storage', output_path=f'{OUT}/06_{K}_클로징.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
body=load_font('regular',28)
def title(d,t,s):
    d.text((60,55),t,font=load_font('extrabold',40),fill=c(NAVY)); d.text((60,120),s,font=body,fill=c(GRAY))
def bars(d,rows,y0,mx,step=95,lw=300,x0=430,wmax=560,hi=45000):
    y=y0
    for k,v,col in rows:
        d.text((60,y+22),k,font=load_font('bold',26),fill=c(NAVY),anchor='lm')
        w=int(wmax*v/mx); d.rectangle([x0,y,x0+w,y+44],fill=c(col))
        d.text((x0+w+14,y+22),f"{v:,}원",font=load_font('extrabold',26),fill=c(NAVY),anchor='lm'); y+=step
# 02 호수별
rows=[("담치락 1호",28400,GREEN),("담치락 2호",33400,GREEN),("담치락 3호",38400,GREEN),("담치락 4호",43300,GOLD),("반영구 펌프(별도 옵션)",15400,GRAY)]
im,d=canvas(900)
title(d,"담치락 호수별 쿠팡 옵션가","2026-10-23 조회 · 배송비 포함 표기 · 판매자배송")
bars(d,rows,210,45000,110,x0=470,wmax=520)
im.save(f'{OUT}/02_{K}_호수별가격.png')
# 03 세트
rows=[("시그니처 세트",99800),("풀세트",134800),("프라임 세트",164800),("올인원 세트",196800),("맥스 세트",249800),("메가 세트",299800)]
im,d=canvas(1000)
title(d,"담치락 세트 옵션 쿠팡 표기가","2026-10-23 조회 · 무료배송 표기 · 세트별 구성은 확인하지 못했어요")
bars(d,[(k,v,GOLD if v<200000 else RED) for k,v in rows],210,300000,120,x0=360,wmax=560)
im.save(f'{OUT}/03_{K}_세트가격.png')
# 04 체크리스트
im,d=canvas(1000)
title(d,"결제 전 확인할 여섯 가지","같은 상품번호 아래 옵션이 11개예요")
chk=["호수와 세트 구성(몇 개, 어떤 용량)","펌프가 포함된 옵션인지","배송비 포함가인지 무료배송인지","소재와 뚜껑 재질 표기","전자레인지·식기세척기 사용 안내","교환·반품 조건과 고객센터 연락 방법"]
for i,t in enumerate(chk):
    col=i%2; rw=i//2; x=60+col*570; yy=200+rw*190
    d.rectangle([x,yy,x+540,yy+150],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((x+40,yy+75),"□",font=load_font('extrabold',44),fill=c(GREEN),anchor='lm')
    d.text((x+110,yy+75),t,font=load_font('bold',23),fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/04_{K}_확인체크리스트.png')
# 05 핵심 정리
im,d=canvas(900)
d.rectangle([0,0,W,14],fill=c(GOLD)); d.text((60,70),"핵심 정리",font=load_font('extrabold',52),fill=c(NAVY))
pts=["단품은 1호 28,400원부터 4호 43,300원, 세트는 99,800원부터 299,800원","같은 상품번호 아래 옵션 11개, 펌프는 15,400원 별도 옵션","세트 구성과 호수별 용량은 확인하지 못해서 상세 페이지 확인이 필요해요"]
y=200
for i,t in enumerate(pts,1):
    d.ellipse([60,y,130,y+70],fill=c(GOLD)); d.text((95,y+35),str(i),font=load_font('extrabold',40),fill=c("#FFFFFF"),anchor='mm')
    d.text((160,y+35),t,font=load_font('bold',24),fill=c(NAVY),anchor='lm'); y+=190
im.save(f'{OUT}/05_{K}_핵심정리.png')
