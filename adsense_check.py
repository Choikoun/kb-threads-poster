#!/usr/bin/env python3
"""티스토리 애드센스 사이트 승인 상태 확인 (자동화 크롬의 구글 로그인 사용)
상태가 '준비 중'이면 승인 대기, '준비됨'이면 승인 완료(광고 게재 시작), '검토 필요/주의 필요'면 조치 필요.
사용: python adsense_check.py   → 상태 출력 + adsense_status.json 기록(바뀌면 CHANGED 표시)"""
import sys, json, os, time, re
sys.stdout.reconfigure(encoding='utf-8')
import naver_blog_poster as nb

URL = 'https://adsense.google.com/adsense/u/0/pub-9666114277793331/sites'
FILE = 'adsense_status.json'


def check():
    d = nb.get_driver()
    d.get(URL)
    time.sleep(10)
    t = d.execute_script("return document.body.innerText")
    i = t.find('freedom-of-economic.tistory.com')
    seg = t[i:i + 200] if i >= 0 else t[:200]
    status = next((s for s in ('준비됨', '준비 중', '검토 필요', '주의 필요') if s in seg), '확인불가')
    return status, ' '.join(seg.split())


if __name__ == '__main__':
    status, seg = check()
    prev = json.load(open(FILE, encoding='utf-8')).get('status') if os.path.exists(FILE) else None
    json.dump({'status': status, 'checked': time.strftime('%Y-%m-%d %H:%M'), 'raw': seg}, open(FILE, 'w', encoding='utf-8'), ensure_ascii=False)
    print('애드센스 사이트 상태:', status, '| 이전:', prev, '| CHANGED' if prev and prev != status else '')
