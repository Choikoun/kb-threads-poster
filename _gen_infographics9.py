from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
OUT='blog_images/2026-10-16_IRP계좌출금'
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D"
W=1200; c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
sub=load_font('bold',32); body=load_font('regular',28); small=load_font('regular',24); big=load_font('extrabold',40)
def box(d,y,h,col,left,right=None,lsize=36):
    d.rectangle([90,y,W-90,y+h],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((130,y+h//2),left,font=load_font('extrabold',lsize),fill=c(col),anchor='lm')
    if right: d.text((W-130,y+h//2),right,font=body,fill=c(NAVY),anchor='rm')
# 01 대표 (큰 숫자 중심)
im,d=canvas(900)
d.rectangle([0,0,W,14],fill=c(GOLD))
d.text((70,240),"IRP계좌출금",font=load_font('extrabold',84),fill=c(NAVY))
d.text((70,350),"사유 없이 해지하면",font=load_font('extrabold',64),fill=c(NAVY))
d.text((70,440),"세금 16.5%",font=load_font('extrabold',110),fill=c(RED))
d.text((70,620),"중도인출이 되는 법정 사유는 5가지입니다",font=sub,fill=c(GRAY))
im.save(f'{OUT}/01_IRP계좌출금_대표이미지.png')
# 02 법정 사유
im,d=canvas(1020)
d.text((60,55),"중도인출 법정 사유 5가지",font=big,fill=c(NAVY))
d.text((60,120),"금융기관 안내 2026년 9월 기준",font=body,fill=c(GRAY))
items=[("1","무주택자 주택 구입"),("2","무주택자 전세금·임차보증금"),("3","6개월 이상 요양"),("4","5년 이내 개인회생·파산"),("5","재난 피해 (3개월 내 신청)")]
y=190
for k,v in items:
    box(d,y,115,NAVY if k!="5" else GOLD,k,None,40)
    d.text((220,y+57),v,font=sub,fill=c(NAVY),anchor='lm'); y+=150
im.save(f'{OUT}/02_IRP계좌출금_법정사유.png')
# 03 해지 세금 계산
im,d=canvas(860)
d.text((60,55),"5년 납입 A씨의 해지 계산",font=big,fill=c(NAVY))
d.text((60,120),"연 900만원 × 5년, 공제율 13.2% 가정",font=body,fill=c(GRAY))
box(d,200,120,NAVY,"총 납입","4,500만원")
box(d,350,120,GREEN,"받은 환급","594만원")
box(d,500,120,RED,"해지 세금(16.5%)","742만 5천원")
d.text((90,670),"환급보다 148만 5천원을 더 냅니다 (수익 제외)",font=sub,fill=c(RED))
d.text((90,730),"가정 계산이며 실제 공제율은 소득에 따라 다릅니다",font=small,fill=c(GRAY))
im.save(f'{OUT}/03_IRP계좌출금_해지세금계산.png')
# 04 연금 세율
im,d=canvas(760)
d.text((60,55),"연금으로 받을 때 세율",font=big,fill=c(NAVY))
d.text((60,120),"만 55세 이상 · 지방소득세 포함",font=body,fill=c(GRAY))
box(d,200,120,GOLD,"55~69세","5.5%"); box(d,350,120,GOLD,"70~79세","4.4%"); box(d,500,120,GREEN,"80세 이상","3.3%")
d.text((90,660),"사적연금 연 1,500만원 초과 시 종합과세 또는 16.5% 분리과세",font=small,fill=c(GRAY))
im.save(f'{OUT}/04_IRP계좌출금_연금세율.png')
# 05 핵심정리
im,d=canvas(780)
d.text((60,55),"핵심 정리",font=big,fill=c(NAVY))
for i,(k,v,col) in enumerate([("1","중도인출은 법정 사유 5가지만",NAVY),("2","사유 없이 해지하면 16.5%",RED),("3","급하지 않으면 연금 수령이 가볍다",GREEN)]):
    box(d,160+i*190,150,col,k,None,44); d.text((220,160+i*190+75),v,font=sub,fill=c(NAVY),anchor='lm')
im.save(f'{OUT}/05_IRP계좌출금_핵심정리.png')
print('ok')
