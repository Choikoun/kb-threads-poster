from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
OUT='blog_images/2026-10-17_즉시연금1억'
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D"
W=1200; c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
sub=load_font('bold',32); body=load_font('regular',28); small=load_font('regular',24); big=load_font('extrabold',40)
def box(d,y,h,col,left,right=None,lsize=36):
    d.rectangle([90,y,W-90,y+h],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((130,y+h//2),left,font=load_font('extrabold',lsize),fill=c(col),anchor='lm')
    if right: d.text((W-130,y+h//2),right,font=body,fill=c(NAVY),anchor='rm')
# 01 대표
im,d=canvas(900)
d.rectangle([0,0,W,14],fill=c(GOLD))
d.text((70,230),"즉시연금1억",font=load_font('extrabold',92),fill=c(NAVY))
d.text((70,360),"월 수령액보다 먼저",font=load_font('extrabold',64),fill=c(NAVY))
d.text((70,450),"비과세 조건",font=load_font('extrabold',100),fill=c(GOLD))
d.text((70,620),"일시납 1억 이하 · 10년 이상 유지",font=sub,fill=c(GRAY))
im.save(f'{OUT}/01_즉시연금1억_대표이미지.png')
# 02 비과세 조건
im,d=canvas(780)
d.text((60,55),"일시납 저축성보험 비과세 조건",font=big,fill=c(NAVY))
d.text((60,120),"가입 시점에 따라 요건이 다를 수 있습니다",font=body,fill=c(GRAY))
box(d,200,120,NAVY,"보험료 합계","1억원 이하"); box(d,350,120,GREEN,"유지 기간","10년 이상"); box(d,500,120,GOLD,"합산 기준","계약자 1인 전체")
d.text((90,670),"여러 보험사에 나눠 넣어도 합쳐서 판단합니다",font=small,fill=c(GRAY))
im.save(f'{OUT}/02_즉시연금1억_비과세조건.png')
# 03 수령 계산
im,d=canvas(860)
d.text((60,55),"상속형 1억의 단순 가정 계산",font=big,fill=c(NAVY))
d.text((60,120),"공시이율 연 3% 가정, 사업비 등 미반영",font=body,fill=c(GRAY))
box(d,200,120,NAVY,"원금","1억원 (유지)"); box(d,350,120,GREEN,"연 수령","300만원"); box(d,500,120,GOLD,"월 수령","25만원")
d.text((90,670),"실제 월 수령액은 이보다 적습니다",font=sub,fill=c(RED))
d.text((90,730),"2027년 평균공시이율 2.50% → 2.25% (보도 기준)",font=small,fill=c(GRAY))
im.save(f'{OUT}/03_즉시연금1억_수령계산.png')
# 04 핵심정리
im,d=canvas(780)
d.text((60,55),"핵심 정리",font=big,fill=c(NAVY))
for i,(k,v,col) in enumerate([("1","비과세 선은 일시납 1억 이하, 10년 유지",NAVY),("2","수령 방식에 따라 월 수령액이 달라짐",GOLD),("3","한도·수령 방식·해지 조건 먼저 확인",GREEN)]):
    box(d,160+i*190,150,col,k,None,44); d.text((220,160+i*190+75),v,font=sub,fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/04_즉시연금1억_핵심정리.png')
print('ok')
