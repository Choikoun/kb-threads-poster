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
desc = "간병인 사용일당은 간병 서비스 이용 비용을 낸 사실이 확인되어야 지급됩니다. 금융감독원 2025년 4월 보도자료에 따르면 실제 사용 여부가 불분명하면 간병인사용계약서, 간병근무일지, 계좌이체내역 같은 추가 서류를 요청받을 수 있고, 간호·간병통합서비스를 받으면 약관에 따라 지급되지 않을 수 있습니다. 내 보험의 지급 여부는 약관과 보험사에 확인하세요. 특정 상품 가입을 권유하지 않습니다. #간병인보험 #간병인사용일당 #간병비"
sys.exit(subprocess.run([sys.executable,'naver_clip_poster.py','_tmp_vid/kb_anim.mp4',desc,'간병인보험','1']).returncode)
