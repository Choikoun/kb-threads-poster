#!/usr/bin/env python3
"""
연금보험 소재 주간 포스팅 (Threads + Instagram, 목 20:30 KST)
- 상품명·회사명 비노출 원칙 준수, 4개 각도를 주차별로 로테이션
- Gemini 미사용: 실제 상품 소재라 고정 검수 템플릿 유지 (리드마그넷과 동일 원칙)
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
        'threads': '''요즘 92살까지 사는 게 흔한 일이 됐어.

문제는 은퇴자금 계산은 다들 85살 기준으로 해놨다는 거야.

⚠️ 그 갭을 메우려고 나온 연금이 있어. 살아있으면 100살까지 계속 나와.

오래 유지할수록 받는 돈이 늘어. 45년 넘게 유지하면 나중 지급률이 60%까지 붙어.

은퇴 초반 몇 년은 안 받고, 그 뒤로 몰아서 더 받는 것도 고를 수 있어.

급전 필요하면 일부는 미리 뺄 수 있는데, 그만큼 나중 연금은 줄어.

단점도 있어. 중간에 해지하면 낸 돈보다 덜 받을 수 있어.

내가 몇 살까지 살지 모른다는 게, 노후 설계에서 제일 큰 변수야.''',
        'card_data': {
            'tag': '# 노후연금',
            'hook_big': '92세까지 사는데\n노후자금은 85세 기준?',
            'hook_sub': '기대수명 계산부터 다시 점검해보세요',
            'points': [
                {'title': '100세까지 계속 지급', 'body': '살아있는 동안은\n100세까지 연금이\n계속 나오는 구조입니다.'},
                {'title': '오래 유지할수록 유리', 'body': '45년 이상 유지하면\n지급률이 최대 60%까지\n늘어납니다.'},
                {'title': '받는 시점도 선택 가능', 'body': '은퇴 초반엔 적게,\n후반엔 몰아 받는 방식도\n고를 수 있습니다.'},
                {'title': '중도 해지는 손해', 'body': '중간에 해지하면\n납입한 금액보다\n적게 받을 수 있습니다.'},
            ],
            'closing': '몇 살까지 살지 모른다는 것,\n노후 준비의 가장 큰 변수입니다.',
            'cta': '내 상황엔 어떻게 적용될지\n궁금하신가요?'
        },
        'caption': '''92세까지 사는 시대, 노후자금은 몇 살까지 계산해두셨나요?

대부분 85세를 기준으로 준비하시는데, 실제 기대수명은 그보다 훨씬 깁니다.

1. 살아있는 동안 100세까지 계속 지급되는 연금 형태가 있습니다.
2. 오래 유지할수록 지급률이 올라가는 방식이라, 45년 이상 유지하면 지급률이 최대 60%까지 늘어납니다.
3. 은퇴 초반엔 적게 받고 후반에 몰아 받는 방식도 선택할 수 있습니다.
4. 급하게 목돈이 필요할 땐 일부 인출도 가능한데, 그만큼 이후 연금액은 줄어듭니다.

다만 중도 해지 시에는 납입한 금액보다 해약환급금이 적을 수 있다는 점은 꼭 알아두셔야 합니다.

노후 준비, '몇 살까지 사느냐'를 기준으로 다시 점검해보시길 추천드립니다.

#노후준비 #연금 #은퇴설계 #자산관리''',
    },
    {
        'threads': '''연금 받다가 일찍 죽으면 손해라고 생각하지.

⚠️ 근데 그것도 최소한은 막아주는 구조가 있어.

살아있는 동안 받은 연금 다 빼고도, 낸 돈의 120%는 최소한으로 보장해줘.

가족한테 남는 돈이 0원이 되는 상황 자체를 막아놓은 거야.

반대로 오래 살아도 문제없어. 100살까지 살아있으면 계속 나와.

물론 이것도 중간에 깨면 얘기가 달라져. 해지하면 원금보다 적게 나올 수 있어.

연금은 '얼마나 받나'보다 '언제 죽어도 손해 안 보나'가 먼저야.''',
        'card_data': {
            'tag': '# 노후연금',
            'hook_big': '연금 받다가 일찍 사망하면\n손해 아닌가요?',
            'hook_sub': '최소한의 보장 장치가 있습니다',
            'points': [
                {'title': '사망 시 최소 보장', 'body': '이미 받은 연금을 빼고도\n납입액의 120%는\n최소한으로 보장됩니다.'},
                {'title': '가족에게 남는 돈', 'body': '가족에게 남는 금액이\n0원이 되는 상황을\n막아두는 구조입니다.'},
                {'title': '오래 살아도 안심', 'body': '반대로 오래 살아도\n100세까지 계속\n지급됩니다.'},
                {'title': '중도 해지는 예외', 'body': '다만 중간에 해지하면\n납입한 금액보다\n적게 받을 수 있습니다.'},
            ],
            'closing': '"언제 무슨 일이 생겨도\n손해 안 보나"가\n연금 선택의 첫 번째 기준입니다.',
            'cta': '내 상황엔 어떻게 적용될지\n궁금하신가요?'
        },
        'caption': '''연금 받다가 일찍 세상을 떠나면 손해라고 생각하시나요?

최소한의 보장 장치를 갖춘 연금 형태도 있습니다.

1. 이미 받은 연금을 빼고도 납입액의 120%는 최소한으로 보장됩니다.
2. 가족에게 남는 금액이 0원이 되는 상황 자체를 막아두는 구조입니다.
3. 반대로 오래 살아도 100세까지 계속 지급됩니다.
4. 다만 중간에 해지하면 납입한 금액보다 적게 받을 수 있다는 점은 유의하셔야 합니다.

연금 선택에서는 '얼마나 받는가'보다 '언제 무슨 일이 생겨도 손해를 보지 않는가'를 먼저 따져보시길 추천드립니다.

#노후준비 #연금 #은퇴설계 #자산관리''',
    },
    {
        'threads': '''은퇴하자마자 연금 받으면 세금·건보료가 같이 올라가는 거 알아?

⚠️ 그래서 받는 시점 자체를 미룰 수 있는 구조가 있어.

은퇴 초반엔 안 받고, 나중에 몰아서 받는 걸 골라도 돼.

그 사이엔 공시이율로 계속 불어나니까 무작정 손해 보는 것도 아니야.

반대로 급하게 목돈 필요하면 일부만 미리 뺄 수도 있어.

단, 미리 빼면 그만큼 나중 연금이 줄어드는 건 감안해야 해.

받는 타이밍까지 설계할 수 있다는 걸 모르는 사람이 많아.''',
        'card_data': {
            'tag': '# 노후연금',
            'hook_big': '은퇴하자마자 연금 받으면\n세금·건보료가 오른다?',
            'hook_sub': '수령 시점도 선택할 수 있습니다',
            'points': [
                {'title': '수령 시점 선택 가능', 'body': '은퇴 초반엔 적게 받고\n후반에 몰아 받는 방식도\n선택할 수 있습니다.'},
                {'title': '미루는 동안도 적립', 'body': '받지 않는 기간에도\n공시이율로 계속\n불어납니다.'},
                {'title': '급전은 일부 인출로', 'body': '목돈이 필요하면\n전체 해지 없이\n일부만 인출 가능합니다.'},
                {'title': '미리 빼면 그만큼 감소', 'body': '다만 미리 인출한 만큼\n이후 받는 연금액은\n줄어듭니다.'},
            ],
            'closing': '받는 타이밍까지\n설계할 수 있다는 걸\n모르는 분들이 많습니다.',
            'cta': '내 상황엔 어떻게 적용될지\n궁금하신가요?'
        },
        'caption': '''은퇴하자마자 연금을 받기 시작하면 세금·건강보험료 부담이 함께 늘어날 수 있다는 사실, 알고 계셨나요?

수령 시점 자체를 조절할 수 있는 연금 형태도 있습니다.

1. 은퇴 초반엔 적게 받고 후반에 몰아 받는 방식을 선택할 수 있습니다.
2. 받지 않는 기간에도 공시이율로 계속 불어납니다.
3. 목돈이 필요하면 전체 해지 없이 일부만 인출할 수 있습니다.
4. 다만 미리 인출한 만큼 이후 받는 연금액은 줄어듭니다.

받는 타이밍까지 설계할 수 있다는 걸 모르고 계신 분들이 의외로 많습니다.

#노후준비 #연금 #은퇴설계 #자산관리''',
    },
    {
        'threads': '''연금은 한번 넣으면 못 건드린다고 알고 있지.

⚠️ 아니야. 연 12회까지, 필요할 때 일부 인출할 수 있는 구조도 있어.

해지하는 게 아니라 잔액에서 일부만 빼는 거라 연금 자체는 유지돼.

빼낸 만큼 나중 연금액은 줄어들지만, 급전 막느라 통째로 해지하는 것보단 나아.

10년 안에 뺀 금액 합이 낸 돈을 넘으면 못 빼는 제한은 있어.

유동성이 아예 없는 상품이라고 오해해서 안 알아보는 사람이 많더라.''',
        'card_data': {
            'tag': '# 노후연금',
            'hook_big': '연금은 한번 넣으면\n못 건드린다고 생각하시나요?',
            'hook_sub': '일부 인출이 가능한 구조도 있습니다',
            'points': [
                {'title': '연 12회 일부 인출', 'body': '연 12회까지\n필요할 때 일부\n인출할 수 있습니다.'},
                {'title': '해지가 아닌 인출', 'body': '전체 해지가 아니라\n잔액 일부만 빼는 것이라\n연금은 유지됩니다.'},
                {'title': '인출한 만큼 감소', 'body': '다만 빼낸 만큼\n이후 받는 연금액은\n줄어듭니다.'},
                {'title': '10년 내 인출 한도', 'body': '가입 후 10년 이내에는\n인출 총액이 납입액을\n넘을 수 없습니다.'},
            ],
            'closing': '유동성이 전혀 없는 상품이라고\n오해해서 알아보지 않는 분들이\n많습니다.',
            'cta': '내 상황엔 어떻게 적용될지\n궁금하신가요?'
        },
        'caption': '''연금은 한번 넣으면 절대 못 건드린다고 알고 계신가요?

연 12회까지, 필요할 때 일부 인출이 가능한 구조도 있습니다.

1. 전체 해지가 아니라 잔액에서 일부만 인출하는 것이라 연금은 그대로 유지됩니다.
2. 다만 인출한 만큼 이후 받는 연금액은 줄어듭니다.
3. 가입 후 10년 이내에는 인출 총액이 납입한 금액을 넘을 수 없다는 제한이 있습니다.
4. 급전이 필요할 때 전체를 해지하는 것보다는 나은 선택이 될 수 있습니다.

유동성이 전혀 없는 상품이라고 오해해서 아예 알아보지 않는 분들이 의외로 많습니다.

#노후준비 #연금 #은퇴설계 #자산관리''',
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
    paths = cg.generate_card_set(variant['card_data'], output_dir='annuity_cards_tmp', category='insurance')
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

    time.sleep(3)
    rc = requests.post(f'{BASE_IG}/{media_id}/comments',
                       params={'message': CONSULT_COMMENT_IG, 'access_token': TOKEN}, timeout=30)
    print('상담링크 댓글:', rc.json())
    return media_id


def main():
    week = datetime.now(KST).isocalendar()[1]
    variant = VARIANTS[week % len(VARIANTS)]
    print(f'=== 연금보험 주간 포스팅 (variant {week % len(VARIANTS)}) ===')

    threads_id = post_threads(variant)
    if threads_id:
        nap.log_content(threads_id, 'insurance', 'annuity_sales', '연금보험 노후설계 소재',
                        line_count=variant['threads'].count('\n') + 1)

    ig_id = post_instagram(variant)
    if ig_id:
        log_instagram(ig_id, '연금보험 노후설계 소재')


if __name__ == '__main__':
    main()
