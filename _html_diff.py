import sys, re, requests, collections
sys.stdout.reconfigure(encoding='utf-8')
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/150 Safari/537.36'}
posts = {'노출 66년생': '224453401041', '노출 가지급금': '224451981855', '노출 건보료': '224451379798',
         '없음 코인': '224453876931', '없음 비상장': '224455198187', '없음 가업': '224457544162',
         '없음 노란우산': '224459014413', '없음 퇴직연금': '224460330088'}


def page(lg):
    r = requests.get(f'https://blog.naver.com/PostView.naver?blogId=sobok__biz&logNo={lg}&redirect=Dlog&widgetTypeCall=true', headers=H, timeout=20)
    return r.text


for name, lg in posts.items():
    t = page(lg)
    i = t.find('se-main-container')
    body = t[i:] if i >= 0 else t
    comps = collections.Counter(re.findall(r'se-component se-(\w+)', body))
    text = re.sub(r'<[^>]+>', ' ', body)
    text = re.sub(r'\s+', ' ', text)
    esc = len(re.findall(r'&lt;|&gt;', body))
    hidden = len(re.findall(r'display:\s*none|visibility:\s*hidden|font-size:\s*0', body))
    spans = len(re.findall(r'<span', body))
    ps = len(re.findall(r'se-text-paragraph', body))
    stray = re.findall(r'(?:&lt;|<)(?:strong|a |b>|br|div|span)[^ ]{0,20}', text)[:3]
    print(f"{name:10} 컴포넌트 {dict(comps)} 문단{ps} span{spans} 이스케이프{esc} 숨김{hidden} 본문길이{len(text)} 의심{stray}")
