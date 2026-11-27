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
desc = "실업급여 소정급여일수는 고용보험법 제50조에 따라 피보험기간과 연령별로 정해집니다. 고용노동부 FAQ 기준 1년 이상 3년 미만 근무는 50세 미만 150일, 50세 이상과 장애인 180일입니다. 신고일부터 7일은 대기기간이고 이직 다음 날부터 12개월 안에 소정급여일수를 한도로 지급됩니다. 내 지급일수는 고용센터에 확인하세요. 특정 상품 가입을 권유하지 않습니다. #실업급여 #실업급여몇개월 #소정급여일수"
sys.exit(subprocess.run([sys.executable,'naver_clip_poster.py','_tmp_vid/kb_anim.mp4',desc,'실업급여 소정급여일수, 1년 4개월 근무하면 150일','1']).returncode)
