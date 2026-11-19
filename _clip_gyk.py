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
desc = "건강보험임의계속가입은 퇴직 전 18개월 중 직장가입 기간이 통산 1년 이상이면 퇴직 다음 날부터 최대 36개월까지 직장가입자 자격을 유지하는 제도입니다. 신청 기한은 첫 지역보험료를 고지받은 날부터 그 납부기한에서 2개월이 지나기 전까지이고, 신청 뒤 첫 보험료를 제때 내지 않으면 자격을 유지할 수 없습니다. 내 자격과 보험료는 국민건강보험공단에 확인하세요. 특정 상품 가입을 권유하지 않습니다. #건강보험임의계속가입 #퇴직후건강보험 #임의계속가입"
sys.exit(subprocess.run([sys.executable,'naver_clip_poster.py','_tmp_vid/kb_anim.mp4',desc,'건강보험임의계속가입','1']).returncode)
