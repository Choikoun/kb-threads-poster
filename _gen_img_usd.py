import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/2026-10-08_달러통장'
print(search_pexels_photo('us dollar banknotes close up desk', output_path=f'{OUT}/01_달러통장_대표이미지.jpg', orientation='landscape'))
print(search_pexels_photo('senior couple relaxing home calm retirement', output_path=f'{OUT}/05_달러통장_클로징삽화.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
body=load_font('regular',28); small=load_font('regular',24)
im,d=canvas(1060)
d.text((60,55),"달러통장 vs 달러 변액연금",font=load_font('extrabold',40),fill=c(NAVY))
d.text((60,120),"같은 달러, 쓰임새가 다릅니다",font=body,fill=c(GRAY))
rows=[("달러통장(외화보통예금)",["언제든 입출금 · 이자는 낮은 편","환차익 비과세 · 이자는 15.4% 과세"],GREEN),
      ("달러 변액연금(일시납)",["US$30,000 이상 · 달러로 운용·지급","원금손실·환율손실 가능, 85세 연금개시"],NAVY)]
y=190
for k,ls,col in rows:
    d.rectangle([60,y,W-60,y+330],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((100,y+60),k,font=load_font('extrabold',38),fill=c(col),anchor='lm')
    yy=y+150
    for l in ls:
        d.text((100,yy),"· "+l,font=load_font('regular',32),fill=c(NAVY),anchor='lm'); yy+=70
    y+=370
im.save(f'{OUT}/02_달러통장_구조도.png')
im,d=canvas(1080)
d.text((60,55),"이 상품에서 꼭 볼 숫자",font=load_font('extrabold',40),fill=c(NAVY))
d.text((60,120),"사업방법서·약관 기준",font=body,fill=c(GRAY))
rows=[("가입 금액","일시납 US$30,000 이상",NAVY),
      ("연금 개시","85세 · 5년 보증 종신연금",NAVY),
      ("중도인출","연 12회 · 1회 해약환급금의 50% 이내",GOLD),
      ("운용보수","연 0.33%(채권형) · 0.45%(주식형)",GOLD),
      ("최저사망적립액","이미 납입한 보험료",GREEN),
      ("위험","원금손실 · 환율손실 계약자 부담",RED)]
y=190
for k,v,col in rows:
    d.rectangle([60,y,W-60,y+125],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((100,y+62),k,font=load_font('bold',32),fill=c(col),anchor='lm')
    d.text((W-100,y+62),v,font=load_font('regular',30),fill=c(NAVY),anchor='rm')
    y+=145
im.save(f'{OUT}/03_달러통장_비교표.png')
