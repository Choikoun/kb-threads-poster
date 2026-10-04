import sys, os
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/2026-10-06_사망보험금세금'
print(search_pexels_photo('businessman reviewing insurance documents office desk', output_path=f'{OUT}/01_사망보험금세금_대표이미지.jpg', orientation='landscape'))
print(search_pexels_photo('family walking together park calm evening', output_path=f'{OUT}/05_사망보험금세금_클로징삽화.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
body=load_font('regular',28); small=load_font('regular',24)
im,d=canvas(1020)
d.text((60,55),"사망보험금, 누가 보험료를 냈는가",font=load_font('extrabold',40),fill=c(NAVY))
d.text((60,120),"세금은 받는 사람이 아니라 낸 사람 기준으로 갈립니다",font=body,fill=c(GRAY))
rows=[("본인 계약 · 본인 피보험자","보험금 전액이 상속재산",RED),
      ("자녀 계약 · 자녀가 자기 소득으로 납부","상속세·증여세 대상 아님",GREEN),
      ("자녀 계약 · 부모가 보험료 납부","부모 납부 비율만큼 상속재산",GOLD),
      ("법인 계약 · 법인이 수령","상속재산 아님, 주식 평가에 반영",NAVY)]
y=190
for k,v,col in rows:
    d.rectangle([60,y,W-60,y+170],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((100,y+55),k,font=load_font('bold',32),fill=c(NAVY),anchor='lm')
    d.text((100,y+115),"→ "+v,font=load_font('extrabold',34),fill=c(col),anchor='lm')
    y+=195
im.save(f'{OUT}/02_사망보험금세금_구조도.png')
im,d=canvas(900)
d.text((60,55),"보험금 20억이 더해지면",font=load_font('extrabold',40),fill=c(NAVY))
d.text((60,120),"기존 재산 30억 · 배우자 있음 · 일괄공제 5억 + 배우자공제 5억 가정",font=small,fill=c(GRAY))
cols=[("보험금 없을 때",["상속재산 30억","공제 10억","과세표준 20억","산출세액 약 6.4억"],NAVY),
      ("보험금 20억 있을 때",["상속재산 50억","공제 10억","과세표준 40억","산출세액 약 15.4억"],RED)]
x=60
for title,lines,col in cols:
    d.rectangle([x,200,x+500,740],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((x+250,250),title,font=load_font('extrabold',36),fill=c(col),anchor='mm')
    yy=330
    for i,l in enumerate(lines):
        f=load_font('extrabold',38) if i==3 else load_font('regular',32)
        d.text((x+40,yy),l,font=f,fill=c(col if i==3 else NAVY)); yy+=90
    x+=580
d.text((60,790),"세금이 약 9억 늘어납니다 (그 밖의 공제·신고세액공제 제외한 단순 계산)",font=load_font('bold',28),fill=c(RED))
im.save(f'{OUT}/03_사망보험금세금_비교표.png')
