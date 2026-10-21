import sys,re,os,requests,urllib.parse
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
H={'X-NCP-APIGW-API-KEY-ID':os.environ['NAVER_APIHUB_ID'],'X-NCP-APIGW-API-KEY':os.environ['NAVER_APIHUB_SECRET']}
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/150 Safari/537.36'}
PRO=re.compile(r'세무|회계|법무|변호|노무|법률|보험|금융|컨설팅|연구소|설계사|FP|CFP')
for k in sys.argv[1:]:
    r=requests.get('https://naverapihub.apigw.ntruss.com/search/v1/blog',params={'query':k,'display':15,'sort':'sim'},headers=H,timeout=20).json()
    it=r.get('items',[])
    rec=sum(1 for x in it if x.get('postdate','0')>='20261001'); old=sum(1 for x in it if x.get('postdate','0')<'20260901')
    pro=sum(1 for x in it if PRO.search(x.get('bloggername','')+re.sub('<[^>]+>','',x['title'])))
    h=requests.get('https://search.naver.com/search.naver?ssc=tab.blog.all&sm=tab_opt&query='+urllib.parse.quote(k),headers=UA,timeout=20).text
    print(f"{k:<16} 10월글 {rec:>2}/15 | 9월 이전 {old:>2}/15 | 전문가·업체 {pro:>2}/15 | 광고 {len(re.findall(r'ader\.naver',h))}")
