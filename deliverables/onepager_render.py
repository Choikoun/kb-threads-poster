#!/usr/bin/env python3
"""숫자 결과 1장 공통 렌더러 (헤더 + 핵심숫자 3칸 + 계산흐름 표 + 해설 + 유의사항). 상속세 1장과 같은 톤."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from checklist_render import NAVY, CORAL, EMERALD, GRAY, LIGHT, OUT_DIR, FONT  # 폰트 등록 부수효과


def fmt(n):
    n = int(round(n))
    if n == 0: return '0원'
    if n >= 10000:
        return f'{n//10000}억원' if n % 10000 == 0 else f'{n//10000}억 {n%10000:,}만원'
    return f'{n:,}만원'


def render_numbers(title, subtitle, boxes, table_title, rows, sections, note, out_name,
                   out_dir=OUT_DIR, prepared_by='재무설계 상담'):
    """boxes: [(label, value, color)]x3 · rows: [(항목, 금액문자열, 설명)] · sections: [(heading, [line,...])]"""
    os.makedirs(out_dir, exist_ok=True)
    fig = plt.figure(figsize=(8.27, 11.69), facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis('off'); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.add_patch(FancyBboxPatch((0.06, 0.905), 0.88, 0.065, boxstyle='round,pad=0,rounding_size=0.008', color=NAVY))
    ax.text(0.085, 0.948, title, color='white', fontsize=17, fontweight='bold', va='center')
    ax.text(0.085, 0.921, subtitle, color='#D7DEE9', fontsize=9.5, va='center')

    for i, (k, v, c) in enumerate(boxes):
        x = 0.06 + i * 0.295
        ax.add_patch(FancyBboxPatch((x, 0.80), 0.275, 0.08, boxstyle='round,pad=0,rounding_size=0.01', facecolor=LIGHT, edgecolor='none'))
        ax.text(x + 0.1375, 0.862, k, ha='center', fontsize=8.8, color=GRAY)
        ax.text(x + 0.1375, 0.826, v, ha='center', fontsize=15, fontweight='bold', color=c)

    ax.text(0.07, 0.765, table_title, fontsize=11, fontweight='bold', va='top')
    tb_ax = fig.add_axes([0.07, 0.50, 0.86, 0.245]); tb_ax.axis('off')
    tb = tb_ax.table(cellText=[[r[0], r[1], r[2]] for r in rows], colLabels=['항목', '금액', '설명'],
                     loc='upper center', bbox=[0, 0, 1, 1], cellLoc='left', colWidths=[0.28, 0.24, 0.48])
    tb.auto_set_font_size(False); tb.set_fontsize(8.8)
    for (r, c), cell in tb.get_celld().items():
        cell.set_edgecolor('#E3E7EE')
        if r == 0:
            cell.set_facecolor(NAVY); cell.set_text_props(color='white', fontweight='bold')
        elif r % 2 == 0:
            cell.set_facecolor(LIGHT)
        if c == 1 and r > 0:
            cell.set_text_props(fontweight='bold', color=CORAL if r == len(rows) else '#222')

    y = 0.46
    for heading, lines in sections:
        ax.text(0.07, y, heading, fontsize=11, fontweight='bold', va='top'); y -= 0.03
        for l in lines:
            ax.text(0.085, y, '• ' + l, fontsize=9, va='top', color='#333'); y -= 0.022
        y -= 0.012

    ny = 0.085
    for l in note.split('\n'):
        ax.text(0.07, ny, l, fontsize=7.3, color='#666', va='top'); ny -= 0.014
    ax.text(0.93, 0.03, prepared_by, fontsize=8, color=GRAY, ha='right', va='bottom')

    png = os.path.join(out_dir, out_name + '.png'); pdf = png[:-4] + '.pdf'
    fig.savefig(png, dpi=170, facecolor='white'); fig.savefig(pdf, facecolor='white'); plt.close(fig)
    return png, pdf
