#!/usr/bin/env python3
"""
리드 마그넷 주간 포스팅 (일요일 11:00 KST)
- 상담 전환 다리(2026-07-28): 무료 체크리스트 안내 → 댓글 '점검' → DM 발송(수동)
- Gemini 미사용: 금지 문구 사고 원천 차단을 위해 고정 템플릿 + 주차별 훅 로테이션
- 체크리스트 실물은 lead_magnet/ (make_lead_magnet.py로 재생성)
"""
import os, sys
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import news_auto_poster as nap
from card_generator import upload_to_imgbb

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

KST = timezone(timedelta(hours=9))
CHECKLIST_IMAGE = os.path.join('lead_magnet', 'inheritance_checklist_p1.png')

# 주차별 로테이션 훅 — 전부 검수된 고정 문구 (놓치다/기회/혜택 계열 금지 준수)
HOOKS = [
    '상속 얘기, 꺼내기 어려워서 다들 미루지.\n근데 미룬 순서대로 세금과 분쟁이 온다.',
    '상속 준비됐냐고 물으면 다들 "아직 멀었어"라고 해.\n근데 이 12개 중 몇 개나 답할 수 있어?',
    '가족끼리 돈 얘기 안 하는 집일수록\n나중에 법정에서 만나는 경우가 많아.',
    '상속세는 재산 많은 집 얘기라고 생각하지.\n서울에 집 한 채면 이미 남 얘기가 아니야.',
]

BODY = '''

상속·증여 사전점검 체크리스트 12항목으로 정리했어.

- 최근 10년 증여 이력, 날짜·금액까지 정리돼 있는지
- 상속세 낼 현금이 어디서 나올지 계산해봤는지
- 유언장이 법적 형식 요건을 갖췄는지

이런 것들, 미리 점검한 집과 안 한 집의 결말이 완전히 달라.

필요하면 댓글에 '점검' 남겨줘. DM으로 무료로 보내줄게.

#상속 #증여'''

COMMENT = '''체크리스트에는 이것도 들어있어.

- 가족 간 계좌이체 기록 남기는 법
- 형제간 사전증여, 서로 알고 있는지
- 부양·간병 기여를 문서로 남겼는지

12개 중 8개 미만이면 절세 팁보다 구조 정리가 먼저야.
댓글에 '점검' 남기면 DM으로 보내줄게.'''


def main():
    week = datetime.now(KST).isocalendar()[1]
    hook = HOOKS[week % len(HOOKS)]
    main_text = hook + BODY

    print('=== 리드 마그넷 주간 포스팅 ===')
    print(main_text)
    print()

    image_url = None
    if os.path.exists(CHECKLIST_IMAGE):
        image_url = upload_to_imgbb(CHECKLIST_IMAGE)
        print(f'체크리스트 미리보기 업로드: {image_url}')

    main_id = nap.post_to_threads(main_text, [COMMENT], image_url=image_url, topic_tag='상속')
    if not main_id:
        print('포스팅 실패 - 종료')
        sys.exit(1)
    print(f'완료! 메인 포스트 ID: {main_id}')
    nap.log_content(main_id, 'insurance', 'lead_magnet', '상속·증여 사전점검 체크리스트 안내',
                    line_count=main_text.count('\n') + 1)


if __name__ == '__main__':
    main()
