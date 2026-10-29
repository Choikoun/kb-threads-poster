import sys,re,json,requests
sys.stdout.reconfigure(encoding='utf-8')
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/150 Safari/537.36'}
posts={p['key']:p for p in json.load(open('blog_posts.json',encoding='utf-8'))}
tests=[('코인과세유예가능성','crypto_tax_deferral'),('비상장주식양도세율','unlisted_stock_tax_rate'),('국민연금반납금','nps_lumpsum_repay'),('가업상속공제개정안','family_business_deduction_reform'),('66년생국민연금수령나이','pension_age_1966')]
def find(url_params,log):
    r=requests.get('https://search.naver.com/search.naver',params=url_params,headers=UA,timeout=20)
    ids=[]
    for m in re.finditer(r'blog\.naver\.com/([A-Za-z0-9_]+)/(\d{9,})',r.text):
        k=m.group(2)
        if k not in ids: ids.append(k)
    return (ids.index(log)+1 if log in ids else None), len(ids)
for kw,key in tests:
    log=posts[key]['naver'].rstrip('/').split('/')[-1]
    t=posts[key]['title']
    a=find({'ssc':'tab.blog.all','query':kw,'sm':'tab_opt','nso':'so:dd,p:all'},log)
    b=find({'ssc':'tab.blog.all','query':t},log)
    c=find({'ssc':'tab.blog.all','query':f'{kw} sobok__biz'},log)
    print(f"{kw}: 최신순 {a[0] or '없음'}/{a[1]} | 제목전체검색 {b[0] or '없음'}/{b[1]} | '키워드+블로그ID' {c[0] or '없음'}/{c[1]}")
