#!/usr/bin/env python3
"""
상속세 대략 계산 1장 — 신청자 숫자를 넣어 만드는 개인 결과물
- 현행 상속세법의 확정된 기본 구조만 사용(일괄공제 5억, 배우자상속공제 최소 5억·최대 30억(법정상속분 한도), 누진세율, 신고세액공제 3%).
- 금융재산공제·동거주택공제·가업상속공제·사전증여 합산 등은 반영하지 않는 '대략'임을 명시한다. 개정안(미확정)은 절대 반영하지 않는다.

사용: python deliverables/inheritance_estimate.py [입력.json]
입력 예: {"label": "서울 아파트 한 채 + 예금", "assets": 150000, "spouse": true, "children": 2, "debts": 20000}  (단위: 만원)
"""
import os, sys, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from checklist_render import NAVY, CORAL, EMERALD, GRAY, LIGHT, OUT_DIR, FONT  # 폰트 등록 부수효과 포함

BRACKETS = [(10000, 0.10, 0), (50000, 0.20, 1000), (100000, 0.30, 6000), (300000, 0.40, 16000), (float('inf'), 0.50, 46000)]

SAMPLE = {"label": "예시: 서울 아파트 한 채 + 예금", "assets": 150000, "spouse": True, "children": 2, "debts": 20000}


def fmt(n):
    n = int(round(n))
    if n == 0: return '0원'
    if n >= 10000:
        return f'{n//10000}억원' if n % 10000 == 0 else f'{n//10000}억 {n%10000:,}만원'
    return f'{n:,}만원'


def estimate(d):
    net = max(d['assets'] - d.get('debts', 0), 0)
    lump = 50000                                # 일괄공제 5억
    spouse_ded = 0
    if d.get('spouse'):
        heirs = 1 + d.get('children', 0)
        legal_share = net * 1.5 / (1.5 + d.get('children', 0)) if heirs > 1 else net   # 배우자 법정상속분(1.5 : 1 ...)
        spouse_ded = min(max(legal_share, 50000), 300000)   # 최소 5억, 최대 30억
    taxable = max(net - lump - spouse_ded, 0)
    rate = cum = 0
    for limit, r, c in BRACKETS:
        if taxable <= limit:
            rate, cum = r, c; break
    tax = max(taxable * rate - cum, 0)
    tax_after = tax * 0.97                       # 신고세액공제 3%
    return dict(net=net, lump=lump, spouse_ded=spouse_ded, taxable=taxable, rate=rate, tax=tax, tax_after=tax_after)


