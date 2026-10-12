import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/shop_2026-10-12_가열식가습기'
print(search_pexels_photo('humidifier steam bedroom cozy', output_path=f'{OUT}/01_가열식가습기_대표이미지.jpg', orientation='landscape'))
print(search_pexels_photo('winter morning living room warm home', output_path=f'{OUT}/05_가열식가습기_클로징.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
body=load_font('regular',28); small=load_font('regular',24)
# 02 방식별 비교
im,d=canvas(1060)
d.text((60,55),"가습기 13개 비교시험 결과",font=load_font('extrabold',40),fill=c(NAVY))
d.text((60,120),"한국소비자원 · 2025년 10월 30일 발표",font=body,fill=c(GRAY))
rows=[("가습량 (시간당)","182 ~ 606ml",NAVY),("가열식 연간 유지관리비","72,750 ~ 91,070원",RED),("초음파식 연간 유지관리비","4,640 ~ 6,420원",GREEN),("가열식 끓는 동안 소음","52 ~ 55dB",GOLD),("가열식 증기 온도","약 99도",RED)]
y=190
for k,v,col in rows:
    d.rectangle([60,y,W-60,y+140],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((100,y+70),k,font=load_font('bold',34),fill=c(NAVY),anchor='lm')
    d.text((W-100,y+70),v,font=load_font('extrabold',40),fill=c(col),anchor='rm')
    y+=165
im.save(f'{OUT}/02_가열식가습기_시험결과.png')
# 03 화상 통계
im,d=canvas(900)
d.text((60,55),"가열식 가습기 화상 사고 건수",font=load_font('extrabold',40),fill=c(NAVY))
d.text((60,120),"한국소비자원 · 2024년 2월 발표 (2023년은 10월까지)",font=small,fill=c(GRAY))
data=[("2020",6),("2021",16),("2022",23),("2023",47)]
base=760;x=140
for yr,n in data:
    h=n*11
    d.rectangle([x,base-h,x+160,base],fill=c(RED if yr=="2023" else GOLD))
    d.text((x+80,base-h-30),f"{n}건",font=load_font('extrabold',34),fill=c(NAVY),anchor='mm')
    d.text((x+80,base+30),yr,font=load_font('bold',30),fill=c(GRAY),anchor='mm')
    x+=250
d.text((60,840),"화상 92건 중 만 6세 이하가 77.2%",font=load_font('bold',30),fill=c(RED))
im.save(f'{OUT}/03_가열식가습기_화상통계.png')
