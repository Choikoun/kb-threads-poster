#!/usr/bin/env python3
"""
종신보험 활용 시나리오 1장 — 신청자 설계서 숫자를 넣어 만드는 개인 결과물
- 숫자(보험료·사망보험금·연차별 해약환급금)는 회사 설계 프로그램 값을 그대로 입력. 이 스크립트는 계산하지 않고 '포장'만 한다.
- 상품명·회사명 비노출. 해약환급금은 시점에 따라 납입액보다 적을 수 있음을 반드시 표기.

사용: python deliverables/jongsin_scenario.py [입력.json]
입력 예: {"label": "40세 남성", "monthly_premium": 50, "pay_years": 10, "death_benefit": 20000,
          "rows": [[5, 3000, 2100], [10, 6000, 5400], [15, 6000, 6300], [20, 6000, 7200], [25, 6000, 8100]],   # [경과연차, 납입누계, 해약환급금] (만원)
          "scenarios": [["자녀 대학 입학 (15년 후)", 15], ["은퇴 시점 (25년 후)", 25]], "rate_note": "2026년 8월 설계 기준"}
"""
import os, sys, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from checklist_render import NAVY, CORAL, EMERALD, GRAY, LIGHT, OUT_DIR, FONT

SAMPLE = {"label": "예시: 40세 남성", "monthly_premium": 50, "pay_years": 10, "death_benefit": 20000,
          "rows": [[5, 3000, 2100], [10, 6000, 5400], [15, 6000, 6300], [20, 6000, 7200], [25, 6000, 8100]],
          "scenarios": [["자녀 대학 입학 시점 (15년 후)", 15], ["은퇴 시점 (25년 후)", 25]],
          "rate_note": "설계서 예시 숫자 (실제 설계값으로 교체 필요)"}


def fmt(n):
    n = int(round(n))
    if n >= 10000:
        return f'{n//10000}억원' if n % 10000 == 0 else f'{n//10000}억 {n%10000:,}만원'
    return f'{n:,}만원'


