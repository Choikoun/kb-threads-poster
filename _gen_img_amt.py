import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/shop_2026-10-15_AMT사각팬'; K='AMT사각팬'
print(search_pexels_photo('stainless steel square frying pan stove kitchen', output_path=f'{OUT}/01_{K}_대표이미지.jpg', orientation='landscape'))
print(search_pexels_photo('warm kitchen dinner table home cooking', output_path=f'{OUT}/07_{K}_클로징.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
body=load_font('regular',28)
def title(d,t,s):
    d.text((60,55),t,font=load_font('extrabold',40),fill=c(NAVY)); d.text((60,120),s,font=body,fill=c(GRAY))
# 02 모델별 판매처 가격
im,d=canvas(960)
title(d,"같은 이름 모델의 판매처별 표기 가격","2026-10-15 조회 · 네이버쇼핑(브랜드 커넥트) · 쿠팡")
groups=[("프로 사각 컴바인 팬(22cm)",[("네이버 AMT 코리아",152000,GOLD),("네이버 뎀블루",146670,GOLD),("쿠팡 로켓배송",122760,GREEN)]),
        ("정사각 베스트 팬(24cm)",[("네이버 AMT 코리아",132000,GOLD),("쿠팡 로켓배송",109880,GREEN)]),
        ("가로형 사각 피쉬 팬(24cm)",[("네이버 AMT 코리아",152000,GOLD),("네이버 뎀블루",168890,GOLD),("쿠팡 목록",141360,GREEN)])]
y=190; mx=170000
for g,rows in groups:
    d.text((60,y),g,font=load_font('extrabold',32),fill=c(NAVY)); y+=55
    for k,v,col in rows:
        d.text((60,y+22),k,font=load_font('bold',24),fill=c(GRAY),anchor='lm')
        w=int((W-760)*v/mx); d.rectangle([330,y,330+w,y+44],fill=c(col))
        d.text((330+w+12,y+22),f"{v:,}원",font=load_font('extrabold',26),fill=c(NAVY),anchor='lm'); y+=62
    y+=30
im.save(f'{OUT}/02_{K}_판매처가격.png')
# 03 공개 사양
im,d=canvas(1100)
title(d,"판매처 공개 사양 정리","코오롱몰 AMT 브랜드 설명 · 코스트코 코리아 상품 페이지 표기")
rows=[("본체 두께","2.7티 (약 2.7mm)"),("구조","통5중 · 316Ti 스테인리스+알루미늄"),("무게","약 1.5kg (컴바인 팬)"),("크기","24×24×3.5cm (24cm 정사각 베스트 팬)"),("사용 열원","인덕션·가스·하이라이트·오븐"),("식기세척기 / 전자레인지","가능 / 불가")]
y=190
for k,v in rows:
    d.rectangle([60,y,W-60,y+130],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((100,y+65),k,font=load_font('bold',30),fill=c(GRAY),anchor='lm')
    d.text((W-100,y+65),v,font=load_font('extrabold',30),fill=c(NAVY),anchor='rm'); y+=150
im.save(f'{OUT}/03_{K}_공개사양.png')
# 04 모델별 네이버 정가→할인가
im,d=canvas(900)
title(d,"AMT 코리아 스토어 모델별 가격","네이버쇼핑 표기 · 정가 → 할인가(2026-10-15)")
rows=[("프로 사각 컴바인 팬 22cm","185,000원","152,000원"),("정사각 베스트 팬 24cm","165,000원","132,000원"),("가로형 사각 피쉬 팬 24cm","190,000원","152,000원"),("사각 그리들 팬(뚜껑 포함)","300,000원","240,000원")]
y=190
for k,a,b in rows:
    d.rectangle([60,y,W-60,y+140],fill=c("#FFFFFF"),outline=c(NAVY),width=3)
    d.text((100,y+70),k,font=load_font('bold',30),fill=c(NAVY),anchor='lm')
    d.text((720,y+70),a,font=load_font('regular',28),fill=c(GRAY),anchor='rm')
    d.text((760,y+70),"→",font=load_font('extrabold',30),fill=c(GOLD),anchor='mm')
    d.text((W-100,y+70),b,font=load_font('extrabold',34),fill=c(RED),anchor='rm'); y+=165
im.save(f'{OUT}/04_{K}_모델별가격.png')
# 05 체크리스트
im,d=canvas(1000)
title(d,"결제 전 확인할 6가지","같은 이름이라도 모델·크기·판매처가 다를 수 있어요")
chk=["모델명 (컴바인·베스트·피쉬·그리들)","크기 (22cm · 24cm 등)","뚜껑 포함 여부","판매처 · 정식 유통 여부","최종 결제가와 배송비","원산지 · 교환·반품 조건"]
for i,t in enumerate(chk):
    col=i%2; row=i//2; x=60+col*570; y=200+row*190
    d.rectangle([x,y,x+540,y+150],fill=c("#FFFFFF"),outline=c(GOLD),width=3)
    d.text((x+40,y+75),"□",font=load_font('extrabold',44),fill=c(GREEN),anchor='lm')
    d.text((x+110,y+75),t,font=load_font('bold',25),fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/05_{K}_확인체크리스트.png')
# 06 핵심 정리
im,d=canvas(900)
d.rectangle([0,0,W,14],fill=c(GOLD)); d.text((60,70),"핵심 정리",font=load_font('extrabold',52),fill=c(NAVY))
pts=["컴바인 팬은 네이버 152,000원 · 쿠팡 로켓 122,760원 (표기)","정사각 베스트 팬도 쿠팡 로켓이 22,120원 낮게 표기","크기·뚜껑 포함·판매처를 맞춰야 같은 모델 비교"]
y=200
for i,t in enumerate(pts,1):
    d.ellipse([60,y,130,y+70],fill=c(GOLD)); d.text((95,y+35),str(i),font=load_font('extrabold',40),fill=c("#FFFFFF"),anchor='mm')
    d.text((160,y+35),t,font=load_font('bold',28),fill=c(NAVY),anchor='lm'); y+=190
im.save(f'{OUT}/06_{K}_핵심정리.png')
