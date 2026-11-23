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
desc = "소상공인 정책자금 일반경영안정자금은 연간 7천만 원, 정책자금 기준금리 + 0.6%p 변동금리, 5년 이내(거치 2년 포함) 대리대출입니다. 공통 한도는 소진공 대출잔액을 합산해 운전자금 5억 원, 시설자금 포함 10억 원이며, 세금 체납과 신용도판단정보 등록은 융자제한 사유입니다. 최신 변경 공고와 접수 상황은 소진공에서 확인하세요. 특정 상품 가입을 권유하지 않습니다. #소상공인정책자금 #일반경영안정자금 #소진공"
sys.exit(subprocess.run([sys.executable,'naver_clip_poster.py','_tmp_vid/kb_anim.mp4',desc,'소상공인 정책자금, 일반경영안정자금','1']).returncode)
