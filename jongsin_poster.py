#!/usr/bin/env python3
"""
종신보험 소재 주간 포스팅 (Threads + Instagram, 화 20:30 KST)
- 상품명·회사명 비노출 원칙 준수, 4개 각도를 주차별로 로테이션
- 팀 내부 판매사례 요약(KB 리턴종신보험)을 참고해 세일즈 포인트만 재구성 (사례 내러티브·고객정보는 그대로 안 씀)
- Gemini 미사용: 실제 상품 소재라 고정 검수 템플릿 유지 (연금보험·리드마그넷과 동일 원칙)
- 상담 유도: 상품 소재 콘텐츠는 항상 댓글에 naver.me 링크 첨부 (2026-08-19 사용자 확정)
"""
import os, sys, time, json, requests
sys.stdout.reconfigure(encoding='utf-8')

from datetime import datetime, timezone, timedelta
import news_auto_poster as nap
import card_generator as cg

KST = timezone(timedelta(hours=9))
CONSULT_COMMENT_THREADS = '이 얘기 더 궁금하면 여기서 확인할 수 있어 → https://naver.me/FRLbSbiJ'
CONSULT_COMMENT_IG = '더 자세한 내용이 궁금하시면 아래에서 확인해보세요 → https://naver.me/FRLbSbiJ'

