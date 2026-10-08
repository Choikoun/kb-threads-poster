import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/2026-10-10_퇴직연금디폴트옵션'
print(search_pexels_photo('small business owner meeting employees office', output_path=f'{OUT}/01_퇴직연금디폴트옵션_대표이미지.jpg', orientation='landscape'))
print(search_pexels_photo('business owner relaxed office window sunrise', output_path=f'{OUT}/05_퇴직연금디폴트옵션_클로징삽화.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
body=load_font('regular',28); small=load_font('regular',24)
im,d=canvas(1000)
d.text((60,55),"디폴트옵션, 언제 자동으로 적용되나",font=load_font('extrabold',40),fill=c(NAVY))
d.text((60,120),"DC형·IRP 가입자가 운용 지시를 하지 않으면",font=body,fill=c(GRAY))
rows=[("신규 입금 후","2주간 지시가 없으면 디폴트옵션 적용",RED),
      ("기존 상품 만기 후","4주 뒤 통지 → 2주 더 지나면 적용 (약 6주)",GOLD),
      ("가입자 동의","사전동의(옵트인) 필요, 언제든 변경 가능",GREEN),
      ("DB형 사업장","해당 없음 (회사가 운용)",NAVY)]
y=190
for k,v,col in rows:
    d.rectangle([60,y,W-60,y+170],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((100,y+55),k,font=load_font('bold',32),fill=c(NAVY),anchor='lm')
    d.text((100,y+115),"→ "+v,font=load_font('extrabold',32),fill=c(col),anchor='lm')
    y+=195
im.save(f'{OUT}/02_퇴직연금디폴트옵션_구조도.png')
im,d=canvas(1000)
d.text((60,55),"2025년 디폴트옵션 유형별 현황",font=load_font('extrabold',40),fill=c(NAVY))
d.text((60,120),"고용노동부 발표(2026.2) 기준 · 과거 수익률이며 미래를 보장하지 않습니다",font=small,fill=c(GRAY))
rows=[("안정형","적립금 85.4%","수익률 2.63%",NAVY),
      ("안정투자형","적립금 7.3%","수익률 7.47%",GOLD),
      ("중립투자형","적립금 4.7%","수익률 10.81%",GOLD),
      ("적극투자형","적립금 2.6%","수익률 14.93%",RED)]
y=200
for k,a,b,col in rows:
    d.rectangle([60,y,W-60,y+150],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((100,y+75),k,font=load_font('extrabold',38),fill=c(col),anchor='lm')
    d.text((560,y+75),a,font=load_font('regular',32),fill=c(NAVY),anchor='lm')
    d.text((W-100,y+75),b,font=load_font('extrabold',34),fill=c(col),anchor='rm')
    y+=175
d.text((60,y+10),"전체 평균 3.7% (전년 4.1%) · 가입자 약 734만 명 · 적립금 53.3조 원",font=load_font('bold',28),fill=c(GRAY))
im.save(f'{OUT}/03_퇴직연금디폴트옵션_비교표.png')
