#!/usr/bin/env python3
"""
연금 설계 1장 요약 — 상담 신청자에게 보내는 결과물 템플릿
- 숫자는 회사 설계 프로그램에서 뽑은 값을 넣는다 (이 스크립트는 계산기가 아니라 '포장').
- 상품명·회사명 비노출, 예시금액·공시이율 기준일·변동가능·중도해지 손실 문구 필수.

사용: python deliverables/annuity_onepager.py [입력.json]  (인자 없으면 아래 SAMPLE로 샘플 생성)
출력: deliverables/out/연금1장_<대상>.png 및 .pdf
"""
import os, sys, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
for name, fp in [('bold', 'NanumGothicBold.ttf'), ('extra', 'NanumGothicExtraBold.ttf'), ('reg', 'NanumGothic.ttf')]:
    font_manager.fontManager.addfont(os.path.join(ROOT, 'fonts', fp))
FONT = font_manager.FontProperties(fname=os.path.join(ROOT, 'fonts', 'NanumGothicBold.ttf')).get_name()
plt.rcParams['font.family'] = FONT
plt.rcParams['axes.unicode_minus'] = False

NAVY, CORAL, EMERALD, GRAY, LIGHT = '#0F1F3D', '#E8715A', '#3FA687', '#8B9BB4', '#F4F6F9'

SAMPLE = {
    "label": "34세 여성",
    "age": 34, "monthly_premium": 80, "pay_years": 7, "start_age": 65,
    "monthly_pension": 73.2, "annual_pension": 878, "total_to_100": 31609,
    "rate_note": "2026년 8월 공시이율 2.55%",
    "death_table": [["65세 (개시 직후)", 0, 8064], ["68세", 2634, 5430], ["70세", 4390, 3674],
                    ["72세", 6146, 1918], ["74세", 7902, 162], ["75세 이후", 8780, 0]],
    "prepared_by": "재무설계 상담"
}


def fmt(n):
    n = int(round(n))
    return f'{n//10000}억 {n%10000:,}만원' if n >= 10000 else f'{n:,}만원'


