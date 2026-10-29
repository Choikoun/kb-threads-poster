import sys, re, json, requests, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/150 Safari/537.36'}
posts=json.load(open('blog_posts.json',encoding='utf-8'))
want={'가수금뜻':'gasugeum_meaning','지역가입자건보료상한액':'regional_premium_cap','가지급금뜻':'gajigeum_meaning','66년생국민연금수령나이':'pension_age_1966','코인과세유예가능성':'crypto_tax_deferral','비상장주식양도세율':'unlisted_stock_tax_rate','국민연금반납금':'nps_lumpsum_repay','가업상속공제개정안':'family_business_deduction_reform','톤틴연금':'tontine_annuity','일시납달러연금보험':'dollar_annuity_lump'}
bykey={p['key']:p for p in posts}
for kw,key in want.items():
    p=bykey.get(key)
    if not p: print(kw,'기록없음'); continue
    log=p['naver'].rstrip('/').split('/')[-1]
    r=requests.get('https://search.naver.com/search.naver',params={'ssc':'tab.blog.all','query':kw},headers=UA,timeout=20)
    ids=[]
    for m in re.finditer(r'blog\.naver\.com/([A-Za-z0-9_]+)/(\d{9,})',r.text):
        k=(m.group(1),m.group(2))
        if k not in ids: ids.append(k)
    pos=[i+1 for i,k in enumerate(ids) if k[1]==log]
    print(f"{kw:<14} 우리 글 {'%d위'%pos[0] if pos else '결과 밖'} (수집 {len(ids)}개) 발행 {p['date']}")