def render(d, out_dir=OUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    rows = d['rows']; years = [r[0] for r in rows]; paid = [r[1] for r in rows]; cv = [r[2] for r in rows]
    total_paid = d['monthly_premium'] * 12 * d['pay_years']

    fig = plt.figure(figsize=(8.27, 11.69), facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis('off'); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.add_patch(FancyBboxPatch((0.06, 0.905), 0.88, 0.065, boxstyle='round,pad=0,rounding_size=0.008', color=NAVY))
    ax.text(0.085, 0.948, '종신보험, 이렇게 쓸 수 있습니다', color='white', fontsize=17, fontweight='bold', va='center')
    ax.text(0.085, 0.921, f"{d['label']} · 월 {d['monthly_premium']}만원 · {d['pay_years']}년 납입 · 사망보장 {fmt(d['death_benefit'])}", color='#D7DEE9', fontsize=9.5, va='center')
    ax.text(0.935, 0.921, f"기준: {d['rate_note']}", color='#AFC0D4', fontsize=7.5, va='center', ha='right')

    boxes = [('총 납입', fmt(total_paid), NAVY), ('사망보장 (가입 즉시)', fmt(d['death_benefit']), CORAL), (f'{years[-1]}년 후 해약환급금', fmt(cv[-1]), EMERALD)]
    for i, (k, v, c) in enumerate(boxes):
        x = 0.06 + i * 0.295
        ax.add_patch(FancyBboxPatch((x, 0.80), 0.275, 0.08, boxstyle='round,pad=0,rounding_size=0.01', facecolor=LIGHT, edgecolor='none'))
        ax.text(x + 0.1375, 0.862, k, ha='center', fontsize=8.8, color=GRAY)
        ax.text(x + 0.1375, 0.826, v, ha='center', fontsize=15, fontweight='bold', color=c)

    # 납입누계 vs 해약환급금
    axc = fig.add_axes([0.10, 0.50, 0.80, 0.25])
    axc.plot(years, paid, color=GRAY, lw=2.2, marker='o', label='납입 누계')
    axc.plot(years, cv, color=EMERALD, lw=2.6, marker='o', label='해약환급금')
    for x, p, c in zip(years, paid, cv):
        axc.text(x, c + max(cv) * 0.03, f'{c:,}', ha='center', fontsize=8, color=EMERALD, fontweight='bold')
    for name, yr in d.get('scenarios', []):
        if yr in years:
            axc.axvline(yr, color=CORAL, ls='--', lw=1); axc.text(yr, max(cv) * 1.16, name, ha='center', fontsize=7.8, color=CORAL, fontweight='bold')
    axc.set_ylim(0, max(max(cv), max(paid)) * 1.28); axc.set_xticks(years); axc.set_xticklabels([f'{y}년' for y in years], fontsize=9)
    axc.spines[['top', 'right', 'left']].set_visible(False); axc.get_yaxis().set_visible(False)
    axc.legend(frameon=False, fontsize=9, loc='upper left')
    axc.set_title('낸 돈과 돌려받을 수 있는 돈의 흐름 (만원)', fontsize=10.5, fontweight='bold', pad=8)

    y = 0.44
    ax.text(0.07, y, '세 가지 쓰임새', fontsize=11, fontweight='bold', va='top'); y -= 0.032
    cv_by_year = {r[0]: r[2] for r in rows}
    nums = '①②③④⑤⑥'
    uses = [f"사망보장: 가입 직후부터 {fmt(d['death_benefit'])}. 가족 생활비·부채·교육비 공백을 막는 기본 기능입니다."]
    for name, yr in d.get('scenarios', []):
        if yr in cv_by_year:
            uses.append(f"{name}: 해약환급금 약 {fmt(cv_by_year[yr])}을 목돈으로 쓰거나(일부 인출·해지), 보장을 유지한 채 대출로 활용할 수 있습니다.")
    uses.append('은퇴 후: 환급금을 연금 형태로 바꾸는 선택지가 있는 상품도 있습니다(상품별 상이).')
    uses = [f'{nums[i]} {u}' for i, u in enumerate(uses)]
    for u in uses:
        import textwrap
        for i, line in enumerate(textwrap.wrap(u, 60)):
            ax.text(0.085 if i == 0 else 0.10, y, line, fontsize=9.1, va='top', color='#222'); y -= 0.02
        y -= 0.008

    y -= 0.01
    ax.text(0.07, y, '꼭 같이 봐야 할 것', fontsize=11, fontweight='bold', va='top'); y -= 0.03
    for l in ['초기 몇 년은 해약환급금이 납입액보다 적습니다 — 위 표에서 언제 넘어서는지 확인하세요.',
              '중간에 돈을 빼면(인출·해지) 사망보장이 줄거나 없어질 수 있습니다.',
              '"교육자금·은퇴자금 활용"은 보장을 유지한 상태에서의 선택지이지, 저축상품이 아닙니다.']:
        ax.text(0.085, y, '• ' + l, fontsize=9, va='top', color='#333'); y -= 0.022

    note = (f"※ 위 숫자는 {d['rate_note']}이며, 실제 해약환급금·보장금액은 설계서와 약관에 따릅니다.\n"
            '※ 해약환급금은 시점에 따라 납입한 보험료보다 적을 수 있습니다.\n'
            '※ 특정 상품의 가입을 권유하는 자료가 아니며, 가입 전 상품설명서·약관을 반드시 확인하시기 바랍니다.')
    ny = 0.085
    for l in note.split('\n'):
        ax.text(0.07, ny, l, fontsize=7.3, color='#666', va='top'); ny -= 0.014
    ax.text(0.93, 0.03, d.get('prepared_by', '재무설계 상담'), fontsize=8, color=GRAY, ha='right', va='bottom')

    safe = d['label'].replace(' ', '_').replace(':', '')[:20]
    png = os.path.join(out_dir, f'종신시나리오_{safe}.png'); pdf = png[:-4] + '.pdf'
    fig.savefig(png, dpi=170, facecolor='white'); fig.savefig(pdf, facecolor='white'); plt.close(fig)
    return png, pdf


if __name__ == '__main__':
    data = SAMPLE
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding='utf-8') as f:
            data = json.load(f)
    print(render(data))
