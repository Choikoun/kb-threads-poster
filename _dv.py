import naver_blog_poster as nb, time, re
d=nb.get_driver()
d.get('https://www.ncloud.com/product/applicationService/naverApiHub'); time.sleep(8)
t=d.execute_script("return document.body.innerText")
for kw in ['무료','유료','요금','과금','한도','검색','크레딧','결제']:
    for m in re.finditer(kw,t):
        s=max(0,m.start()-60); print(kw,'::',t[s:m.start()+110].replace('\n',' ')); break
print(len(t))
