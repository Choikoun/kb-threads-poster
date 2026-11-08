import sys, re, ast
sys.stdout.reconfigure(encoding='utf-8')
src = open('shop_reel_c3_split_anim.py', encoding='utf-8').read()
head = src[:src.index('SCENES = [')]
tail = src[src.index('_bg = {}'):]


def build(name, doc, img, bg, out, scenes):
    h = head
    h = re.sub(r'""".*?"""', '"""' + doc + '\nSHOP_VOICE / SHOP_OUT / SHOP_PREVIEW"""', h, count=1, flags=re.S)
    h = h.replace("IMG = 'blog_images/shop_2026-11-06_타임모어C3'", "IMG = '" + img + "'")
    h = h.replace("reel_c3_split.mp4", out).replace("BG = '01_타임모어C3_대표이미지.jpg'", "BG = '" + bg + "'")
    code = h + 'SCENES = [\n' + ''.join(scenes) + ']\n' + tail
    ast.parse(code)
    open(name, 'w', encoding='utf-8').write(code)
    print('ok', name)


CTA = "    dict(kind='cta', title='모델별 정리와 링크는 블로그에', head='댓글에 \\'비교\\'', note='직접 써본 후기 아님 · 쿠팡 파트너스 수수료',\n         say='링크는 블로그에 있어요. 궁금하면 댓글에 비교라고 남겨 주세요.'),\n"

hurom = [
"    dict(kind='split', title='휴롬 H420', head='공식몰과 쿠팡 목록 가격 차이', note='공식몰·쿠팡 검색 목록 · 2026-11-08 조회',\n         L=dict(name='공식몰', price='499,000원', sub='할인 없음'), R=dict(name='쿠팡 목록', price='347,760원', sub='로켓 표기', win=True),\n         say='휴롬 H420은 공식몰 499,000원, 쿠팡 목록에서는 347,760원부터예요.'),\n",
"    dict(kind='split', title='휴롬 H420', head='15만 원 넘게 차이', note='쿠팡 배송비와 옵션은 확인하지 못했어요',\n         L=dict(name='공식몰', price='499,000원', sub='판매가', bad=True), R=dict(name='쿠팡 목록', price='347,760원', sub='151,240원 낮음', win=True),\n         say='차이는 151,240원이에요.'),\n",
"    dict(kind='split', title='공식몰 판매가', head='나중 모델이 더 비싸요', note='공식몰 상품 페이지 기준 · 정가는 모두 499,000원',\n         L=dict(name='H400 (2022.11)', price='419,000원', sub='16% 할인', win=True), R=dict(name='H420 (2024.04)', price='499,000원', sub='할인 없음', bad=True),\n         say='공식몰 정가는 같은데 H400은 419,000원, H420은 499,000원이에요.'),\n",
"    dict(kind='split', title='공식몰 상품정보', head='H410과 H420 표기가 같아요', note='크기와 정격 전압 표기 기준',\n         L=dict(name='H410', price='449,000원', sub='174x216x441mm · 150W'), R=dict(name='H420', price='499,000원', sub='174x216x441mm · 150W'),\n         say='H410과 H420은 크기와 정격 전압이 같게 적혀 있어요.'),\n",
"    dict(kind='big', title='결제 전 확인', head='모델명과 보증부터', note='페이지마다 표기가 달라요', lines=['상품명에 모델명 H420', '판매 주체와 A/S 조건', '쿠팡 옵션과 배송비'],\n         say='모델명과 판매 주체, 보증, 옵션을 확인하세요.'),\n",
CTA]

build('shop_reel_hurom_split_anim.py', '휴롬 H420 릴스 분할비교형(2026-11-09): 첫 화면부터 가격, 좌우 분할 비교, 장면 약 3초.\n참고: 조회수 높은 가격비교 쇼츠의 구조(첫 화면 가격·분할 비교·짧은 컷·댓글 유도)만 반영.',
      'blog_images/shop_2026-11-09_휴롬H420', '01_휴롬H420_대표이미지.jpg', 'reel_hurom_split.mp4', hurom)
