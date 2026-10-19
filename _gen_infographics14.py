from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
OUT='blog_images/2026-10-21_일시납달러연금보험'
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
d.text((70,200),"일시납달러연금보험",font=load_font('extrabold',86),fill=c(NAVY))
d.text((70,360),"1억 넣기 전에 확인할",font=load_font('extrabold',64),fill=c(NAVY))
d.text((70,450),"환율 세 지점",font=load_font('extrabold',100),fill=c(GOLD))
d.text((70,640),"금감원 소비자경보(2026.1.15) 내용을 보도 기준으로 정리",font=sub,fill=c(GRAY))
im.save(f'{OUT}/01_일시납달러연금보험_대표이미지.png')
# 02 경보
im,d=canvas(860)
d.text((60,55),"금감원 소비자경보 핵심",font=big,fill=c(NAVY))
d.text((60,120),"2026년 1월 15일 · 언론 보도 기준",font=body,fill=c(GRAY))
box(d,200,120,RED,"환테크 아님","일반 보장성 보험과 같은 성격",32)
box(d,345,120,GOLD,"전액 투자 아님","납입보험료 전부가 투자되지 않음",32)
box(d,490,120,NAVY,"판매 급증","2023년 1.2만 건 → 2025년 1~10월 9.5만 건",30)
d.text((90,690),"환차익만 강조하면 불완전판매로 이어질 수 있음",font=small,fill=c(GRAY))
im.save(f'{OUT}/02_일시납달러연금보험_경보내용.png')
# 03 환율 세 지점
im,d=canvas(980)
d.text((60,55),"환율이 영향을 주는 세 지점",font=big,fill=c(NAVY))
d.text((60,120),"A씨(가정) 1억 원 · 환율 1,400원 → 약 7만 1,400달러",font=body,fill=c(GRAY))
box(d,200,100,NAVY,"1 넣을 때","일시납 환전 1회",32)
box(d,320,100,NAVY,"2 받을 때","연금 받을 때마다 환전",32)
box(d,440,100,NAVY,"3 해지할 때","해지환급금도 그때 환율",32)
d.text((90,610),"달러 금액이 같아도 원화는 달라집니다",font=sub,fill=c(NAVY))
box(d,680,100,RED,"환율 1,200원","약 8,570만 원",32)
box(d,800,100,GREEN,"환율 1,600원","약 1억 1,430만 원",32)
d.text((90,935),"환율은 설명용 가정 · 이자와 사업비 제외",font=small,fill=c(GRAY))
im.save(f'{OUT}/03_일시납달러연금보험_환율세지점.png')
# 04 금리 해지
im,d=canvas(780)
d.text((60,55),"환율 말고 두 가지 변수",font=big,fill=c(NAVY))
d.text((60,120),"금감원 안내 기준",font=body,fill=c(GRAY))
box(d,200,130,GOLD,"해외 금리 하락","보험금·해약환급금 감소 가능",32)
box(d,360,130,RED,"중도 해지","환급금이 납입 원금에 못 미칠 수 있음",32)
d.text((90,560),"일시납은 낸 금액이 커서 차이도 커질 수 있습니다",font=sub,fill=c(NAVY))
im.save(f'{OUT}/04_일시납달러연금보험_금리해지.png')
# 05
im,d=canvas(780)
d.text((60,55),"핵심 정리",font=big,fill=c(NAVY))
for i,(k,v,col) in enumerate([("1","환율은 넣을 때·받을 때·해지할 때 영향",RED),("2","환테크 아님, 금리와 중도해지도 위험",NAVY),("3","비과세 적용은 약관과 국세청에 확인",GREEN)]):
    box(d,160+i*190,150,col,k,None,44); d.text((220,160+i*190+75),v,font=sub,fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/05_일시납달러연금보험_핵심정리.png')
print('ok')
