#!/usr/bin/env python3
"""
상속세 30초 계산기(자료실 calc.html) 홍보 — 인스타 카드뉴스 1회성 게시
- Threads는 로컬에서 별도 발행(댓글봇 연동). 여기선 IG만.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import annuity_poster as ap

VARIANT = {
    'card_data': {
        'tag': '# 상속세 계산',
        'hook_big': '우리 집 상속세,\n30초면 나옵니다',
        'hook_sub': '세무사 가기 전에 대략은 알고 가세요 · 무료',
        'points': [
            {'title': '넣는 건 4가지', 'body': '재산·부채·배우자 유무·\n자녀 수만 넣으면\n바로 계산됩니다.'},
            {'title': '예시: 재산 15억', 'body': '부채 2억, 배우자·자녀 2명이면\n예상 상속세 약 3,741만원\n(일괄·배우자공제 반영)'},
            {'title': '배우자공제가 핵심', 'body': '배우자 상속분에 따라\n공제가 5억~30억까지\n달라집니다.'},
            {'title': '줄이는 방향도 같이', 'body': '사전증여 시기, 납부 재원,\n배우자·자녀 배분까지\n결과 화면에서 확인.'},
        ],
        'closing': '숫자를 알아야\n줄일 방법도 보입니다.',
        'cta': '프로필 링크 → 자료실 → 상속세 계산기'
    },
    'caption': ('우리 집 상속세, 30초면 나옵니다.\n\n'
                '세무사 가기 전에 대략은 알고 가세요. 재산·부채·배우자·자녀 수만 넣으면 끝. 무료입니다.\n'
                '예시: 재산 15억·부채 2억·배우자·자녀 2명 → 약 3,741만원\n\n'
                '프로필 링크 → 자료실 → 상속세 계산기\n'
                '결과 보고 "이거 어떻게 줄이지" 싶으면 내 상황 1장으로 정리해드립니다 → https://naver.me/FRLbSbiJ\n'
                "점검표·체크리스트가 필요하시면 DM으로 '자료'라고 보내주세요.\n\n"
                '#상속세 #상속세계산 #상속세계산기 #상속세일괄공제 #배우자상속공제 #상속세절세 #사전증여 #자산가 #재무설계'),
}


def main():
    ig_id = ap.post_instagram(VARIANT)
    if not ig_id:
        print('발행 실패')
        sys.exit(1)
    ap.log_instagram(ig_id, '상속세 계산기 홍보')
    print(f'IG 발행 완료: {ig_id}')


if __name__ == '__main__':
    main()
