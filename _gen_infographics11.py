from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
OUT='blog_images/2026-10-19_311간편보험'
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D"
W=1200; c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
sub=load_font('bold',32); body=load_font('regular',28); small=load_font('regular',24); big=load_font('extrabold',40)
def box(d,y,h,col,left,right=None,lsize=36):
    d.rectangle([90,y,W-90,y+h],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((130,y+h//2),left,font=load_font('extrabold',lsize),fill=c(col),anchor='lm')
    if right: d.text((W-130,y+h//2),right,font=body,fill=c(NAVY),anchor='rm')
# 01
im,d=canvas(900)
d.rectangle([0,0,W,14],fill=c(GOLD))
d.text((70,230),"311간편보험",font=load_font('extrabold',92),fill=c(NAVY))
d.text((70,360),"치료 후 1년이면",font=load_font('extrabold',64),fill=c(NAVY))
d.text((70,450),"달라지는 질문",font=load_font('extrabold',100),fill=c(GOLD))
d.text((70,620),"3개월 · 1년 · 1년, 세 묶음의 고지 질문",font=sub,fill=c(GRAY))
im.save(f'{OUT}/01_311간편보험_대표이미지.png')
# 02 비교
im,d=canvas(1120)
d.text((60,55),"고지 질문 기간 비교",font=big,fill=c(NAVY))
d.text((60,120),"3·2·5는 금융감독원 안내 기준, 3.1.1은 상품에 따라 다름",font=body,fill=c(GRAY))
d.text((130,200),"기존 간편보험 (3·2·5)",font=sub,fill=c(GRAY))
box(d,245,100,NAVY,"3개월","입원·수술·추가검사 소견"); box(d,365,100,NAVY,"2년","입원·수술"); box(d,485,100,RED,"5년","암 등 주요 질병")
d.text((130,640),"311 간편보험",font=sub,fill=c(GRAY))
box(d,685,100,NAVY,"3개월","입원·수술·추가검사 소견"); box(d,805,100,NAVY,"1년","입원·수술")
d.rectangle([90,925,W-90,1025],fill=c("#FFFFFF"),outline=c(GREEN),width=4)
d.text((130,975),"1년",font=load_font('extrabold',36),fill=c(GREEN),anchor='lm'); d.text((W-130,975),"암 등 주요 질병",font=body,fill=c(NAVY),anchor='rm')
im.save(f'{OUT}/02_311간편보험_질문비교.png')
# 03 사례
im,d=canvas(900)
d.text((60,55),"A씨(가정) 고지 질문 점검",font=big,fill=c(NAVY))
d.text((60,120),"암 수술 후 14개월 경과 가정 · 실제 가능 여부는 상품·심사에 따라 다름",font=small,fill=c(GRAY))
box(d,200,120,GOLD,"3개월","추가검사 소견은 상품 정의 확인",34)
box(d,350,120,GREEN,"1년","입원·수술: 해당 없음",34)
box(d,500,120,GREEN,"1년","주요 질병: 해당 없음",34)
d.text((90,690),"고지에서 빠질 수 있어도 가입이 보장되는 것은 아닙니다",font=sub,fill=c(RED))
d.text((90,745),"인수 심사 · 보험료 · 보장 제한은 별개입니다",font=small,fill=c(GRAY))
im.save(f'{OUT}/03_311간편보험_사례점검.png')
# 04
im,d=canvas(780)
d.text((60,55),"핵심 정리",font=big,fill=c(NAVY))
for i,(k,v,col) in enumerate([("1","311은 3개월·1년·1년 세 묶음 질문",NAVY),("2","치료 후 1년 = 가입 보장이 아님",RED),("3","일반보험 가능 여부부터 확인",GREEN)]):
    box(d,160+i*190,150,col,k,None,44); d.text((220,160+i*190+75),v,font=sub,fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/04_311간편보험_핵심정리.png')
print('ok')
