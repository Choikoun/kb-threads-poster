#!/usr/bin/env python3
"""연금 사망시 남는 돈 — 블로그 유도 인스타 카드뉴스 1회성 게시"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import annuity_poster as ap
import blog_links

BLOG_URL = blog_links.get_blog_url('annuity_death_benefit')

VARIANT = {
    'card_data': {
        'tag': '# 연금보험',
        'hook_big': '연금 받다가 죽으면\n그냥 손해 아니야?',
        'hook_sub': '약관 뜯어보니 최소한은 막아주는 장치가 있음',
        'points': [
            {'title': '기준은 낸 돈의 120%', 'body': '이미 낸 보험료의 120%\n에서 받은 연금을 빼고\n나머지를 가족에게.'},
            {'title': '65세, 개시 직후 사망', 'body': '받은 연금 0원\n→ 가족에게\n8,064만원 (예시 기준)'},
            {'title': '74세 사망', 'body': '받은 연금 7,902만원\n→ 가족에게\n162만원'},
            {'title': '75세 이후', 'body': '120%를 이미 다 받음\n→ 사망보장 0원\n(대신 연금은 계속 나옴)'},
        ],
        'closing': '일찍 죽으면 가족에게 남고,\n오래 살면 연금이 계속 나온다.\n손해 보는 구간이 없다.',
        'cta': '시점별 실제 숫자는\n블로그에 정리해뒀어'
    },
    'caption': ('연금 받다가 죽으면 손해 아니냐고?\n\n'
                '약관 기준 낸 돈의 120%에서 받은 연금을 뺀 만큼 가족에게 남아. '
                '일찍 죽으면 많이 남고, 오래 살면 연금이 계속 나오고.\n\n'
                '65세부터 75세까지 시점별로 얼마 남는지 표로 정리했어. '
                '프로필 링크 → 블로그에서 전체 숫자 확인 가능.\n\n'
                "점검표·체크리스트가 필요하시면 DM으로 '자료'라고 보내주세요.\n\n"
                '#연금보험 #연금보험사망시 #노후준비 #사망보험금 #연금개시 #재무설계 #보험점검'),
}


def main():
    ig_id = ap.post_instagram(VARIANT)
    if not ig_id:
        print('발행 실패')
        sys.exit(1)
    ap.log_instagram(ig_id, '연금 사망시 남는 돈 블로그 유도')
    print(f'IG 발행 완료: {ig_id}')


if __name__ == '__main__':
    main()
