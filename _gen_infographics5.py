from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
OUT='blog_images/2026-10-03_며느리증여'
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";LIGHT="#E8E4DC";RED="#B5473A";GREEN="#2F7D5D"
W=1200
def canvas(h):
    im=Image.new('RGB',(W,h),hex_to_rgb(BG)); return im, ImageDraw.Draw(im)
sub=load_font('bold',32); body=load_font('regular',28); small=load_font('regular',24)
c=lambda x:hex_to_rgb(x)
# 02 구조도: 관계별 공제
im,d=canvas(900)
d.text((60,55),"받는 사람에 따라 공제 한도가 갈립니다",font=load_font('extrabold',38),fill=c(NAVY))
d.text((60,115),"10년간 합산, 받는 사람 기준 증여재산공제",font=body,fill=c(GRAY))
rows=[("배우자","6억원",GREEN),("아들·딸 (직계비속)","5천만원",GREEN),("며느리·사위 (기타친족)","1천만원",RED)]
y=200
for name,amt,col in rows:
    d.rectangle([90,y,W-90,y+150],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((130,y+75),name,font=sub,fill=c(NAVY),anchor='lm')
    d.text((W-130,y+75),amt,font=load_font('extrabold',52),fill=c(col),anchor='rm')
    y+=185
d.rectangle([60,y+10,W-60,y+120],fill=c(LIGHT))
d.text((90,y+35),"며느리는 혼인으로 맺어진 1촌 인척이라",font=body,fill=c(NAVY))
d.text((90,y+75),"아들 공제의 5분의 1만 적용됩니다.",font=body,fill=c(NAVY))
im.save(f'{OUT}/02_며느리증여_구조도.png')
# 03 비교표
im,d=canvas(900)
d.text((60,55),"같은 금액, 받는 사람에 따라 세금이 갈립니다",font=load_font('extrabold',36),fill=c(NAVY))
d.text((60,118),"부모가 보내는 경우, 10% 구간 기준",font=body,fill=c(GRAY))
cols=[("아들",GREEN,"0원","500만원"),("며느리",RED,"400만원","900만원")]
x0=90
for i,(who,col,t5,t10) in enumerate(cols):
    x=x0+i*560
    d.rectangle([x,210,x+500,600],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((x+250,255),who,font=sub,fill=c(NAVY),anchor='mm')
    d.text((x+250,330),"5천만원 증여",font=body,fill=c(GRAY),anchor='mm')
    d.text((x+250,395),t5,font=load_font('extrabold',54),fill=c(col),anchor='mm')
    d.text((x+250,475),"1억원 증여",font=body,fill=c(GRAY),anchor='mm')
    d.text((x+250,540),t10,font=load_font('extrabold',54),fill=c(col),anchor='mm')
d.rectangle([60,650,W-60,790],fill=c(LIGHT))
d.text((90,675),"신고세액공제(3%) 전 금액이며, 기한 내 신고 시",font=body,fill=c(NAVY))
d.text((90,725),"산출세액의 3%를 깎아줍니다.",font=body,fill=c(NAVY))
im.save(f'{OUT}/03_며느리증여_비교표.png')
print("ok")
