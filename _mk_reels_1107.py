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
    body = 'SCENES = [\n' + ''.join(scenes) + ']\n'
    code = h + body + tail
    ast.parse(code)
    open(name, 'w', encoding='utf-8').write(code)
    print('ok', name)

CTA = "    dict(kind='cta', title='모델별 정리와 링크는 블로그에', head='댓글에 \\'비교\\'', note='직접 써본 후기 아님 · 제휴 수수료',\n         say='링크는 블로그에 있어요. 궁금하면 댓글에 비교라고 남겨 주세요.'),\n"

pot = [
"    dict(kind='split', title='1.7L 온도조절 전기포트', head='같은 용량, 가격이 달라요', note='네이버 스마트스토어 · 2026-11-06 조회',\n         L=dict(name='한경희', price='38,000원', sub='무료배송', win=True), R=dict(name='모즈스웨덴', price='59,000원', sub='무료배송'),\n         say='같은 1.7리터 전기포트인데 가격이 달라요.'),\n",
"    dict(kind='split', title='1.7L 온도조절 전기포트', head='2만 1천 원 차이', note='두 곳 모두 무료배송 표기',\n         L=dict(name='한경희', price='38,000원', sub='정가 79,000원', win=True), R=dict(name='모즈스웨덴', price='59,000원', sub='정가 69,000원', bad=True),\n         say='한경희와 모즈스웨덴은 2만 1천 원 차이예요.'),\n",
"    dict(kind='split', title='모즈스웨덴 쿠팡 목록', head='작은 용량이 더 비싸요', note='쿠팡은 옵션·배송비를 확인하지 못했어요',\n         L=dict(name='1.9L', price='49,000원', sub='로켓 표기', win=True), R=dict(name='1L MC-1500', price='69,000원', sub='로켓 표기 없음', bad=True),\n         say='쿠팡 목록에서는 1리터가 1.9리터보다 2만 원 비싸요.'),\n",
"    dict(kind='split', title='다룸 멜로우 1L', head='쿠팡 목록이 더 낮아요', note='같은 상품인지는 확인하지 못했어요',\n         L=dict(name='네이버', price='51,700원', sub='판매가'), R=dict(name='쿠팡 목록', price='47,410원', sub='목록 표기', win=True),\n         say='다룸은 쿠팡 목록이 4천 2백 원 더 낮아요.'),\n",
"    dict(kind='big', title='결제 전 확인', head='용량과 쿠폰가부터', note='페이지마다 표기가 달라요', lines=['용량 1L·1.5L·1.7L', '쿠폰 적용가와 할인율', '쿠팡 모델명 일치 여부'],\n         say='용량과 쿠폰 적용가, 모델명을 확인하세요.'),\n",
CTA]

rice = [
"    dict(kind='split', title='락앤락 도어포켓 잡곡통 2kg', head='배송비 더해도 쿠팡보다 낮아요', note='네이버 스마트스토어 · 2026-11-06 조회',\n         L=dict(name='네이버 합계', price='8,600원', sub='5,600원 + 배송 3,000원', win=True), R=dict(name='쿠팡 목록', price='13,500원', sub='목록 표기'),\n         say='락앤락 도어포켓 2킬로는 네이버가 배송비를 더해도 더 낮아요.'),\n",
"    dict(kind='split', title='락앤락 도어포켓 2kg', head='4천 9백 원 차이', note='쿠팡은 배송비를 확인하지 못했어요',\n         L=dict(name='네이버 합계', price='8,600원', sub='배송비 포함', win=True), R=dict(name='쿠팡 목록', price='13,500원', sub='4,900원 높음', bad=True),\n         say='네이버와 쿠팡이 4천 9백 원 차이 나요.'),\n",
"    dict(kind='split', title='5kg 판매가 비교', head='5kg이 10kg보다 비싸요', note='네이버 판매가 기준',\n         L=dict(name='ANA 10kg', price='19,800원', sub='배송비 3,000원', win=True), R=dict(name='김형철물점 5KG', price='20,600원', sub='배송비 3,000원', bad=True),\n         say='판매가만 보면 5킬로가 10킬로보다 높아요.'),\n",
"    dict(kind='split', title='상품명에 락앤락이 있어도', head='브랜드 칸이 달라요', note='네이버 판매 페이지 기준 · 정품 여부는 확인 못함',\n         L=dict(name='ANA 10kg', price='락앤락', sub='브랜드 칸', win=True), R=dict(name='김형철물점 5KG', price='김형2501DO', sub='브랜드 칸', small=True),\n         say='상품명에 락앤락이 있어도 브랜드 칸이 다른 페이지가 있어요.'),\n",
"    dict(kind='big', title='결제 전 확인', head='총액과 브랜드 칸부터', note='페이지마다 표기가 달라요', lines=['배송비 더한 총액', '용량 kg와 L 구분', '브랜드·제조사 칸'],\n         say='총액과 용량, 브랜드 칸을 확인하세요.'),\n",
CTA]

build('shop_reel_pot_split_anim.py', '온도조절 전기포트 릴스 분할비교형(2026-11-07): 첫 화면부터 가격, 좌우 분할 비교, 장면 약 3초.\n참고: 조회수 높은 가격비교 쇼츠의 구조(첫 화면 가격·분할 비교·짧은 컷·댓글 유도)만 반영.',
      'blog_images/shop_2026-11-07_온도조절전기포트', '01_온도조절전기포트_대표이미지.jpg', 'reel_pot_split.mp4', pot)
build('shop_reel_rice_split_anim.py', '락앤락 쌀통 릴스 분할비교형(2026-11-08): 첫 화면부터 가격, 좌우 분할 비교, 장면 약 3초.\n참고: 조회수 높은 가격비교 쇼츠의 구조(첫 화면 가격·분할 비교·짧은 컷·댓글 유도)만 반영.',
      'blog_images/shop_2026-11-08_락앤락쌀통', '01_락앤락쌀통_대표이미지.jpg', 'reel_rice_split.mp4', rice)
