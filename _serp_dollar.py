import sys,re,requests,os
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv; load_dotenv()
H={'X-NCP-APIGW-API-KEY-ID':os.environ['NAVER_APIHUB_ID'],'X-NCP-APIGW-API-KEY':os.environ['NAVER_APIHUB_SECRET']}
q=sys.argv[1]
r=requests.get('https://naverapihub.apigw.ntruss.com/search/v1/blog',params={'query':q,'display':15,'sort':'sim'},headers=H,timeout=20).json()
for i,it in enumerate(r.get('items',[]),1):
    print(i,it.get('bloggername'),'|',re.sub('<[^>]+>','',it['title'])[:50],'|',it.get('postdate'))
