from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
OUT='blog_images/2026-10-25_66년생국민연금수령나이'
P='66년생국민연금수령나이'
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D"
W=1200; c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
sub=load_font('bold',32); body=load_font('regular',28); small=load_font('regular',24); big=load_font('extrabold',40)
def box(d,y,h,col,left,right=None,lsize=36):
    d.rectangle([90,y,W-90,y+h],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((130,y+h//2),left,font=load_font('extrabold',lsize),fill=c(col),anchor='lm')
    if right: d.text((W-130,y+h//2),right,font=body,fill=c(NAVY),anchor='rm')
im,d=canvas(900)
d.rectangle([0,0,W,14],fill=c(GOLD))
d.text((70,230),"66년생",font=load_font('extrabold',110),fill=c(NAVY))
d.text((70,380),"국민연금수령나이",font=load_font('extrabold',84),fill=c(NAVY))
d.text((70,500),"64세, 조기는 59세",font=load_font('extrabold',84),fill=c(GOLD))
d.text((70,680),"국민연금공단 안내 기준으로 정리",font=sub,fill=c(GRAY))
im.save(f'{OUT}/01_{P}_대표이미지.png')
im,d=canvas(960)
d.text((60,55),"조기 수령 시 지급률(66년생 기준)",font=big,fill=c(NAVY))
d.text((60,120),"받는 나이가 빠를수록 평생 금액이 줄어듭니다",font=body,fill=c(GRAY))
rows=[("59세","70%",RED),("60세","76%",RED),("61세","82%",GOLD),("62세","88%",GOLD),("63세","94%",GREEN)]
for i,(a,b,col) in enumerate(rows):
    box(d,190+i*120,100,col,a,b,34)
d.text((90,820),"64세 정상 수령이 100%",font=sub,fill=c(NAVY))
im.save(f'{OUT}/02_{P}_조기지급률.png')
im,d=canvas(860)
d.text((60,55),"월 100만 원 가정, 받는 시기별 월 연금",font=big,fill=c(NAVY))
d.text((60,120),"설명용 가정 · 정상 수령 연금이 월 100만 원일 때",font=body,fill=c(GRAY))
box(d,200,130,RED,"59세 조기","월 70만 원 (30% 감액)",34)
box(d,360,130,NAVY,"64세 정상","월 100만 원",34)
box(d,520,130,GREEN,"69세 연기","월 136만 원 (5년, 36% 증가)",34)
d.text((90,730),"한 번 정해진 비율은 평생 이어집니다",font=sub,fill=c(NAVY))
im.save(f'{OUT}/03_{P}_월100만가정.png')
im,d=canvas(860)
d.text((60,55),"받는 시기별 따라잡는 데 걸리는 기간",font=big,fill=c(NAVY))
d.text((60,120),"필자의 단순 계산 · 물가 연동·세금·건보료 제외",font=body,fill=c(GRAY))
box(d,200,150,RED,"조기 → 정상","64세부터 약 11년 8개월 (75세 후반)",34)
box(d,390,150,GREEN,"연기 → 정상","69세부터 약 14년 (83세 즈음)",34)
d.text((90,610),"공단이 안내한 수치가 아닙니다",font=sub,fill=c(NAVY))
d.text((90,665),"실제는 물가 연동과 개인 사정에 따라 달라집니다",font=small,fill=c(GRAY))
im.save(f'{OUT}/04_{P}_손익분기가정.png')
im,d=canvas(900)
d.text((60,55),"소득이 있으면 5년 동안 감액될 수 있습니다",font=big,fill=c(NAVY))
d.text((60,120),"기준: 월평균소득금액이 A값+200만 원 초과(2026년 약 519만 원)",font=small,fill=c(GRAY))
box(d,200,120,GOLD,"초과 200만~300만 원","15만 원 + 초과분의 15%",30)
box(d,345,120,RED,"초과 300만~400만 원","30만 원 + 초과분의 20%",30)
box(d,490,120,NAVY,"초과 400만 원 이상","50만 원 + 초과분의 25%",30)
d.text((90,690),"감액 한도는 노령연금의 절반",font=sub,fill=c(NAVY))
d.text((90,745),"어떤 소득이 어떻게 계산되는지는 공단에서 확인하세요",font=small,fill=c(GRAY))
im.save(f'{OUT}/05_{P}_소득감액.png')
im,d=canvas(780)
d.text((60,55),"핵심 정리",font=big,fill=c(NAVY))
for i,(k,v,col) in enumerate([("1","64세(2030년) · 조기는 59세",NAVY),("2","조기 연 6% 감액 · 연기 연 7.2% 증가",RED),("3","소득이 있으면 5년 감액 확인",GREEN)]):
    box(d,160+i*190,150,col,k,None,44); d.text((220,160+i*190+75),v,font=sub,fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/06_{P}_핵심정리.png')
print('ok')
