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
desc = "67년생이라면 올해가 조기노령연금 개시 나이인 만 59세가 되는 해입니다. 국민연금공단 안내에서 1965~68년생은 노령연금 64세, 조기노령연금 59세이고, 조기노령연금은 가입기간 10년 이상에 소득이 있는 업무에 종사하지 않아야 합니다. 64세 이후 5년 동안은 소득에 따라 감액될 수 있습니다. 내 연금액은 국민연금공단에서 확인하세요. 특정 상품 가입을 권유하지 않습니다. #67년생국민연금수령나이 #조기노령연금 #국민연금소득감액"
sys.exit(subprocess.run([sys.executable,'naver_clip_poster.py','_tmp_vid/kb_anim.mp4',desc,'67년생국민연금수령나이','1']).returncode)
