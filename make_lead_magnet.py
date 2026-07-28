#!/usr/bin/env python3
"""
리드 마그넷 제작: 상속·증여 사전점검 체크리스트 12 (PNG 2장 + PDF)
- 상담 전환 다리(2026-07-28): 무료 자료 → 댓글 '점검' → DM 발송(수동) 퍼널의 실물
- 내용은 장기 확정 법령만 사용 (미확정 개정안 금지 원칙 준수)
- 수정 후 재실행하면 lead_magnet/ 산출물이 갱신됨
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')

W, H = 1080, 1528
MARGIN = 72
COLORS = {
    'bg': (10, 22, 40),        # #0A1628
    'card': (15, 31, 61),      # #0F1F3D
    'accent': (245, 200, 66),  # #F5C842
    'white': (255, 255, 255),
    'gray': (139, 155, 180),   # #8B9BB4
    'divider': (30, 58, 95),   # #1E3A5F
}

OUT_DIR = 'lead_magnet'


def font(weight, size):
    path = {
        'regular': 'fonts/NanumGothic.ttf',
        'bold': 'fonts/NanumGothicBold.ttf',
        'extrabold': 'fonts/NanumGothicExtraBold.ttf',
    }[weight]
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ''
    for word in text.split(' '):
        trial = f'{cur} {word}'.strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# (그룹, [(항목, 부연)]) — 전부 장기 확정 법령·일반 원칙만
CHECKLIST = [
    ('증여 이력', [
        ('최근 10년 내 가족 간 증여를 날짜·금액까지 정리해뒀다',
         '증여세는 10년 단위로 합산 과세된다'),
        ('가족 간 계좌이체에 성격을 증명할 기록(메모·차용증)이 있다',
         '국세청은 서류가 아니라 돈의 흐름을 본다'),
        ('10년 주기 증여 플랜을 세워뒀다',
         '증여재산공제는 10년마다 다시 쓸 수 있다'),
    ]),
    ('재산 파악', [
        ('상속재산 목록(부동산·예금·주식·보험)을 한 곳에 정리해뒀다',
         '가족이 몰랐던 재산은 기한 내 신고를 어렵게 만든다'),
        ('채무·보증 목록도 함께 정리했다',
         '빚도 상속된다 — 몰랐던 보증이 분쟁의 시작'),
        ('사망보험금 수익자 지정을 최근에 확인했다',
         '수익자가 누구로 되어 있느냐가 돈의 행선지를 정한다'),
    ]),
    ('가족 합의', [
        ('유언장이 법적 형식 요건을 갖췄는지 확인했다',
         '자필 유언은 전문·날짜·주소·성명 자필 + 날인이 없으면 무효'),
        ('부양·간병 기여를 가족끼리 문서로 남겼다',
         '말로 한 약속은 법정에서 힘이 없다'),
        ('형제간 사전증여 내역을 서로 알고 있다',
         '몰랐던 증여가 드러나는 순간 가족 소송이 시작된다'),
    ]),
    ('세금 준비', [
        ('상속세 신고기한(사망월 말일부터 6개월)을 알고 있다',
         '기한을 넘기면 가산세가 붙는다'),
        ('상속세 낼 현금이 어디서 나올지 계산해봤다',
         '재산이 부동산뿐이면 세금 낼 돈이 없는 경우가 많다'),
        ('배우자 상속공제 등 기본 공제 구조를 분할 계획에 반영했다',
         '같은 재산도 나누는 방법에 따라 세금이 달라진다'),
    ]),
]


def draw_header(d, page_no):
    d.rectangle([0, 0, W, 12], fill=COLORS['accent'])
    y = MARGIN + 10
    if page_no == 1:
        d.text((MARGIN, y), '상속·증여', font=font('extrabold', 58), fill=COLORS['accent'])
        y += 74
        d.text((MARGIN, y), '사전점검 체크리스트 12', font=font('extrabold', 58), fill=COLORS['white'])
        y += 92
        intro = '미리 점검 안 하면 세금과 분쟁으로 돌아오는 항목들.'
        d.text((MARGIN, y), intro, font=font('regular', 30), fill=COLORS['gray'])
        y += 46
        d.text((MARGIN, y), '해당되면 체크해봐.', font=font('regular', 30), fill=COLORS['gray'])
        y += 64
    else:
        d.text((MARGIN, y), '사전점검 체크리스트 12', font=font('extrabold', 44), fill=COLORS['white'])
        d.text((W - MARGIN - 60, y + 8), '2/2', font=font('bold', 30), fill=COLORS['gray'])
        y += 90
    return y


def draw_group(d, y, title, items, start_no):
    d.text((MARGIN, y), title, font=font('extrabold', 36), fill=COLORS['accent'])
    y += 58
    no = start_no
    for main_txt, sub_txt in items:
        box = 34
        d.rounded_rectangle([MARGIN, y + 4, MARGIN + box, y + 4 + box],
                            radius=7, outline=COLORS['accent'], width=3)
        tx = MARGIN + box + 26
        max_w = W - tx - MARGIN
        f_main = font('bold', 31)
        for i, line in enumerate(wrap(d, f'{no}. {main_txt}', f_main, max_w)):
            d.text((tx, y), line, font=f_main, fill=COLORS['white'])
            y += 44
        f_sub = font('regular', 26)
        for line in wrap(d, sub_txt, f_sub, max_w):
            d.text((tx, y), line, font=f_sub, fill=COLORS['gray'])
            y += 38
        y += 26
        no += 1
    d.line([MARGIN, y, W - MARGIN, y], fill=COLORS['divider'], width=2)
    return y + 42, no


def make_pages():
    os.makedirs(OUT_DIR, exist_ok=True)
    pages = []
    # 1페이지: 그룹 1~2, 2페이지: 그룹 3~4 + 스코어 가이드
    for page_no, group_slice in ((1, CHECKLIST[:2]), (2, CHECKLIST[2:])):
        img = Image.new('RGB', (W, H), COLORS['bg'])
        d = ImageDraw.Draw(img)
        y = draw_header(d, page_no)
        start_no = 1 if page_no == 1 else 7
        for title, items in group_slice:
            y, start_no = draw_group(d, y, title, items, start_no)

        if page_no == 2:
            y += 8
            d.rounded_rectangle([MARGIN, y, W - MARGIN, y + 170], radius=16, fill=COLORS['card'])
            cy = y + 34
            d.text((MARGIN + 36, cy), '체크가 8개 미만이라면,', font=font('extrabold', 34), fill=COLORS['accent'])
            cy += 54
            d.text((MARGIN + 36, cy), '지금 필요한 건 절세 팁이 아니라 구조 정리야.',
                   font=font('bold', 30), fill=COLORS['white'])
            y += 200
            d.text((MARGIN, y), '* 일반 정보이며, 개별 상황에 따라 적용이 달라질 수 있습니다.',
                   font=font('regular', 22), fill=COLORS['gray'])

        path = os.path.join(OUT_DIR, f'inheritance_checklist_p{page_no}.png')
        img.save(path, 'PNG')
        pages.append(img)
        print(f'저장: {path}')

    pdf_path = os.path.join(OUT_DIR, 'inheritance_checklist.pdf')
    pages[0].save(pdf_path, 'PDF', resolution=150, save_all=True, append_images=pages[1:])
    print(f'저장: {pdf_path}')


if __name__ == '__main__':
    make_pages()
