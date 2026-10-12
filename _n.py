import naver_blog_poster as nb, time, json
d=nb.get_driver()
d.switch_to.window(open('_naver_tab.txt').read())
d.switch_to.default_content(); d.switch_to.frame(d.find_elements('tag name','iframe')[5])
orig=d.execute_script("return document.querySelector('#frmIntroduce').value")
json.dump({'introduce':orig},open('_intro_backup.json','w',encoding='utf-8'),ensure_ascii=False)
print(repr(orig))
d.execute_script("""const t=document.querySelector('#frmIntroduce'); t.value=arguments[0]+'\nG-090056'; t.dispatchEvent(new Event('input',{bubbles:true})); t.dispatchEvent(new Event('change',{bubbles:true}));""",orig)
print(d.execute_script("return [...document.querySelectorAll('a,button,input[type=button],input[type=submit],img')].filter(e=>e.offsetParent).map(e=>(e.innerText||e.value||e.alt||'').trim()+'|'+(e.id||e.className)).filter(s=>/확인|저장/.test(s))"))
