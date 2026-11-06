#!/usr/bin/env python3
"""상속세연부연납 릴스 — kb_anim 애니메이션(4장면·저장 유도). 사실 출처: 국세청 상속세 납부 안내."""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import kb_anim as K
from kb_anim import RED, GREEN, GOLD

TITLE = '상속세연부연납 블로그 유도 릴스(애니메이션)'

SCENES = [
    dict(kind='list', title='상속세 연부연납', big='최대 10년', small='국세청 상속세 납부 안내 기준', col=GOLD,
         items=['납부세액 2천만 원 초과', '납세담보 제공', '신고기한까지 신청'],
         say='상속세 연부연납은 세액이 2천만 원을 넘고 담보를 내면 신청할 수 있습니다.'),
    dict(kind='list', title='분납과 연부연납', big='둘 중 하나', small='허가받으면 분납은 불가', col=GOLD,
         items=['분납 기한 후 2개월 안 2회', '연부연납 허가일부터 장기간', '연부연납 허가 시 분납 불가'],
         say='분납은 두 번에 나눠 내고, 연부연납을 허가받으면 분납은 쓸 수 없습니다.'),
    dict(kind='list', title='기간과 이자', big='연 3.5%', small='가산금 이자율 2024년 3월 22일부터', col=GREEN,
         items=['일반재산 최대 10년', '가업상속재산 2023년 이후 최대 20년', '신청은 신고기한까지'],
         say='일반재산은 최대 10년이고 가산금 이자율은 연 3.5%입니다.'),
    dict(kind='cta', title='저장해두세요', big='신고기한 전에 확인', small='현금 · 담보 · 물납 요건', col=GOLD,
         panel='프로필 링크 → 블로그에 전체 정리',
         say='저장해 두세요. 세금 낼 현금, 신고기한 전에 따져 보셨나요?'),
]

CAPTION = '''상속세는 부동산 위주로 받으면 낼 현금이 모자랄 수 있습니다. 나눠 내는 방법, 알고 계신가요?

1. 국세청 안내: 납부세액이 2천만 원을 넘고 담보를 내면 연부연납을 신청할 수 있습니다. 신청 기한은 신고기한까지입니다.
2. 연부연납을 허가받으면 분납은 쓸 수 없습니다. 분납은 신고납부기한 후 2개월 안에 나눠 내는 방식입니다.
3. 일반재산은 허가일부터 최대 10년, 가산금 이자율은 2024년 3월 22일부터 연 3.5%입니다.

자세한 내용은 블로그에 정리해두었습니다. 내 허가 여부와 세액은 세무서나 세무 전문가와 확인하세요.

#상속세연부연납 #상속세분납 #상속세물납 #상속세'''


def main():
    K.publish(SCENES, CAPTION, TITLE)


if __name__ == '__main__':
    K.make_video(SCENES, os.environ.get('KB_OUT') or 'npa_anim_test.mp4')
