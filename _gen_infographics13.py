from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
OUT='blog_images/2026-10-21_달러종신보험'
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
d.text((70,230),"달러종신보험",font=load_font('extrabold',92),fill=c(NAVY))
d.text((70,380),"금감원 소비자경보 주의",font=load_font('extrabold',64),fill=c(NAVY))
d.text((70,470),"환테크 상품 아님",font=load_font('extrabold',100),fill=c(GOLD))
d.text((70,650),"2026.1.15 경보 내용을 보도 기준으로 정리",font=sub,fill=c(GRAY))
im.save(f'{OUT}/01_달러종신보험_대표이미지.png')
# 02 경보 내용
im,d=canvas(860)
d.text((60,55),"금감원 소비자경보 핵심",font=big,fill=c(NAVY))
d.text((60,120),"2026년 1월 15일 · 언론 보도 기준",font=body,fill=c(GRAY))
box(d,200,120,RED,"환테크 아님","일반 보장성 보험과 같은 성격",32)
box(d,345,120,GOLD,"전액 투자 아님","납입보험료 전부가 투자되지 않음",32)
box(d,490,120,NAVY,"위험 설명","환율·금리 변동 위험 이해",32)
d.text((90,690),"환차익만 강조하면 불완전판매로 이어질 수 있음",font=small,fill=c(GRAY))
im.save(f'{OUT}/02_달러종신보험_경보내용.png')
# 03 판매건수 막대
im,d=canvas(780)
d.text((60,55),"달러보험 판매 건수",font=big,fill=c(NAVY))
d.text((60,120),"금감원 공개 수치 · 2025년은 1~10월",font=body,fill=c(GRAY))
vals=[("2023년",11977,NAVY),("2024년",40594,GOLD),("2025년 1~10월",95421,RED)]
mx=95421
for i,(k,v,col) in enumerate(vals):
    y=210+i*150
    d.text((90,y+35),k,font=sub,fill=c(NAVY),anchor='lm')
    w=int(700*v/mx)
    d.rectangle([330,y,330+w,y+70],fill=c(col))
    d.text((330+w+15,y+35),f"{v:,}건",font=sub,fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/03_달러종신보험_판매건수.png')
# 04 환율 사례
im,d=canvas(860)
d.text((60,55),"A씨(가정) 사망보험금 10만 달러",font=big,fill=c(NAVY))
d.text((60,120),"환율은 설명용 가정이며 전망이 아닙니다",font=body,fill=c(GRAY))
box(d,200,130,NAVY,"환율 1,400원","1억 4,000만 원",34)
box(d,360,130,RED,"환율 1,200원","1억 2,000만 원",34)
d.text((90,570),"달러 금액은 같아도 원화는 2,000만 원 차이",font=sub,fill=c(NAVY))
d.text((90,625),"실제 환율 적용 방식은 약관과 지급 시점에 따라 다릅니다",font=small,fill=c(GRAY))
im.save(f'{OUT}/04_달러종신보험_환율사례.png')
# 05 목적 비교
im,d=canvas(860)
d.text((60,55),"목적에 따라 다른 그릇",font=big,fill=c(NAVY))
d.text((60,120),"외화예금 보호 여부는 상품설명서로 확인",font=body,fill=c(GRAY))
box(d,200,150,GOLD,"달러 통장·예금","환율에 따라 원화 가치 변동, 필요할 때 인출",30)
box(d,380,150,NAVY,"달러 종신보험","사망 보장 중심, 납입보험료 전액 투자 아님",30)
d.text((90,610),"환율 대비가 목적인지 보장이 목적인지 먼저 정하기",font=sub,fill=c(RED))
im.save(f'{OUT}/05_달러종신보험_목적비교.png')
# 06
im,d=canvas(780)
d.text((60,55),"핵심 정리",font=big,fill=c(NAVY))
for i,(k,v,col) in enumerate([("1","환테크 상품 아님, 전액 투자도 아님",RED),("2","환율·금리·중도해지 모두 변수",NAVY),("3","목적부터 정하고 설명서로 확인",GREEN)]):
    box(d,160+i*190,150,col,k,None,44); d.text((220,160+i*190+75),v,font=sub,fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/06_달러종신보험_핵심정리.png')
print('ok')
