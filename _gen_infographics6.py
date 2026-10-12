from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
OUT='blog_images/2026-10-04_연금저축해지'
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";LIGHT="#E8E4DC";RED="#B5473A";GREEN="#2F7D5D"
W=1200
c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
sub=load_font('bold',32); body=load_font('regular',28); small=load_font('regular',24)
# 02: 3,300만원 해지 vs 연금
im,d=canvas(900)
d.text((60,55),"같은 3,300만원, 받는 방식에 따라 세금이 갈립니다",font=load_font('extrabold',36),fill=c(NAVY))
d.text((60,118),"원금 3,000만원 + 수익 300만원 가정",font=body,fill=c(GRAY))
cols=[("지금 해지",RED,"기타소득세 16.5%","544.5만원","손에 남는 돈 약 2,755만원"),("55세 이후 연금",GREEN,"연금소득세 5.5%","181.5만원","손에 남는 돈 약 3,118만원")]
for i,(t,col,rate,tax,left) in enumerate(cols):
    x=90+i*560
    d.rectangle([x,210,x+500,640],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((x+250,260),t,font=sub,fill=c(NAVY),anchor='mm')
    d.text((x+250,330),rate,font=body,fill=c(GRAY),anchor='mm')
    d.text((x+250,430),tax,font=load_font('extrabold',58),fill=c(col),anchor='mm')
    d.text((x+250,500),"세금",font=small,fill=c(GRAY),anchor='mm')
    d.text((x+250,580),left,font=small,fill=c(col),anchor='mm')
d.rectangle([60,690,W-60,820],fill=c(LIGHT))
d.text((90,715),"차이는 약 363만원입니다.",font=sub,fill=c(NAVY))
d.text((90,765),"급전이 필요해도 해지 전에 이 숫자부터 확인하세요.",font=body,fill=c(NAVY))
im.save(f'{OUT}/02_연금저축해지_구조도.png')
# 03: 나이별 세율
im,d=canvas(820)
d.text((60,55),"연금으로 받으면 나이에 따라 세율이 낮아집니다",font=load_font('extrabold',36),fill=c(NAVY))
d.text((60,118),"연금소득세 (지방소득세 포함)",font=body,fill=c(GRAY))
rows=[("55세~69세","5.5%",GOLD),("70세~79세","4.4%",GOLD),("80세 이상","3.3%",GREEN),("연금 외 인출(해지)","16.5%",RED)]
y=200
for name,rate,col in rows:
    d.rectangle([90,y,W-90,y+105],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((130,y+52),name,font=sub,fill=c(NAVY),anchor='lm')
    d.text((W-130,y+52),rate,font=load_font('extrabold',48),fill=c(col),anchor='rm')
    y+=125
d.rectangle([60,y+10,W-60,y+110],fill=c(LIGHT))
d.text((90,y+30),"연금 수령 요건: 가입 5년 경과, 만 55세 이후,",font=body,fill=c(NAVY))
d.text((90,y+70),"10년 이상 나누어 수령",font=body,fill=c(NAVY))
im.save(f'{OUT}/03_연금저축해지_비교표.png')
print("ok")
