#!/usr/bin/env python3
"""
연금보험 소재 릴스형 영상 (Threads 반말 + Instagram Reels 존댓말) — 1회성
- annuity_poster.py의 2번째 각도(사망보장)를 영상으로 재구성
- Gemini 미사용(고정 스크립트), video_poster.py/instagram_reels_poster.py의
  파이프라인(장면합성·TTS·ffmpeg)만 재사용
- 상품명·회사명 비노출, 상담링크는 항상 댓글에만 (기존 정책 동일)
"""
import os, sys, json, tempfile, shutil, requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

import news_auto_poster as nap
from video_poster import (
    create_scene_frames, generate_narration_timed, make_subtitle_phrases,
    get_audio_duration, build_video_multi, pick_bgm,
)

KST = timezone(timedelta(hours=9))
IG_LOG_FILE = 'instagram_log.json'
CONSULT_COMMENT_THREADS = '이 얘기 더 궁금하면 여기서 확인할 수 있어 → https://naver.me/FRLbSbiJ'
CONSULT_COMMENT_IG = '더 자세한 내용이 궁금하시면 아래에서 확인해보세요 → https://naver.me/FRLbSbiJ'

HOOK = '연금 받다가 일찍 죽으면\n가족은 손해만 볼까'

SCENES = [
    {'image_query': 'family holding hands support'},
    {'image_query': 'elderly parent adult child care'},
    {'image_query': 'piggy bank protection security'},
    {'image_query': 'peaceful senior lifestyle sunset'},
]

NARRATION_THREADS = (
    '연금 받다가 일찍 죽으면 가족이 손해만 본다고 생각하지. '
    '근데 최소한은 막아주는 구조가 있어. 이미 낸 보험료의 백이십 퍼센트에서 그동안 받은 연금을 뺀 만큼은 최소한 가족한테 남아. '
    '오래 받을수록 이 금액은 줄어들지만, 가족이 받는 돈이 0원 밑으로는 안 내려가. 자세한 계산은 캡션에서 확인해봐.'
)
NARRATION_IG = (
    '연금을 받다가 일찍 사망하시면 가족이 손해만 본다고 생각하실 수 있습니다. '
    '하지만 최소한은 보장해주는 구조가 있습니다. 이미 낸 보험료의 120%에서 그동안 받은 연금을 뺀 금액만큼은 최소한 가족에게 남습니다. '
    '오래 받으실수록 이 금액은 줄어들지만, 0원 밑으로는 내려가지 않습니다. 자세한 계산은 캡션에서 확인해보세요.'
)

CAPTION_THREADS = '''연금 받다가 일찍 죽으면 손해만 본다고 생각하지.

근데 최소한은 막아주는 구조가 있어.

이미 낸 보험료의 120%에서, 그동안 받은 연금을 뺀 나머지는 가족한테 남아.

오래 받을수록 이 금액은 줄어들지만, 가족이 받는 돈이 0원 아래로는 안 내려가.

반대로 오래 살아도 걱정 없어. 살아있는 동안은 계속 나오는 구조니까.

물론 중간에 해지하면 얘기가 달라져. 원금보다 적게 나올 수 있어.

연금은 얼마나 받나보다, 언제 죽어도 손해 안 보는지가 먼저야.'''

CAPTION_IG = '''연금을 받다가 일찍 사망하시면 손해만 본다고 생각하시나요?

최소한은 보장해주는 구조가 있습니다.

1. 이미 낸 보험료의 120%에서 그동안 받은 연금을 뺀 금액만큼은 가족에게 남습니다.
2. 오래 받으실수록 이 금액은 줄어들지만, 가족이 받는 돈이 0원 아래로 내려가지는 않습니다.
3. 반대로 오래 사셔도 걱정 없습니다. 생존하시는 동안은 계속 지급되는 구조입니다.

다만 중도 해지 시에는 해약환급금이 납입한 금액보다 적을 수 있습니다.

연금은 '얼마나 받나'보다 '언제 사망해도 손해 보지 않는가'를 먼저 따져보시길 권합니다.

#노후준비 #연금보험 #은퇴설계 #자산관리'''


def load_ig_log():
    if os.path.exists(IG_LOG_FILE):
        with open(IG_LOG_FILE, encoding='utf-8') as f:
            return json.load(f)
    return []


