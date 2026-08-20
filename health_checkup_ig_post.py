#!/usr/bin/env python3
"""
건강검진 이상판정·1인실 입원비 소재 인스타 카드뉴스 1회성 게시
"""
import os, sys, time, requests
sys.stdout.reconfigure(encoding='utf-8')

import card_generator as cg

TOKEN = os.environ['INSTAGRAM_ACCESS_TOKEN']
IG_USER_ID = os.environ['INSTAGRAM_BUSINESS_ACCOUNT_ID']
BASE_IG = 'https://graph.facebook.com/v21.0'

CARD_DATA = {
    'tag': '# 건강검진',
    'hook_big': '건강검진 받으면\n대부분 정상일까요?',
    'hook_sub': '10명 중 6명은 이상 판정을 받습니다',
    'points': [
        {'title': '이상 판정 60.9%', 'body': '지난해 국가건강검진\n수검자 10명 중 6명이\n질환의심·유질환 판정입니다.'},
        {'title': '1인실을 쓰게 되는 이유', 'body': '다인실 자리가 없어\n1인실을 쓰게 되는 경우가\n생각보다 많습니다.'},
        {'title': '비급여라 부담이 큽니다', 'body': '대학병원 기준 하루\n40~50만 원, 종합병원도\n20~30만 원대입니다.'},
        {'title': '입원일당을 따로 준비', 'body': '그래서 병실 종류별로\n입원일당을 준비해두는 분들이\n늘고 있습니다.'},
    ],
    'closing': '정상이길 바라는 것과\n만약을 대비하는 것은\n다른 이야기입니다.',
    'cta': '내 보장은 어떻게 돼있는지\n궁금하신가요?'
}

CAPTION = '''건강검진을 받으면 대부분 정상으로 나올 거라고 생각하시나요?

지난해 국가건강검진을 받은 분들 중 10명 중 6명이 질환의심 또는 유질환 판정을 받았습니다.

1. 문제는 그다음입니다. 막상 입원할 때 다인실 자리가 없어 1인실을 쓰게 되는 경우가 생각보다 많습니다.
2. 1인실은 건강보험이 적용되지 않는 비급여 병실이라, 대학병원 기준 하루 40~50만 원, 종합병원도 20~30만 원 정도가 나갑니다.
3. 입원 기간이 길어질수록 부담이 커지는 구조입니다.
4. 그래서 요즘은 병실 종류별로 입원일당을 따로 준비해두시는 분들이 늘고 있습니다.

검진 결과가 정상이길 바라는 것과, 만약을 대비해두는 것은 다른 이야기입니다.

#건강검진 #실손보험 #입원비 #보험상식'''


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
    paths = cg.generate_card_set(CARD_DATA, output_dir='health_checkup_cards_tmp', category='insurance')
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


if __name__ == '__main__':
    main()
