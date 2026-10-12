import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/shop_2026-10-12_깃든탄소매트'
K='깃든탄소매트'
print(search_pexels_photo('cozy bedroom bed warm blanket winter morning', output_path=f'{OUT}/01_{K}_대표이미지.jpg', orientation='landscape'))
print(search_pexels_photo('quiet bedroom evening lamp', output_path=f'{OUT}/07_{K}_클로징.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
body=load_font('regular',28); small=load_font('regular',24)
def title(d,t,s):
    d.text((60,55),t,font=load_font('extrabold',40),fill=c(NAVY)); d.text((60,120),s,font=body,fill=c(GRAY))
# 02 가격 비교 막대
im,d=canvas(900)
title(d,"깃든 온 탄소매트 표기 가격 비교","2026-10-12 조회 · 옵션·판매처에 따라 다름")
rows=[("공식몰 표기",129000,GREEN),("쿠팡 'GITDEN 9colors' 최저",160100,GOLD),("쿠팡 '깃든 온' 최저",180000,GOLD),("쿠팡 'GITDEN 9colors' 최고",185200,GOLD),("쿠팡 '깃든 온' 중간",205900,RED),("쿠팡 '깃든 온' 최고",232500,RED)]
y=200; mx=232500
for k,v,col in rows:
    d.text((60,y+28),k,font=load_font('bold',26),fill=c(NAVY),anchor='lm')
    w=int((W-720)*v/mx)
    d.rectangle([420,y,420+w,y+56],fill=c(col))
    d.text((420+w+12,y+28),f"{v:,}원",font=load_font('extrabold',28),fill=c(NAVY),anchor='lm')
    y+=105
im.save(f'{OUT}/02_{K}_가격비교.png')
# 03 공식몰 판매 조건
im,d=canvas(900)
title(d,"공식몰 판매 조건 한눈에","gitdenkorea.com 상품 페이지 기준 · 2026-10-12")
items=[("판매가","129,000원 (소비자가 160,000원)"),("옵션","싱글 · 더블 (가격 구분 표기 없음)"),("색상","10가지 (스트라이프 6종 포함)"),("배송","택배 1~3일 · 3,500원 (10만원 이상 무료)"),("교환·반품","단순 변심은 반송비 고객 부담")]
y=190
for k,v in items:
    d.rectangle([60,y,W-60,y+120],fill=c("#FFFFFF"),outline=c(NAVY),width=3)
    d.text((100,y+60),k,font=load_font('extrabold',32),fill=c(GOLD),anchor='lm')
    d.text((330,y+60),v,font=load_font('bold',32),fill=c(NAVY),anchor='lm')
    y+=140
im.save(f'{OUT}/03_{K}_공식몰조건.png')
# 04 확인 체크리스트
im,d=canvas(1000)
title(d,"구매 전 직접 확인할 8가지","공식몰 텍스트 정보에 표기가 없는 항목")
chk=["가로·세로 크기(cm)","원단 소재","소비전력 · 정격전압","최대 표면온도","세탁 방법과 제한","안전기능(과열 방지 등)","KC 인증번호","무상 보증기간"]
for i,t in enumerate(chk):
    col=i%2; row=i//2
    x=60+col*570; y=200+row*190
    d.rectangle([x,y,x+540,y+150],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((x+40,y+75),"□",font=load_font('extrabold',44),fill=c(GREEN),anchor='lm')
    d.text((x+110,y+75),t,font=load_font('bold',32),fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/04_{K}_확인체크리스트.png')
# 05 소비자원 일반 기준
im,d=canvas(1060)
title(d,"탄소매트 일반 확인 기준","한국소비자원 10개 제품 시험 · 깃든 제품은 시험 대상 아님")
rows=[("최대 표면온도","39 ~ 64도",NAVY),("위치별 온도편차","0.4 ~ 10.5도",GOLD),("발열속도 (20→35도)","12 ~ 49분",RED),("머리 쪽 열선 없는 제품","10개 중 4개",GREEN),("수면 중 권고 표면온도","37도 이하",NAVY)]
y=190
for k,v,col in rows:
    d.rectangle([60,y,W-60,y+140],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((100,y+70),k,font=load_font('bold',34),fill=c(NAVY),anchor='lm')
    d.text((W-100,y+70),v,font=load_font('extrabold',40),fill=c(col),anchor='rm')
    y+=165
im.save(f'{OUT}/05_{K}_소비자원기준.png')
# 06 핵심 정리
im,d=canvas(900)
d.rectangle([0,0,W,14],fill=c(GOLD))
d.text((60,70),"핵심 정리",font=load_font('extrabold',52),fill=c(NAVY))
pts=["공식몰 표기 129,000원, 쿠팡 목록은 16만~23만 원대","같은 이름이라도 옵션·판매처에 따라 가격이 다름","크기·소비전력·세탁법은 상세 이미지와 라벨로 확인"]
y=200
for i,t in enumerate(pts,1):
    d.ellipse([60,y,130,y+70],fill=c(GOLD)); d.text((95,y+35),str(i),font=load_font('extrabold',40),fill=c("#FFFFFF"),anchor='mm')
    d.text((160,y+35),t,font=load_font('bold',34),fill=c(NAVY),anchor='lm')
    y+=190
im.save(f'{OUT}/06_{K}_핵심정리.png')
