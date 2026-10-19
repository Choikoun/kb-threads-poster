#!/usr/bin/env python3
"""블로그 발행 후 릴스(blog_reel_now.yml) 영상을 받아 네이버 클립에 올린다 (2026-10-19 사용자 요청: 블로그 올릴 때마다 클립도).
사용: python clip_after_reel.py "<블로그 글 제목 일부>" "<클립 설명 300자 이내>" [--dry]
순서: 최신 blog_reel_now 실행이 끝날 때까지 대기 → 최신 video-* 릴리스의 mp4 다운로드 → naver_clip_poster.py 실행.
릴스 디스패치 직후에 실행한다. 자동화 크롬(9222)이 떠 있어야 한다(python naver_blog_poster.py start)."""
import subprocess, sys, time, os, json
sys.stdout.reconfigure(encoding='utf-8')
title, desc = sys.argv[1], sys.argv[2]
dry = ['--dry'] if '--dry' in sys.argv else []


def sh(*a):
    return subprocess.run(a, capture_output=True, text=True, encoding='utf-8').stdout.strip()


run = json.loads(sh('gh', 'run', 'list', '--workflow=blog_reel_now.yml', '-L', '1', '--json', 'databaseId,status,conclusion'))[0]
for _ in range(40):
    run = json.loads(sh('gh', 'run', 'view', str(run['databaseId']), '--json', 'status,conclusion') or '{}') | {'databaseId': run['databaseId']}
    if run.get('status') == 'completed':
        break
    time.sleep(30)
if run.get('conclusion') != 'success':
    sys.exit(f"릴스 워크플로우가 성공하지 않아 클립 업로드를 건너뜁니다: {run}")
tag = sh('gh', 'release', 'list', '-L', '1', '--json', 'tagName', '-q', '.[0].tagName')
os.makedirs('_tmp_vid', exist_ok=True)
subprocess.run(['gh', 'release', 'download', tag, '-p', 'kb_anim.mp4', '-D', '_tmp_vid', '--clobber'], check=True)
print('영상:', tag)
sys.exit(subprocess.run([sys.executable, 'naver_clip_poster.py', '_tmp_vid/kb_anim.mp4', desc, title, '1'] + dry).returncode)
