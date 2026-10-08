import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/shop_2026-10-08_탄소매트'
print(search_pexels_photo('cozy bed warm blanket bedroom winter', output_path=f'{OUT}/01_탄소매트_대표이미지.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
body=load_font('regular',28); small=load_font('regular',24)
im,d=canvas(1060)
d.text((60,55),"탄소매트 10개 비교시험 결과",font=load_font('extrabold',40),fill=c(NAVY))
d.text((60,120),"한국소비자원 비교공감 2025-22호 · 제품별 차이",font=body,fill=c(GRAY))
rows=[("최대 표면온도","39 ~ 64℃",NAVY),("위치별 온도편차","0.4 ~ 10.5℃",GOLD),("발열속도 (20→35℃)","12 ~ 49분",RED),("머리부 열선 없는 제품","10개 중 4개",GREEN),("전자파·감전 안전성","10개 모두 적합",GREEN)]
y=190
for k,v,col in rows:
    d.rectangle([60,y,W-60,y+140],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((100,y+70),k,font=load_font('bold',34),fill=c(NAVY),anchor='lm')
    d.text((W-100,y+70),v,font=load_font('extrabold',40),fill=c(col),anchor='rm')
    y+=165
im.save(f'{OUT}/02_탄소매트_시험결과.png')
im,d=canvas(900)
d.text((60,55),"저가형 vs 중·고가형, 무엇이 다를까",font=load_font('extrabold',40),fill=c(NAVY))
d.text((60,120),"소비자원 시험 제품 기준 (10개 중 저가 4개 · 중·고가 6개)",font=small,fill=c(GRAY))
cols=[("저가형 (약 3만~7만 원대)",["평균 발열속도 19분","기본 발열 위주"],GOLD),("중·고가형 (약 15만~36만 원대)",["평균 발열속도 34분","에러표시·타이머 등 부가기능"],NAVY)]
x=60
for title,lines,col in cols:
    d.rectangle([x,200,x+500,640],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((x+250,255),title,font=load_font('extrabold',30),fill=c(col),anchor='mm')
    yy=350
    for l in lines:
        d.text((x+30,yy),"· "+l,font=load_font('regular',30),fill=c(NAVY)); yy+=90
    x+=580
d.text((60,690),"발열은 저가형이 약 1.8배 빠르고, 부가기능은 중·고가형이 많았습니다",font=load_font('bold',28),fill=c(RED))
im.save(f'{OUT}/03_탄소매트_가격대비교.png')
