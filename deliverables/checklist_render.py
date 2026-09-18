#!/usr/bin/env python3
"""공통 렌더러: 체크리스트/점검표 형태의 A4 1장 (PNG+PDF). 상품·회사명 비노출."""
import os, textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
for fp in ['NanumGothicBold.ttf', 'NanumGothicExtraBold.ttf', 'NanumGothic.ttf']:
    font_manager.fontManager.addfont(os.path.join(ROOT, 'fonts', fp))
FONT = font_manager.FontProperties(fname=os.path.join(ROOT, 'fonts', 'NanumGothicBold.ttf')).get_name()
plt.rcParams['font.family'] = FONT
plt.rcParams['axes.unicode_minus'] = False

NAVY, CORAL, EMERALD, GRAY, LIGHT = '#0F1F3D', '#E8715A', '#3FA687', '#8B9BB4', '#F4F6F9'
OUT_DIR = os.path.join(BASE, 'out')


def render_checklist(title, subtitle, sections, note, out_name, intro=None, prepared_by='재무설계 상담'):
    """sections: [(heading, [item, ...]), ...]  item은 문자열(한 줄) 또는 (문자열, 보조설명)"""
    os.makedirs(OUT_DIR, exist_ok=True)
    fig = plt.figure(figsize=(8.27, 11.69), facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis('off'); ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    # 헤더
    ax.add_patch(FancyBboxPatch((0.06, 0.905), 0.88, 0.065, boxstyle='round,pad=0,rounding_size=0.008', color=NAVY))
    ax.text(0.085, 0.948, title, color='white', fontsize=17, fontweight='bold', va='center')
    ax.text(0.085, 0.921, subtitle, color='#D7DEE9', fontsize=9.5, va='center')

    y = 0.885
    if intro:
        for line in textwrap.wrap(intro, 62):
            ax.text(0.07, y, line, fontsize=9, color='#444', va='top'); y -= 0.02
        y -= 0.012

    for heading, items in sections:
        ax.add_patch(FancyBboxPatch((0.065, y - 0.021), 0.87, 0.026, boxstyle='round,pad=0,rounding_size=0.004', color=LIGHT))
        ax.text(0.08, y - 0.008, heading, fontsize=10.5, fontweight='bold', color=NAVY, va='center')
        y -= 0.036
        for it in items:
            main, sub = (it if isinstance(it, tuple) else (it, None))
            ax.add_patch(FancyBboxPatch((0.085, y - 0.0135), 0.013, 0.013, boxstyle='square,pad=0', facecolor='white', edgecolor=GRAY, lw=1))
            lines = textwrap.wrap(main, 58)
            for i, line in enumerate(lines):
                ax.text(0.108, y - 0.0025 - i * 0.017, line, fontsize=9.2, va='top', color='#222');
            y -= 0.017 * len(lines)
            if sub:
                for line in textwrap.wrap(sub, 68):
                    ax.text(0.108, y - 0.001, line, fontsize=7.8, va='top', color=GRAY); y -= 0.0148
            y -= 0.006
        y -= 0.010

    # 하단 노트
    ny = 0.075
    for line in note.split('\n'):
        ax.text(0.07, ny, line, fontsize=7.4, color='#666', va='top'); ny -= 0.014
    ax.text(0.93, 0.03, prepared_by, fontsize=8, color=GRAY, ha='right', va='bottom')

    png = os.path.join(OUT_DIR, out_name + '.png'); pdf = os.path.join(OUT_DIR, out_name + '.pdf')
    fig.savefig(png, dpi=170, facecolor='white'); fig.savefig(pdf, facecolor='white'); plt.close(fig)
    return png, pdf
