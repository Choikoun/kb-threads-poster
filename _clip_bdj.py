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
desc = "부담부증여는 채무를 넘긴 부분은 양도소득세, 나머지는 증여세로 세금이 갈립니다. 평가액 10억, 취득가액 4억, 채무 3억이면 양도가액 3억, 취득가액 1억 2천만 원입니다(필자 가정). 배우자나 직계존비속 사이는 채무 인수가 안 된 것으로 추정되어 증빙이 필요하고, 신고기한은 각각 말일부터 3개월입니다. 내 증여의 적용은 세무 전문가와 확인하세요. 특정 상품 가입을 권유하지 않습니다. #부담부증여 #부담부증여양도세 #증여세"
sys.exit(subprocess.run([sys.executable,'naver_clip_poster.py','_tmp_vid/kb_anim.mp4',desc,'부담부증여','1']).returncode)
