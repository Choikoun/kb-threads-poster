#!/usr/bin/env python3
"""
증여세 대략 계산 1장 — 현행 확정 법령만 (개정안 반영 금지)
- 10년 합산 공제: 배우자 6억 · 직계존속→성인 자녀 5천만 · 미성년 2천만 · 직계비속→존속 5천만 · 기타친족 1천만 · 타인 0
- 혼인·출산 공제 1억(2024.1.1 이후, 직계존속→자녀), 세대생략 할증 30%(미성년·20억 초과 40%), 신고세액공제 3%
- 단순화: 10년 내 기증여에 대해 이미 쓴 공제·기납부세액은 없다고 가정(표기)

입력 예: {"amount": 50000, "relation": "adult_child", "prior": 0, "marriage": false, "skip": false}  (만원)
"""
import os, sys, json
from onepager_render import render_numbers, fmt, NAVY, CORAL, EMERALD

BRACKETS = [(10000, 0.10, 0), (50000, 0.20, 1000), (100000, 0.30, 6000), (300000, 0.40, 16000), (float('inf'), 0.50, 46000)]
RELATIONS = {
    'spouse': ('배우자', 60000), 'adult_child': ('성인 자녀', 5000), 'minor_child': ('미성년 자녀', 2000),
    'parent': ('부모(직계존속)', 5000), 'relative': ('기타 친족', 1000), 'other': ('타인', 0),
}


def estimate(d):
    rel_name, ded = RELATIONS[d['relation']]
    marriage = 10000 if d.get('marriage') and d['relation'] in ('adult_child', 'minor_child') else 0
    gross = d['amount'] + d.get('prior', 0)
    deduction = ded + marriage
    taxable = max(gross - deduction, 0)
    rate = cum = 0
    for limit, r, c in BRACKETS:
        if taxable <= limit:
            rate, cum = r, c; break
    tax = max(taxable * rate - cum, 0)
    surcharge = 0
    if d.get('skip'):
        surcharge = tax * (0.4 if d['relation'] == 'minor_child' and d['amount'] > 200000 else 0.3)
    final = (tax + surcharge) * 0.97
    remain = max(deduction - gross, 0)
    return dict(rel=rel_name, gross=gross, deduction=deduction, marriage=marriage, taxable=taxable,
                rate=rate, tax=tax, surcharge=surcharge, final=final, remain=remain)


def render(d, out_dir=None, label=''):
    e = estimate(d)
    boxes = [('증여재산 (10년 합산)', fmt(e['gross']), NAVY), ('공제 후 과세표준', fmt(e['taxable']), CORAL), ('예상 증여세 (대략)', fmt(e['final']), EMERALD)]
    rows = [('이번 증여액', fmt(d['amount']), f"{e['rel']}에게"),
            ('10년 내 기증여 합산', fmt(d.get('prior', 0)), '같은 사람에게서 받은 금액'),
            ('증여재산공제', '- ' + fmt(e['deduction']), f"{e['rel']} 공제" + (' + 혼인·출산 1억' if e['marriage'] else '')),
            ('과세표준', fmt(e['taxable']), f"세율 {int(e['rate']*100)}% 구간"),
            ('산출세액', fmt(e['tax']), '누진공제 반영')]
    if e['surcharge']:
        rows.append(('세대생략 할증', '+ ' + fmt(e['surcharge']), '조부모→손자녀 30%(미성년·20억 초과 40%)'))
    rows.append(('신고세액공제 3% 후', fmt(e['final']), '기한 내 신고 시'))
    tips = ['공제 한도 안에서 10년 단위로 나눠 증여하면 세금 없이 넘길 수 있음' if e['remain'] == 0 else f"공제 잔여 {fmt(e['remain'])} — 이 금액까지는 추가 증여해도 세금 0",
            '부동산은 시가 평가 방법에 따라 세액이 크게 달라짐 — 감정평가 여부 검토',
            '증여 후 10년 내 사망 시 상속재산에 합산되므로 상속 계획과 같이 볼 것',
            '증여세는 받는 사람이 내는 세금 — 세금 낼 돈까지 같이 주면 그것도 증여']
    note = ('※ 이 표는 현행 증여세법의 기본 구조(관계별 공제·누진세율·할증·신고세액공제)만으로 계산한 "대략"입니다.\n'
            '※ 10년 내 기증여에 대해 이미 적용한 공제와 기납부 증여세는 반영하지 않았습니다. 재산 평가 방법에 따라 실제 세액은 달라집니다.\n'
            '※ 국회 통과 전 개정안은 반영하지 않았습니다. 정확한 계산은 세무사와 확인하시기 바랍니다.')
    sub = (label or '댓글 기준') + f" · {e['rel']}에게 {fmt(d['amount'])}"
    kw = {'out_dir': out_dir} if out_dir else {}
    return render_numbers('증여세, 대략 얼마일까', sub, boxes, '계산 흐름', rows,
                          [('이 숫자를 줄이는 방향 (일반론)', tips)], note,
                          f"증여세대략_{e['rel']}_{fmt(d['amount']).replace(' ', '')}", **kw)


if __name__ == '__main__':
    data = {"amount": 50000, "relation": "adult_child", "prior": 0}
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding='utf-8') as f:
            data = json.load(f)
    print(render(data))
