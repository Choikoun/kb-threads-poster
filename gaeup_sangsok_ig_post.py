#!/usr/bin/env python3
"""
가업상속공제 요건 강화(2026 세제개편안) 소재 인스타 카드뉴스 1회성 게시
"""
import os, sys, time, requests
sys.stdout.reconfigure(encoding='utf-8')

import card_generator as cg

TOKEN = os.environ['INSTAGRAM_ACCESS_TOKEN']
IG_USER_ID = os.environ['INSTAGRAM_BUSINESS_ACCOUNT_ID']
BASE_IG = 'https://graph.facebook.com/v21.0'

CARD_DATA = {
    'tag': '# 가업상속공제',
    'hook_big': '가업상속공제 요건이\n10년에서 30년으로',
    'hook_sub': '2026년 세제개편안 기준, 아직 개정안 단계입니다',
    'points': [
        {'title': '경영기간 요건 3배', 'body': '피상속인 계속경영 요건이\n10년에서 30년으로\n늘어날 예정입니다.'},
        {'title': '상속인 요건도 강화', 'body': '상속 전 가업 종사 기간이\n2년에서 5년으로\n늘어날 예정입니다.'},
        {'title': '사후관리 기간 2배', 'body': '공제 받은 뒤 지켜야 하는\n사후관리 기간이\n5년에서 10년으로 늘어납니다.'},
        {'title': '한도는 늘지만', 'body': '공제 한도는 최대\n1,000억원까지 늘지만,\n그만큼 요건도 까다로워집니다.'},
    ],
    'closing': '가업승계, 물려받는 것보다\n물려받고 지키는 게\n더 길어질 전망입니다.',
    'cta': '우리 회사는 어떻게 준비해야 할지\n궁금하신가요?'
}

CAPTION = '''가업상속공제, 받는 조건이 훨씬 까다로워질 전망입니다.

2026년 세제개편안(2026.8.3 기획재정부 발표, 아직 국회 통과 전 개정안 단계) 기준으로 말씀드리면,

1. 피상속인의 계속경영 요건이 10년에서 30년으로 늘어날 예정입니다.
2. 상속인이 상속 전 가업에 종사해야 하는 기간도 2년에서 5년으로 늘어날 예정입니다.
3. 공제를 받은 뒤 지켜야 하는 사후관리 기간도 5년에서 10년으로 두 배 늘어납니다.
4. 다만 공제 한도는 최대 1,000억 원까지 늘어날 예정입니다.

아직 확정된 법은 아니지만, 방향은 분명해 보입니다. 준비할 시간이 있을 때 미리 점검해보시는 걸 추천드립니다.

#가업상속 #가업승계 #세제개편 #법인대표'''

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
    paths = cg.generate_card_set(CARD_DATA, output_dir='gaeup_sangsok_cards_tmp', category='corporate')
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
