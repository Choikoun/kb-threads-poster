import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/shop_2026-10-14_라바제식기건조대'; K='라바제식기건조대'
print(search_pexels_photo('stainless dish drying rack kitchen sink clean', output_path=f'{OUT}/01_{K}_대표이미지.jpg', orientation='landscape'))
print(search_pexels_photo('bright kitchen counter morning plates', output_path=f'{OUT}/07_{K}_클로징.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
body=load_font('regular',28)
def title(d,t,s):
    d.text((60,55),t,font=load_font('extrabold',40),fill=c(NAVY)); d.text((60,120),s,font=body,fill=c(GRAY))
# 02 공식 모델 사양
im,d=canvas(1000)
title(d,"라바제 식기건조대 공식 모델 정보","제조사 와헤이 공식 페이지 · 3종 세트 구성 · 크기·무게는 약값")
hdr=["모델","형태","크기(mm)","무게"]; xs=[70,260,560,980]
d.rectangle([60,190,W-60,250],fill=c(NAVY))
for x,h in zip(xs,hdr): d.text((x,220),h,font=load_font('bold',28),fill=c("#FFFFFF"),anchor='lm' if h!='무게' else 'rm')
rows=[("DLM-8690","슬림 세로형","450×300×140","2,180g"),("DLM-8585","대형 세로형","452×390×140","2,770g"),("DLM-8563","대형 가로형","538×312×140","2,570g"),("DLM-8775","슬림 가로형","538×312×140","2,570g"),("LB-101","소형 세로형","358×322×142","1,814g")]
y=250
for i,r in enumerate(rows):
    d.rectangle([60,y,W-60,y+110],fill=c("#FFFFFF" if i%2==0 else "#F0EDE5"))
    for x,v,h in zip(xs,r,hdr): d.text((x,y+55),v,font=load_font('extrabold' if h=='모델' else 'bold',30),fill=c(NAVY),anchor='lm' if h!='무게' else 'rm')
    y+=110
d.text((60,880),"소재: 18-8 스테인리스 · 고무발: 실리콘 · 원산지: 일본",font=load_font('bold',30),fill=c(GREEN))
im.save(f'{OUT}/02_{K}_공식사양.png')
# 03 쿠팡 가격
im,d=canvas(860)
title(d,"쿠팡 목록 표기 가격 (같은 이름, 다른 가격)","2026-10-14 조회 · 구성과 옵션이 서로 다름")
rows=[("DLM-8690 슬림 세로형(일본직수입)",88900,GREEN),("DLM-8690 슬림 세로형(다른 옵션)",116000,GREEN),("DLM-8563 가로형 대",168000,GOLD),("DLM-8690 슬림 가로 올스텐",209860,GOLD),("DLM-8690 3종세트",255000,RED)]
y=190; mx=255000
for k,v,col in rows:
    d.text((60,y+28),k,font=load_font('bold',24),fill=c(NAVY),anchor='lm')
    w=int((W-700)*v/mx); d.rectangle([520,y,520+w,y+56],fill=c(col))
    d.text((520+w+12,y+28),f"{v:,}원",font=load_font('extrabold',28),fill=c(NAVY),anchor='lm'); y+=125
im.save(f'{OUT}/03_{K}_쿠팡가격.png')
# 04 네이버 쇼핑 커넥트 목록
im,d=canvas(900)
title(d,"네이버쇼핑 라바제 목록 3개","브랜드 커넥트 조회 · 2026-10-14 · 세 목록 모두 리뷰 0건 표기")
rows=[("홈바 싱크 라바제 식기건조대 (마켓블렌드)","48,510원"),("가로형 선반 건조대 (ongoshop)","98,800원"),("올스텐 세로형 건조선반 (제이에스글로벌샵)","351,800원")]
y=190
for k,v in rows:
    d.rectangle([60,y,W-60,y+170],fill=c("#FFFFFF"),outline=c(GOLD),width=4)
    d.text((100,y+85),k,font=load_font('bold',28),fill=c(NAVY),anchor='lm')
    d.text((W-100,y+85),v,font=load_font('extrabold',40),fill=c(RED if v.startswith('351') else GREEN),anchor='rm'); y+=200
im.save(f'{OUT}/04_{K}_네이버목록.png')
# 05 체크리스트
im,d=canvas(1000)
title(d,"결제 전 확인할 6가지","모델명이 같아도 구성·판매처가 다를 수 있어요")
chk=["모델명 (DLM-8690 등)","3종 세트인지 건조대 단품인지","크기(mm)가 싱크대에 맞는지","일본 직수입·정식 유통 여부","최종 결제가와 배송비","교환·반품 조건"]
for i,t in enumerate(chk):
    col=i%2; row=i//2; x=60+col*570; y=200+row*190
    d.rectangle([x,y,x+540,y+150],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((x+40,y+75),"□",font=load_font('extrabold',44),fill=c(GREEN),anchor='lm')
    d.text((x+110,y+75),t,font=load_font('bold',26),fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/05_{K}_확인체크리스트.png')
# 06 핵심 정리
im,d=canvas(900)
d.rectangle([0,0,W,14],fill=c(GOLD)); d.text((60,70),"핵심 정리",font=load_font('extrabold',52),fill=c(NAVY))
pts=["같은 DLM-8690이 쿠팡에서 88,900~255,000원으로 표기","3종 세트(건조대·수저통·물받이)인지 단품인지부터 확인","크기와 판매처 · 정식 유통 여부는 상세 페이지로 확인"]
y=200
for i,t in enumerate(pts,1):
    d.ellipse([60,y,130,y+70],fill=c(GOLD)); d.text((95,y+35),str(i),font=load_font('extrabold',40),fill=c("#FFFFFF"),anchor='mm')
    d.text((160,y+35),t,font=load_font('bold',28),fill=c(NAVY),anchor='lm'); y+=190
im.save(f'{OUT}/06_{K}_핵심정리.png')
