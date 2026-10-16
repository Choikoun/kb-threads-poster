import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/shop_2026-10-16_카이손톱깎이'; K='카이손톱깎이'
print(search_pexels_photo('nail clipper manicure hands close up', output_path=f'{OUT}/01_{K}_대표이미지.jpg', orientation='landscape'))
print(search_pexels_photo('bathroom shelf towels clean home', output_path=f'{OUT}/07_{K}_클로징.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
body=load_font('regular',28)
def title(d,t,s):
    d.text((60,55),t,font=load_font('extrabold',40),fill=c(NAVY)); d.text((60,120),s,font=body,fill=c(GRAY))
# 02 사이즈별 가격
im,d=canvas(1000)
title(d,"카이 손톱깎이 사이즈별 표기 가격","2026-10-16 · 네이버쇼핑(브랜드 커넥트) · 쿠팡 로켓배송 목록")
groups=[("소(S)",[("네이버 N펀키보이",4000,GOLD),("네이버 일상라이프",5100,GOLD),("쿠팡 로켓 '카이 손톱깎이 소'",5000,GREEN)]),
        ("중(M)",[("네이버 N펀키보이",4800,GOLD),("쿠팡 로켓 '카이 손톱깎이 중'",5800,GREEN)]),
        ("대(L)",[("네이버 119 일자 L",6500,GOLD),("쿠팡 로켓 투명케이스 세트 L",6900,GREEN)])]
y=190; mx=7500
for g,rs in groups:
    d.text((60,y),g,font=load_font('extrabold',32),fill=c(NAVY)); y+=52
    for k,v,col in rs:
        d.text((60,y+22),k,font=load_font('bold',22),fill=c(GRAY),anchor='lm')
        w=int((W-760)*v/mx); d.rectangle([420,y,420+w,y+44],fill=c(col))
        d.text((420+w+12,y+22),f"{v:,}원",font=load_font('extrabold',26),fill=c(NAVY),anchor='lm'); y+=58
    y+=24
im.save(f'{OUT}/02_{K}_사이즈별가격.png')
# 03 품번 정리
im,d=canvas(900)
title(d,"119 시리즈 품번 정리","일본 판매처(빅카메라·카인즈) 표기 기준 · 판매처마다 표기가 달라요")
rows=[("KF1000","001 S","곡선날"),("KF1001","001 M","곡선날"),("KF1002","001 L","직선날")]
y=200
for kf,nm,bl in rows:
    d.rectangle([60,y,W-60,y+150],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((100,y+75),kf,font=load_font('extrabold',40),fill=c(NAVY),anchor='lm')
    d.text((420,y+75),nm,font=load_font('bold',36),fill=c(GRAY),anchor='lm')
    d.text((W-100,y+75),bl,font=load_font('extrabold',36),fill=c(RED),anchor='rm'); y+=180
im.save(f'{OUT}/03_{K}_품번정리.png')
# 04 네이버 003 라인
im,d=canvas(900)
title(d,"네이버쇼핑 카이 003 라인","브랜드 커넥트 목록 표기가(2026-10-16)")
rows=[("카이 003 손톱깎이 S","7,600원"),("카이 003 손톱깎이 M","8,800원"),("카이 003 손톱깎이 L","9,800원"),("카이 119 일자 손톱깎이 L","6,500원")]
y=190
for k,b in rows:
    d.rectangle([60,y,W-60,y+140],fill=c("#FFFFFF"),outline=c(NAVY),width=3)
    d.text((100,y+70),k,font=load_font('bold',30),fill=c(NAVY),anchor='lm')
    d.text((W-100,y+70),b,font=load_font('extrabold',36),fill=c(RED),anchor='rm'); y+=165
im.save(f'{OUT}/04_{K}_003라인가격.png')
# 05 체크리스트
im,d=canvas(1000)
title(d,"결제 전 확인할 6가지","소·중·대 표기와 001·003·119 품번이 섞여 있어요")
chk=["품번 (001·003·119, KF 번호)","사이즈 (S · M · L)","날 모양 (곡선날 · 직선날)","손톱용인지 발톱용인지","판매처와 배송비","세트·케이스 포함 여부"]
for i,t in enumerate(chk):
    col=i%2; row=i//2; x=60+col*570; y=200+row*190
    d.rectangle([x,y,x+540,y+150],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((x+40,y+75),"□",font=load_font('extrabold',44),fill=c(GREEN),anchor='lm')
    d.text((x+110,y+75),t,font=load_font('bold',24),fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/05_{K}_확인체크리스트.png')
# 06 핵심 정리
im,d=canvas(900)
d.rectangle([0,0,W,14],fill=c(GOLD)); d.text((60,70),"핵심 정리",font=load_font('extrabold',52),fill=c(NAVY))
pts=["중(M)은 네이버 4,800원 · 쿠팡 로켓 5,800원으로 표기","같은 소·중·대여도 품번과 날 모양이 다를 수 있어요","결제 전 품번(KF 번호)과 사이즈를 맞춰 보세요"]
y=200
for i,t in enumerate(pts,1):
    d.ellipse([60,y,130,y+70],fill=c(GOLD)); d.text((95,y+35),str(i),font=load_font('extrabold',40),fill=c("#FFFFFF"),anchor='mm')
    d.text((160,y+35),t,font=load_font('bold',26),fill=c(NAVY),anchor='lm'); y+=190
im.save(f'{OUT}/06_{K}_핵심정리.png')
