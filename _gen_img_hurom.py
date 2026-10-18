import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/shop_2026-10-19_휴롬H400'; K='휴롬H400'
print(search_pexels_photo('fresh vegetable juice glass kitchen', output_path=f'{OUT}/01_{K}_대표이미지.jpg', orientation='landscape'))
print(search_pexels_photo('fruits vegetables kitchen counter morning light', output_path=f'{OUT}/07_{K}_클로징.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
body=load_font('regular',28)
def title(d,t,s):
    d.text((60,55),t,font=load_font('extrabold',40),fill=c(NAVY)); d.text((60,120),s,font=body,fill=c(GRAY))
# 02 같은 H400 판매처별
im,d=canvas(900)
title(d,"휴롬 H400 판매처별 표기 가격","2026-10-19 조회 · 쿠팡 목록 · 네이버쇼핑(브랜드 커넥트)")
rows=[("쿠팡 브랜드샵 H400 (쿠폰 적용 표기)",324000,GREEN),("쿠팡 오픈마켓 H400 목록",349000,GREEN),("쿠팡 로켓 H400 (목록 기본 표기)",361620,GREEN),("네이버 H400 웜화이트",379000,GOLD)]
y=200; mx=400000
for k,v,col in rows:
    d.text((60,y+22),k,font=load_font('bold',24),fill=c(GRAY),anchor='lm')
    w=int((W-760)*v/mx); d.rectangle([560,y,560+w,y+46],fill=c(col))
    d.text((560+w+12,y+23),f"{v:,}원",font=load_font('extrabold',26),fill=c(NAVY),anchor='lm'); y+=120
d.text((60,y+10),"최저 324,000원과 최고 379,000원의 차이는 55,000원",font=load_font('extrabold',32),fill=c(RED))
im.save(f'{OUT}/02_{K}_판매처가격.png')
# 03 모델별
im,d=canvas(900)
title(d,"H400 · H410 · H430 표기 가격","쿠팡 휴롬 브랜드샵 정가·할인가, H430은 오픈마켓 목록 표기")
rows=[("H400","599,000원","324,000원"),("H410","699,000원","351,730원"),("H430","(정가 미표기)","349,000원")]
y=200
for k,a,b in rows:
    d.rectangle([60,y,W-60,y+150],fill=c("#FFFFFF"),outline=c(NAVY),width=3)
    d.text((100,y+75),k,font=load_font('extrabold',40),fill=c(NAVY),anchor='lm')
    d.text((700,y+75),a,font=load_font('regular',28),fill=c(GRAY),anchor='rm')
    d.text((740,y+75),"→",font=load_font('extrabold',30),fill=c(GOLD),anchor='mm')
    d.text((W-100,y+75),b,font=load_font('extrabold',34),fill=c(RED),anchor='rm'); y+=180
im.save(f'{OUT}/03_{K}_모델별가격.png')
# 04 정가 표기 차이
im,d=canvas(800)
title(d,"같은 H400, 정가 표기도 달라요","판매처마다 기준가가 다르면 할인율 숫자만으로 비교할 수 없어요")
rows=[("쿠팡 휴롬 브랜드샵","정가 599,000원","45% 할인"),("네이버 H400 웜화이트","정가 499,000원","24% 할인")]
y=220
for k,a,b in rows:
    d.rectangle([60,y,W-60,y+170],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((100,y+60),k,font=load_font('bold',32),fill=c(NAVY),anchor='lm')
    d.text((100,y+115),a,font=load_font('regular',28),fill=c(GRAY),anchor='lm')
    d.text((W-100,y+85),b,font=load_font('extrabold',44),fill=c(RED),anchor='rm'); y+=210
im.save(f'{OUT}/04_{K}_정가표기.png')
# 05 체크리스트
im,d=canvas(1000)
title(d,"결제 전 확인할 6가지","모델명·색상·쿠폰 적용 여부에 따라 결제가가 달라져요")
chk=["모델명 (H400 · H410 · H430)","색상 (웜화이트 · 티타늄그레이)","쿠폰 적용 전·후 가격","판매자 (브랜드샵 · 오픈마켓)","보증기간과 A/S 안내","구성품 (주스 컵·세척 솔 등)"]
for i,t in enumerate(chk):
    col=i%2; row=i//2; x=60+col*570; y=200+row*190
    d.rectangle([x,y,x+540,y+150],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((x+40,y+75),"□",font=load_font('extrabold',44),fill=c(GREEN),anchor='lm')
    d.text((x+110,y+75),t,font=load_font('bold',24),fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/05_{K}_확인체크리스트.png')
# 06 핵심 정리
im,d=canvas(900)
d.rectangle([0,0,W,14],fill=c(GOLD)); d.text((60,70),"핵심 정리",font=load_font('extrabold',52),fill=c(NAVY))
pts=["같은 H400이 324,000~379,000원으로 표기돼 55,000원 차이","정가 표기도 599,000원과 499,000원으로 달라요","모델명·색상·쿠폰 적용 여부를 맞춰야 비교가 돼요"]
y=200
for i,t in enumerate(pts,1):
    d.ellipse([60,y,130,y+70],fill=c(GOLD)); d.text((95,y+35),str(i),font=load_font('extrabold',40),fill=c("#FFFFFF"),anchor='mm')
    d.text((160,y+35),t,font=load_font('bold',26),fill=c(NAVY),anchor='lm'); y+=190
im.save(f'{OUT}/06_{K}_핵심정리.png')
