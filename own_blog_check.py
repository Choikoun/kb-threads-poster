#!/usr/bin/env python3
"""키워드를 정하기 전에 우리 네이버 블로그(sobok__biz)에 이미 쓴 글이 있는지 확인(2026-10-21: blog_posts.json에는 10월 이전 글이 없어 가지급금 글 3개를 놓칠 뻔함).
사용: python own_blog_check.py 가지급금 [키워드2 ...]
방법: 네이버 블로그탭에서 '<키워드> sobok__biz'를 검색해 우리 블로그 글을 모으고 제목·작성일을 출력한다. 네이버는 같은 블로그의 비슷한 글을 묶어 낮출 수 있어 같은 키워드 글은 각도를 확실히 다르게 쓴다."""
import re, sys, html, urllib.parse, requests
sys.stdout.reconfigure(encoding='utf-8')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/150 Safari/537.36'}
for kw in sys.argv[1:]:
    h = requests.get('https://search.naver.com/search.naver?ssc=tab.blog.all&sm=tab_opt&query=' + urllib.parse.quote(f'{kw} sobok__biz'), headers=UA, timeout=20).text
    ids = []
    for m in re.finditer(r'blog\.naver\.com/sobok__biz/(\d{9,})', h):
        if m.group(1) not in ids: ids.append(m.group(1))
    print(f'== {kw}: 우리 글 {len(ids)}개')
    for ln in ids:
        t = requests.get(f'https://blog.naver.com/PostView.naver?blogId=sobok__biz&logNo={ln}', headers=UA, timeout=20).text
        ti = re.search(r'<title>(.*?)</title>', t, re.S); d = re.search(r'se_publishDate[^>]*>([^<]+)<', t)
        print('  ', ln, '|', html.unescape(ti.group(1)).replace(' : 네이버 블로그', '').strip()[:60] if ti else '?', '|', d.group(1) if d else '')
