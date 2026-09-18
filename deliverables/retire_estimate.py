#!/usr/bin/env python3
"""
임원 퇴직금 한도 1장 — 확정 법령 기준
- 소득세법 임원 퇴직소득 한도: 퇴직 전 3년 평균급여 × 10% × (2020년 이후 근속 × 2 + 2012~2019 근속 × 3). 2011년 이전분은 없다고 가정.
- 정관(주총결의) 지급액 = 평균급여 × 10% × 총근속 × 배수. 정관 규정 없으면 법인세법 시행령 기준(1년 총급여 × 10% × 근속).
- 한도 초과분은 퇴직소득이 아니라 근로소득으로 과세.

입력 예: {"salary": 12000, "years": 15, "years_after_2020": 6.7, "multiple": 3}  (만원, 년)
"""
import os, sys, json
from onepager_render import render_numbers, fmt, NAVY, CORAL, EMERALD


def estimate(d):
    sal, yrs = d['salary'], d['years']
    after = min(d.get('years_after_2020', min(yrs, 6.7)), yrs)
    before = yrs - after
    limit = sal * 0.1 * (after * 2 + before * 3)
    mult = d.get('multiple', 2)
    if mult and mult > 0:
        pay = sal * 0.1 * yrs * mult; basis = f'정관 {mult}배'
    else:
        pay = sal * 0.1 * yrs; basis = '정관 규정 없음 → 법인세법 기준(1배)'
    excess = max(pay - limit, 0)
    safe_mult = limit / (sal * 0.1 * yrs) if yrs else 0
    return dict(limit=limit, pay=pay, excess=excess, basis=basis, after=after, before=before, safe_mult=safe_mult)


def render(d, out_dir=None, label=''):
    e = estimate(d)
    boxes = [('정관 기준 퇴직금', fmt(e['pay']), NAVY), ('퇴직소득 인정 한도', fmt(e['limit']), EMERALD), ('한도 초과 (근로소득 과세)', fmt(e['excess']), CORAL)]
    rows = [('퇴직 전 3년 평균 연봉', fmt(d['salary']), '급여·상여 포함'),
            ('총 근속연수', f"{d['years']}년", f"2020년 이후 {e['after']:.1f}년 · 이전 {e['before']:.1f}년"),
            ('지급 기준', e['basis'], '연봉 × 10% × 근속 × 배수'),
            ('정관 기준 퇴직금', fmt(e['pay']), '실제 지급 예정액'),
            ('소득세법 한도', fmt(e['limit']), '2020년 이후분 2배 · 2019년 이전분 3배'),
            ('한도 초과분', fmt(e['excess']), '퇴직소득 아님, 근로소득으로 과세')]
    tips = [f"현재 근속·연봉이면 정관 배수 {e['safe_mult']:.1f}배까지가 전액 퇴직소득 인정 범위" if d['years'] else '',
            '정관에 임원 퇴직금 지급 규정이 없으면 1배만 손금 인정 — 규정 정비가 먼저',
            '퇴직 직전 급여 인상은 3년 평균에 일부만 반영 — 미리 올려야 효과',
            '퇴직금 재원(현금)을 법인에 미리 쌓아두지 않으면 지급 시점에 자금 압박']
    note = ('※ 이 표는 소득세법상 임원 퇴직소득 한도와 정관 지급 기준만으로 계산한 "대략"입니다. 2011년 이전 근속분은 반영하지 않았습니다.\n'
            '※ 퇴직소득세·근로소득세 실제 세액, 4대보험, 법인 손금 인정 범위는 별도 계산이 필요합니다.\n'
            '※ 정확한 내용은 정관·주총 결의 내용과 함께 세무사와 확인하시기 바랍니다.')
    sub = (label or '댓글 기준') + f" · 연봉 {fmt(d['salary'])} · 근속 {d['years']}년"
    kw = {'out_dir': out_dir} if out_dir else {}
    return render_numbers('임원 퇴직금, 한도는 얼마일까', sub, boxes, '계산 흐름', rows,
                          [('확인할 점 (일반론)', [t for t in tips if t])], note,
                          f"임원퇴직금_{fmt(d['salary']).replace(' ', '')}_{d['years']}년", **kw)


if __name__ == '__main__':
    data = {"salary": 12000, "years": 15, "years_after_2020": 6.7, "multiple": 3}
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding='utf-8') as f:
            data = json.load(f)
    print(render(data))
