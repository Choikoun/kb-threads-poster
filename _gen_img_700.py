import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/2026-10-09_700종신판매중지'
print(search_pexels_photo('insurance contract paperwork pen desk', output_path=f'{OUT}/01_700종신판매중지_대표이미지.jpg', orientation='landscape'))
print(search_pexels_photo('man thinking window calm morning coffee', output_path=f'{OUT}/05_700종신판매중지_클로징삽화.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
body=load_font('regular',28); small=load_font('regular',24)
im,d=canvas(1000)
d.text((60,55),"700종신 vs 단기납종신",font=load_font('extrabold',40),fill=c(NAVY))
d.text((60,120),"판매 여부를 가른 것은 '원금에 도달하는 시점'",font=body,fill=c(GRAY))
rows=[("700종신 (판매중지)",["보험료를 내는 도중인 약 7년 전후에","해약환급금이 낸 보험료 수준(100%)에 도달"],RED),
      ("단기납종신 (판매 계속)",["보험료 납입을 끝낸 뒤","일정 기간이 지나며 원금 수준에 도달"],GREEN)]
y=190
for k,ls,col in rows:
    d.rectangle([60,y,W-60,y+330],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((100,y+60),k,font=load_font('extrabold',38),fill=c(col),anchor='lm')
    yy=y+155
    for l in ls:
        d.text((100,yy),"· "+l,font=load_font('regular',32),fill=c(NAVY),anchor='lm'); yy+=70
    y+=370
im.save(f'{OUT}/02_700종신판매중지_구조도.png')
im,d=canvas(900)
d.text((60,55),"700종신 판매중지 일정과 내 계약",font=load_font('extrabold',40),fill=c(NAVY))
d.text((60,120),"금융당국 감독행정 공문 기준",font=body,fill=c(GRAY))
rows=[("9월 21일 18시 이후","신규 가입 설계 중단",RED),
      ("9월 28일 18시까지","그 전에 만든 설계서는 입금분까지 인정",GOLD),
      ("이미 가입한 계약","그대로 유지",GREEN),
      ("앞으로 나올 상품","7년 100% 환급·과도한 체증 구조 제한 방향",NAVY)]
y=200
for k,v,col in rows:
    d.rectangle([60,y,W-60,y+135],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((100,y+68),k,font=load_font('extrabold',34),fill=c(col),anchor='lm')
    d.text((W-100,y+68),v,font=load_font('regular',30),fill=c(NAVY),anchor='rm')
    y+=165
im.save(f'{OUT}/03_700종신판매중지_비교표.png')
