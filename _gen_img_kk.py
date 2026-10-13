import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/shop_2026-10-13_끌리젠가습기'; K='끌리젠가습기'
print(search_pexels_photo('humidifier steam bedroom night calm', output_path=f'{OUT}/01_{K}_대표이미지.jpg', orientation='landscape'))
print(search_pexels_photo('cozy living room winter evening', output_path=f'{OUT}/07_{K}_클로징.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
body=load_font('regular',28)
def title(d,t,s):
    d.text((60,55),t,font=load_font('extrabold',40),fill=c(NAVY)); d.text((60,120),s,font=body,fill=c(GRAY))
def bars(d,rows,y0,labw,mx,fs=28):
    y=y0
    for k,v,col in rows:
        d.text((60,y+28),k,font=load_font('bold',fs),fill=c(NAVY),anchor='lm')
        w=int((W-labw-320)*v/mx); d.rectangle([labw,y,labw+w,y+56],fill=c(col))
        d.text((labw+w+12,y+28),f"{v:,}원",font=load_font('extrabold',28),fill=c(NAVY),anchor='lm'); y+=115
# 02 가격 비교
im,d=canvas(640)
title(d,"끌리젠 가열식 가습기 6L 표기 가격","2026-10-13 조회 · 모델명 klz-hh01 기준 / 판매처별")
bars(d,[("네이버쇼핑 할인가",298000,GREEN),("쿠팡 로켓배송",298000,GREEN),("쿠팡 다른 판매 목록",527000,RED)],200,380,527000)
d.text((60,560),"네이버쇼핑 정가 표기는 400,000원 (25% 할인)",font=load_font('bold',28),fill=c(GRAY))
im.save(f'{OUT}/02_{K}_가격비교.png')
# 03 부품 가격
im,d=canvas(1060)
title(d,"별도 판매되는 부품·소모품 가격","쿠팡 목록 표기 · 2026-10-13 · 모델 호환은 상세 확인")
rows=[("26년형 리뉴얼 내솥 (316 스텐)","62,100원",NAVY),("리모컨","33,300원",GOLD),("내솥커버 테두리 패킹","12,000~13,800원",GREEN),("내솥커버 온도센서 패킹","12,600원",GREEN)]
y=190
for k,v,col in rows:
    d.rectangle([60,y,W-60,y+150],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((100,y+75),k,font=load_font('bold',32),fill=c(NAVY),anchor='lm')
    d.text((W-100,y+75),v,font=load_font('extrabold',38),fill=c(col),anchor='rm'); y+=175
im.save(f'{OUT}/03_{K}_부품가격.png')
# 04 소비자원 기준
im,d=canvas(1060)
title(d,"가열식 가습기 확인 기준","한국소비자원 시험·조사 · 끌리젠은 시험 대상 아님")
rows=[("가열식 연간 유지관리비","72,750 ~ 91,070원",RED),("끓는 동안 소음","52 ~ 55dB",GOLD),("증기 온도","약 99도",RED),("넘어뜨리면 누수 (21개 중)","21개 모두",NAVY),("화상 중 만 6세 이하","77.2%",GREEN)]
y=190
for k,v,col in rows:
    d.rectangle([60,y,W-60,y+140],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((100,y+70),k,font=load_font('bold',32),fill=c(NAVY),anchor='lm')
    d.text((W-100,y+70),v,font=load_font('extrabold',36),fill=c(col),anchor='rm'); y+=165
im.save(f'{OUT}/04_{K}_소비자원기준.png')
# 05 체크리스트
im,d=canvas(1000)
title(d,"결제 전 확인할 6가지","같은 이름이라도 모델·판매처가 다를 수 있어요")
chk=["모델명 klz-hh01 일치","판매처와 최종 결제가","용량 6L와 구성품","넘어질 때 누수 방지 구조","설치 높이 · 아이 손 닿는지","내솥·패킹 교체 부품 호환"]
for i,t in enumerate(chk):
    col=i%2; row=i//2; x=60+col*570; y=200+row*190
    d.rectangle([x,y,x+540,y+150],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((x+40,y+75),"□",font=load_font('extrabold',44),fill=c(GREEN),anchor='lm')
    d.text((x+110,y+75),t,font=load_font('bold',28),fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/05_{K}_확인체크리스트.png')
# 06 핵심정리
im,d=canvas(900)
d.rectangle([0,0,W,14],fill=c(GOLD)); d.text((60,70),"핵심 정리",font=load_font('extrabold',52),fill=c(NAVY))
pts=["6L 모델은 네이버·쿠팡 모두 298,000원 표기","쿠팡의 다른 판매 목록은 527,000원 · 같은 모델인지 확인","가열식은 전도 누수·소음·전기요금부터 확인"]
y=200
for i,t in enumerate(pts,1):
    d.ellipse([60,y,130,y+70],fill=c(GOLD)); d.text((95,y+35),str(i),font=load_font('extrabold',40),fill=c("#FFFFFF"),anchor='mm')
    d.text((160,y+35),t,font=load_font('bold',30),fill=c(NAVY),anchor='lm'); y+=190
im.save(f'{OUT}/06_{K}_핵심정리.png')
