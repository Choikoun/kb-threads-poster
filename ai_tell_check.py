#!/usr/bin/env python3
"""발행 전 'AI 티' 점검기 — 사용자 지적(2026-10-14~18)을 규칙으로 고정.
사용: python ai_tell_check.py <글파일.txt>   /  모듈에서 check_lines(lines) -> (errors, warnings)
errors 는 발행 중단 사유, warnings 는 고칠 것을 권고(발행은 가능).
규칙 출처: 별표 강조 절대 금지(10-18), 주소 노출 대신 링크(10-18), 대조 공식·정형 문구·균일한 문장(10-14),
         라벨: 설명 병렬 목록 남발, 이모지."""
import re, sys

HEAD_LINE = re.compile(r'^\*\*[^*]+\*\*$')                         # 소제목 줄 전체가 **...** 인 것만 허용(소제목 표기법)
LABEL_BULLET = re.compile(r'^\s*(?:\d+[.)]|[①-⑳]|[·•\-])\s*\*\*')  # 목록 항목 앞머리 별표 강조
LABEL_COLON = re.compile(r'^\s*(?:\d+[.)]|[①-⑳]|[·•\-])\s*[^:：\s][^:：]{1,14}[:：]\s')  # '· 라벨: 설명'
EMOJI = re.compile('[\U0001F300-\U0001FAFF☀-➿]')
RAW_URL = re.compile(r'(?<!\]\()https?://[^\s)]+')
LINK_MD = re.compile(r'\[[^\]]+\]\(https?://[^)\s]+\)')
STOCK = ['각별히 주목', '하늘과 땅 차이', '고민하시는 분들이라면', '에 대해 알아보겠습니다', '반드시 짚고 넘어', '천차만별',
         '꽂히는', '극명하게', '통찰을', '심도 있는', '~하는 것이 먼저입니다', '핵심만 쏙', '한눈에 쏙', '지름길']
CONTRAST = re.compile(r'[^.\n]{2,40}(?:가|이|는|은)\s*아니라\s*[^.\n]{2,40}(?:입니다|합니다|됩니다|이에요)')
ALLOWED_URL_HOSTS = ('naver.me/FRLbSbiJ',)


def check_lines(lines):
    errors, warnings = [], []
    body = [l.rstrip('\n') for l in lines]
    text_lines = [l for l in body if l.strip() and not l.strip().startswith('[IMG:')]
    for i, l in enumerate(text_lines, 1):
        s = l.strip()
        if '**' in s and not HEAD_LINE.match(s):
            # 소제목 줄 + 같은 줄에 본문이 붙은 형태(**제목** 본문)도 파서가 허용하므로 별표가 앞머리 한 쌍일 때만 통과
            m = re.match(r'^\*\*[^*]+\*\*\s+[^*]*$', s)
            if not m:
                errors.append(f'별표(**) 인라인 강조 금지: {s[:40]}')
        if s.startswith('> ') and ('==' in s or LINK_MD.search(s)):
            errors.append(f'인용구 박스(> ) 안에서는 강조(==)·링크 사용 불가: {s[:30]}')
        if LABEL_BULLET.match(s):
            errors.append(f'목록 항목 앞머리 별표 강조 금지: {s[:40]}')
        if EMOJI.search(s):
            errors.append(f'이모지 금지: {s[:30]}')
        for u in RAW_URL.findall(s):
            if not any(h in u for h in ALLOWED_URL_HOSTS):
                errors.append(f'주소를 그대로 노출 금지 → [표시문구](주소) 형식 사용: {u[:50]}')
        for w in STOCK:
            if w in s:
                warnings.append(f'정형 문구: "{w}"')
        if '—' in s or '–' in s:
            warnings.append(f'긴 줄표(—) 사용: {s[:30]}')
    n_hl = sum(len(re.findall(r'==[^=]+==', l)) for l in text_lines)
    if n_hl > 3:
        warnings.append(f'노란 강조(==)가 {n_hl}곳 — 핵심 숫자 2~3곳만')
    labels = [l for l in text_lines if LABEL_COLON.match(l)]
    if len(labels) > 4:
        warnings.append(f"'라벨: 설명' 병렬 목록이 {len(labels)}줄 — 일부는 줄글로 풀 것")
    first = ' '.join(text_lines[:3])
    if CONTRAST.search(first):
        warnings.append("도입에 '~가 아니라 ~입니다' 대조 공식")
    sents = [s for l in text_lines for s in re.split(r'(?<=[.?!])\s+', l.strip()) if len(s) > 8]
    if sents:
        rate = sum(1 for s in sents if re.search(r'(입니다|합니다|됩니다)[.]?$', s)) / len(sents)
        if rate > 0.75:
            warnings.append(f'문장 끝이 "~입니다/합니다"로 {int(rate * 100)}% 쏠림 — 구어(~죠/~거든요)·짧은 문장 섞기')
    return errors, warnings


def report(path_or_lines, label=''):
    lines = open(path_or_lines, encoding='utf-8').read().split('\n') if isinstance(path_or_lines, str) else path_or_lines
    if isinstance(path_or_lines, str) and '---' in lines:
        lines = lines[lines.index('---') + 1:]
    e, w = check_lines(lines)
    for x in sorted(set(w)):
        print('  [권고]', x)
    for x in e:
        print('  [오류]', x)
    print(f'AI 티 점검{label}: 오류 {len(e)}개, 권고 {len(set(w))}개')
    return e, w


if __name__ == '__main__':
    e, w = report(sys.argv[1])
    sys.exit(1 if e else 0)
