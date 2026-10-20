import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/shop_2026-10-20_도마교체시기'; K='도마교체시기'
print(search_pexels_photo('worn cutting board knife marks kitchen', output_path=f'{OUT}/01_{K}_대표이미지.jpg', orientation='landscape'))
print(search_pexels_photo('clean wooden cutting board drying kitchen counter', output_path=f'{OUT}/07_{K}_클로징.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
body=load_font('regular',28)
def title(d,t,s):
    d.text((60,55),t,font=load_font('extrabold',40),fill=c(NAVY)); d.text((60,120),s,font=body,fill=c(GRAY))
def card(d,x,y,w,h,head,lines,col):
    d.rectangle([x,y,x+w,y+h],fill=c("#FFFFFF"),outline=c(col),width=3)
    d.text((x+30,y+44),head,font=load_font('extrabold',30),fill=c(col),anchor='lm')
    yy=y+96
    for l in lines:
        d.text((x+30,yy),l,font=load_font('bold',24),fill=c(NAVY),anchor='lm'); yy+=46
# 02 교체 신호
im,d=canvas(900)
title(d,"도마 교체를 고려하는 신호","위키트리 2026-07-07 · 레이디경향 2024-09-20, 2024-11-01 기사 정리")
sig=[("칼자국","손가락·손톱이 걸릴 만큼 깊은 홈"),("냄새·얼룩","씻어도 냄새가 남거나 색이 안 빠짐"),("모양 변형","뒤틀리거나 갈라짐")]
y=200
for i,(a,b) in enumerate(sig,1):
    d.rectangle([60,y,W-60,y+170],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.ellipse([90,y+45,170,y+125],fill=c(GOLD)); d.text((130,y+85),str(i),font=load_font('extrabold',44),fill=c("#FFFFFF"),anchor='mm')
    d.text((210,y+60),a,font=load_font('extrabold',36),fill=c(NAVY),anchor='lm'); d.text((210,y+115),b,font=load_font('bold',26),fill=c(GRAY),anchor='lm'); y+=200
im.save(f'{OUT}/02_{K}_교체신호.png')
# 03 재질별 특징
im,d=canvas(1000)
title(d,"재질별 특징(기사 정리)","같은 기사의 설명이며 제품마다 다를 수 있어요")
rows=[("나무","칼날 충격을 줄임 · 수분 흡수, 건조 관리 중요",GREEN),("플라스틱","가볍고 씻기 쉬움 · 흠집 생기면 위생 관리 어려움",GOLD),("유리","냄새·착색 적음 · 칼날 빨리 무뎌짐, 보조용 권장",GRAY),("돌·대나무","흠집은 덜 생김 · 너무 단단해 칼날 손상 가능",GRAY)]
y=200
for a,b,col in rows:
    d.rectangle([60,y,W-60,y+155],fill=c("#FFFFFF"),outline=c(col),width=3)
    d.text((100,y+78),a,font=load_font('extrabold',38),fill=c(col),anchor='lm'); d.text((330,y+78),b,font=load_font('bold',25),fill=c(NAVY),anchor='lm'); y+=185
im.save(f'{OUT}/03_{K}_재질별특징.png')
# 04 세척·건조
im,d=canvas(900)
title(d,"씻고 말리는 순서","기사에서 공통으로 안내한 방법")
st=[("씻기","세제로 양면과 가장자리까지 문질러 씻기 (미지근한 물 헹굼만으로는 부족)"),("분리","육류·생선·채소과일·조리 후 음식용으로 나눠 쓰기"),("말리기","물기 털고 세워서 통풍되는 곳에서 완전히 말리기")]
y=200
for i,(a,b) in enumerate(st,1):
    d.rectangle([60,y,W-60,y+170],fill=c("#FFFFFF"),outline=c(NAVY),width=3)
    d.text((110,y+85),f"{i}",font=load_font('extrabold',60),fill=c(GOLD),anchor='mm')
    d.text((190,y+55),a,font=load_font('extrabold',34),fill=c(NAVY),anchor='lm')
    d.text((190,y+115),b,font=load_font('bold',23),fill=c(GRAY),anchor='lm'); y+=200
im.save(f'{OUT}/04_{K}_세척건조.png')
# 05 체크리스트
im,d=canvas(1000)
title(d,"교체 전에 확인할 다섯 가지","손으로 만져 보고 점검해 보세요")
chk=["칼자국에 손톱이 걸리는지","씻어도 냄새·얼룩이 남는지","뒤틀림이나 갈라짐이 있는지","육류용·채소용을 나눠 쓰는지","쓴 뒤 세워서 완전히 말리는지"]
for i,t in enumerate(chk):
    col=i%2; row=i//2; x=60+col*570; y=200+row*190
    d.rectangle([x,y,x+540,y+150],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((x+40,y+75),"□",font=load_font('extrabold',44),fill=c(GREEN),anchor='lm')
    d.text((x+110,y+75),t,font=load_font('bold',24),fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/05_{K}_확인체크리스트.png')
# 06 핵심 정리
im,d=canvas(900)
d.rectangle([0,0,W,14],fill=c(GOLD)); d.text((60,70),"핵심 정리",font=load_font('extrabold',52),fill=c(NAVY))
pts=["손톱이 걸리는 칼자국, 안 빠지는 냄새, 뒤틀림이 교체 신호","1~1.5년 권고는 출처 불분명, 참고만","재질보다 세척·건조·용도별 분리가 더 중요"]
y=200
for i,t in enumerate(pts,1):
    d.ellipse([60,y,130,y+70],fill=c(GOLD)); d.text((95,y+35),str(i),font=load_font('extrabold',40),fill=c("#FFFFFF"),anchor='mm')
    d.text((160,y+35),t,font=load_font('bold',26),fill=c(NAVY),anchor='lm'); y+=190
im.save(f'{OUT}/06_{K}_핵심정리.png')
