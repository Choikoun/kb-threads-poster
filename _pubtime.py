import sys,re,json,requests
sys.stdout.reconfigure(encoding='utf-8')
posts=json.load(open('blog_posts.json',encoding='utf-8'))
log=json.load(open('blog_index_log.json',encoding='utf-8')); last=log[sorted(log)[-1]]
H={'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148'}
rows=[]
for p in posts[-30:]:
    ln=p['naver'].rstrip('/').split('/')[-1]
    try:
        r=requests.get(f'https://m.blog.naver.com/PostView.naver?blogId=sobok__biz&logNo={ln}',headers=H,timeout=20)
        m=re.search(r'(20\d\d)\. (\d+)\. (\d+)\. (\d+):(\d+)',r.text)
        t=m.group(0) if m else '?'
        mi=re.findall(r'<img[^>]+data-lazy-src',r.text)
        rows.append((t,last.get(ln),p['title'][:18]))
    except Exception as e:
        rows.append(('ERR',last.get(ln),p['title'][:18]))
for t,st,ti in rows: print(t,{True:'노출',False:'없음',None:'?'}[st],ti)
