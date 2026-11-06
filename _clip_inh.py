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
desc = "자녀 상속세 면제 한도는 국세청 안내 기준으로 일괄공제 5억 원, 자녀공제 1인당 5천만 원입니다. 배우자공제는 최소 5억 원이라 배우자가 있으면 합계 10억 원, 없으면 5억 원이 출발점입니다. 순금융재산 공제와 동거주택 공제는 요건을 갖춰야 하고 사전증여가 있으면 달라질 수 있습니다. 내 세액은 세무 전문가와 확인하세요. 특정 상품 가입을 권유하지 않습니다. #자녀상속세면제한도 #상속세일괄공제 #배우자상속공제"
sys.exit(subprocess.run([sys.executable,'naver_clip_poster.py','_tmp_vid/kb_anim.mp4',desc,'자녀상속세면제한도','1']).returncode)
