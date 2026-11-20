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
desc = "케어네이션 가족간병은 앱에 간병 기간, 환자 정보, 보험사 정보를 입력하면 보험사 제출용 이용증명서를 당일 발급한다고 안내합니다. 다만 금융감독원 약관 예시는 간병인을 유상으로 제공하고 비용 지불이 확인된 사람으로 보며, 사용 여부가 불분명하면 추가 서류를 요청할 수 있습니다. 내 보험의 지급 여부는 약관과 보험사에 확인하세요. 특정 상품 가입을 권유하지 않습니다. #케어네이션가족간병 #가족간병 #간병보험금청구"
sys.exit(subprocess.run([sys.executable,'naver_clip_poster.py','_tmp_vid/kb_anim.mp4',desc,'케어네이션 가족간병 이용증명서','1']).returncode)
