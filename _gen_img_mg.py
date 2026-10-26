import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/shop_2026-10-26_태안물결카라반'; K='태안물결카라반'
print(search_pexels_photo('caravan campsite beach evening lights camping', output_path=f'{OUT}/01_{K}_대표이미지.jpg', orientation='landscape'))
print(search_pexels_photo('seaside camping sunset tent beach family', output_path=f'{OUT}/08_{K}_클로징.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
def title(d,t,s):
    d.text((60,55),t,font=load_font('extrabold',40),fill=c(NAVY)); d.text((60,120),s,font=load_font('regular',27),fill=c(GRAY))
# 02 객실 유형
rows=[("오션뷰 노천탕 독채 카라반","1~4호","기준 2인 · 최대 6인"),("사이드 오션뷰 노천탕 독채 카라반","8·9호","기준 2인 · 최대 6인"),("바다5초 노천탕 독채 감성 커플카라반","5·6·7호","기준 2인 · 최대 3인"),("바다5초 카라반","10·11호","기준 2인 · 최대 4인")]
im,d=canvas(850)
title(d,"객실 유형과 인원","쿠팡 여행(NOL) 객실 목록 · 2026-10-26 조회")
y=205
for n,h,p in rows:
    d.rectangle([60,y,W-60,y+135],fill=c("#FFFFFF"),outline=c(NAVY),width=3)
    d.text((100,y+45),n,font=load_font('bold',29),fill=c(NAVY),anchor='lm')
    d.text((100,y+95),h,font=load_font('extrabold',28),fill=c(GOLD),anchor='lm')
    d.text((W-100,y+68),p,font=load_font('extrabold',28),fill=c(RED),anchor='rm'); y+=160
im.save(f'{OUT}/02_{K}_객실유형.png')
# 03 요일별 요금
data=[("오션뷰 카라반 2호",[99000,179000,349000,119000]),("사이드 오션뷰 8호",[99000,149000,349000,109000]),("커플카라반 5호(최대 3인)",[49000,99000,149000,69000]),("바다5초 카라반 11호",[69000,129000,249000,89000])]
im,d=canvas(950)
title(d,"요일별 1박 요금 (2026년 12월 7~13일 주)","쿠팡 여행 표기 · 월~목 / 금 / 토 / 일 · 날짜마다 달라요")
xs=[560,720,880,1040]
for t,x in zip(("월~목","금","토","일"),xs): d.text((x+60,210),t,font=load_font('extrabold',26),fill=c(GRAY),anchor='mm')
y=260
for n,v in data:
    d.rectangle([40,y-35,W-40,y+60],fill=c("#FFFFFF"),outline=c("#E3DED2"),width=2)
    d.text((60,y+12),n,font=load_font('bold',24),fill=c(NAVY),anchor='lm')
    for p,x in zip(v,xs):
        d.text((x+110,y+12),f"{p:,}",font=load_font('extrabold',28),fill=c(RED if p>=249000 else NAVY),anchor='rm')
    y+=130
d.text((60,y+10),"금액 단위는 원이에요. 예약불가 날짜가 있어 같은 호수라도 표에 없는 날이 있어요.",font=load_font('regular',24),fill=c(GRAY))
im.save(f'{OUT}/03_{K}_요일별요금.png')
# 04 추가 요금
items=[("바비큐(숯·그릴·토치·장갑)","30,000원 (4인 기준) · 1인 추가 5,000원"),("불멍","20,000원"),("노천탕 냉수 / 온수","20,000원 / 50,000원 (사전 예약)"),("퇴실 연장(12시까지)","시간당 10,000원 · 성수기·공휴일 불가")]
im,d=canvas(800)
title(d,"현장 추가 요금","쿠팡 여행 숙소 공지 기준 · 2026-10-26")
y=205
for k,v in items:
    d.rectangle([60,y,W-60,y+115],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((100,y+58),k,font=load_font('bold',28),fill=c(NAVY),anchor='lm')
    d.text((W-100,y+58),v,font=load_font('extrabold',26),fill=c(RED),anchor='rm'); y+=135
im.save(f'{OUT}/04_{K}_추가요금.png')
# 05 이용 안내
info=[("체크인 / 체크아웃","15:00 / 11:00 (입실은 20시까지, 이후는 연락)"),("반려동물","동반 입실 금지"),("카라반 안","흡연·고기·생선 굽기 금지, 식수·음식은 직접 준비"),("제공 비품","에어컨·온풍기·TV·냉장고·전자레인지·쿡탑·전기밥솥·침구"),("취소","취소 수수료는 체크인 날짜 기준, 마이쿠팡에서 확인")]
im,d=canvas(950)
title(d,"이용 안내 요약","쿠팡 여행 숙소 정책 · 2026-10-26")
y=200
for k,v in info:
    d.text((60,y+20),k,font=load_font('extrabold',27),fill=c(GOLD),anchor='lm')
    d.text((60,y+68),v,font=load_font('bold',25),fill=c(NAVY),anchor='lm'); y+=140
im.save(f'{OUT}/05_{K}_이용안내.png')
# 06 체크리스트
im,d=canvas(1000)
title(d,"예약 전 확인할 여섯 가지","날짜마다 요금과 잔여 객실이 달라요")
chk=["가는 날 요일(금·토 요금이 크게 올라요)","객실 유형과 최대 인원(아기 포함 여부)","바비큐·불멍·노천탕 추가 요금","체크인 시간(입실 20시 마감)","식수·음식·아기용품 직접 준비","취소 수수료와 예약처별 가격"]
for i,t in enumerate(chk):
    col=i%2; rw=i//2; x=60+col*570; yy=200+rw*190
    d.rectangle([x,yy,x+540,yy+150],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((x+40,yy+75),"□",font=load_font('extrabold',44),fill=c(GREEN),anchor='lm')
    d.text((x+110,yy+75),t,font=load_font('bold',22),fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/06_{K}_확인체크리스트.png')
# 07 핵심 정리
im,d=canvas(900)
d.rectangle([0,0,W,14],fill=c(GOLD)); d.text((60,70),"핵심 정리",font=load_font('extrabold',52),fill=c(NAVY))
pts=["평일 49,000원부터, 토요일은 최대 349,000원까지 표기됐어요","바비큐 30,000원, 노천탕 20,000~50,000원은 현장 추가 요금이에요","추천은 작성자 의견이고, 쿠팡 상품평은 시설·청결이 엇갈려요"]
y=200
for i,t in enumerate(pts,1):
    d.ellipse([60,y,130,y+70],fill=c(GOLD)); d.text((95,y+35),str(i),font=load_font('extrabold',40),fill=c("#FFFFFF"),anchor='mm')
    d.text((160,y+35),t,font=load_font('bold',24),fill=c(NAVY),anchor='lm'); y+=190
im.save(f'{OUT}/07_{K}_핵심정리.png')
