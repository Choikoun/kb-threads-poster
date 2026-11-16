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
desc = "퇴직금 중간정산은 대통령령으로 정한 사유에 해당해 근로자가 요구할 때만 사용자가 지급할 수 있습니다. 시행령 제3조 사유는 무주택자 주택 구입, 전세금·보증금 부담, 연간 임금총액의 1천분의 125를 넘는 의료비 등 아홉 가지입니다. 정산 뒤 계속근로기간은 정산 시점부터 새로 계산하고 사용자는 증빙을 퇴직 후 5년 되는 날까지 보존합니다. 내 회사의 적용은 노무 전문가와 확인하세요. 특정 상품 가입을 권유하지 않습니다. #퇴직금중간정산 #퇴직금중간정산사유 #근로자퇴직급여보장법"
sys.exit(subprocess.run([sys.executable,'naver_clip_poster.py','_tmp_vid/kb_anim.mp4',desc,'퇴직금중간정산','1']).returncode)
