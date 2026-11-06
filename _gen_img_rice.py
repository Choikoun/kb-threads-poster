import sys,os
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/shop_2026-11-08_락앤락쌀통'; K='락앤락쌀통'
if not os.path.exists(f'{OUT}/01_{K}_대표이미지.jpg'): print(search_pexels_photo('rice storage container kitchen grains', output_path=f'{OUT}/01_{K}_대표이미지.jpg', orientation='landscape'))
if not os.path.exists(f'{OUT}/08_{K}_클로징.jpg'): print(search_pexels_photo('bowl of cooked rice kitchen table', output_path=f'{OUT}/08_{K}_클로징.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
def title(d,t,s):
    d.text((60,55),t,font=load_font('extrabold',40),fill=c(NAVY)); d.text((60,120),s,font=load_font('regular',26),fill=c(GRAY))
# 02 네이버 총액
rows=[("락앤락 도어포켓 2kg",5600,3000),("김형철물점 5L",16440,3000),("ANA스토어 락앤락 10kg",19800,3000),("김형철물점 5KG",20600,3000),("글로벌웨이스 20kg 구매대행",35000,0)]
im,d=canvas(1000)
title(d,"락앤락 쌀통 네이버 판매가와 배송비","막대는 판매가 · 오른쪽 숫자는 배송비를 더한 합계 · 2026-11-06 조회")
y=200
for n,v,sh in rows:
    d.text((60,y),n,font=load_font('bold',26),fill=c(NAVY)); y+=42
    w=int(520*v/40000)
    d.rectangle([60,y,60+w,y+40],fill=c(GOLD))
    d.text((60+w+14,y+20),f"{v+sh:,}원",font=load_font('extrabold',28),fill=c(NAVY),anchor='lm')
    d.text((W-60,y+20),f"판매가 {v:,} + 배송 {sh:,}" if sh else f"판매가 {v:,} · 무료배송",font=load_font('bold',22),fill=c(GRAY),anchor='rm'); y+=66
    y+=26
im.save(f'{OUT}/02_{K}_네이버가격.png')
# 03 쿠팡 목록
hdr=["상품명(쿠팡 표기)","쿠팡 목록","로켓 표기"]; x=[60,800,1000]; y=200
data=[("락앤락 도어포켓 잡곡통 2kg","13,500원","없음"),("락앤락 쌀통 (용량 미표기)","15,200원","있음"),("락앤락 잡곡통 캔디통 5kg","11,400원","없음"),("락앤락 쌀통 5kg 계량컵 제습제","29,900원","없음"),("락앤락쌀통 바퀴형 12L(10kg)","18,400원","없음"),("락앤락 쌀통 계량컵 제습제","22,900원","없음"),("락앤락 쌀통 10kg 캔디통 5L 세트","23,450원","있음")]
im,d=canvas(1250)
title(d,"락앤락 쌀통 쿠팡 목록 가격","쿠팡은 검색 목록 가격이에요 · 배송비와 옵션은 확인하지 못했어요")
for i,h in enumerate(hdr): d.text((x[i],y),h,font=load_font('extrabold',24),fill=c(GOLD))
y+=56
for r in data:
    d.rectangle([40,y-10,W-40,y+90],fill=c("#FFFFFF"))
    for i,t in enumerate(r): d.text((x[i],y+40),t,font=load_font('bold',23),fill=c(NAVY),anchor='lm')
    y+=125
im.save(f'{OUT}/03_{K}_쿠팡목록.png')
# 04 브랜드 표기
hdr=["판매 페이지","용량","브랜드 칸","제조사·모델 칸"]; x=[60,430,620,900]; y=200
data=[("도어포켓 2kg","2kg","락앤락","모델명 HPL520"),("ANA스토어 10kg","10kg","락앤락","락앤락"),("김형철물점 5KG","5KG","김형2501DO","김형협력사"),("김형철물점 5L","5L","김형2501DO","김형협력사"),("글로벌웨이스 20kg","20kg","브랜드없음","협력사 · 구매대행")]
im,d=canvas(1000)
title(d,"판매 페이지에 적힌 브랜드 표기","상품명에는 모두 락앤락이 들어 있어요")
for i,h in enumerate(hdr): d.text((x[i],y),h,font=load_font('extrabold',26),fill=c(GOLD))
y+=56
for r in data:
    flag=r[2]!="락앤락"
    d.rectangle([40,y-10,W-40,y+80],fill=c("#FFFFFF"),outline=c(RED) if flag else None,width=4 if flag else 0)
    for i,t in enumerate(r): d.text((x[i],y+35),t,font=load_font('bold',22),fill=c(NAVY),anchor='lm')
    y+=125
im.save(f'{OUT}/04_{K}_브랜드표기.png')
# 05 평점
rows=[("락앤락 도어포켓 2kg",5.0,"27"),("ANA스토어 락앤락 10kg",4.8,"88"),("김형철물점 5KG",0,"0"),("김형철물점 5L",0,"0"),("글로벌웨이스 20kg",0,"0")]
im,d=canvas(960)
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
title(d,"결제 전 확인할 여섯 가지","총액과 브랜드 칸부터 보세요")
chk=["판매가에 배송비를 더한 총액 비교","용량 kg와 L 구분해서 확인","계량컵·제습제 포함 여부 확인","브랜드 칸과 제조사 칸 확인","쿠팡은 옵션·배송비 직접 확인","평점은 리뷰 건수와 함께 보기"]
for i,t in enumerate(chk):
    col=i%2; rw=i//2; xx=60+col*570; yy=200+rw*190
    d.rectangle([xx,yy,xx+540,yy+150],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((xx+40,yy+75),"□",font=load_font('extrabold',44),fill=c(GREEN),anchor='lm')
    d.text((xx+110,yy+75),t,font=load_font('bold',21),fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/06_{K}_확인체크리스트.png')
# 07 핵심
im,d=canvas(900)
d.rectangle([0,0,W,14],fill=c(GOLD)); d.text((60,70),"핵심 정리",font=load_font('extrabold',52),fill=c(NAVY))
pts=["도어포켓 2kg은 네이버 합계 8,600원, 쿠팡 목록 13,500원","10kg은 네이버 합계 22,800원, 쿠팡은 18,400원부터 23,450원","상품명에 락앤락이 있어도 브랜드 칸이 다른 페이지가 세 곳"]
y=200
for i,t in enumerate(pts,1):
    d.ellipse([60,y,130,y+70],fill=c(GOLD)); d.text((95,y+35),str(i),font=load_font('extrabold',40),fill=c("#FFFFFF"),anchor='mm')
    d.text((160,y+35),t,font=load_font('bold',21),fill=c(NAVY),anchor='lm'); y+=190
im.save(f'{OUT}/07_{K}_핵심정리.png')
print('ok')
