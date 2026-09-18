#!/usr/bin/env python3
"""
주간 "댓글로 계산해준 사례 모음" 게시물 (Threads) — 사회적 증거 자동 생성
reply_bot_state.json 의 최근 7일 답글 로그에서 사례를 뽑아 익명 요약 글로 발행.
사례가 MIN_CASES 미만이면 발행하지 않음. 매주 일요일 실행.
"""
import os, sys, json, re
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'deliverables')

MIN_CASES = 3
KST = timezone(timedelta(hours=9))
STATE_FILE = 'reply_bot_state.json'
CONSULT_LINK = 'https://naver.me/FRLbSbiJ'
PAGES = 'https://choikoun.github.io/kb-threads-poster/'


def case_line(entry):
    """로그 항목 → '재산 15억·배우자·자녀 2 → 상속세 약 3,741만원' 한 줄"""
    import comment_reply_bot as b
    h, text = entry['handler'], entry['text']
    if h == 'inheritance':
        from inheritance_estimate import estimate, fmt
        p = b.parse_inheritance(text)
        if not p: return None
        e = estimate(p)
        return (f"재산 {fmt(p['assets'])}" + (f"·부채 {fmt(p['debts'])}" if p['debts'] else '')
                + f"·배우자 {'O' if p['spouse'] else 'X'}·자녀 {p['children']} → 상속세 약 {fmt(e['tax_after'])}")
    if h == 'gift':
        from gift_estimate import estimate, fmt
        p = b.parse_gift(text)
        if not p: return None
        e = estimate(p)
        return f"{e['rel']}에게 {fmt(p['amount'])} → 증여세 약 {fmt(e['final'])}"
    if h == 'retire':
        from retire_estimate import estimate, fmt
        p = b.parse_retire(text)
        if not p: return None
        e = estimate(p)
        return f"연봉 {fmt(p['salary'])}·근속 {p['years']:g}년 → 한도 {fmt(e['limit'])}" + (f", 초과 {fmt(e['excess'])}" if e['excess'] else '')
    return None


def build_post(cases):
    kinds = {'inheritance': '상속세', 'gift': '증여세', 'retire': '임원 퇴직금'}
    names = sorted({kinds[c[0]] for c in cases if c[0] in kinds})
    lines = [f"이번 주 댓글로 계산해준 {'·'.join(names)} {len(cases)}건 정리.", '']
    for i, (h, line) in enumerate(cases[:7], 1):
        lines.append(f'{i}. {line}')
    lines += ['', '전부 댓글에 숫자만 남긴 사람들이야. 세무사 가기 전에 대략은 알고 가는 거지.',
              '너도 궁금하면 이번 주 글 댓글에 숫자만 남겨. 표로 답글 달아줄게.']
    main = '\n'.join(lines)
    comments = [f'직접 해보려면 → 상속세 {PAGES}calc.html · 증여세 {PAGES}gift_calc.html · 임원 퇴직금 {PAGES}retire_calc.html',
                f'내 상황에 맞춰 줄이는 방향까지 1장으로 정리 원하면 → {CONSULT_LINK}']
    return main, comments


def main(dry=False):
    if not os.path.exists(STATE_FILE):
        print('상태 파일 없음'); return
    with open(STATE_FILE, encoding='utf-8-sig') as f:
        state = json.load(f)
    cutoff = (datetime.now(KST) - timedelta(days=7)).strftime('%Y-%m-%d %H:%M')
    recent = [e for e in state.get('log', []) if e.get('time', '') >= cutoff]
    cases = []
    for e in recent:
        line = case_line(e)
        if line:
            cases.append((e['handler'], line))
    print(f'최근 7일 사례 {len(cases)}건')
    if len(cases) < MIN_CASES:
        print(f'{MIN_CASES}건 미만 — 발행 안 함'); return
    main_text, comments = build_post(cases)
    print(main_text); print(comments)
    if dry:
        return
    import news_auto_poster as nap
    pid = nap.post_to_threads(main_text, comments, image_url=None, topic_tag='상속세')
    nap.log_content(pid, 'inheritance', 'weekly_cases', f'댓글 계산 사례 {len(cases)}건 모음', source='bot:weekly', line_count=main_text.count('\n') + 1)
    print('발행 완료', pid)


if __name__ == '__main__':
    main(dry='--dry' in sys.argv)
