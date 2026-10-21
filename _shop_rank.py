import json, sys, time, urllib.parse, requests, re
sys.stdout.reconfigure(encoding='utf-8')
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/150 Safari/537.36'}
d=json.load(open('shop_posts.json',encoding='utf-8')); ps=d if isinstance(d,list) else d.get('posts',d)
def order(q,start):
    u='https://search.naver.com/search.naver?ssc=tab.blog.all&sm=tab_opt&query='+urllib.parse.quote(q)+(f'&start={start}' if start>1 else '')
    h=requests.get(u,headers=UA,timeout=20).text
    ids=[]
    for m in re.finditer(r'blog\.naver\.com/([A-Za-z0-9_\-]+)/(\d{9,})',h):
        k=(m.group(1),m.group(2))
        if k not in ids: ids.append(k)
    return ids
for p in ps:
    pid=p['naver'].split('/')[-1]
    res=[]
    for lab,q in (('제목',p['title']),('키워드',p['keyword'])):
        pos=None; tot=0
        for st in (1,16,31):
            try: ids=order(q,st)
            except Exception: break
            for i,(b,n) in enumerate(ids):
                if n==pid: pos=tot+i+1; break
            tot+=len(ids)
            if pos or not ids: break
            time.sleep(1)
        res.append(f'{lab}:'+(f'{pos}위' if pos else f'권외(상위{tot}개 확인)'))
    print(p['date'],p['keyword'],'|',' '.join(res))
