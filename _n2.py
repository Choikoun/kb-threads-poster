import naver_blog_poster as nb, time
d=nb.get_driver()
d.switch_to.window(open('_naver_tab.txt').read())
d.get('https://admin.blog.naver.com/sobok__biz/config/bloginfo'); time.sleep(6)
d.switch_to.frame(d.find_elements('tag name','iframe')[5])
print(d.execute_script("return [...document.querySelectorAll('a,button,input,img,span')].filter(e=>e.offsetParent&&/확인|저장|취소/.test((e.innerText||e.value||e.alt||'')+(e.className||'')+(e.id||''))).map(e=>e.tagName+'|'+(e.innerText||e.value||e.alt||'').trim()+'|'+e.id+'|'+e.className)"))
