import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
OUT='blog_images/2026-10-14_증여세율표'
BG="#FFFFFF";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c("#FBF9F4")); return im, ImageDraw.Draw(im)
# 세율 막대형
im,d=canvas(900)
d.text((60,50),"과세표준이 올라갈수록 세율도 올라갑니다",font=load_font('extrabold',44),fill=c(NAVY))
bars=[("1억 이하",10,GREEN),("5억 이하",20,GREEN),("10억 이하",30,GOLD),("30억 이하",40,RED),("30억 초과",50,RED)]
y=170
for lab,r,col in bars:
    d.text((60,y+40),lab,font=load_font('bold',32),fill=c(NAVY),anchor='lm')
    d.rectangle([300,y,300+r*14,y+80],fill=c(col))
    d.text((300+r*14+20,y+40),f"{r}%",font=load_font('extrabold',40),fill=c(col),anchor='lm'); y+=125
d.text((60,y+5),"세액 = 과세표준 × 세율 − 누진공제 · 국세청 안내 기준",font=load_font('regular',28),fill=c(GRAY))
im.save(f'{OUT}/02t_증여세율표_세율막대.png')
# 사례 비교(좌우 2열)
im,d=canvas(900)
d.text((60,50),"증여액 대비 세금 부담",font=load_font('extrabold',44),fill=c(NAVY))
d.text((60,120),"성년 자녀 첫 증여, 공제 5천만 원, 신고세액공제 전",font=load_font('regular',28),fill=c(GRAY))
rows=[("1억","500만 원","0.5%"),("3억","4,000만 원","13.3%"),("5억","8,000만 원","16%"),("15억","4억 2천만 원","28%")]
y=200
for a,b,pct in rows:
    d.rectangle([60,y,W-60,y+130],fill=c("#FFFFFF"),outline=c(NAVY),width=3)
    d.text((100,y+65),a+" 증여",font=load_font('bold',36),fill=c(NAVY),anchor='lm')
    d.text((560,y+65),b,font=load_font('extrabold',40),fill=c(RED),anchor='lm')
    d.text((W-100,y+65),"실부담 "+pct,font=load_font('regular',30),fill=c(GRAY),anchor='rm'); y+=155
im.save(f'{OUT}/04t_증여세율표_부담비율.png')
