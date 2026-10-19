#!/usr/bin/env python3
"""사실 누락 점검기 — 사실자료(_facts_*.txt)의 숫자·날짜가 원고(naver.txt)에 반영됐는지, 필수 안내 장치가 있는지 확인한다.
사용: python fact_coverage_check.py <사실자료.txt> <원고.txt>
근거(2026-10-19 스터디 research/ai_omission_study.md): 누락은 환각과 다른 실패 유형이고 모델의 자기 점검으로는 잘 안 잡힌다 →
사실을 원자 단위(숫자·날짜)로 뽑아 원고와 대조(recall)하고, 필수 항목은 명시 체크리스트로 확인한다.
'빠진 숫자'가 의도적 제외(글에 쓰지 않기로 한 것)면 무시하고, 아니면 원고에 반영한다."""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
facts = open(sys.argv[1], encoding='utf-8').read()
draft = open(sys.argv[2], encoding='utf-8').read()
body = draft.split('\n---\n', 1)[-1]
facts_nourl = re.sub(r'https?://\S+', '', facts)
NUM = re.compile(r'\d{4}-\d{2}-\d{2}|\d[\d,\.]*\s?(?:만|억|천)?\s?(?:건|원|%|년|월|일|배|세|개|명|회|달러)?')
norm = lambda s: re.sub(r'[\s,]', '', s)
body_n = norm(body)
want = []
for m in NUM.finditer(facts_nourl):
    t = m.group(0).strip()
    if re.fullmatch(r'\d{1,2}', t) or len(norm(t)) < 2:
        continue
    want.append(t)
seen, missing = set(), []
for t in want:
    k = norm(t)
    if k in seen: continue
    seen.add(k)
    forms = {k, k.replace('2026-', '2026년').replace('-', '')}
    y = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', k)
    if y:
        forms |= {f'{y[1]}년{int(y[2])}월{int(y[3])}일', f'{y[1]}년{int(y[2])}월'}
    n = re.fullmatch(r'(\d+)(건|원|명|개|회|달러)?', k)
    if n and int(n[1]) >= 10000:
        v, u = int(n[1]), n[2] or ''
        forms |= {f'{v // 10000}만{v % 10000}{u}', f'{v // 10000}만{v % 10000:,}{u}'.replace(',', '')}
        if v % 10000 == 0: forms.add(f'{v // 10000}만{u}')
    if not any(f in body_n for f in forms):
        missing.append(t)
print(f'사실자료 숫자 {len(seen)}개 중 원고에 없는 것 {len(missing)}개')
for t in missing: print('  [빠짐?]', t)
CHECK = [
    ('출처 링크 [표시문구](주소)', r'\]\(https?://'),
    ('가정·설명용 표시', r'가정|설명용'),
    ('가입 권유 아님 문구', r'권유하지 않'),
    ('확인하지 못한 항목 명시', r'확인하지 못'),
    ('위험·손실 가능성 언급', r'손실|줄 수 있|못 미칠|위험'),
    ('가입 전 확인 항목', r'가입 전|상품설명서|약관'),
]
print('필수 장치 점검')
for name, pat in CHECK:
    print(('  [OK] ' if re.search(pat, body) else '  [없음] ') + name)
