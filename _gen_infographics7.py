from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
OUT='blog_images/2026-10-05_퇴직금정산'
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";LIGHT="#E8E4DC";RED="#B5473A";GREEN="#2F7D5D"
W=1200; c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
sub=load_font('bold',32); body=load_font('regular',28); small=load_font('regular',24)
# 02 계산 한 장
im,d=canvas(900)
d.text((60,55),"퇴직금, 이렇게 계산됩니다",font=load_font('extrabold',40),fill=c(NAVY))
d.text((60,120),"월급 400만원, 3년 근무 가정",font=body,fill=c(GRAY))
steps=[("퇴직 전 3개월 임금","1,200만원",NAVY),("그 기간 총 일수","92일",NAVY),("1일 평균임금","약 13만 435원",GOLD),("× 30일 × 근속 3년","퇴직금 약 1,174만원",RED)]
y=200
for name,val,col in steps:
    d.rectangle([90,y,W-90,y+120],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((130,y+60),name,font=sub,fill=c(NAVY),anchor='lm')
    d.text((W-130,y+60),val,font=load_font('extrabold',40),fill=c(col),anchor='rm')
    y+=150
d.text((90,y+10),"상여금·연차수당은 연간 총액의 4분의 1을 더해 계산합니다.",font=small,fill=c(GRAY))
im.save(f'{OUT}/02_퇴직금정산_구조도.png')
# 03 일정
im,d=canvas(820)
d.text((60,55),"퇴사 후 지급 일정",font=load_font('extrabold',40),fill=c(NAVY))
d.text((60,120),"합의가 없으면 기한은 14일입니다",font=body,fill=c(GRAY))
rows=[("퇴사일","퇴직금 지급 의무 발생",NAVY),("14일 이내","지급 기한 (합의 시 연장 가능)",GREEN),("14일 초과","연 20% 지연이자 (1개월이면 약 19만원)",RED),("3년","청구할 수 있는 기간(소멸시효)",GOLD)]
y=200
for k,v,col in rows:
    d.rectangle([90,y,W-90,y+120],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((130,y+60),k,font=load_font('extrabold',38),fill=c(col),anchor='lm')
    d.text((420,y+60),v,font=body,fill=c(NAVY),anchor='lm')
    y+=145
im.save(f'{OUT}/03_퇴직금정산_비교표.png')
print("ok")
