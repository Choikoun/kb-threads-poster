#!/usr/bin/env python3
"""증여세신고기한 릴스 — kb_anim 애니메이션(4장면·저장 유도). 사실 출처: 국세청 증여세 안내."""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import kb_anim as K
from kb_anim import RED, GREEN, GOLD

TITLE = '증여세신고기한 블로그 유도 릴스(애니메이션)'

SCENES = [
    dict(kind='list', title='증여세 신고기한', big='3개월', small='국세청 증여세 안내 기준', col=GOLD,
         items=['증여받은 달 말일부터 3개월', '기한이 휴일이면 다음 날까지', '수증자 주소지 세무서에 신고'],
         say='증여세 신고기한은 증여받은 달 말일부터 3개월 이내입니다.'),
    dict(kind='list', title='기한 안에 신고하면', big='공제 3%', small='신고세액공제', col=GREEN,
         items=['기한 안에 신고하면 3% 공제', '기한까지 미신고면 공제 불가', '홈택스 전자신고 가능'],
         say='기한 안에 신고하면 신고세액공제 3%를 받을 수 있습니다.'),
    dict(kind='list', title='신고하지 않으면', big='가산세 20%', small='국세청 증여세 가산세 표', col=RED,
         items=['일반 무신고 20%', '일반 과소신고 10%', '부정 무신고·과소신고 40%'],
         say='신고하지 않으면 일반 무신고 가산세 20%가 붙을 수 있습니다.'),
    dict(kind='cta', title='저장해두세요', big='증여일부터 3개월', small='달력에 기한 적어두기', col=GOLD,
         panel='프로필 링크 → 블로그에 전체 정리',
         say='저장해 두세요. 증여받은 날짜, 달력에 적어 두셨나요?'),
]

CAPTION = '''증여세는 증여받은 날이 아니라 그달 말일부터 3개월을 셉니다. 우리 가족 증여, 기한을 달력에 적어 두셨나요?

1. 국세청 안내: 증여일이 속하는 달의 말일부터 3개월 이내에 수증자 주소지 관할 세무서에 신고합니다. 기한이 휴일이면 다음 날까지입니다.
2. 기한 안에 신고하면 신고세액공제 3%를 받을 수 있습니다.
3. 신고하지 않으면 일반 무신고 가산세 20%, 과소신고는 10%이고 부정은 40%입니다. 납부지연가산세는 별도입니다.

자세한 내용은 블로그에 정리해두었습니다. 내 기한과 세액은 홈택스나 세무 전문가와 확인하세요.

#증여세신고기한 #증여세신고방법 #증여세가산세 #증여세'''


def main():
    K.publish(SCENES, CAPTION, TITLE)


if __name__ == '__main__':
    K.make_video(SCENES, os.environ.get('KB_OUT') or 'npa_anim_test.mp4')
