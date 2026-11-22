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
desc = "육아휴직급여는 시행령 제95조에 따라 시작일 기준 월 통상임금으로 1~3개월 상한 250만 원, 4~6개월 상한 200만 원, 7개월부터 80%에 상한 160만 원입니다. 고용보험법 제70조는 시작일 이전 피보험 단위기간 합산 180일 이상을 요건으로 두고, 신청은 휴직 시작일 이후 1개월부터 종료 후 12개월 이내입니다. 내 지급액은 고용센터에 확인하세요. 특정 상품 가입을 권유하지 않습니다. #육아휴직급여 #육아휴직급여상한 #부모육아휴직"
sys.exit(subprocess.run([sys.executable,'naver_clip_poster.py','_tmp_vid/kb_anim.mp4',desc,'육아휴직급여, 첫 3개월','1']).returncode)