VARIANTS = [
    {
        'threads': '''종신보험은 사망보험금만 나오는 거라고 생각하지.

⚠️ 근데 살아있는 동안 자녀 대학 등록금으로 미리 활용할 수 있는 구조도 있어.

가족 사망보장은 그대로 유지하면서, 필요한 시점에 자금을 빼 쓰는 거야.

자녀가 초등학생일 때 가입해서, 대학 갈 때쯤 활용하는 식으로 설계가 가능해.

죽어야만 쓰는 보험이 아니라, 살아있는 동안 쓰는 자산으로 보는 거지.

물론 미리 빼 쓴 만큼 나중에 남는 보장금액은 줄어드는 구조야.

'사망보험'이라는 이름 때문에 이런 활용법을 모르는 사람이 많아.''',
        'card_data': {
            'tag': '# 종신보험',
            'hook_big': '종신보험은\n사망보험금만 나온다?',
            'hook_sub': '살아있는 동안 활용하는 방법도 있습니다',
            'points': [
                {'title': '자녀 교육자금으로 활용', 'body': '가족 사망보장은 유지하면서\n필요한 시점에 자금을\n빼서 쓸 수 있습니다.'},
                {'title': '자녀 성장에 맞춘 설계', 'body': '초등학생일 때 가입해서\n대학 갈 시점에 활용하는\n방식도 가능합니다.'},
                {'title': '평생 쓰는 자산', 'body': '죽어야만 받는 보험이 아니라\n생애 중 쓸 수 있는\n자산으로 보는 관점입니다.'},
                {'title': '인출한 만큼 감소', 'body': '다만 미리 활용한 만큼\n나중에 남는 보장금액은\n줄어듭니다.'},
            ],
            'closing': "'사망보험'이라는 이름 때문에\n이런 활용법을 모르는 분들이\n많습니다.",
            'cta': '우리 가족은 어떻게 설계할 수 있을지\n궁금하신가요?'
        },
        'caption': '''종신보험은 사망보험금만 나온다고 생각하시나요?

살아있는 동안 자녀 교육자금 등으로 미리 활용할 수 있는 구조도 있습니다.

1. 가족 사망보장은 그대로 유지하면서 필요한 시점에 자금을 인출해 쓸 수 있습니다.
2. 자녀가 초등학생일 때 가입해서 대학 진학 시점에 활용하는 방식으로 설계할 수 있습니다.
3. 죽어야만 받는 보험이 아니라, 살아있는 동안 쓰는 자산으로 보는 관점입니다.
4. 다만 미리 활용한 만큼 나중에 남는 보장금액은 줄어듭니다.

'사망보험'이라는 이름 때문에 이런 활용법을 모르고 계신 분들이 많습니다.

#종신보험 #자녀교육자금 #보험활용 #자산설계''',
    },
    {
        'threads': '''미혼이면 종신보험 필요 없다고 생각하지.

⚠️ 근데 사망보장 목적이 아니라 은퇴 후 자금으로 쓰는 사람도 있어.

지금 넣어두고, 은퇴하고 나서 취미 생활비로 활용하는 거야.

부양가족이 없어도 내가 나중에 쓸 자금이라는 관점으로 보면 얘기가 달라져.

물론 이것도 중간에 빼 쓰면 남는 보장이 그만큼 줄어드는 건 똑같아.

'미혼이라 안 맞다'가 아니라 '어떻게 쓸지'가 먼저야.

보험을 보장으로만 보면 좁아지고, 자산으로 보면 넓어져.''',
        'card_data': {
            'tag': '# 종신보험',
            'hook_big': '미혼이면\n종신보험이 필요 없다?',
            'hook_sub': '사망보장이 아닌 다른 활용법도 있습니다',
            'points': [
                {'title': '은퇴자금으로 활용', 'body': '사망보장 목적이 아니라\n은퇴 후 생활·취미자금으로\n활용하는 방법도 있습니다.'},
                {'title': '부양가족이 없어도', 'body': '내가 나중에 쓸 자금이라는\n관점으로 보면\n얘기가 달라집니다.'},
                {'title': '중요한 건 활용 방법', 'body': "'미혼이라 안 맞다'가 아니라\n'어떻게 쓸지'를\n먼저 따져봐야 합니다."},
                {'title': '인출한 만큼 감소', 'body': '중간에 자금을 빼 쓰면\n남는 보장금액은\n그만큼 줄어듭니다.'},
            ],
            'closing': '보험을 보장으로만 보면 좁아지고,\n자산으로 보면\n넓어집니다.',
            'cta': '내 상황엔 어떻게 적용될지\n궁금하신가요?'
        },
        'caption': '''미혼이면 종신보험이 필요 없다고 생각하시나요?

사망보장 목적이 아니라 은퇴 후 자금으로 활용하는 방법도 있습니다.

1. 지금 준비해두고, 은퇴 이후 생활비나 취미자금으로 활용하는 방식입니다.
2. 부양가족이 없어도 본인이 나중에 쓸 자금이라는 관점으로 보면 이야기가 달라집니다.
3. '미혼이라 안 맞다'가 아니라 '어떻게 활용할지'를 먼저 따져보시는 걸 추천드립니다.
4. 다만 중간에 자금을 인출하면 남는 보장금액은 그만큼 줄어듭니다.

보험을 보장으로만 보면 좁아지고, 자산으로 보면 넓어집니다.

#종신보험 #미혼 #은퇴자금 #자산설계''',
    },
    {
        'threads': '''퇴직 앞두고 있으면 보험 새로 드는 거 부담스럽지.

⚠️ 근데 퇴직 전 10년 동안 활용할 '용돈' 개념으로 설계하는 사람들이 있어.

퇴직 후 현금흐름 끊기기 전에, 미리 준비해둔 자금을 그 기간에 꺼내 쓰는 거야.

사망보장은 유지되면서 생활비로도 쓸 수 있는 구조지.

당장 필요 없어 보여도, 퇴직 시점 되면 체감이 완전히 달라져.

이것도 빼 쓴 만큼 나중 보장은 줄어드는 건 감안해야 해.

은퇴 준비를 사망보험으로 한다는 게 낯설게 들릴 수 있는데, 실제로 이렇게 설계하는 사람들이 있어.''',
        'card_data': {
            'tag': '# 종신보험',
            'hook_big': '퇴직 전 10년,\n생활비는 어떻게 준비하세요?',
            'hook_sub': "'퇴직 전 용돈' 개념으로 설계하는 방법도 있습니다",
            'points': [
                {'title': '퇴직 전 현금흐름', 'body': '퇴직 전 10년 동안\n활용할 자금으로\n미리 준비해두는 방식입니다.'},
                {'title': '보장은 그대로 유지', 'body': '사망보장은 유지되면서\n생활비로도 쓸 수 있는\n구조입니다.'},
                {'title': '체감은 퇴직 시점에', 'body': '당장은 필요 없어 보여도\n퇴직 시점이 되면\n체감이 달라집니다.'},
                {'title': '인출한 만큼 감소', 'body': '다만 빼 쓴 만큼\n나중에 남는 보장은\n줄어듭니다.'},
            ],
            'closing': '은퇴 준비를 종신보험으로 한다는 게\n낯설게 들릴 수 있지만,\n실제로 이렇게 설계하는 분들이 있습니다.',
            'cta': '내 퇴직 시점엔 어떻게 준비해야 할지\n궁금하신가요?'
        },
        'caption': '''퇴직을 앞두고 있으면 새로 보험에 가입하는 게 부담스러우신가요?

퇴직 전 10년 동안 활용할 자금 개념으로 설계하는 방법도 있습니다.

1. 퇴직 후 현금흐름이 끊기기 전, 미리 준비해둔 자금을 그 기간에 활용하는 방식입니다.
2. 사망보장은 유지되면서 생활비로도 활용할 수 있는 구조입니다.
3. 당장은 필요 없어 보여도 퇴직 시점이 되면 체감이 완전히 달라집니다.
4. 다만 활용한 만큼 나중에 남는 보장금액은 줄어듭니다.

은퇴 준비를 종신보험으로 한다는 게 낯설게 느껴지실 수 있지만, 실제로 이렇게 설계하시는 분들이 있습니다.

#종신보험 #퇴직준비 #은퇴설계 #자산설계''',
    },
    {
        'threads': '''종신보험은 한번 넣으면 못 뺀다고 생각해서 거절하는 사람 많아.

⚠️ 근데 요즘은 납입한 보험료를 환급받는 구조로 설계된 것도 있어.

자금이 묶인다는 부담 때문에 안 든 사람들이 다시 관심 갖는 이유야.

보장은 유지하면서 필요하면 환급 구조로 자금을 회수할 수 있는 거지.

예전에 거절했던 이유가 지금은 해결된 상품 구조도 있다는 얘기야.

물론 환급 조건이나 시기는 계약마다 다르니까 확인은 필요해.

거절했던 이유, 다시 한번 확인해볼 만해.''',
        'card_data': {
            'tag': '# 종신보험',
            'hook_big': '종신보험은\n한번 넣으면 못 뺀다?',
            'hook_sub': '납입보험료를 환급받는 구조도 있습니다',
            'points': [
                {'title': '자금 묶임 부담', 'body': "자금이 묶인다는 부담 때문에\n가입을 미뤄온 분들이\n많습니다."},
                {'title': '환급구조 설계', 'body': '납입한 보험료를\n환급받을 수 있는 구조로\n설계된 상품도 있습니다.'},
                {'title': '보장은 유지', 'body': '보장은 그대로 유지하면서\n필요하면 환급 구조로\n자금을 회수할 수 있습니다.'},
                {'title': '조건은 계약마다 다름', 'body': '환급 조건이나 시기는\n계약마다 다르니\n확인이 필요합니다.'},
            ],
            'closing': '예전에 거절했던 이유가\n지금은 해결된 상품 구조도\n있습니다.',
            'cta': '예전에 거절했던 이유,\n지금은 어떤지 궁금하신가요?'
        },
        'caption': '''종신보험은 한번 넣으면 못 뺀다고 생각해서 가입을 미뤄오셨나요?

납입한 보험료를 환급받는 구조로 설계된 상품도 있습니다.

1. 자금이 묶인다는 부담 때문에 가입을 미뤄온 분들이 많습니다.
2. 요즘은 납입보험료를 환급받을 수 있는 구조로 설계된 상품도 있습니다.
3. 보장은 그대로 유지하면서 필요하면 환급 구조로 자금을 회수할 수 있습니다.
4. 다만 환급 조건이나 시기는 계약마다 다르니 확인이 필요합니다.

예전에 거절했던 이유가 지금은 해결된 상품 구조도 있으니, 한 번쯤 다시 확인해보시는 걸 추천드립니다.

#종신보험 #환급형보험 #자산설계 #보험상식''',
    },
]


