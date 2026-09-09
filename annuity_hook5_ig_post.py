#!/usr/bin/env python3
"""
연금보험 5번째 각도(가입시기 3년 비교 후킹) 인스타 카드뉴스 1회성 게시
- Threads는 이미 로컬에서 발행 완료(18107551526149910), 여기선 IG만 발행
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import annuity_poster as ap


def main():
    variant = ap.VARIANTS[4]
    ig_id = ap.post_instagram(variant)
    if not ig_id:
        print('발행 실패')
        sys.exit(1)
    ap.log_instagram(ig_id, '연금보험 가입시기 비교 후킹 소재')
    print(f'IG 발행 완료: {ig_id}')


if __name__ == '__main__':
    main()
