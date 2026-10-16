import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/shop_2026-10-16_엔드그레인도마'; K='엔드그레인도마'
print(search_pexels_photo('end grain wooden cutting board kitchen knife', output_path=f'{OUT}/01_{K}_대표이미지.jpg', orientation='landscape'))
print(search_pexels_photo('wooden cutting board vegetables kitchen warm', output_path=f'{OUT}/07_{K}_클로징.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
body=load_font('regular',28)
def title(d,t,s):
    d.text((60,55),t,font=load_font('extrabold',40),fill=c(NAVY)); d.text((60,120),s,font=body,fill=c(GRAY))
# 02 소재별 쿠팡 목록 가격대 (최저~최고 구간 막대)
im,d=canvas(1000)
title(d,"소재별 쿠팡 목록 표기 가격대","2026-10-16 조회 · '엔드그레인 도마' 검색 상위 목록 기준(크기 제각각)")
rows=[("아카시아",23400,71440),("레인트리",33750,120000),("월넛",19800,107150),("편백",64000,99750),("탄화 느티·애쉬·메이플",82100,135460)]
y=200; mx=140000; x0=380; wm=620
for k,lo,hi in rows:
    d.text((60,y+30),k,font=load_font('bold',28),fill=c(NAVY),anchor='lm')
    a=x0+int(wm*lo/mx); b=x0+int(wm*hi/mx)
    d.rectangle([x0,y+14,x0+wm,y+46],fill=c("#E8E2D6")); d.rectangle([a,y+8,b,y+52],fill=c(GOLD))
    d.text((a,y+78),f"{lo:,}원",font=load_font('bold',22),fill=c(GRAY),anchor='rm'); d.text((b,y+78),f"{hi:,}원",font=load_font('bold',22),fill=c(RED),anchor='lm')
    y+=150
im.save(f'{OUT}/02_{K}_소재별가격.png')
# 03 같은 이름·브랜드 가격 차이
im,d=canvas(1000)
title(d,"같은 이름 상품의 판매처별 가격","2026-10-16 · 네이버쇼핑(브랜드 커넥트) · 쿠팡 표기가")
groups=[("제우스 EN4030ST 아카시아 밧드 도마",[("네이버 칼백화점",72400,GOLD),("쿠팡 목록",71440,GREEN)]),
        ("BOUMBI 북미산 월넛 엔드그레인 도마",[("쿠팡 로켓 목록 A",86200,GREEN),("쿠팡 로켓 목록 B",107150,GREEN)]),
        ("에비히슈테른 레인트리 엔드그레인 도마",[("네이버 서피니아",108000,GOLD),("쿠팡 목록(재트파파)",109000,GREEN),("쿠팡 특대 48cm 목록",120000,GREEN)])]
y=190; mx=125000
for g,rs in groups:
    d.text((60,y),g,font=load_font('extrabold',30),fill=c(NAVY)); y+=52
    for k,v,col in rs:
        d.text((60,y+22),k,font=load_font('bold',23),fill=c(GRAY),anchor='lm')
        w=int((W-800)*v/mx); d.rectangle([380,y,380+w,y+44],fill=c(col))
        d.text((380+w+12,y+22),f"{v:,}원",font=load_font('extrabold',26),fill=c(NAVY),anchor='lm'); y+=60
    y+=26
im.save(f'{OUT}/03_{K}_같은이름가격.png')
# 04 네이버 목록 캄포 정가→할인가
im,d=canvas(900)
title(d,"네이버쇼핑 캄포·월넛 엔드그레인 도마","브랜드 커넥트 목록 표기 · 정가 → 할인가(2026-10-16)")
rows=[("아르네목공방 캄포 사각 중","97,900원","55,000원"),("콕스타 캄포나무","298,000원","129,000원"),("가이타이너 캄포","199,000원","129,000원"),("신현공예 북미산 월넛 사각 대형","300,000원","180,000원")]
y=190
for k,a,b in rows:
    d.rectangle([60,y,W-60,y+140],fill=c("#FFFFFF"),outline=c(NAVY),width=3)
    d.text((100,y+70),k,font=load_font('bold',28),fill=c(NAVY),anchor='lm')
    d.text((770,y+70),a,font=load_font('regular',26),fill=c(GRAY),anchor='rm')
    d.text((810,y+70),"→",font=load_font('extrabold',30),fill=c(GOLD),anchor='mm')
    d.text((W-100,y+70),b,font=load_font('extrabold',32),fill=c(RED),anchor='rm'); y+=165
im.save(f'{OUT}/04_{K}_캄포월넛가격.png')
# 05 관리·체크
im,d=canvas(1000)
title(d,"사기 전 확인 · 사고 나서 지킬 것","같은 이름이라도 크기·두께·소재가 다를 수 있어요")
chk=["수종 (아카시아·월넛·편백 등)","크기와 두께 (cm)","접합 방식 · 식기세척기 가능 여부","판매처 · 최종 결제가와 배송비","물에 담가 두지 않기","쓴 뒤 세워서 완전히 말리기"]
for i,t in enumerate(chk):
    col=i%2; row=i//2; x=60+col*570; y=200+row*190
    d.rectangle([x,y,x+540,y+150],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((x+40,y+75),"□",font=load_font('extrabold',44),fill=c(GREEN),anchor='lm')
    d.text((x+110,y+75),t,font=load_font('bold',24),fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/05_{K}_확인체크리스트.png')
# 06 핵심 정리
im,d=canvas(900)
d.rectangle([0,0,W,14],fill=c(GOLD)); d.text((60,70),"핵심 정리",font=load_font('extrabold',52),fill=c(NAVY))
pts=["쿠팡 목록 가격대: 아카시아 2만 원대부터, 탄화목은 13만 원대까지","같은 이름도 판매처·크기 옵션에 따라 가격이 달라요","접합부가 있어 식기세척기·물 담금은 피하는 게 권장돼요"]
y=200
for i,t in enumerate(pts,1):
    d.ellipse([60,y,130,y+70],fill=c(GOLD)); d.text((95,y+35),str(i),font=load_font('extrabold',40),fill=c("#FFFFFF"),anchor='mm')
    d.text((160,y+35),t,font=load_font('bold',26),fill=c(NAVY),anchor='lm'); y+=190
im.save(f'{OUT}/06_{K}_핵심정리.png')