def log_instagram(ig_post_id, selected_title):
    log = []
    if os.path.exists('instagram_log.json'):
        with open('instagram_log.json', encoding='utf-8-sig') as f:
            log = json.load(f)
    log.append({
        'ig_post_id': ig_post_id,
        'type': 'card',
        'selected_title': selected_title,
        'date': datetime.now(KST).strftime('%Y-%m-%d %H:%M'),
    })
    with open('instagram_log.json', 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def post_threads(variant):
    print('Threads 발행 중...')
    main_id = nap.post_to_threads(variant['threads'], [CONSULT_COMMENT_THREADS], image_url=None, topic_tag='보험')
    print(f'Threads 완료: {main_id}')
    return main_id


def post_instagram(variant):
    TOKEN = os.environ['INSTAGRAM_ACCESS_TOKEN']
    IG_USER_ID = os.environ['INSTAGRAM_BUSINESS_ACCOUNT_ID']
    BASE_IG = 'https://graph.facebook.com/v21.0'

    print('카드 이미지 생성 중...')
    paths = cg.generate_card_set(variant['card_data'], output_dir='jongsin_cards_tmp', category='insurance')
    print(f'{len(paths)}장 생성 완료')

    print('imgbb 업로드 중...')
    image_urls = []
    for i, p in enumerate(paths):
        url = cg.upload_to_imgbb(p)
        image_urls.append(url)
        print(f'카드 {i+1}/{len(paths)} 업로드 완료')
        time.sleep(1)

    child_ids = []
    for i, url in enumerate(image_urls):
        r = requests.post(f'{BASE_IG}/{IG_USER_ID}/media',
                          params={'image_url': url, 'is_carousel_item': 'true', 'access_token': TOKEN}, timeout=30)
        if not r.ok:
            print(f'카드 {i+1} 컨테이너 실패: {r.text}')
            return None
        child_ids.append(r.json()['id'])
        time.sleep(2)

    r = requests.post(f'{BASE_IG}/{IG_USER_ID}/media',
                      params={'media_type': 'CAROUSEL', 'children': ','.join(child_ids),
                              'caption': variant['caption'], 'access_token': TOKEN}, timeout=30)
    if not r.ok:
        print(f'캐러셀 컨테이너 실패: {r.text}')
        return None
    carousel_id = r.json()['id']
    time.sleep(5)

    r = requests.post(f'{BASE_IG}/{IG_USER_ID}/media_publish',
                      params={'creation_id': carousel_id, 'access_token': TOKEN}, timeout=30)
    if not r.ok:
        print(f'발행 실패: {r.text}')
        return None
    media_id = r.json()['id']
    print(f'Instagram 완료: {media_id}')

    # A/B 테스트 (2026-08-31): 연금보험 등 상담링크 댓글 단 4건이 도달 3~4회로
    # 전체 카드뉴스 중앙값(133)보다 비정상적으로 낮게 나옴 — 링크 댓글이 Meta
    # 스캠 분류기에 걸려 도달 억제됐을 가능성 의심. IG_SKIP_CONSULT_LINK=1이면
    # 이번 건은 댓글 없이 올려서 다음 주간분석에서 도달 비교할 것.
    if os.environ.get('IG_SKIP_CONSULT_LINK') == '1':
        print('상담링크 댓글 스킵 (A/B 테스트)')
    else:
        time.sleep(3)
        rc = requests.post(f'{BASE_IG}/{media_id}/comments',
                           params={'message': CONSULT_COMMENT_IG, 'access_token': TOKEN}, timeout=30)
        print('상담링크 댓글:', rc.json())
    return media_id


def main():
    week = datetime.now(KST).isocalendar()[1]
    variant = VARIANTS[week % len(VARIANTS)]
    print(f'=== 종신보험 주간 포스팅 (variant {week % len(VARIANTS)}) ===')

    threads_id = post_threads(variant)
    if threads_id:
        nap.log_content(threads_id, 'insurance', 'jongsin_sales', '종신보험 활용법 소재',
                        line_count=variant['threads'].count('\n') + 1)

    ig_id = post_instagram(variant)
    if ig_id:
        log_instagram(ig_id, '종신보험 활용법 소재')


if __name__ == '__main__':
    main()
