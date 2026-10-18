from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
OUT='blog_images/2026-10-20_톤틴연금'
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
d.text((70,230),"톤틴연금",font=load_font('extrabold',100),fill=c(NAVY))
d.text((70,380),"연금액 38% 기대,",font=load_font('extrabold',64),fill=c(NAVY))
d.text((70,470),"사망 시 환급 70%",font=load_font('extrabold',92),fill=c(GOLD))
d.text((70,650),"금융위원회 보도자료(2025.3.17) 기준",font=sub,fill=c(GRAY))
im.save(f'{OUT}/01_톤틴연금_대표이미지.png')
# 02 재분배
im,d=canvas(900)
d.text((60,55),"톤틴연금 재분배 구조",font=big,fill=c(NAVY))
d.text((60,120),"설명용 가정 · 재원 1억 원 고정",font=body,fill=c(GRAY))
box(d,200,130,NAVY,"10명","1인 월 100만 원",40)
box(d,360,130,GREEN,"7명","1인 월 138만 원",40)
d.text((90,560),"유지한 사람이 줄수록 몫이 커집니다",font=sub,fill=c(NAVY))
d.text((90,615),"반대로 말하면 일찍 떠난 사람의 몫이 이동하는 구조입니다",font=small,fill=c(GRAY))
im.save(f'{OUT}/02_톤틴연금_재분배구조.png')
# 03 사망환급
im,d=canvas(780)
d.text((60,55),"연금 개시 전 사망 시 환급",font=big,fill=c(NAVY))
d.text((60,120),"금융위원회 보도자료 기준",font=body,fill=c(GRAY))
box(d,200,130,NAVY,"기납입보험료","둘 중 큰 금액",34)
box(d,360,130,GOLD,"적립액의 70%","둘 중 큰 금액",34)
d.text((90,550),"해지 시 환급 비율은 원문에 없어 확인 불가",font=sub,fill=c(RED))
im.save(f'{OUT}/03_톤틴연금_사망환급.png')
# 04 연금액 비교
im,d=canvas(900)
d.text((60,55),"연금액 평가는 조건마다 다릅니다",font=big,fill=c(NAVY))
d.text((60,120),"서로 다른 조건에서 나온 숫자입니다",font=body,fill=c(GRAY))
box(d,200,130,GREEN,"당국 기대","같은 보험료 시 연금액 38% 상승",34)
d.text((130,380),"전문가 칼럼 한 사례 (40세 남성, 월 100만 원 10년 납입, 65세 개시)",font=small,fill=c(GRAY))
box(d,420,110,NAVY,"최저보증형","연 약 1,690만 원",34)
box(d,550,110,RED,"톤틴형","연 약 882만 원",34)
d.text((90,730),"한 사례이고 계산 가정이 공개되지 않았습니다",font=small,fill=c(GRAY))
im.save(f'{OUT}/04_톤틴연금_연금액비교.png')
# 05 환급사례
im,d=canvas(860)
d.text((60,55),"A씨(가정) 사망 시 환급",font=big,fill=c(NAVY))
d.text((60,120),"적립액 1억 원 · 구조 설명용 가정",font=body,fill=c(GRAY))
box(d,200,130,GOLD,"낸 보험료 6천만 원","환급 7천만 원",32)
box(d,360,130,NAVY,"낸 보험료 8천만 원","환급 8천만 원",32)
d.text((90,570),"적립액 70%와 낸 보험료 중 큰 금액",font=sub,fill=c(NAVY))
d.text((90,625),"실제 약관과 다를 수 있습니다",font=small,fill=c(GRAY))
im.save(f'{OUT}/05_톤틴연금_환급사례.png')
# 06
im,d=canvas(780)
d.text((60,55),"핵심 정리",font=big,fill=c(NAVY))
for i,(k,v,col) in enumerate([("1","일찍 떠난 사람의 몫을 남은 사람이 나눔",NAVY),("2","사망 시 환급 70%, 연금액 38%는 기대치",RED),("3","내 조건으로 직접 비교하기",GREEN)]):
    box(d,160+i*190,150,col,k,None,44); d.text((220,160+i*190+75),v,font=sub,fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/06_톤틴연금_핵심정리.png')
print('ok')
