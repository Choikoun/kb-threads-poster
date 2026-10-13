#!/usr/bin/env python3
"""
쇼핑 계정(.env.shop) 전용 Threads 발행 — KB 계정 토큰과 완전 분리
사용:
  python shop_threads.py --text "본문" [--image URL | --video URL] [--reply "답글1" --reply "답글2"] [--dry]
  python shop_threads.py --refresh      # 60일 토큰 갱신
- 영상/이미지는 공개 URL이어야 함 (GitHub Release 등)
- 쿠팡 파트너스 링크가 들어가는 답글에는 수수료 표시 문구(DISCLOSURE)를 자동으로 붙임
"""
import os, sys, time, argparse
import requests
from dotenv import dotenv_values

sys.stdout.reconfigure(encoding='utf-8')
ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env.shop')
ENV = dotenv_values(ENV_PATH)
TOKEN = os.environ.get('SHOP_THREADS_ACCESS_TOKEN') or ENV.get('SHOP_THREADS_ACCESS_TOKEN')
BASE = 'https://graph.threads.net/v1.0'
DISCLOSURE = '이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.'


def _wait_finished(cid, tries=30):
    for i in range(tries):
        time.sleep(10)
        d = requests.get(f'{BASE}/{cid}', params={'fields': 'status,error_message', 'access_token': TOKEN}, timeout=30).json()
        print(f'  처리 상태 ({i+1}/{tries}): {d.get("status")}')
        if d.get('status') == 'FINISHED':
            return True
        if d.get('status') == 'ERROR':
            print('  오류:', d.get('error_message'))
            return False
    return False


def _publish(cid):
    r = requests.post(f'{BASE}/me/threads_publish', params={'creation_id': cid, 'access_token': TOKEN}, timeout=30).json()
    return r.get('id'), r


def post(text, image=None, video=None, replies=(), dry=False):
    if not TOKEN:
        sys.exit('SHOP_THREADS_ACCESS_TOKEN 없음 (.env.shop 확인)')
    params = {'text': text, 'access_token': TOKEN}
    if video:
        params.update(media_type='VIDEO', video_url=video)
    elif image:
        params.update(media_type='IMAGE', image_url=image)
    else:
        params['media_type'] = 'TEXT'
    replies = [r + ('\n\n' + DISCLOSURE if ('coupang' in r.lower() or 'link.coupang' in r) and DISCLOSURE not in r else '') for r in replies]
    if dry:
        print('[DRY] 본문:', text, '\n미디어:', video or image or '-')
        for i, r in enumerate(replies, 1):
            print(f'[DRY] 답글{i}:', r)
        return None
    r1 = requests.post(f'{BASE}/me/threads', params=params, timeout=60).json()
    print('컨테이너:', r1)
    cid = r1.get('id')
    if not cid:
        return None
    if video:
        if not _wait_finished(cid):
            return None
    else:
        time.sleep(4)
    main_id, raw = _publish(cid)
    print('메인 발행:', main_id or raw)
    if not main_id:
        return None
    time.sleep(3)
    for i, rep in enumerate(replies, 1):
        rc = requests.post(f'{BASE}/me/threads', params={'media_type': 'TEXT', 'text': rep, 'reply_to_id': main_id,
                                                         'access_token': TOKEN}, timeout=30).json()
        time.sleep(3)
        rid, raw = _publish(rc.get('id'))
        print(f'답글{i} 발행:', rid or raw)
        time.sleep(2)
    return main_id


def reply_to(post_id, text):
    """이미 올라간 쓰레드 글에 답글 추가(쿠팡 링크 포함 시 수수료 문구 자동)"""
    if 'coupang' in text.lower() and DISCLOSURE not in text:
        text += '\n\n' + DISCLOSURE
    rc = requests.post(f'{BASE}/me/threads', params={'media_type': 'TEXT', 'text': text, 'reply_to_id': post_id,
                                                     'access_token': TOKEN}, timeout=30).json()
    time.sleep(3)
    rid, raw = _publish(rc.get('id'))
    print('답글 발행:', rid or raw)
    return rid


def refresh():
    r = requests.get('https://graph.threads.net/refresh_access_token',
                     params={'grant_type': 'th_refresh_token', 'access_token': TOKEN}, timeout=30).json()
    print({k: v for k, v in r.items() if k != 'access_token'})
    if 'access_token' in r:
        lines = open(ENV_PATH, encoding='utf-8').read().splitlines()
        out = [('SHOP_THREADS_ACCESS_TOKEN=' + r['access_token']) if l.startswith('SHOP_THREADS_ACCESS_TOKEN=') else l for l in lines]
        open(ENV_PATH, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
        print('토큰 갱신·저장 완료')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--text')
    ap.add_argument('--image')
    ap.add_argument('--video')
    ap.add_argument('--reply', action='append', default=[])
    ap.add_argument('--dry', action='store_true')
    ap.add_argument('--refresh', action='store_true')
    ap.add_argument('--reply-to')
    a = ap.parse_args()
    if a.refresh:
        refresh()
    elif a.reply_to and a.text:
        reply_to(a.reply_to, a.text)
    elif a.text:
        post(a.text, a.image, a.video, a.reply, a.dry)
    else:
        ap.print_help()
