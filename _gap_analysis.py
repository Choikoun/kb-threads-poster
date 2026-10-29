import json,re,os,glob,sys
sys.stdout.reconfigure(encoding='utf-8')
posts=json.load(open('blog_posts.json',encoding='utf-8'))
log=json.load(open('blog_index_log.json',encoding='utf-8'))
last=log[sorted(log)[-1]]
rows=[]
for p in posts:
    lg=p['naver'].rstrip('/').split('/')[-1]
    st=last.get(lg)
    # find folder
    cand=[f for f in glob.glob('blog_images/*/naver.txt')]
    txt=None
    for f in cand:
        s=open(f,encoding='utf-8').read()
        if p['title'][:12] in s.split('\n')[0] or p['title'].split(',')[0] in s.split('\n')[0]:
            txt=s; break
    if not txt: 
        rows.append((p['date'],p['title'][:22],st,None)); continue
    body=txt.split('---',1)[1] if '---' in txt else txt
    links=re.findall(r'\]\((https?://[^)]+)\)',body)
    ext=[l for l in links if 'blog.naver.com' not in l and 'naver.me' not in l]
    rel=[l for l in links if 'blog.naver.com' in l]
    imgs=len(re.findall(r'\[IMG:',body))
    cat=re.search(r'카테고리:\s*(.*)',txt); cat=cat.group(1).strip() if cat else ''
    rows.append((p['date'],p['title'][:22],st,dict(chars=len(body),ext=len(ext),rel=len(rel),imgs=imgs,cat=cat,tl=len(p['title']))))
for r in rows[-30:]:
    f=r[3]
    print(r[0], {True:'노출',False:'없음',None:'?'}[r[2]], r[1], (f"글자{f['chars']} 외부링크{f['ext']} 내부링크{f['rel']} 이미지{f['imgs']} 제목{f['tl']}자 {f['cat']}" if f else '원고폴더없음'))
