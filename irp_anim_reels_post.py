#!/usr/bin/env python3
"""IRP계좌출금 릴스 — kb_anim 애니메이션 버전(데이터 장면 + 루프 구조). 새 릴스 스크립트의 견본.
이 소재의 일반 릴스는 10-15에 이미 발행됨 → main()을 실행하면 중복 발행되므로 테스트는 KB_PREVIEW=1 로 미리보기만 한다.
루프: 마지막 장면이 질문으로 끝나고 첫 장면이 그 답으로 시작 → 반복 재생 시 자연스럽게 이어짐.
첫 장면은 결과 숫자(742만 원)를 카운트업으로 바로 보여준다."""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import kb_anim as K
from kb_anim import RED, GREEN, GOLD

TITLE = 'IRP계좌출금 블로그 유도 릴스(애니메이션)'

SCENES = [
    dict(kind='hook', title='IRP를 급하게 해지하면', count=(742, '만 원'), small='연 900만 원 × 5년 납입 · 공제율 13.2% 가정', col=RED,
         rows=[('받은 환급', 5940, GREEN), ('해지 세금', 7425, RED)], gap='환급보다 약 148만 원을 더 냄',
         fmt=lambda v: f'{int(v / 10):,}만', hi=None,
         say='IRP를 급하게 해지하면 세금이 약 742만 원입니다.'),
    dict(kind='bars', title='같은 사람이 돌려받은 돈', big='594만 원', small='5년간 세액공제 합계', col=GREEN,
         rows=[('받은 환급', 5940, GREEN), ('해지 세금', 7425, RED)], gap='세금 16.5%가 환급보다 큽니다',
         fmt=lambda v: f'{int(v / 10):,}만', hi=1,
         say='5년 동안 돌려받은 세액공제는 594만 원이라서, 환급보다 148만 원을 더 냅니다.'),
    dict(kind='list', title='중도인출이 되는 법정 사유', big='5가지뿐', small='금융기관 안내 2026년 9월 기준', col=GOLD,
         items=['주택 구입 · 전세금', '6개월 이상 요양', '회생 · 파산 · 재난 피해'],
         say='중도인출은 주택 구입과 전세금, 6개월 이상 요양, 회생이나 파산, 재난 피해, 이 다섯 가지 사유에만 됩니다.'),
    dict(kind='bars', title='꺼내는 방법별 세율', big='16.5% vs 5.5%', small='해지 vs 55세 이후 연금 수령', col=GOLD,
         rows=[('사유 없이 해지', 165, RED), ('연금으로 수령', 55, GREEN)], gap='급하지 않으면 연금이 훨씬 가볍습니다',
         fmt=lambda v: f'{v / 10:.1f}%', hi=1,
         say='급하지 않다면 55세 이후 연금으로 받는 쪽이 세율이 5.5퍼센트 이하입니다.'),
    dict(kind='cta', title='저장해두세요', big='꺼내기 전에 확인', small='세액공제 받은 원금 · 사유 · 연금 개시 시기', col=GOLD,
         panel='프로필 링크 → 블로그에 전체 정리',
         say='나중에 다시 보시려면 저장해두세요. 확인 없이 해지하면 어떻게 될까요?'),
]

CAPTION = '''IRP를 급하게 해지하면 세금이 얼마일까요?

1. 연 900만 원씩 5년(총 4,500만 원) 넣고 공제율 13.2%를 받은 A씨(가정)가 해지하면 세금은 742만 5천 원, 받은 환급은 594만 원입니다.
2. 중도인출은 법으로 정한 5가지 사유(주택 구입, 전세금, 6개월 이상 요양, 5년 이내 회생·파산, 재난 피해)에만 가능합니다.
3. 사유 없이 해지하면 세액공제 받은 원금과 수익에 기타소득세 16.5%, 만 55세 이후 연금으로 받으면 5.5% 이하입니다.

공제율과 실제 세금은 소득과 가입 내역에 따라 다릅니다. 인출 전에는 가입한 금융기관 안내를 확인하세요. 자세한 내용은 블로그에 정리해두었습니다.

#IRP계좌출금 #IRP중도인출 #IRP해지 #연금소득세 #퇴직연금'''


def main():
    K.publish(SCENES, CAPTION, TITLE)


if __name__ == '__main__':
    K.make_video(SCENES, os.environ.get('KB_OUT') or 'irp_anim_test.mp4')
