import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/shop_2026-11-04_데팔후라이팬'; K='데팔후라이팬'
print(search_pexels_photo('non stick frying pan kitchen cooking', output_path=f'{OUT}/01_{K}_대표이미지.jpg', orientation='landscape'))
print(search_pexels_photo('cooking pan stove home kitchen', output_path=f'{OUT}/09_{K}_클로징.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
def title(d,t,s):
    d.text((60,55),t,font=load_font('extrabold',40),fill=c(NAVY)); d.text((60,120),s,font=load_font('regular',28),fill=c(GRAY))
# 02 28cm 라인별 가격(배송비 모두 무료)
rows=[("쿡이지 1X",29880,36900),("심플리쉐프 1X",37190,53900),("라이트쿡 1X",39370,52500),("퍼펙트 레지스트 3X",46170,67900),("데일리 엑스퍼트 2X",49200,65800),("퍼펙트 터치 3X",56720,79900)]
im,d=canvas(1000)
title(d,"테팔 프라이팬 28cm 라인별 가격","모두 무료배송 표기 · 네이버 스마트스토어 2026-11-04 조회")
y=200
for n,v,lp in rows:
    d.text((60,y),n,font=load_font('extrabold',28),fill=c(NAVY)); y+=44
    w=int(620*v/60000)
    d.rectangle([60,y,60+w,y+40],fill=c(GOLD))
    d.text((60+w+14,y+20),f"{v:,}원 (정가 표기 {lp:,}원)",font=load_font('extrabold',24),fill=c(NAVY),anchor='lm'); y+=70
    y+=24
im.save(f'{OUT}/02_{K}_28cm라인별가격.png')
# 03 크기별 가격(같은 페이지 옵션)
hdr=["라인","20cm(22cm)","24cm","28cm"]; x=[60,480,720,940]
data=[("쿡이지 1X","24,210원","26,640원","29,880원"),("심플리쉐프 1X","32,340원","34,250원","37,190원"),("라이트쿡 1X","35,920원 (22cm)","37,350원","39,370원"),("퍼펙트 레지스트 3X","41,260원","39,370원","46,170원"),("데일리 엑스퍼트 2X","37,500원","41,800원","49,200원"),("퍼펙트 터치 3X","51,920원","48,910원","56,720원")]
im,d=canvas(1100)
title(d,"같은 라인의 크기별 가격","20cm가 24cm보다 비싼 라인이 있어요 · 2026-11-04")
y=200
for i,h in enumerate(hdr): d.text((x[i],y),h,font=load_font('extrabold',26),fill=c(GOLD))
y+=60
for r in data:
    flip = r[0] in ("퍼펙트 레지스트 3X","퍼펙트 터치 3X")
    d.rectangle([40,y-12,W-40,y+90],fill=c("#FFFFFF"),outline=c(RED) if flip else None,width=4 if flip else 0)
    for i,t in enumerate(r): d.text((x[i],y+40),t,font=load_font('bold',24),fill=c(RED) if (flip and i in (1,2)) else c(NAVY),anchor='lm')
    y+=125
im.save(f'{OUT}/03_{K}_크기별가격.png')
# 04 네이버 vs 쿠팡 목록
hdr=["모델","네이버 표기","쿠팡 목록 표기"]; x=[60,430,800]; y=200
im,d=canvas(900)
title(d,"네이버와 쿠팡 목록 표기가","쿠팡은 검색 목록에 보인 가격이며 옵션·배송비는 확인하지 못했어요 · 2026-11-04")
for i,h in enumerate(hdr): d.text((x[i],y),h,font=load_font('extrabold',26),fill=c(GOLD))
data=[("쿡이지 1X 28cm","29,880원 (공식몰)","35,000원"),("데일리 엑스퍼트 2X","49,200원 (28cm)","53,900원 (사이즈 미확인)"),("퍼펙트 레지스트 3X","46,170원 (28cm)","47,550원 (스텐 3X, 같은 상품인지 미확인)")]
y+=60
for r in data:
    d.rectangle([40,y-12,W-40,y+128],fill=c("#FFFFFF"))
    for i,t in enumerate(r): d.text((x[i],y+58),t,font=load_font('bold',23),fill=c(NAVY),anchor='lm')
    y+=170
im.save(f'{OUT}/04_{K}_채널별가격.png')
# 05 사양
hdr=["라인","코팅·소재","원산지","특징 칸"]; x=[60,300,620,880]; y=200
data=[("쿡이지 1X","티타늄코팅","중국산","인덕션 표기 없음"),("심플리쉐프 1X","티타늄코팅","중국산 등","인덕션 사용가능"),("라이트쿡 1X","티타늄코팅","프랑스","인덕션 사용가능"),("퍼펙트 레지스트 3X","티타늄코팅·통3중","중국산","인덕션 사용가능"),("데일리 엑스퍼트 2X","티타늄코팅","프랑스산","인덕션 사용가능"),("퍼펙트 터치 3X","소재 티타늄","프랑스산","인덕션 사용가능")]
im,d=canvas(1250)
title(d,"판매 페이지에 적힌 사양","같은 28cm여도 원산지와 인덕션 표기가 달랐어요")
for i,h in enumerate(hdr): d.text((x[i],y),h,font=load_font('extrabold',26),fill=c(GOLD))
y+=60
for r in data:
    d.rectangle([40,y-12,W-40,y+80],fill=c("#FFFFFF"),outline=c(RED) if r[3].startswith("인덕션 표기 없음") else None,width=4)
    for i,t in enumerate(r): d.text((x[i],y+34),t,font=load_font('bold',22),fill=c(RED) if (i==3 and t.startswith("인덕션 표기 없음")) else c(NAVY),anchor='lm')
    y+=120
im.save(f'{OUT}/05_{K}_공개사양.png')
# 06 평점
rows=[("쿡이지 1X 28cm 페이지",4.83,"859"),("쿡이지 1X 20cm 페이지",4.82,"414"),("심플리쉐프 1X",4.77,"418"),("라이트쿡 1X",4.76,"398"),("퍼펙트 레지스트 3X",4.79,"192"),("데일리 엑스퍼트 2X",4.84,"669"),("퍼펙트 터치 3X",4.84,"202"),("트라토리아 주물 28cm",4.83,"3,625"),("스텐 논코팅 20cm",4.63,"862")]
im,d=canvas(1400)
title(d,"네이버 표기 평점(리뷰 수)","리뷰 수는 상품 페이지 전체 기준 · 2026-11-04")
y=200
for k,r,n in rows:
    d.text((60,y+25),k,font=load_font('bold',24),fill=c(NAVY),anchor='lm')
    d.rectangle([420,y+5,420+int(300*r/5),y+45],fill=c(GOLD))
    d.text((750,y+25),f"{r}",font=load_font('extrabold',30),fill=c(NAVY),anchor='lm')
    d.text((W-60,y+25),f"리뷰 {n}건",font=load_font('bold',26),fill=c(GRAY),anchor='rm'); y+=125
im.save(f'{OUT}/06_{K}_평점리뷰.png')
# 07 체크리스트
im,d=canvas(1000)
title(d,"결제 전 확인할 여섯 가지","라인과 크기마다 가격·표기가 달라요")
chk=["라인 이름(1X·2X·3X)과 크기 일치","같은 크기 옵션 가격 비교","인덕션 사용 가능 표기","원산지와 코팅 종류 표기","쿠팡은 옵션·배송비 직접 확인","평점과 리뷰 건수 함께 보기"]
for i,t in enumerate(chk):
    col=i%2; rw=i//2; xx=60+col*570; yy=200+rw*190
    d.rectangle([xx,yy,xx+540,yy+150],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((xx+40,yy+75),"□",font=load_font('extrabold',44),fill=c(GREEN),anchor='lm')
    d.text((xx+110,yy+75),t,font=load_font('bold',22),fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/07_{K}_확인체크리스트.png')
# 08 핵심정리
im,d=canvas(900)
d.rectangle([0,0,W,14],fill=c(GOLD)); d.text((60,70),"핵심 정리",font=load_font('extrabold',52),fill=c(NAVY))
pts=["28cm는 쿡이지 29,880원부터 퍼펙트 터치 56,720원까지 26,840원 차이","퍼펙트 레지스트·퍼펙트 터치는 20cm가 24cm보다 비싸게 표기됨","쿡이지 20cm는 페이지에 따라 20,800원과 24,210원으로 표기됨"]
y=200
for i,t in enumerate(pts,1):
    d.ellipse([60,y,130,y+70],fill=c(GOLD)); d.text((95,y+35),str(i),font=load_font('extrabold',40),fill=c("#FFFFFF"),anchor='mm')
    d.text((160,y+35),t,font=load_font('bold',21),fill=c(NAVY),anchor='lm'); y+=190
im.save(f'{OUT}/08_{K}_핵심정리.png')
