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
desc = "증여세면제한도는 배우자 6억 원, 직계존속·직계비속 5천만 원(미성년자 2천만 원), 그 밖의 친족 1천만 원입니다. 직계존속에게 혼인 전후 2년 또는 출산·입양 2년 안에 받으면 별도로 1억 원이 공제되고 합쳐서 1억 원이 한도이며, 공제 한도는 10년 안에 공제받은 금액과 합산합니다. 내 증여의 적용은 세무 전문가와 확인하세요. 특정 상품 가입을 권유하지 않습니다. #증여세면제한도 #증여재산공제 #혼인증여공제"
sys.exit(subprocess.run([sys.executable,'naver_clip_poster.py','_tmp_vid/kb_anim.mp4',desc,'증여세면제한도','1']).returncode)
