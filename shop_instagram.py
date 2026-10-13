#!/usr/bin/env python3
"""쇼핑 계정(.env.shop) 전용 Instagram 발행 (Instagram Login API, graph.instagram.com) — KB 계정과 분리
사용:
  python shop_instagram.py --reel 영상URL --caption "캡션" [--dry]
  python shop_instagram.py --image 이미지URL --caption "캡션"
  python shop_instagram.py --refresh     # 60일 토큰 갱신
영상/이미지는 공개 URL이어야 함(GitHub Release 등).
"""
import os, sys, time, argparse
import requests
from dotenv import dotenv_values

sys.stdout.reconfigure(encoding='utf-8')
ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env.shop')
ENV = dotenv_values(ENV_PATH)
TOKEN = os.environ.get('SHOP_IG_LOGIN_TOKEN') or ENV.get('SHOP_IG_LOGIN_TOKEN')
UID = os.environ.get('SHOP_IG_USER_ID') or ENV.get('SHOP_IG_USER_ID')
BASE = 'https://graph.instagram.com/v21.0'


def post(media_url, caption, kind='reel', dry=False):
    if not TOKEN:
        sys.exit('SHOP_IG_LOGIN_TOKEN 없음 (.env.shop 확인)')
    params = {'caption': caption, 'access_token': TOKEN}
    if kind == 'reel':
        params.update(media_type='REELS', video_url=media_url, share_to_feed='true')
    else:
        params['image_url'] = media_url
    if dry:
        print('[DRY]', kind, media_url, '\n', caption)
        return None
    r = requests.post(f'{BASE}/me/media', data=params, timeout=60).json()
    print('컨테이너:', r)
    cid = r.get('id')
    if not cid:
        return None
    for i in range(40):
        time.sleep(8)
        s = requests.get(f'{BASE}/{cid}', params={'fields': 'status_code,status', 'access_token': TOKEN}, timeout=30).json()
        print(f'  처리 상태 ({i+1}/40):', s.get('status_code'), s.get('status', ''))
        if s.get('status_code') == 'FINISHED':
            break
        if s.get('status_code') in ('ERROR', 'EXPIRED'):
            return None
    else:
        return None
    p = requests.post(f'{BASE}/me/media_publish', data={'creation_id': cid, 'access_token': TOKEN}, timeout=60).json()
    print('발행:', p)
    return p.get('id')


def refresh():
    r = requests.get('https://graph.instagram.com/refresh_access_token',
                     params={'grant_type': 'ig_refresh_token', 'access_token': TOKEN}, timeout=30).json()
    print({k: v for k, v in r.items() if k != 'access_token'})
    if 'access_token' in r:
        lines = open(ENV_PATH, encoding='utf-8').read().splitlines()
        out = [('SHOP_IG_LOGIN_TOKEN=' + r['access_token']) if l.startswith('SHOP_IG_LOGIN_TOKEN=') else l for l in lines]
        open(ENV_PATH, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
        print('토큰 갱신·저장 완료')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--reel')
    ap.add_argument('--image')
    ap.add_argument('--caption', default='')
    ap.add_argument('--dry', action='store_true')
    ap.add_argument('--refresh', action='store_true')
    a = ap.parse_args()
    if a.refresh:
        refresh()
    elif a.reel:
        post(a.reel, a.caption, 'reel', a.dry)
    elif a.image:
        post(a.image, a.caption, 'image', a.dry)
    else:
        ap.print_help()
