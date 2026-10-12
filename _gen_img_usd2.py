import sys
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
from PIL import Image, ImageDraw
from card_generator import load_font, hex_to_rgb
from stock_card_poster import search_pexels_photo
OUT='blog_images/2026-10-13_달러보험단점'
print(search_pexels_photo('currency exchange rate board dollar won', output_path=f'{OUT}/01_달러보험단점_대표이미지.jpg', orientation='landscape'))
print(search_pexels_photo('man reading document carefully coffee table', output_path=f'{OUT}/05_달러보험단점_클로징삽화.jpg', orientation='landscape'))
BG="#F7F5F0";NAVY="#1B2A4A";GOLD="#B8925A";GRAY="#6B7280";RED="#B5473A";GREEN="#2F7D5D";W=1200;c=hex_to_rgb
def canvas(h):
    im=Image.new('RGB',(W,h),c(BG)); return im, ImageDraw.Draw(im)
body=load_font('regular',28); small=load_font('regular',24)
im,d=canvas(1000)
d.text((60,55),"같은 US$100,000, 환율에 따라",font=load_font('extrabold',40),fill=c(NAVY))
d.text((60,120),"원화로 환산하면 이렇게 달라집니다 (구조 설명용 가정)",font=body,fill=c(GRAY))
cols=[("환율 1,300원",["US$100,000","× 1,300원","= 1억 3,000만 원"],NAVY),
      ("환율 1,500원",["US$100,000","× 1,500원","= 1억 5,000만 원"],RED)]
x=60
for title,lines,col in cols:
    d.rectangle([x,200,x+500,640],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((x+250,255),title,font=load_font('extrabold',38),fill=c(col),anchor='mm')
    yy=340
    for i,l in enumerate(lines):
        f=load_font('extrabold',38) if i==2 else load_font('regular',34)
        d.text((x+40,yy),l,font=f,fill=c(col if i==2 else NAVY)); yy+=85
    x+=580
d.text((60,690),"같은 달러인데 원화 환산액은 2,000만 원 차이 — 낼 때와 받을 때 모두 영향",font=load_font('bold',28),fill=c(RED))
d.text((60,740),"납입·지급 환율은 회사가 정하는 값이라 은행 환전 환율과 다를 수 있습니다",font=small,fill=c(GRAY))
im.save(f'{OUT}/02_달러보험단점_구조도.png')
im,d=canvas(1060)
d.text((60,55),"달러 변액연금, 단점이 되는 구조",font=load_font('extrabold',40),fill=c(NAVY))
d.text((60,120),"약관·사업방법서 기준",font=body,fill=c(GRAY))
rows=[("원금 손실","펀드 실적·중도 해지 시 손실 가능",RED),
      ("환율 손실","낼 때·받을 때 환율, 손실은 계약자 몫",RED),
      ("비용","운용보수 최대 0.46~0.58% + 월공제액",GOLD),
      ("유동성","보험계약대출 없음, 인출 연 12회·50% 한도",GOLD),
      ("예금자보호","최저사망적립액 등만, 1인 1억 원 한도",NAVY),
      ("가입 금액","일시납 US$30,000 이상",NAVY)]
y=190
for k,v,col in rows:
    d.rectangle([60,y,W-60,y+125],fill=c("#FFFFFF"),outline=c(col),width=4)
    d.text((100,y+62),k,font=load_font('bold',32),fill=c(col),anchor='lm')
    d.text((W-100,y+62),v,font=load_font('regular',29),fill=c(NAVY),anchor='rm')
    y+=145
im.save(f'{OUT}/03_달러보험단점_비교표.png')
