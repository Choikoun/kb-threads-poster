import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/2026-10-07_배당소득세'
print(search_pexels_photo('business owner reviewing financial statements office', output_path=f'{OUT}/01_배당소득세_대표이미지.jpg', orientation='landscape'))
print(search_pexels_photo('couple walking together sunset calm', output_path=f'{OUT}/05_배당소득세_클로징삽화.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
body=load_font('regular',28); small=load_font('regular',24)
im,d=canvas(1000)
d.text((60,55),"금융소득 2천만 원이 경계선",font=load_font('extrabold',40),fill=c(NAVY))
d.text((60,120),"이자소득과 배당소득을 합친 연간 금액 기준",font=body,fill=c(GRAY))
rows=[("연 2천만 원 이하","15.4% 원천징수로 끝 (분리과세)",GREEN),
      ("2천만 원 초과분","다른 소득과 합산해 종합과세 (6~45%)",RED),
      ("배당소득 합산 시","10% 가산 후 같은 금액 세액공제",GOLD),
      ("직장가입자 건강보험","보수 외 소득 2천만 원 초과분에 보험료 추가",NAVY)]
y=190
for k,v,col in rows:
    d.rectangle([60,y,W-60,y+170],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((100,y+55),k,font=load_font('bold',32),fill=c(NAVY),anchor='lm')
    d.text((100,y+115),"→ "+v,font=load_font('extrabold',32),fill=c(col),anchor='lm')
    y+=195
im.save(f'{OUT}/02_배당소득세_구조도.png')
im,d=canvas(900)
d.text((60,55),"배당 1억 원, 누가 받느냐에 따라",font=load_font('extrabold',40),fill=c(NAVY))
d.text((60,120),"대표 다른 소득 과세표준 1.5억 가정 · 지방소득세 포함 단순 계산",font=small,fill=c(GRAY))
cols=[("대표 혼자 수령",["대표 1억 원","2천만 원 분리과세","8천만 원 종합과세","세금 약 3,100만 원"],RED),
      ("가족 4인 분산",["대표 4천만 · 배우자 2천만","자녀 2천만 × 2","종합과세는 대표 2천만 원분만","세금 약 1,900만 원"],GREEN)]
x=60
for title,lines,col in cols:
    d.rectangle([x,200,x+500,740],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((x+250,250),title,font=load_font('extrabold',36),fill=c(col),anchor='mm')
    yy=330
    for i,l in enumerate(lines):
        f=load_font('extrabold',36) if i==3 else load_font('regular',28)
        d.text((x+30,yy),l,font=f,fill=c(col if i==3 else NAVY)); yy+=90
    x+=580
d.text((60,790),"약 1,200만 원 차이 (지분 이전에 드는 증여 비용은 별도)",font=load_font('bold',28),fill=c(RED))
im.save(f'{OUT}/03_배당소득세_비교표.png')
