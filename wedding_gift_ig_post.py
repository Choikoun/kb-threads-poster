#!/usr/bin/env python3
"""축의금증여세(축의금 비과세 vs 혼인증여재산공제) — 블로그 유도 인스타 카드뉴스 1회성 게시."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import annuity_poster as ap

VARIANT = {
    'card_data': {
        'tag': '# 축의금증여세',
        'hook_big': '안 내도 되는 돈과\n신고해야 하는 돈은\n따로 있어',
        'hook_sub': '축의금이랑 혼인공제, 완전히 다른 얘기야',
        'points': [
            {'title': '하객 축의금', 'body': '사회통념상\n비과세\n(친분 범위 내)'},
            {'title': '혼인공제', 'body': '부모님이 주는 돈\n1억원 별도 공제\n(2024년 신설)'},
            {'title': '자금출처조사', 'body': '"축의금으로\n받았다" 설명\n그냥 안 믿어줌'},
            {'title': '신고기한', 'body': '증여받은 달\n말일부터\n3개월 이내'},
        ],
        'closing': '누구 몫인지\n구분해두는 습관이\n제일 확실한 방법.',
        'cta': '세목별 계산 구조\n블로그에 정리했어'
    },
    'caption': ('결혼식 축의금에도 세금이 붙을까 궁금해하는 분들 많은데, 결론은 대부분 안 붙어.\n\n'
                '친구·동료가 낸 축의금은 사회통념상 비과세라 걱정할 필요 없어. 문제는 그 돈이 부모님한테서 자녀한테로 넘어가는 순간이야.\n\n'
                '2024년 생긴 혼인공제(1억원, 기존 5천만원 공제랑 별도)랑 축의금을 헷갈리는 경우가 많은데, 세법상 완전히 다르게 취급돼.\n\n'
                '프로필 링크 → 자료실에서 더 자세히 확인해봐.\n\n'
                "점검표·체크리스트가 필요하시면 DM으로 '자료'라고 보내주세요.\n\n"
                '#축의금증여세 #혼인증여재산공제 #증여세 #결혼자금증여 #재무설계 #절세'),
}


def main():
    ig_id = ap.post_instagram(VARIANT)
    if not ig_id:
        print('발행 실패')
        sys.exit(1)
    ap.log_instagram(ig_id, '축의금증여세 블로그 유도')
    print(f'IG 발행 완료: {ig_id}')


if __name__ == '__main__':
    main()
