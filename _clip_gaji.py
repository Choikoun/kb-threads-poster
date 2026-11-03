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
desc = "우리 가족의 공동상속인과 상속세 신고기한을 정리해 보셨나요? 민법 제1013조는 공동상속인이 언제든지 협의로 상속재산을 분할할 수 있다고 정하고, 법정상속분은 균분이며 배우자는 5할이 가산됩니다. 상속세는 상속개시일이 속하는 달의 말일부터 6개월 이내에 신고합니다. 협의서 서류와 세금은 세무서나 전문가에게 확인하세요. 특정 상품 가입을 권유하지 않습니다. #상속재산분할협의서예시 #법정상속분 #상속세신고기한"
sys.exit(subprocess.run([sys.executable,'naver_clip_poster.py','_tmp_vid/kb_anim.mp4',desc,'상속재산분할협의서예시','1']).returncode)
