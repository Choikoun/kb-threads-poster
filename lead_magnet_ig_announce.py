#!/usr/bin/env python3
"""
인스타그램 리드 마그넷 안내 게시물 (1회성 수동 실행)
- 상속·증여 사전점검 체크리스트 12 캐러셀 발행 + ManyChat 댓글→DM 자동화 트리거용
- 댓글 키워드 '점검' → ManyChat이 자동으로 체크리스트 링크 DM 발송
- 인스타는 항상 존댓말
"""
import os, sys, time, requests
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

from card_generator import upload_to_imgbb

TOKEN = os.environ['INSTAGRAM_ACCESS_TOKEN']
IG_USER_ID = os.environ['INSTAGRAM_BUSINESS_ACCOUNT_ID']
BASE_IG = 'https://graph.facebook.com/v21.0'

IMAGES = [
    os.path.join('lead_magnet', 'inheritance_checklist_p1.png'),
    os.path.join('lead_magnet', 'inheritance_checklist_p2.png'),
]

CAPTION = '''상속·증여, 미리 점검해보셨나요?

증여 이력부터 재산 파악, 가족 합의, 세금 준비까지
꼭 확인해야 할 12가지를 정리했습니다.

📌 도움이 필요하시면 댓글에 "점검"이라고 남겨주세요.
DM으로 체크리스트를 바로 보내드립니다.

#상속 #증여 #상속세 #증여세 #자산관리'''


def post_carousel(image_urls, caption):
    child_ids = []
    for i, url in enumerate(image_urls):
        r = requests.post(f'{BASE_IG}/{IG_USER_ID}/media',
                          params={'image_url': url,
                                  'is_carousel_item': 'true',
                                  'access_token': TOKEN}, timeout=30)
        if not r.ok:
            print(f'  이미지 {i+1} 컨테이너 실패: {r.text}')
            return None
        child_ids.append(r.json()['id'])
        print(f'  카드 {i+1}/{len(image_urls)} 컨테이너 생성')
        time.sleep(2)

    r = requests.post(f'{BASE_IG}/{IG_USER_ID}/media',
                      params={'media_type': 'CAROUSEL',
                              'children': ','.join(child_ids),
                              'caption': caption,
                              'access_token': TOKEN}, timeout=30)
    if not r.ok:
        print(f'캐러셀 컨테이너 실패: {r.text}')
        return None
    carousel_id = r.json()['id']
    print(f'캐러셀 컨테이너: {carousel_id}')
    time.sleep(5)

    r = requests.post(f'{BASE_IG}/{IG_USER_ID}/media_publish',
                      params={'creation_id': carousel_id,
                              'access_token': TOKEN}, timeout=30)
    if not r.ok:
        print(f'발행 실패: {r.text}')
        return None
    return r.json()['id']


def main():
    print('체크리스트 이미지 업로드 중...')
    image_urls = []
    for path in IMAGES:
        url = upload_to_imgbb(path)
        if not url:
            print(f'업로드 실패: {path}')
            sys.exit(1)
        image_urls.append(url)
        print(f'  업로드 완료: {url}')

    print('\n캡션:')
    print(CAPTION)
    print()

    post_id = post_carousel(image_urls, CAPTION)
    if not post_id:
        print('게시 실패 - 종료')
        sys.exit(1)
    print(f'완료! 게시물 ID: {post_id}')
    print('이 게시물을 ManyChat 자동화 트리거로 지정하세요.')


if __name__ == '__main__':
    main()