def render(d, out_dir=OUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    e = estimate(d)
    fig = plt.figure(figsize=(8.27, 11.69), facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis('off'); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.add_patch(FancyBboxPatch((0.06, 0.905), 0.88, 0.065, boxstyle='round,pad=0,rounding_size=0.008', color=NAVY))
    ax.text(0.085, 0.948, '우리 집 상속세, 대략 얼마일까', color='white', fontsize=17, fontweight='bold', va='center')
    ax.text(0.085, 0.921, f"{d['label']} · 배우자 {'있음' if d.get('spouse') else '없음'} · 자녀 {d.get('children', 0)}명", color='#D7DEE9', fontsize=9.5, va='center')

    # 핵심 숫자 3칸
    boxes = [('순재산 (재산 - 채무)', fmt(e['net']), NAVY), ('공제 후 과세표준', fmt(e['taxable']), CORAL), ('예상 상속세 (대략)', fmt(e['tax_after']), EMERALD)]
    for i, (k, v, c) in enumerate(boxes):
        x = 0.06 + i * 0.295
        ax.add_patch(FancyBboxPatch((x, 0.80), 0.275, 0.08, boxstyle='round,pad=0,rounding_size=0.01', facecolor=LIGHT, edgecolor='none'))
        ax.text(x + 0.1375, 0.862, k, ha='center', fontsize=8.8, color=GRAY)
        ax.text(x + 0.1375, 0.826, v, ha='center', fontsize=15, fontweight='bold', color=c)

    # 계산 흐름 (폭포)
    steps = [('재산', d['assets']), ('- 채무', -d.get('debts', 0)), ('- 일괄공제', -e['lump']), ('- 배우자공제', -e['spouse_ded']), ('= 과세표준', e['taxable'])]
    axc = fig.add_axes([0.10, 0.50, 0.80, 0.25])
    running = 0; xs = range(len(steps))
    for i, (lab, val) in enumerate(steps):
        if lab.startswith('='):
            axc.bar(i, val, color=CORAL, width=0.6); top = val
        else:
            bottom = running if val >= 0 else running + val
            axc.bar(i, abs(val), bottom=bottom, color=NAVY if val >= 0 else GRAY, width=0.6)
            running += val; top = max(running, running - val)
        axc.text(i, top + d['assets'] * 0.02, fmt(abs(val)), ha='center', fontsize=8.5, fontweight='bold')
    axc.set_xticks(list(xs)); axc.set_xticklabels([s[0] for s in steps], fontsize=9)
    axc.spines[['top', 'right', 'left']].set_visible(False); axc.get_yaxis().set_visible(False)
    axc.set_title('재산에서 공제를 빼면 과세표준이 남습니다', fontsize=10.5, fontweight='bold', pad=8)

    # 세율 설명
    y = 0.44
    ax.text(0.07, y, '세율 적용', fontsize=11, fontweight='bold', va='top'); y -= 0.03
    lines = [
        f"과세표준 {fmt(e['taxable'])}에 세율 {int(e['rate']*100)}% 구간이 적용됩니다.",
        f"산출세액 약 {fmt(e['tax'])} → 기한 내 신고 시 3% 공제 → 약 {fmt(e['tax_after'])}",
        '상속세율: 1억 이하 10% · 5억 이하 20% · 10억 이하 30% · 30억 이하 40% · 30억 초과 50% (누진)',
    ]
    for l in lines:
        ax.text(0.07, y, l, fontsize=9.2, va='top', color='#222'); y -= 0.024

    y -= 0.012
    ax.text(0.07, y, '이 숫자를 줄이는 방향 (일반론)', fontsize=11, fontweight='bold', va='top'); y -= 0.03
    for l in ['사전 증여로 재산을 미리 나누되, 10년 합산 규정을 감안해 시기를 정하기',
              '상속세 낼 현금(납부 재원)을 어디서 마련할지 미리 정하기 — 부동산만 있으면 급매 위험',
              '배우자 상속분·자녀 배분을 미리 합의해 공제를 최대한 활용하기',
              '금융재산공제·동거주택공제 등 추가 공제 해당 여부 확인하기(이 표에는 미반영)']:
        ax.text(0.085, y, '• ' + l, fontsize=9, va='top', color='#333'); y -= 0.022

    note = ('※ 이 표는 현행 상속세법의 기본 구조(일괄공제·배우자공제·누진세율·신고세액공제)만으로 계산한 "대략"입니다.\n'
            '※ 금융재산공제·동거주택공제·가업상속공제, 10년 내 사전증여 합산, 재산 평가 방법 등에 따라 실제 세액은 크게 달라질 수 있습니다.\n'
            '※ 국회 통과 전 개정안은 반영하지 않았습니다. 정확한 계산은 세무사와 확인하시기 바랍니다.')
    ny = 0.085
    for l in note.split('\n'):
        ax.text(0.07, ny, l, fontsize=7.3, color='#666', va='top'); ny -= 0.014
    ax.text(0.93, 0.03, d.get('prepared_by', '재무설계 상담'), fontsize=8, color=GRAY, ha='right', va='bottom')

    safe = d['label'].replace(' ', '_').replace(':', '')[:20]
    png = os.path.join(out_dir, f'상속세대략_{safe}.png'); pdf = png[:-4] + '.pdf'
    fig.savefig(png, dpi=170, facecolor='white'); fig.savefig(pdf, facecolor='white'); plt.close(fig)
    return png, pdf


if __name__ == '__main__':
    data = SAMPLE
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding='utf-8') as f:
            data = json.load(f)
    print(render(data))
