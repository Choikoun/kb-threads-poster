from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
OUT='blog_images/2026-10-22_가수금뜻'
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
d.text((70,230),"가수금뜻",font=load_font('extrabold',110),fill=c(NAVY))
d.text((70,400),"대표가 넣은 돈이",font=load_font('extrabold',68),fill=c(NAVY))
d.text((70,500),"회사엔 빚이 되는 이유",font=load_font('extrabold',84),fill=c(GOLD))
d.text((70,680),"국세청 회신과 보도 기준으로 정리",font=sub,fill=c(GRAY))
im.save(f'{OUT}/01_가수금뜻_대표이미지.png')
# 02 비교
im,d=canvas(860)
d.text((60,55),"가수금과 가지급금, 방향이 반대입니다",font=big,fill=c(NAVY))
d.text((60,120),"같은 사람 사이의 돈이어도 계정이 다릅니다",font=body,fill=c(GRAY))
box(d,200,170,GOLD,"가수금","대표 → 회사 · 회사가 갚을 돈(부채)",32)
box(d,400,170,RED,"가지급금","회사 → 대표 · 회사가 받을 돈(채권)",32)
d.text((90,620),"두 계정은 한 쌍으로 같이 따져 봅니다",font=sub,fill=c(NAVY))
d.text((90,675),"같은 사람이면 상계해 계산하는 것이 원칙이라는 회신이 있습니다",font=small,fill=c(GRAY))
im.save(f'{OUT}/02_가수금뜻_가지급금비교.png')
# 03 부채비율
im,d=canvas(860)
d.text((60,55),"가수금이 부채비율에 미치는 영향",font=big,fill=c(NAVY))
d.text((60,120),"A씨(가정) · 자기자본 5억 원 · 구조 설명용",font=body,fill=c(GRAY))
box(d,200,130,NAVY,"가수금 없음","부채 5억 → 부채비율 100%",34)
box(d,360,130,RED,"가수금 3억 추가","부채 8억 → 부채비율 160%",34)
d.text((90,560),"돈이 새로 생긴 것이 아니라 갚을 돈이 드러난 것",font=sub,fill=c(NAVY))
d.text((90,615),"금융기관 대출·입찰에서 불리해질 수 있습니다",font=small,fill=c(GRAY))
im.save(f'{OUT}/03_가수금뜻_부채비율.png')
# 04 확인표
im,d=canvas(900)
d.text((60,55),"이자와 세금은 확인이 필요한 부분",font=big,fill=c(NAVY))
d.text((60,120),"자료마다 설명이 달라 단정하지 않았습니다",font=body,fill=c(GRAY))
box(d,200,120,GOLD,"이자 지급","자료마다 설명이 다름",32)
box(d,345,120,RED,"연 4.6%","가지급금 인정이자 규정 · 가수금 적용 미확인",28)
box(d,490,120,NAVY,"상계","1999·2000년 회신 · 현행 확인 필요",30)
d.text((90,690),"세무사와 사실관계를 같이 확인하세요",font=sub,fill=c(NAVY))
im.save(f'{OUT}/04_가수금뜻_이자세금확인.png')
# 05
im,d=canvas(780)
d.text((60,55),"핵심 정리",font=big,fill=c(NAVY))
for i,(k,v,col) in enumerate([("1","가수금은 회사가 갚을 부채",NAVY),("2","부채비율·이자·상속 문제가 따라옴",RED),("3","상계와 이자 처리부터 확인",GREEN)]):
    box(d,160+i*190,150,col,k,None,44); d.text((220,160+i*190+75),v,font=sub,fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/05_가수금뜻_핵심정리.png')
print('ok')
