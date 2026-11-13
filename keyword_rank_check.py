#!/usr/bin/env python3
"""키워드별 네이버 블로그 검색 순위 추적. 상위(10위 안)였던 키워드가 연속 2회 빠지면 '재작성 후보'로 표시.
사용: python keyword_rank_check.py [--build]   (--build: blog_posts.json·naver.txt에서 키워드 목록 새로 만들기)
"""
import sys, re, json, glob, os, time, urllib.parse
from datetime import datetime, timezone, timedelta
sys.stdout.reconfigure(encoding='utf-8')
import requests

KST = timezone(timedelta(hours=9))
REG, LOG, CAND = 'keyword_registry.json', 'keyword_rank_log.json', 'rewrite_candidates.md'
H = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148'}
TOP = 10
MIN_AGE_DAYS = 30

def build_registry():
    reg = {}
    if os.path.exists(REG):
        reg = {r['logNo']: r for r in json.load(open(REG, encoding='utf-8'))}
    for p in json.load(open('blog_posts.json', encoding='utf-8')):
        if p['date'] < '2026-09-18':
            continue
        log_no = p['naver'].rstrip('/').split('/')[-1]
        if log_no in reg:
            continue
        kw = ''
        for f in glob.glob(f"blog_images/{p['date']}_*/naver.txt"):
            t = open(f, encoding='utf-8').read()
            if p['title'] in t.split('\n')[0]:
                m = re.search(r'^키워드:\s*(.+)$', t, re.M)
                kw = m.group(1).strip() if m else ''
        if not kw:
            kw = p['title'].split(',')[0].strip()
        reg[log_no] = {'logNo': log_no, 'keyword': kw, 'title': p['title'], 'date': p['date'], 'key': p['key']}
    json.dump(list(reg.values()), open(REG, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    return list(reg.values())

def rank_of(keyword, log_no):
    url = 'https://m.search.naver.com/search.naver?ssc=tab.m_blog.all&query=' + urllib.parse.quote(keyword)
    html = requests.get(url, headers=H, timeout=20).text
    ids, seen = re.findall(r'blog\.naver\.com/([A-Za-z0-9_]+)/(\d{9,})', html), []
    for blog, no in ids:
        if no not in seen:
            seen.append(no)
    return (seen.index(log_no) + 1) if log_no in seen else None, len(seen)

def integrated_rank(keyword, log_no):
    """통합검색(실제 유입 경로) 화면에서 블로그 링크 출현 순서. 근사치."""
    url = 'https://m.search.naver.com/search.naver?query=' + urllib.parse.quote(keyword)
    html = requests.get(url, headers=H, timeout=20).text
    seen = []
    for blog, no in re.findall(r'blog\.naver\.com/([A-Za-z0-9_]+)/(\d{9,})', html):
        if no not in seen:
            seen.append(no)
    return (seen.index(log_no) + 1) if log_no in seen else None

def main():
    reg = build_registry() if ('--build' in sys.argv or not os.path.exists(REG)) else json.load(open(REG, encoding='utf-8'))
    log = json.load(open(LOG, encoding='utf-8')) if os.path.exists(LOG) else {}
    today = datetime.now(KST).strftime('%Y-%m-%d')
    cands = []
    for r in reg:
        try:
            rank, n = rank_of(r['keyword'], r['logNo'])
        except Exception as e:
            print('오류', r['keyword'], str(e)[:60]); continue
        h = log.setdefault(r['logNo'], [])
        try:
            ir = integrated_rank(r['keyword'], r['logNo'])
        except Exception:
            ir = None
        h[:] = [x for x in h if x['d'] != today] + [{'d': today, 'rank': rank, 'n': n, 'ir': ir}]
        ranks = [x['rank'] for x in h]
        was_top = any(x is not None and x <= TOP for x in ranks)
        streak = 0
        for x in reversed(ranks):
            if x is None or x > TOP: streak += 1
            else: break
        age = (datetime.now(KST).date() - datetime.strptime(r['date'], '%Y-%m-%d').date()).days
        # 같은 키워드로 너무 자주 쓰면 중복·자기잠식 위험이 있어, 기존 글이 30일 이상 지난 뒤에만 후보로 올린다.
        if was_top and streak >= 1 and age >= MIN_AGE_DAYS:
            cands.append((r, rank, 'confirmed' if streak >= 2 else 'watch', streak))
        time.sleep(0.4)
    json.dump(log, open(LOG, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False)
    top = sum(1 for r in reg if log.get(r['logNo']) and log[r['logNo']][-1]['rank'] and log[r['logNo']][-1]['rank'] <= TOP)
    itop = sum(1 for r in reg if log.get(r['logNo']) and log[r['logNo']][-1].get('ir') and log[r['logNo']][-1]['ir'] <= 10)
    print(f'{today} 키워드 {len(reg)}개 중 블로그탭 {TOP}위 안 {top}개, 통합검색 블로그 10번째 안 {itop}개')
    lines = [f'# 재작성 후보 ({today})', '', f'{TOP}위 안에 있다가 빠진 키워드입니다. confirmed는 연속 2회 이상 빠진 것, watch는 이번에 처음 빠진 것입니다.', '']
    for r, rank, st, _ in cands:
        lines.append(f"- [{st}] {r['keyword']} (현재 {'순위 밖' if rank is None else str(rank) + '위'}, 기존 글 {r['date']} {r['title']})")
    if not cands:
        lines.append('- 해당 없음')
    open(CAND, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
    body = [f"{r['keyword']} ({r['date']} {r['title']})" for r, rank, st, sk in cands if sk == 2]
    with open('new_confirmed.txt', 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(body))
    for r, rank, st, sk in cands:
        print('후보', st, r['keyword'], rank)

if __name__ == '__main__':
    main()
