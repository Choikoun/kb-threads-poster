#!/usr/bin/env python3
"""
게시물 주제에 맞는 무료 계산기 링크 댓글 (Threads 자동 부착)
post_to_threads()가 본문 키워드로 판단해 댓글 1개를 덧붙인다. 이미 계산기 링크가 있으면 생략.
"""
import re

PAGES = 'https://choikoun.github.io/kb-threads-poster/'

TOOLS = [
    # (키워드 정규식, 댓글 문구)
    (r'상속', f'우리 집 상속세 대략 얼마인지 30초 계산기 → {PAGES}calc.html'),
    (r'증여', f'증여세 얼마 나오는지 30초 계산기(공제 잔여액도 나와) → {PAGES}gift_calc.html'),
    (r'퇴직금|임원|정관', f'임원 퇴직금 한도·초과분 30초 계산기 → {PAGES}retire_calc.html'),
]


def tool_comment(main_text, comments=()):
    joined = main_text + ' '.join(comments)
    if PAGES in joined:
        return None
    for pat, text in TOOLS:
        if re.search(pat, main_text):
            return text
    return None
