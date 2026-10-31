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
desc = "우리 집 취득 시점이 출산일로부터 5년 안에 들어가는지 확인해 보셨나요? 신생아 취득세 감면은 출산 후 5년 이내, 12억 원 이하, 거주 목적이 요건이고 100% 감면에 한도 500만 원, 기한은 2028년 12월 31일까지입니다. 5년을 7년으로 늘리는 안은 결정된 바 없습니다. 추징 요건과 신청 방법은 지자체에서 확인하세요. 특정 상품 가입을 권유하지 않습니다. #신생아취득세감면 #출산가구취득세감면 #취득세감면"
sys.exit(subprocess.run([sys.executable,'naver_clip_poster.py','_tmp_vid/kb_anim.mp4',desc,'신생아취득세감면','1']).returncode)
