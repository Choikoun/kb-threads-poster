import re,sys,json
sys.stdout.reconfigure(encoding='utf-8')
D='blog_images/2026-11-02_직장피부양자뜻'
s=open(D+'/naver.txt',encoding='utf-8').read()
head,body=s.split('\n---\n',1)
meta=dict(l.split(': ',1) for l in head.split('\n'))
out=[]
for l in body.strip('\n').split('\n'):
    l=re.sub(r'^> ','▶ ',l)
    l=re.sub(r'\[IMG:([^\]]+)\]',r'\n(여기에 이미지: \1)\n',l)
    l=l.replace('[구분선]','――――――――')
    l=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',r'\1 \2',l)
    l=re.sub(r'==([^=]+)==',r'\1',l)
    m=re.match(r'^\*\*(.+)\*\*$',l)
    if m: l='\n■ '+m.group(1)
    out.append(l)
plain='\n'.join(out)
plain=re.sub(r'\n{3,}','\n\n',plain)
posts=json.load(open('blog_posts.json',encoding='utf-8'))
bad=['regional_premium_cap','gajigeum_meaning','pension_age_1966']  # 노출 확인용 제외
urls=[(p['date'],p['title'],p['naver']) for p in posts if p['date']>='2026-10-26' and p['naver'].startswith('https://blog.naver.com')]
lst='\n'.join(f'  {d}  {t}\n      {u}' for d,t,u in urls)
txt=f"""[직접 발행 시험 안내 — 2026-11-02 직장피부양자뜻]
목적: 자동 발행이 아닌 사람이 평소 쓰는 PC Chrome에서 직접 올린 글이 하루 안에 네이버 검색에 노출되는지 확인.

1. 평소 쓰시는 Chrome으로 네이버 블로그 PC 글쓰기 열기 (blog.naver.com/GoBlogWrite.naver?blogId=sobok__biz)
2. 제목: {meta['제목']}
3. 카테고리: 금융지식
4. 본문: 아래 '본문' 전체를 붙여넣고 (여기에 이미지: 파일명) 자리마다 같은 폴더의 이미지 파일을 넣기
   - ■ 줄은 소제목(굵게), ▶ 줄은 인용구로 넣어도 되고 그냥 두어도 됨(시험이라 완벽하지 않아도 됨)
   - 링크는 주소가 붙은 채로 두면 에디터가 링크로 바꿈
5. 태그: {meta['태그']}
6. 발행 후 글 주소를 알려 주세요. 노출 여부를 1시간 간격으로 확인합니다.
(공개 설정 전체공개, 검색 허용 켜짐 상태 그대로)

=== 본문 ===
{plain}
"""
open(D+'/직접발행_붙여넣기.txt','w',encoding='utf-8').write(txt)
inq=f"""[네이버 고객센터 문의 초안 — 검색 누락 신고]
(문의 경로: 네이버 고객센터 > 블로그 > 검색/노출 관련 문의. 사용자가 직접 제출)

제목: 블로그 글이 검색(블로그 탭)에 노출되지 않습니다

내용:
블로그 주소: https://blog.naver.com/sobok__biz

2026년 10월 26일 이후 발행한 글이 네이버 검색 결과(통합검색·블로그 탭)에서 글 제목으로 검색해도 나오지 않습니다. 같은 블로그에서 10월 25일까지 발행한 글은 검색에 정상 노출됩니다. 글은 전체공개이며 검색 허용 상태입니다.
금칙어나 불법·홍보성 내용은 없고, 보험·세금·건강보험 관련 정보 정리 글입니다. 검색 노출 제한이 걸려 있는지, 누락된 이유가 무엇인지 확인 부탁드립니다.

미노출 글:
{lst}

(참고: 10월 1일~13일 발행분도 같은 증상이 있었습니다.)
"""
open('_네이버_문의_초안.txt','w',encoding='utf-8').write(inq)
print(inq)
