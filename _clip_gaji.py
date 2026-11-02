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
desc = "우리 가족의 소득 합계와 재산세 과세표준이 어느 구간인지 확인해 보셨나요? 직장피부양자는 소득 합계 연 2천만 원 이하, 재산세 과세표준 5억 4천만 원 이하여야 하고, 5.4억 초과 9억 이하면 소득은 연 1천만 원 이하여야 합니다. 사업자등록이 없고 사업소득이 연 500만 원 이하면 없는 것으로 봅니다. 내 자격은 국민건강보험공단에서 확인하세요. 특정 상품 가입을 권유하지 않습니다. #직장피부양자뜻 #건강보험피부양자 #피부양자조건"
sys.exit(subprocess.run([sys.executable,'naver_clip_poster.py','_tmp_vid/kb_anim.mp4',desc,'직장피부양자뜻','1']).returncode)
