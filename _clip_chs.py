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
desc = "출산전후휴가급여는 고용보험법 제75조에 따라 휴가가 끝난 날 이전 피보험 단위기간이 합산 180일 이상이어야 합니다. 제76조에 따라 우선지원대상기업은 휴가 90일 전체, 그 외 기업은 60일을 넘는 일수 중 최대 30일이 급여 대상이고, 신청은 휴가가 끝난 날 이후 12개월 이내입니다. 내 회사 해당 여부와 지급액은 고용센터에 확인하세요. 특정 상품 가입을 권유하지 않습니다. #출산전후휴가급여 #출산휴가급여신청 #고용보험"
sys.exit(subprocess.run([sys.executable,'naver_clip_poster.py','_tmp_vid/kb_anim.mp4',desc,'출산전후휴가급여, 대기업은 90일 중 뒤 30일','1']).returncode)
