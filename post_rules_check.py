#!/usr/bin/env python3
"""발행 전 SEO 규칙 점검(2026-10-20 사용자 전달 규칙 반영). 사용: python post_rules_check.py <naver.txt>
1) 제목 25~30자 목표, 키워드는 제목 맨 앞   2) 키워드가 본문 첫 두 문장 안(도입 인용 박스 줄 포함)
3) 태그는 짧은 단어 대신 구문형   4) '함께 보면 좋은 글'로 앞서 쓴 글 연결(관련 글 후보를 출력)
(제휴 2 : 정보 1 번갈아 올리기는 쇼핑 블로그용이라 KB에는 적용하지 않는다.)
오류 없이 권고만 낸다: 제목 길이처럼 근거가 약한 항목은 훅을 해치면서까지 맞추지 않는다."""
import re, sys, json, os
sys.stdout.reconfigure(encoding='utf-8')
D = os.path.dirname(os.path.abspath(__file__))
lines = open(sys.argv[1], encoding='utf-8').read().split('\n')
head, body = {}, []
sep = lines.index('---') if '---' in lines else 0
for l in lines[:sep]:
    m = re.match(r'(제목|키워드|카테고리|태그):\s*(.*)', l)
    if m: head[m[1]] = m[2].strip()
body = [l for l in lines[sep + 1:] if l.strip() and not l.startswith('[IMG')]
title, kw = head.get('제목', ''), head.get('키워드', '')
tags = [x.strip() for x in head.get('태그', '').split(',') if x.strip()]
warn = []
n = len(title)
if n > 32: warn.append(f'제목 {n}자 — 25~30자 목표(모바일에서 잘림). 키워드 + 핵심 한마디로 줄여 보세요')
elif n < 20: warn.append(f'제목 {n}자 — 25자 안팎으로 구체화')
if title.find(kw) > 3 or title.find(kw) < 0: warn.append(f'키워드 "{kw}"가 제목 맨 앞이 아님(위치 {title.find(kw)})')
# 첫 두 문장: 인용 박스 줄도 문장으로 센다
sents = []
for l in body:
    s = l.lstrip('> ').strip()
    sents += [x for x in re.split(r'(?<=[.?!])\s+', s) if x]
    if len(sents) >= 2: break
if not any(kw in s for s in sents[:2]): warn.append(f'키워드가 본문 첫 두 문장에 없음 — 도입 박스 첫 줄에 "{kw}"를 넣으세요')
short = [t for t in tags if len(t) <= 6]
if short: warn.append(f'태그가 짧은 단어형: {short} → "키워드 + 구체 문제" 구문형(예: {kw}환율, {kw}중도해지)')
if len(tags) < 5: warn.append(f'태그 {len(tags)}개 — 5개 채우기')
has_links = any('함께 보면 좋은 글' in l for l in body)
if not has_links: warn.append('"함께 보면 좋은 글" 섹션이 없음(앞서 쓴 글 2개 연결)')
for w in warn: print('  [권고]', w)
print(f'SEO 규칙 점검: 권고 {len(warn)}개')
# 관련 글 후보: 키워드·제목 단어가 겹치는 앞선 글
posts = json.load(open(os.path.join(D, 'blog_posts.json'), encoding='utf-8'))
words = set(re.findall(r'[가-힣A-Za-z0-9]{2,}', title + ' ' + ' '.join(tags)))
cand = []
for p in posts:
    if p.get('naver') and p['naver'] not in ' '.join(lines) and p['title'] != title:
        pw = set(re.findall(r'[가-힣A-Za-z0-9]{2,}', p['title']))
        sc = len(words & pw) + sum(1 for w in words if len(w) >= 3 and any(w[:2] == x[:2] for x in pw))
        if sc: cand.append((sc, p['date'], p))
cand.sort(key=lambda x: (-x[0], x[1]), reverse=False)
cand = [(c[0], c[2]) for c in cand]
if not has_links and cand:
    print('관련 글 후보(위에서 2개 고르기):')
    for sc, p in cand[:4]: print(f"  · [{p['title']}]({p['naver']})")
    print('붙여 넣을 형식(참고한 자료 뒤, [구분선] 앞):')
    print('  **함께 보면 좋은 글**')
    for sc, p in cand[:2]: print(f"  · [{p['title']}]({p['naver']})")
