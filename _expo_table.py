import json,sys,re,time,glob,os,requests,urllib.parse
sys.stdout.reconfigure(encoding='utf-8')
H={'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148'}
P=json.load(open('blog_posts.json',encoding='utf-8'))
rows=[]
for p in P:
    n=p['naver'].rstrip('/').split('/')[-1]
    q=urllib.parse.quote(p['title'])
    try:
        h=requests.get(f'https://m.search.naver.com/search.naver?ssc=tab.m_blog.all&query={q}',headers=H,timeout=15).text
        ex=n in h
    except Exception as e: ex=None
    body=None
    for d in glob.glob(f"blog_images/{p['date']}_*/naver.txt"):
        body=len(open(d,encoding='utf-8').read())
    rows.append(dict(date=p['date'],n=n,ex=ex,tl=len(p['title']),body=body,title=p['title']))
    time.sleep(0.4)
json.dump(rows,open('_expo_table.json','w',encoding='utf-8'),ensure_ascii=False)
for r in sorted(rows,key=lambda r:r['date']): print(r['date'],'O' if r['ex'] else ('X' if r['ex'] is False else '?'),r['tl'],r['body'],r['title'][:30])
