#!/usr/bin/env python3
"""예약 발행된 블로그 글 후속 자동화 (PC 없이 Actions에서 실행).
네이버 RSS에서 글 URL을 찾아 Threads(댓글에 URL) 게시 + blog_posts.json 등록 + 릴스·IG 카드 워크플로 실행.
사용: python timed_social.py [key]   key 생략 시 오늘(KST) 날짜로 timed_social/schedule.json에서 찾음.
"""
import sys, os, re, json, time, subprocess
from datetime import datetime, timezone, timedelta
sys.stdout.reconfigure(encoding='utf-8')
import requests

KST = timezone(timedelta(hours=9))
RSS = 'https://rss.blog.naver.com/sobok__biz.xml'

def pick_key():
    if len(sys.argv) > 1:
        return sys.argv[1]
    today = datetime.now(KST).strftime('%Y-%m-%d')
    m = json.load(open('timed_social/schedule.json', encoding='utf-8'))
    return m.get(today)

def find_url(title_match, tries=25, wait=60):
    for i in range(tries):
        try:
            x = requests.get(RSS, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20).text
            for item in re.findall(r'<item>(.*?)</item>', x, re.S):
                t = re.search(r'<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>', item, re.S)
                l = re.search(r'<link>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</link>', item, re.S)
                if t and l and title_match in t.group(1):
                    m = re.search(r'/(\d{9,})', l.group(1))
                    if m:
                        return f'https://blog.naver.com/sobok__biz/{m.group(1)}'
        except Exception as e:
            print('RSS 오류', str(e)[:80])
        print(f'RSS에 아직 없음 {i + 1}/{tries}')
        time.sleep(wait)
    return None

def main():
    key = pick_key()
    if not key:
        print('오늘 예약된 후속 작업 없음'); return 0
    cfg = json.load(open(f'timed_social/{key}.json', encoding='utf-8'))
    posts = json.load(open('blog_posts.json', encoding='utf-8'))
    if any(p['key'] == cfg['key'] for p in posts):
        print('이미 처리됨(blog_posts.json에 있음), 중복 방지로 종료'); return 0
    url = find_url(cfg['title_match'])
    if not url:
        print('::error::네이버 RSS에서 글을 찾지 못했습니다 (발행 안 됨 또는 지연)'); return 1
    print('네이버 URL', url)
    import news_auto_poster as n
    ok = n.post_to_threads(cfg['threads_text'], [cfg['comment'].format(url=url)], image_url=None, topic_tag=cfg['topic_tag'])
    print('Threads 결과', ok)
    posts.append({'key': cfg['key'], 'title': cfg['title'], 'naver': url, 'tistory': cfg['tistory'], 'date': cfg['date']})
    json.dump(posts, open('blog_posts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    for cmd in (['gh', 'workflow', 'run', 'blog_reel_now.yml', '-f', f"module={cfg['reel_module']}"],
                ['gh', 'workflow', 'run', 'promo_1022_ig_post.yml', '-f', f"mode={cfg['ig_mode']}"]):
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(' '.join(cmd[:4]), '->', r.returncode, (r.stderr or r.stdout)[:120])
    return 0

if __name__ == '__main__':
    sys.exit(main())
