import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/shop_2026-10-13_네오플램글라쎄Z'
K='네오플램글라쎄Z'
print(search_pexels_photo('glass food storage containers kitchen fridge organized', output_path=f'{OUT}/01_{K}_대표이미지.jpg', orientation='landscape'))
print(search_pexels_photo('tidy kitchen counter morning light', output_path=f'{OUT}/07_{K}_클로징.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
body=load_font('regular',28)
def title(d,t,s):
    d.text((60,55),t,font=load_font('extrabold',40),fill=c(NAVY)); d.text((60,120),s,font=body,fill=c(GRAY))
# 02 이름 관계
im,d=canvas(800)
title(d,"글라쎄 Z pro와 베큐씰, 어떤 관계?","네오플램 2026-06-18 보도 기준")
d.rectangle([60,220,520,520],fill=c("#FFFFFF"),outline=c(GRAY),width=4)
d.text((290,310),"글라쎄 Z pro",font=load_font('extrabold',44),fill=c(NAVY),anchor='mm')
d.text((290,400),"기존 진공 유리용기",font=load_font('bold',30),fill=c(GRAY),anchor='mm')
d.text((600,370),"→",font=load_font('extrabold',80),fill=c(GOLD),anchor='mm')
d.rectangle([680,220,1140,520],fill=c("#FFFFFF"),outline=c(GOLD),width=5)
d.text((910,310),"베큐씰",font=load_font('extrabold',48),fill=c(GOLD),anchor='mm')
d.text((910,400),"리뉴얼 2세대 (보이는 진공)",font=load_font('bold',30),fill=c(NAVY),anchor='mm')
d.text((60,600),"쿠팡 목록에는 '글라쎄Z', 'PRO', '베큐씰' 이름이 섞여 있습니다.",font=load_font('bold',30),fill=c(RED))
d.text((60,660),"같은 제품인지는 상세 페이지에서 직접 확인하세요.",font=load_font('bold',30),fill=c(RED))
im.save(f'{OUT}/02_{K}_이름관계.png')
# 03 공개 사양
im,d=canvas(1060)
title(d,"베큐씰 보도자료 공개 사양","네오플램 2026-06-18 · 기사에 적힌 내용만")
rows=[("진공 표시","뚜껑 중앙 버튼으로 확인",NAVY),("보관일 표시","내장 다이얼",GOLD),("내열 온도","-20 ~ 400도 (유리 본체)",RED),("진공 펌프","USB-C 충전 · 완충 30분 · 최대 2시간",GREEN),("크기","정사각·직사각 각 S/M/L/XL, 8종",NAVY)]
y=190
for k,v,col in rows:
    d.rectangle([60,y,W-60,y+140],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((100,y+70),k,font=load_font('bold',34),fill=c(NAVY),anchor='lm')
    d.text((W-100,y+70),v,font=load_font('extrabold',32),fill=c(col),anchor='rm')
    y+=165
im.save(f'{OUT}/03_{K}_공개사양.png')
# 04 쿠팡 구성별 가격
im,d=canvas(960)
title(d,"쿠팡 구성별 표기 가격","2026-10-13 조회 · 구성과 판매처가 서로 다름")
rows=[("글라쎄Z 냉동밥 5종+펌프",75000,GREEN),("베큐씰 직사각 단품",58850,GREEN),("베큐씰 정사각 2종+펌프",118800,GOLD),("글라쎄Z 진공 세트",173000,GOLD),("글라쎄Z PRO 13종",179800,RED)]
rows.sort(key=lambda r:r[1])
y=200; mx=179800
for k,v,col in rows:
    d.text((60,y+28),k,font=load_font('bold',28),fill=c(NAVY),anchor='lm')
    w=int((W-760)*v/mx)
    d.rectangle([460,y,460+w,y+56],fill=c(col))
    d.text((460+w+12,y+28),f"{v:,}원",font=load_font('extrabold',28),fill=c(NAVY),anchor='lm')
    y+=125
im.save(f'{OUT}/04_{K}_구성별가격.png')
# 05 체크리스트
im,d=canvas(1000)
title(d,"구매 전 확인할 6가지","보도자료에 없어서 직접 확인이 필요한 항목 포함")
chk=["용기 개수와 크기 구성","진공 펌프 포함 여부","식기세척기 사용 가능 여부","KC·식품용 인증 표기","급격한 온도 변화 주의 문구","글라쎄Z·PRO·베큐씰 중 어느 시리즈"]
for i,t in enumerate(chk):
    col=i%2; row=i//2
    x=60+col*570; y=200+row*190
    d.rectangle([x,y,x+540,y+150],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((x+40,y+75),"□",font=load_font('extrabold',44),fill=c(GREEN),anchor='lm')
    d.text((x+110,y+75),t,font=load_font('bold',28),fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/05_{K}_확인체크리스트.png')
# 06 핵심 정리
im,d=canvas(900)
d.rectangle([0,0,W,14],fill=c(GOLD))
d.text((60,70),"핵심 정리",font=load_font('extrabold',52),fill=c(NAVY))
pts=["글라쎄 Z pro는 베큐씰로 리뉴얼됐고 쿠팡에는 이름이 섞여 있음","구성에 따라 5만 원대에서 18만 원 가까이까지 가격 차이","냉동 직후 고온 가열 같은 급격한 온도 변화는 주의"]
y=200
for i,t in enumerate(pts,1):
    d.ellipse([60,y,130,y+70],fill=c(GOLD)); d.text((95,y+35),str(i),font=load_font('extrabold',40),fill=c("#FFFFFF"),anchor='mm')
    d.text((160,y+35),t,font=load_font('bold',30),fill=c(NAVY),anchor='lm')
    y+=190
im.save(f'{OUT}/06_{K}_핵심정리.png')
