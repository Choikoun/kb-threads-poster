import subprocess, json, time, sys, os
sys.stdout.reconfigure(encoding='utf-8')
def sh(*a): return subprocess.run(a, capture_output=True, text=True, encoding='utf-8').stdout.strip()
runs = None
for _ in range(5):
    try:
        runs = json.loads(sh('gh','run','list','--workflow=blog_reel_now.yml','-L','1','--json','databaseId,createdAt')); break
    except Exception:
        time.sleep(10)
rid = str(runs[0]['databaseId']); print('run', rid)
while True:
    try:
        r = json.loads(sh('gh','run','view',rid,'--json','status,conclusion'))
        if r['status']=='completed': break
    except Exception as e:
        print('gh 재시도', str(e)[:60])
    time.sleep(30)
if r['conclusion']!='success': sys.exit('reel failed')
tags = json.loads(sh('gh','release','list','-L','6','--json','tagName'))
os.makedirs('_tmp_vid', exist_ok=True)
for t in tags:
    a = sh('gh','release','view',t['tagName'],'--json','assets','-q','.assets[].name')
    if 'kb_anim.mp4' in a:
        subprocess.run(['gh','release','download',t['tagName'],'-p','kb_anim.mp4','-D','_tmp_vid','--clobber'],check=True); print('영상', t['tagName']); break
desc = "종부세 납부기간은 종합부동산세법 제16조에 따라 12월 1일부터 15일까지입니다. 세액이 250만 원을 넘으면 6개월 이내 분납이 가능하고, 400만 원이면 150만 원까지, 800만 원이면 400만 원까지 분납 대상입니다. 1세대 1주택자는 요건을 갖추면 납부유예도 신청할 수 있습니다. 내 세액과 신청 가능 여부는 관할 세무서에 확인하세요. 특정 상품 가입을 권유하지 않습니다. #종부세납부기간 #종부세분납 #종합부동산세"
sys.exit(subprocess.run([sys.executable,'naver_clip_poster.py','_tmp_vid/kb_anim.mp4',desc,'종부세 납부기간은 12월 1일부터 15일','1']).returncode)
