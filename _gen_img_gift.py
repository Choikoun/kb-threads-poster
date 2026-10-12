import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/2026-10-14_증여세율표'
print(search_pexels_photo('parent and adult child talking home table documents', output_path=f'{OUT}/01_증여세율표_대표이미지.jpg', orientation='landscape'))
print(search_pexels_photo('calm morning window light home plant', output_path=f'{OUT}/07_증여세율표_클로징삽화.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
T=load_font('extrabold',46); S=load_font('regular',30)
def card(d,y,h,col,left,right,lf=34,rf=36):
    d.rectangle([60,y,W-60,y+h],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((100,y+h//2),left,font=load_font('bold',lf),fill=c(NAVY),anchor='lm')
    d.text((W-100,y+h//2),right,font=load_font('extrabold',rf),fill=c(col),anchor='rm')
# 02 세율표 (큰 글씨 5단)
im,d=canvas(1000)
d.text((60,55),"증여세율은 공제 후 금액에 적용됩니다",font=T,fill=c(NAVY))
d.text((60,125),"과세표준 기준 5단계 · 산출세액 = 과세표준 × 세율 − 누진공제",font=S,fill=c(GRAY))
rows=[("1억 이하","10% (공제 없음)",GREEN),("1억 ~ 5억","20% (공제 1천만 원)",GREEN),("5억 ~ 10억","30% (공제 6천만 원)",GOLD),("10억 ~ 30억","40% (공제 1억 6천만 원)",RED),("30억 초과","50% (공제 4억 6천만 원)",RED)]
y=200
for l,r,col in rows:
    card(d,y,130,col,l,r,34,34); y+=150
im.save(f'{OUT}/02_증여세율표_세율구간.png')
# 03 공제 한도
im,d=canvas(900)
d.text((60,55),"관계별 증여재산공제 (10년 합산)",font=T,fill=c(NAVY))
d.text((60,125),"받는 사람 기준, 같은 관계의 증여자를 합쳐서 계산",font=S,fill=c(GRAY))
rows=[("배우자","6억 원",GREEN),("부모·조부모 → 자녀","5천만 원 (미성년 2천만 원)",NAVY),("자녀 → 부모","5천만 원",NAVY),("4촌 이내 혈족·3촌 이내 인척","1천만 원",GOLD)]
y=200
for l,r,col in rows:
    card(d,y,130,col,l,r,30,34); y+=155
im.save(f'{OUT}/03_증여세율표_공제한도.png')
# 04 사례
im,d=canvas(1000)
d.text((60,55),"성년 자녀가 처음 받는 경우 세액",font=T,fill=c(NAVY))
d.text((60,125),"공제 5천만 원 적용, 신고세액공제 전 · 구조 설명용 계산",font=S,fill=c(GRAY))
rows=[("1억 원 증여","과세표준 5천만 → 500만 원",GREEN),("3억 원 증여","과세표준 2.5억 → 4,000만 원",GOLD),("5억 원 증여","과세표준 4.5억 → 8,000만 원",GOLD),("15억 원 증여","과세표준 14.5억 → 4.2억 원",RED)]
y=200
for l,r,col in rows:
    card(d,y,150,col,l,r,34,32); y+=185
im.save(f'{OUT}/04_증여세율표_세액사례.png')
# 05 혼인출산
im,d=canvas(900)
d.text((60,55),"혼인·출산 공제를 더하면",font=T,fill=c(NAVY))
d.text((60,125),"직계존속 증여 · 2024.1.1 이후 증여분",font=S,fill=c(GRAY))
rows=[("기본 공제","5천만 원",NAVY),("혼인·출산 추가 공제","최대 1억 원 (합산 평생)",GREEN),("성년 자녀 최대","1억 5천만 원",RED)]
y=200
for l,r,col in rows:
    card(d,y,140,col,l,r,34,34); y+=165
d.text((60,y+10),"혼인신고일 전후 2년, 출산·입양 후 2년 이내 증여",font=S,fill=c(GRAY))
im.save(f'{OUT}/05_증여세율표_혼인출산공제.png')
# 06 핵심정리 카드
im,d=canvas(900)
d.text((60,55),"핵심 정리",font=load_font('extrabold',54),fill=c(NAVY))
items=["세율 10~50%는 증여액이 아니라\n공제를 뺀 과세표준에 적용됩니다","공제는 받는 사람 기준,\n같은 관계는 10년 합산입니다","혼인·출산 추가 공제는 평생 1억 원,\n성년 자녀는 최대 1억 5천만 원입니다"]
y=170
for i,t in enumerate(items,1):
    d.rectangle([60,y,W-60,y+190],fill=c("#FFFFFF"),outline=c(GOLD),width=4)
    d.text((110,y+95),str(i),font=load_font('extrabold',70),fill=c(GOLD),anchor='lm')
    d.multiline_text((190,y+95),t,font=load_font('bold',34),fill=c(NAVY),anchor='lm',spacing=10)
    y+=220
im.save(f'{OUT}/06_증여세율표_핵심정리.png')