def save_ig_log(log):
    with open(IG_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def post_reels(video_url, caption):
    TOKEN = os.environ['INSTAGRAM_ACCESS_TOKEN']
    IG_USER_ID = os.environ['INSTAGRAM_BUSINESS_ACCOUNT_ID']
    BASE_IG = 'https://graph.facebook.com/v21.0'

    r = requests.post(f'{BASE_IG}/{IG_USER_ID}/media',
                      params={'media_type': 'REELS', 'video_url': video_url, 'caption': caption,
                              'thumb_offset': 800, 'access_token': TOKEN}, timeout=30)
    data = r.json()
    container_id = data.get('id')
    if not container_id:
        print(f'컨테이너 생성 실패: {data}')
        return None
    print(f'릴스 컨테이너: {container_id}')

    import time
    for attempt in range(30):
        time.sleep(10)
        sr = requests.get(f'{BASE_IG}/{container_id}',
                          params={'fields': 'status_code', 'access_token': TOKEN}, timeout=30)
        status = sr.json().get('status_code')
        print(f'  처리 상태 ({attempt+1}/30): {status}')
        if status == 'FINISHED':
            break
        if status == 'ERROR':
            print(f'  오류: {sr.json()}')
            return None
    else:
        print('  처리 타임아웃')
        return None

    r = requests.post(f'{BASE_IG}/{IG_USER_ID}/media_publish',
                      params={'creation_id': container_id, 'access_token': TOKEN}, timeout=30)
    ig_id = r.json().get('id')
    if not ig_id:
        print(f'발행 실패: {r.json()}')
        return None

    time.sleep(3)
    rc = requests.post(f'{BASE_IG}/{ig_id}/comments',
                       params={'message': CONSULT_COMMENT_IG, 'access_token': TOKEN}, timeout=30)
    print('상담링크 댓글:', rc.json())
    return ig_id


def main():
    tmp_dir = tempfile.mkdtemp()
    try:
        print('장면 프레임 생성 중...')
        frames = create_scene_frames({'hook': HOOK, 'scenes': SCENES}, out_dir=tmp_dir, use_scene_text=False)
        if not frames:
            print('비주얼 생성 실패 - 종료')
            sys.exit(1)
        bgm = pick_bgm()

        # --- Threads ---
        print('=== Threads 영상 생성 ===')
        audio_th = os.path.join(tmp_dir, 'narration_threads.mp3')
        _, boundaries_th = generate_narration_timed(NARRATION_THREADS, output_path=audio_th)
        phrases_th = make_subtitle_phrases(boundaries_th)
        duration_th = get_audio_duration(audio_th)
        video_th = os.path.join(tmp_dir, 'video_threads.mp4')
        build_video_multi(frames, audio_th, output_path=video_th, duration=duration_th,
                          bgm_path=bgm, phrases=phrases_th, work_dir=tmp_dir)

        video_url_th = nap.upload_to_github_release(video_th)
        if not video_url_th:
            print('Threads 영상 업로드 실패 - 종료')
            sys.exit(1)

        main_id = nap.post_video_to_threads(CAPTION_THREADS, [CONSULT_COMMENT_THREADS], video_url_th)
        if main_id:
            nap.log_content(main_id, 'insurance', 'annuity_sales_video', '연금보험 사망보장 릴스',
                            line_count=CAPTION_THREADS.count('\n') + 1)
            print(f'Threads 완료: {main_id}')
        else:
            print('Threads 포스팅 실패')

        # --- Instagram ---
        print('=== Instagram Reels 영상 생성 ===')
        audio_ig = os.path.join(tmp_dir, 'narration_ig.mp3')
        _, boundaries_ig = generate_narration_timed(NARRATION_IG, output_path=audio_ig)
        phrases_ig = make_subtitle_phrases(boundaries_ig)
        duration_ig = get_audio_duration(audio_ig)
        video_ig = os.path.join(tmp_dir, 'video_ig.mp4')
        build_video_multi(frames, audio_ig, output_path=video_ig, duration=duration_ig,
                          bgm_path=bgm, phrases=phrases_ig, work_dir=tmp_dir)

        video_url_ig = nap.upload_to_github_release(video_ig)
        if not video_url_ig:
            print('IG 영상 업로드 실패 - 종료')
            sys.exit(1)

        ig_id = post_reels(video_url_ig, CAPTION_IG)
        if ig_id:
            ig_log = load_ig_log()
            ig_log.append({'ig_post_id': ig_id, 'type': 'reels',
                           'selected_title': '연금보험 사망보장 릴스',
                           'date': datetime.now(KST).strftime('%Y-%m-%d %H:%M')})
            save_ig_log(ig_log)
            print(f'Instagram 완료: {ig_id}')
        else:
            print('Instagram 포스팅 실패')

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == '__main__':
    main()
