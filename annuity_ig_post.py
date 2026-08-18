#!/usr/bin/env python3
"""
100세 연금보험 소재 인스타 카드뉴스 1회성 게시 (상품명·회사명 비노출)
"""
import os, sys, time, requests
sys.stdout.reconfigure(encoding='utf-8')

import card_generator as cg

TOKEN = os.environ['INSTAGRAM_ACCESS_TOKEN']
IG_USER_ID = os.environ['INSTAGRAM_BUSINESS_ACCOUNT_ID']
BASE_IG = 'https://graph.facebook.com/v21.0'

CARD_DATA = {
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
}

CAPTION = '''92세까지 사는 시대, 노후자금은 몇 살까지 계산해두셨나요?

대부분 85세를 기준으로 준비하시는데, 실제 기대수명은 그보다 훨씬 깁니다.

1. 살아있는 동안 100세까지 계속 지급되는 연금 형태가 있습니다.
2. 오래 유지할수록 지급률이 올라가는 방식이라, 45년 이상 유지하면 지급률이 최대 60%까지 늘어납니다.
3. 은퇴 초반엔 적게 받고 후반에 몰아 받는 방식도 선택할 수 있습니다.
4. 급하게 목돈이 필요할 땐 일부 인출도 가능한데, 그만큼 이후 연금액은 줄어듭니다.

다만 중도 해지 시에는 납입한 금액보다 해약환급금이 적을 수 있다는 점은 꼭 알아두셔야 합니다.

노후 준비, '몇 살까지 사느냐'를 기준으로 다시 점검해보시길 추천드립니다.

#노후준비 #연금 #은퇴설계 #자산관리'''

CONSULT_COMMENT = '더 자세한 내용이 궁금하시면 아래에서 확인해보세요 → https://naver.me/FRLbSbiJ'


def post_carousel(image_urls, caption):
    child_ids = []
    for i, url in enumerate(image_urls):
        r = requests.post(f'{BASE_IG}/{IG_USER_ID}/media',
                          params={'image_url': url, 'is_carousel_item': 'true', 'access_token': TOKEN}, timeout=30)
        if not r.ok:
            print(f'카드 {i+1} 컨테이너 실패: {r.text}')
            return None
        child_ids.append(r.json()['id'])
        print(f'카드 {i+1}/{len(image_urls)} 컨테이너 생성')
        time.sleep(2)

    r = requests.post(f'{BASE_IG}/{IG_USER_ID}/media',
                      params={'media_type': 'CAROUSEL', 'children': ','.join(child_ids),
                              'caption': caption, 'access_token': TOKEN}, timeout=30)
    if not r.ok:
        print(f'캐러셀 컨테이너 실패: {r.text}')
        return None
    carousel_id = r.json()['id']
    print(f'캐러셀 컨테이너: {carousel_id}')
    time.sleep(5)

    r = requests.post(f'{BASE_IG}/{IG_USER_ID}/media_publish',
                      params={'creation_id': carousel_id, 'access_token': TOKEN}, timeout=30)
    if not r.ok:
        print(f'발행 실패: {r.text}')
        return None
    return r.json()['id']


def main():
    print('카드 이미지 생성 중...')
    paths = cg.generate_card_set(CARD_DATA, output_dir='annuity_cards_tmp', category='insurance')
    print(f'{len(paths)}장 생성 완료')

    print('imgbb 업로드 중...')
    image_urls = []
    for i, p in enumerate(paths):
        url = cg.upload_to_imgbb(p)
        image_urls.append(url)
        print(f'카드 {i+1}/{len(paths)} 업로드 완료: {url}')
        time.sleep(1)

    print('인스타그램 캐러셀 발행 중...')
    media_id = post_carousel(image_urls, CAPTION)
    if not media_id:
        print('발행 실패')
        sys.exit(1)
    print(f'발행 완료! Instagram Post ID: {media_id}')

    time.sleep(3)
    rc = requests.post(f'{BASE_IG}/{media_id}/comments',
                       params={'message': CONSULT_COMMENT, 'access_token': TOKEN}, timeout=30)
    print('상담링크 댓글:', rc.json())


if __name__ == '__main__':
    main()
