import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/shop_2026-10-24_타파웨어반찬통'; K='타파웨어반찬통'
print(search_pexels_photo('plastic food storage containers refrigerator organized side dishes', output_path=f'{OUT}/01_{K}_대표이미지.jpg', orientation='landscape'))
print(search_pexels_photo('kitchen refrigerator containers meal prep home', output_path=f'{OUT}/07_{K}_클로징.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
def title(d,t,s):
    d.text((60,55),t,font=load_font('extrabold',40),fill=c(NAVY)); d.text((60,120),s,font=load_font('regular',28),fill=c(GRAY))
# 02 공식몰 세트 표 (네이버쇼핑 표기)
rows=[("원형 밀폐용기 5개세트","39,000","29,900","23%","4.7 (368)"),("원터치 선물세트(N단독구성)","90,000","56,000","37%","4.8 (204)"),("싱싱블록 베이직세트 8개","166,800","99,000","40%","5.0 (10)"),("모듈러 보울 패키지세트","237,000","106,700","54%","4.85 (99)"),("실속구성 원터치 24개","286,000","179,000","37%","4.88 (346)")]
im,d=canvas(1050)
title(d,"타파웨어 공식몰 세트 네이버 표기가","네이버쇼핑(브랜드 커넥트 목록) 2026-10-24 조회 · 정가→할인가 · 평점(리뷰 수)")
xs=[60,640,800,1000,1140]
for t,x,al in (("세트",60,'lm'),("정가",700,'rm'),("할인가",880,'rm'),("할인율",980,'rm'),("평점(리뷰)",1150,'rm')):
    d.text((x,205),t,font=load_font('extrabold',24),fill=c(GRAY),anchor=al)
y=265
for n,a,b,r,s in rows:
    d.rectangle([40,y-40,W-40,y+50],fill=c("#FFFFFF"),outline=c("#E3DED2"),width=2)
    d.text((60,y+5),n,font=load_font('bold',25),fill=c(NAVY),anchor='lm')
    d.text((700,y+5),a,font=load_font('regular',24),fill=c(GRAY),anchor='rm')
    d.text((880,y+5),b,font=load_font('extrabold',27),fill=c(RED),anchor='rm')
    d.text((980,y+5),r,font=load_font('bold',24),fill=c(NAVY),anchor='rm')
    d.text((1150,y+5),s,font=load_font('bold',24),fill=c(NAVY),anchor='rm')
    y+=140
im.save(f'{OUT}/02_{K}_공식몰세트.png')
# 03 개당 가격
per=[("원형 밀폐용기 5개세트",29900,5),("싱싱블록 미니 정사각 110ml 4개",29900,4)]
im,d=canvas(700)
title(d,"소분 용기 개당 가격 환산","네이버쇼핑 공식몰 표기 할인가 ÷ 개수 · 2026-10-24")
y=230
for k,p,n in per:
    d.rectangle([60,y,W-60,y+170],fill=c("#FFFFFF"),outline=c(NAVY),width=3)
    d.text((100,y+60),k,font=load_font('bold',30),fill=c(NAVY),anchor='lm')
    d.text((100,y+120),f"{p:,}원 ÷ {n}개",font=load_font('regular',26),fill=c(GRAY),anchor='lm')
    d.text((W-100,y+90),f"개당 {p//n:,}원",font=load_font('extrabold',44),fill=c(RED),anchor='rm'); y+=210
im.save(f'{OUT}/03_{K}_개당가격.png')
# 04 쿠팡 목록
cp=[("원형 볼 4P 반찬통",13130),("사각용기 700ml",22900),("다용도 미니밀폐용기 230ml 5개",22610),("냉장고정리용기 6종 400ml",27090),("원터치프레시 540ml 4개",27660),("사각용기 1.7L",29330),("밀폐용기 반찬용기 7종세트",113000)]
im,d=canvas(1100)
title(d,"쿠팡 '타파웨어 반찬통' 목록 표기가","2026-10-24 조회 · 상위 목록 일부 · 판매자와 구성은 목록마다 달라요")
y=210
for k,v in cp:
    d.text((60,y+22),k,font=load_font('bold',25),fill=c(NAVY),anchor='lm')
    w=int(430*v/113000); d.rectangle([520,y,520+w,y+44],fill=c(GOLD if v<100000 else RED))
    d.text((520+w+12,y+22),f"{v:,}원",font=load_font('extrabold',25),fill=c(NAVY),anchor='lm'); y+=115
im.save(f'{OUT}/04_{K}_쿠팡목록.png')
# 05 체크리스트
im,d=canvas(1000)
title(d,"결제 전 확인할 여섯 가지","타파웨어는 모델마다 사용 가능 범위가 달라요")
chk=["공식몰 표기인지 다른 판매자 표기인지","세트 개수와 용량(ml) 구성","냉동·전자레인지 사용 가능 여부(모델별)","식기세척기 사용 안내","평점과 리뷰 수 함께 보기","최종 결제가와 교환·반품 조건"]
for i,t in enumerate(chk):
    col=i%2; rw=i//2; x=60+col*570; yy=200+rw*190
    d.rectangle([x,yy,x+540,yy+150],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((x+40,yy+75),"□",font=load_font('extrabold',44),fill=c(GREEN),anchor='lm')
    d.text((x+110,yy+75),t,font=load_font('bold',23),fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/05_{K}_확인체크리스트.png')
# 06 핵심 정리
im,d=canvas(900)
d.rectangle([0,0,W,14],fill=c(GOLD)); d.text((60,70),"핵심 정리",font=load_font('extrabold',52),fill=c(NAVY))
pts=["공식몰 세트는 29,900원부터 179,000원, 할인율 23~54% 표기","소분 용기는 개당 5,980원(원형 5개)과 7,475원(싱싱블록 미니 4개)","냉동·전자레인지 가능 여부는 모델마다 달라 상세 안내를 확인하세요"]
y=200
for i,t in enumerate(pts,1):
    d.ellipse([60,y,130,y+70],fill=c(GOLD)); d.text((95,y+35),str(i),font=load_font('extrabold',40),fill=c("#FFFFFF"),anchor='mm')
    d.text((160,y+35),t,font=load_font('bold',24),fill=c(NAVY),anchor='lm'); y+=190
im.save(f'{OUT}/06_{K}_핵심정리.png')
