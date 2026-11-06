import sys,os
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/shop_2026-11-06_타임모어C3'; K='타임모어C3'
if not os.path.exists(f'{OUT}/01_{K}_대표이미지.jpg'): print(search_pexels_photo('manual coffee grinder beans hand grinding', output_path=f'{OUT}/01_{K}_대표이미지.jpg', orientation='landscape'))
if not os.path.exists(f'{OUT}/08_{K}_클로징.jpg'): print(search_pexels_photo('pour over coffee brewing kitchen morning', output_path=f'{OUT}/08_{K}_클로징.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
def title(d,t,s):
    d.text((60,55),t,font=load_font('extrabold',40),fill=c(NAVY)); d.text((60,120),s,font=load_font('regular',26),fill=c(GRAY))
# 02 C3S PRO 판매처별
rows=[("네이버 셀렉트온",85000,GOLD),("네이버 미래스토",85000,GOLD),("네이버 N펀키보이",89000,GOLD),("네이버 모던피크 (국내정식)",92500,GOLD),("쿠팡 목록 표기",97400,GREEN),("쿠팡 목록 표기",191800,GREEN)]
im,d=canvas(1100)
title(d,"타임모어 C3S PRO 판매처별 가격","네이버는 판매 페이지 · 쿠팡은 검색 목록 표기 · 2026-11-06 조회")
y=200
for n,v,col in rows:
    d.text((60,y),n,font=load_font('bold',26),fill=c(NAVY)); y+=42
    w=int(640*v/200000)
    d.rectangle([60,y,60+w,y+40],fill=c(col))
    d.text((60+w+14,y+20),f"{v:,}원",font=load_font('extrabold',28),fill=c(NAVY),anchor='lm'); y+=66
    y+=26
im.save(f'{OUT}/02_{K}_PRO판매처가격.png')
# 03 모델별
hdr=["모델","판매 페이지","가격","배송"]; x=[60,330,700,900]; y=200
data=[("C3S","N펀키보이","77,000원","3,000원"),("C3S PRO","셀렉트온","85,000원","무료"),("C3S MAX PRO","모던피크 국내정식","109,500원","무료"),("C3S 블랙","크로바직구 (구매대행)","102,600원","무료·해외직배송")]
im,d=canvas(900)
title(d,"모델별 네이버 판매가","같은 C3S 계열도 판매처와 배송 조건이 달라요 · 2026-11-06")
for i,h in enumerate(hdr): d.text((x[i],y),h,font=load_font('extrabold',26),fill=c(GOLD))
y+=60
for r in data:
    d.rectangle([40,y-12,W-40,y+110],fill=c("#FFFFFF"),outline=c(RED) if r[0]=="C3S 블랙" else None,width=4 if r[0]=="C3S 블랙" else 0)
    for i,t in enumerate(r): d.text((x[i],y+48),t,font=load_font('bold',23),fill=c(NAVY),anchor='lm')
    y+=140
im.save(f'{OUT}/03_{K}_모델별가격.png')
# 04 사양 C3 vs C3S Pro
hdr=["항목","C3","C3S Pro"]; x=[60,330,760]; y=200
data=[("버","S2C 스테인리스 38mm","S2C 660 스테인리스 38mm"),("분쇄도 조절","약 36단계","약 36단계"),("바디","알루미늄 (내부 일부 플라스틱)","풀 메탈 알루미늄 합금"),("핸들","고정형","접이식 스프링 보조 핸들"),("용량","약 20~25g","약 25~30g"),("축","듀얼 베어링","듀얼 베어링")]
im,d=canvas(1000)
title(d,"판매 페이지 사양표","셀렉트온 판매자가 적은 표 기준이에요")
for i,h in enumerate(hdr): d.text((x[i],y),h,font=load_font('extrabold',26),fill=c(GOLD))
y+=60
for r in data:
    d.rectangle([40,y-12,W-40,y+80],fill=c("#FFFFFF"))
    for i,t in enumerate(r): d.text((x[i],y+34),t,font=load_font('bold',21),fill=c(NAVY),anchor='lm')
    y+=120
im.save(f'{OUT}/04_{K}_사양비교.png')
# 05 평점
rows=[("모던피크 C3S PRO",4.93,"29"),("모던피크 C3S MAX PRO",4.81,"16"),("셀렉트온 C3S PRO",5.0,"4"),("미래스토 C3S PRO",5.0,"1"),("N펀키보이 C3S PRO",0,"0"),("N펀키보이 C3S",0,"0"),("크로바직구 C3S 블랙",0,"0")]
im,d=canvas(1180)
title(d,"네이버 표기 평점(리뷰 수)","리뷰 수는 상품 페이지별 기준 · 2026-11-06")
y=200
for k,r,n in rows:
    d.text((60,y+25),k,font=load_font('bold',24),fill=c(NAVY),anchor='lm')
    d.rectangle([440,y+5,440+int(300*r/5),y+45],fill=c(GOLD))
    d.text((770,y+25),f"{r}" if r else "없음",font=load_font('extrabold',30),fill=c(NAVY),anchor='lm')
    d.text((W-60,y+25),f"리뷰 {n}건",font=load_font('bold',26),fill=c(GRAY),anchor='rm'); y+=125
im.save(f'{OUT}/05_{K}_평점리뷰.png')
# 06 체크
im,d=canvas(1000)
title(d,"결제 전 확인할 여섯 가지","모델명 뒤 글자와 판매 조건부터 보세요")
chk=["C3, C3S, C3S PRO 등 모델명 확인","국내정식 표기와 판매자 확인","배송비를 더한 총액 비교","구매대행·해외직배송 여부 확인","쿠팡은 옵션·배송비 직접 확인","평점은 리뷰 건수와 함께 보기"]
for i,t in enumerate(chk):
    col=i%2; rw=i//2; xx=60+col*570; yy=200+rw*190
    d.rectangle([xx,yy,xx+540,yy+150],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((xx+40,yy+75),"□",font=load_font('extrabold',44),fill=c(GREEN),anchor='lm')
    d.text((xx+110,yy+75),t,font=load_font('bold',21),fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/06_{K}_확인체크리스트.png')
# 07 핵심
im,d=canvas(900)
d.rectangle([0,0,W,14],fill=c(GOLD)); d.text((60,70),"핵심 정리",font=load_font('extrabold',52),fill=c(NAVY))
pts=["C3S PRO는 네이버 4곳에서 85,000원부터 92,500원까지 7,500원 차이","쿠팡 목록 C3S PRO는 97,400원과 191,800원 두 가지로 표기","C3S는 77,000원이지만 배송비 3,000원이 붙어 합계 80,000원"]
y=200
for i,t in enumerate(pts,1):
    d.ellipse([60,y,130,y+70],fill=c(GOLD)); d.text((95,y+35),str(i),font=load_font('extrabold',40),fill=c("#FFFFFF"),anchor='mm')
    d.text((160,y+35),t,font=load_font('bold',21),fill=c(NAVY),anchor='lm'); y+=190
im.save(f'{OUT}/07_{K}_핵심정리.png')
