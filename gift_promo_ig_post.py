#!/usr/bin/env python3
"""증여세 계산기 홍보 — 인스타 카드뉴스 1회성 게시. ManyChat 댓글 자동화('계산' 키워드) 대상 게시물."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import annuity_poster as ap

VARIANT = {
    'card_data': {
        'tag': '# 증여세',
        'hook_big': '같은 5억을 줘도\n세금이 천차만별',
        'hook_sub': '누구한테 주느냐에 따라 공제가 다름',
        'points': [
            {'title': '관계별 공제 한도', 'body': '배우자 6억\n성인 자녀 5천만원\n며느리·사위 1천만원'},
            {'title': '성인 자녀 5억 증여', 'body': '공제 5천만원 빼면\n세금 약 7,760만원\n(10년 합산 기준)'},
            {'title': '배우자 10억 증여', 'body': '공제 6억 빼면\n세금 약 6,790만원\n두 배 줘도 세금 비슷'},
            {'title': '며느리·사위는 조심', 'body': '공제 겨우 1천만원\n자녀를 거쳐 주는 게\n나을 수 있음'},
        ],
        'closing': '얼마를 주느냐보다\n누구에게 어떻게 나눠 주느냐가\n세금을 더 좌우함.',
        'cta': '댓글에 "성인 자녀에게 5억"\n이렇게 남기면 계산해줄게'
    },
    'caption': ('같은 5억을 줘도 누구한테 주느냐에 따라 세금이 천차만별이야.\n\n'
                '배우자 공제 6억, 성인 자녀 5천만원, 며느리·사위는 1천만원.\n'
                '관계별 공제를 모르고 몰아주면 안 내도 될 세금까지 내.\n\n'
                '댓글에 "계산"이라고 남기면 DM으로 계산기 링크 보내줄게. '
                '직접 해보고 싶으면 프로필 링크 → 자료실 → 증여세 계산기.\n\n'
                '줄이는 방향까지 내 상황 1장으로 정리 원하면 DM 주세요.\n\n'
                '#증여세 #증여세계산 #증여세면제한도 #자녀증여 #배우자증여공제 #며느리증여세 #상속증여 #재무설계 #절세'),
}


def main():
    ig_id = ap.post_instagram(VARIANT)
    if not ig_id:
        print('발행 실패')
        sys.exit(1)
    ap.log_instagram(ig_id, '증여세 계산기 홍보')
    print(f'IG 발행 완료: {ig_id}')


if __name__ == '__main__':
    main()
