import json, sys, time, urllib.parse, requests, re
sys.stdout.reconfigure(encoding='utf-8')
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/150 Safari/537.36'}
d=json.load(open('shop_posts.json',encoding='utf-8')); ps=d if isinstance(d,list) else d.get('posts',d)
def get(q,tab):
    u=f'https://search.naver.com/search.naver?ssc=tab.{tab}.all&sm=tab_opt&query='+urllib.parse.quote(q)
    return requests.get(u,headers=UA,timeout=20).text
for p in ps:
    pid=p['naver'].split('/')[-1]
    r=[]
    for lab,q,tab in (('제목/블로그탭',p['title'],'blog'),('키워드/블로그탭',p['keyword'],'blog'),('키워드/통합',p['keyword'],'nx')):
        try:
            h=get(q,tab); r.append(f'{lab}:'+('노출' if pid in h else '없음')+f'(sobok {h.count("sobok_biz")})')
        except Exception as e: r.append(lab+':오류')
        time.sleep(1.5)
    print(p['date'],p['keyword'],'|',' '.join(r))