def render(d, out_dir=os.path.join(BASE, 'out')):
    os.makedirs(out_dir, exist_ok=True)
    total_paid = d['monthly_premium'] * 12 * d['pay_years']
    pay_end = d['age'] + d['pay_years']
    defer = d['start_age'] - pay_end
    yrs = list(range(0, 101 - d['start_age']))
    cum = [d['annual_pension'] * (y + 1) for y in yrs]
    be_idx = next((i for i, c in enumerate(cum) if c >= total_paid), None)
    be_age = d['start_age'] + be_idx if be_idx is not None else None

    fig = plt.figure(figsize=(8.27, 11.69), facecolor='white')
    gs = fig.add_gridspec(nrows=6, ncols=2, height_ratios=[0.9, 0.85, 0.5, 2.2, 2.4, 0.7],
                          hspace=0.45, wspace=0.3, left=0.07, right=0.93, top=0.96, bottom=0.04)

    # 1. 헤더
    ax = fig.add_subplot(gs[0, :]); ax.axis('off')
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle='round,pad=0,rounding_size=0.02', transform=ax.transAxes, color=NAVY))
    ax.text(0.03, 0.66, '연금 설계 1장 요약', transform=ax.transAxes, color='white', fontsize=19, fontweight='bold', va='center')
    ax.text(0.03, 0.28, f"{d['label']} · 월 {d['monthly_premium']}만원 · {d['pay_years']}년 납입 · {d['start_age']}세 개시",
            transform=ax.transAxes, color='#D7DEE9', fontsize=11, va='center')
    ax.text(0.97, 0.28, f"기준: {d['rate_note']}", transform=ax.transAxes, color='#AFC0D4', fontsize=8.5, va='center', ha='right')

    # 2. 핵심 숫자 3칸
    ax = fig.add_subplot(gs[1, :]); ax.axis('off')
    boxes = [('총 납입', fmt(total_paid), f"월 {d['monthly_premium']}만원 × {d['pay_years']*12}회", NAVY),
             (f"{d['start_age']}세부터 매달", f"약 {d['monthly_pension']:.0f}만원", f"연 약 {d['annual_pension']:,}만원", CORAL),
             ('100세까지 누적', fmt(d['total_to_100']), f"낸 돈의 {d['total_to_100']/total_paid:.1f}배", EMERALD)]
    for i, (k, v, s, c) in enumerate(boxes):
        x = i / 3 + 0.01
        ax.add_patch(FancyBboxPatch((x, 0.02), 1/3 - 0.02, 0.96, boxstyle='round,pad=0,rounding_size=0.03',
                                    transform=ax.transAxes, facecolor=LIGHT, edgecolor='none'))
        ax.text(x + 1/6 - 0.01, 0.76, k, transform=ax.transAxes, ha='center', fontsize=9.5, color=GRAY)
        ax.text(x + 1/6 - 0.01, 0.44, v, transform=ax.transAxes, ha='center', fontsize=16, fontweight='bold', color=c)
        ax.text(x + 1/6 - 0.01, 0.16, s, transform=ax.transAxes, ha='center', fontsize=8.5, color=GRAY)

    # 3. 타임라인
    ax = fig.add_subplot(gs[2, :]); ax.axis('off')
    pts = [(d['age'], '가입'), (pay_end, '납입완료'), (d['start_age'], '연금개시'), (100, '100세')]
    xs = [p[0] for p in pts]
    ax.plot([xs[0], xs[1]], [0.5, 0.5], color=NAVY, lw=6, solid_capstyle='round')
    ax.plot([xs[1], xs[2]], [0.5, 0.5], color=EMERALD, lw=6, alpha=0.5)
    ax.plot([xs[2], xs[3]], [0.5, 0.5], color=CORAL, lw=6, alpha=0.85)
    for x, lab in pts:
        ax.scatter([x], [0.5], s=60, color=NAVY, zorder=3, edgecolor='white', linewidth=1.5)
        ax.text(x, 0.92, f'{x}세', ha='center', fontsize=9.5, fontweight='bold')
        ax.text(x, 0.05, lab, ha='center', fontsize=8.5, color=GRAY)
    ax.text((xs[1]+xs[2])/2, 0.68, f'거치기간 약 {defer}년', ha='center', fontsize=9, color=EMERALD, fontweight='bold')
    ax.set_xlim(d['age'] - 3, 103); ax.set_ylim(0, 1.15)

    # 4-左. 누적 수령액 vs 납입원금
    ax = fig.add_subplot(gs[3, 0])
    ages = [d['start_age'] + y for y in yrs]
    colors = [NAVY if c < total_paid else EMERALD for c in cum]
    ax.bar(ages, cum, color=colors, width=0.8)
    ax.axhline(total_paid, ls='--', color=CORAL, lw=1.3)
    ax.text(ages[0] - 0.4, total_paid * 1.06, f'납입원금 {fmt(total_paid)}', fontsize=8, color=CORAL,
            fontweight='bold', ha='left', va='bottom')
    if be_age:
        ax.annotate(f'{be_age}세부터 원금 회수', xy=(be_age, cum[be_idx]), xytext=(be_age - 1, max(cum) * 0.62),
                    fontsize=8.5, fontweight='bold', color=EMERALD, ha='left',
                    arrowprops=dict(arrowstyle='->', color=EMERALD))
    ax.set_title('누적 수령액이 낸 돈을 넘는 시점', fontsize=10.5, fontweight='bold', pad=8)
    ax.set_xticks([d['start_age'], 75, 85, 95]); ax.set_xticklabels([f'{a}세' for a in [d['start_age'], 75, 85, 95]], fontsize=8)
    ax.spines[['top', 'right', 'left']].set_visible(False); ax.get_yaxis().set_visible(False)

    # 4-右. 사망 시점별 가족에게 남는 최저보장
    ax = fig.add_subplot(gs[3, 1])
    labels = [r[0].replace(' (', '\n(') for r in d['death_table']]
    left = [r[2] for r in d['death_table']]
    bars = ax.bar(range(len(left)), left, color=[NAVY if v > 2000 else (CORAL if v > 0 else GRAY) for v in left], width=0.6)
    for b, v in zip(bars, left):
        ax.text(b.get_x() + b.get_width()/2, v + max(left)*0.02, f'{v:,}' if v else '0', ha='center', fontsize=8, fontweight='bold')
    ax.set_xticks(range(len(left))); ax.set_xticklabels(labels, fontsize=7.5)
    ax.set_ylim(0, max(left) * 1.18)
    ax.set_title('사망 시점별 가족에게 남는 최저보장 (만원)', fontsize=10.5, fontweight='bold', pad=8)
    ax.spines[['top', 'right', 'left']].set_visible(False); ax.get_yaxis().set_visible(False)

    # 5. 사망보장 표 + 해설
    ax = fig.add_subplot(gs[4, :]); ax.axis('off')
    ax.text(0, 0.98, '연금 받는 도중 사망하면?', fontsize=11, fontweight='bold', va='top')
    ax.text(0, 0.86, f'이미 낸 보험료의 120%({fmt(total_paid*1.2)})에서 그동안 받은 연금을 뺀 금액이 가족에게 남습니다. '
                     '(실제 적립금이 더 크면 그 금액)', fontsize=8.8, va='top', color='#333')
    cell = [[r[0], f'{r[1]:,}만원' if r[1] else '0원', f'{r[2]:,}만원' if r[2] else '0원'] for r in d['death_table']]
    tb = ax.table(cellText=cell, colLabels=['사망 시 나이', '그동안 받은 연금', '가족에게 남는 금액'],
                  loc='upper center', bbox=[0.0, 0.05, 1.0, 0.72], cellLoc='center')
    tb.auto_set_font_size(False); tb.set_fontsize(8.8)
    for (r, c), cellobj in tb.get_celld().items():
        cellobj.set_edgecolor('#E3E7EE')
        if r == 0:
            cellobj.set_facecolor(NAVY); cellobj.set_text_props(color='white', fontweight='bold')
        elif r % 2 == 0:
            cellobj.set_facecolor(LIGHT)

    # 6. 유의사항
    ax = fig.add_subplot(gs[5, :]); ax.axis('off')
    note = (f"※ 위 금액은 {d['rate_note']} 기준 예시금액이며, 공시이율은 매월 변동되어 실제 수령액은 달라질 수 있습니다.\n"
            "※ 중도 해지 시 해약환급금이 납입한 보험료보다 적을 수 있습니다. 연금 개시 전 사망 시 지급 기준은 별도입니다.\n"
            "※ 정확한 내용은 상품설명서·약관을 확인하시기 바랍니다.")
    ax.text(0, 0.95, note, fontsize=7.6, color='#666', va='top', linespacing=1.6)
    ax.text(1, 0.02, d.get('prepared_by', ''), fontsize=8, color=GRAY, ha='right', va='bottom', transform=ax.transAxes)

    safe = d['label'].replace(' ', '_')
    png = os.path.join(out_dir, f'연금1장_{safe}.png'); pdf = png[:-4] + '.pdf'
    fig.savefig(png, dpi=170, facecolor='white'); fig.savefig(pdf, facecolor='white')
    plt.close(fig)
    return png, pdf


if __name__ == '__main__':
    data = SAMPLE
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding='utf-8') as f:
            data = json.load(f)
    print(render(data))
