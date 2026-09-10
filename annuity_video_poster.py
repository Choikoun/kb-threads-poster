#!/usr/bin/env python3
"""
연금보험 소재 릴스형 영상 (Threads 반말 + Instagram Reels 존댓말) — 1회성
- annuity_poster.py의 5번째 각도(가입시기 3년 비교)를 영상으로 재구성
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

HOOK = '3년 차이가\n매달 10만원을 가른다'

SCENES = [
    {'image_query': 'calendar clock desk planning'},
    {'image_query': 'elderly couple retirement savings'},
    {'image_query': 'growing coins savings jar'},
    {'image_query': 'peaceful senior lifestyle sunset'},
]

NARRATION_THREADS = (
    '연금보험, 가입 시기가 3년만 달라져도 받는 돈이 이렇게 벌어져. '
    '34세에 가입하면 65세부터 매달 73만원, 37세에 가입하면 같은 조건인데 매달 63만원. '
    '100세까지 다 받으면 4천만원 넘게 차이가 나. 자세한 계산은 캡션에서 확인해봐.'
)
NARRATION_IG = (
    '연금보험은 가입 시기가 3년만 달라져도 받는 금액이 크게 벌어집니다. '
    '34세에 가입하면 65세부터 매달 73만원, 37세에 가입하면 같은 조건에서 매달 63만원을 받습니다. '
    '100세까지 누적하면 4천만원 넘게 차이가 납니다. 자세한 계산은 캡션에서 확인해보세요.'
)

CAPTION_THREADS = '''연금보험 가입 시점 3년 차이가 실제로 얼마나 벌어질까?

같은 조건(월 80만원, 7년납, 65세 개시)으로 비교하면—

34세에 가입하면 65세부터 매달 73만원.
37세에 가입하면 매달 63만원.
100세까지 누적으로 보면 3억 1,609만원 vs 2억 7,469만원 — 약 4,100만원 차이.

거치 기간이 길수록 최저연금기준금액에 붙는 이자가 더 오래 쌓이는 구조라서 그래.

물론 실제 수령액은 공시이율 변동에 따라 달라질 수 있고, 중도 해지 시엔 원금보다 적을 수 있어. (2026년 8월 공시이율 2.55% 기준 예시)

고민하는 동안 흘러가는 시간이, 그대로 손해로 쌓인다는 거.'''

CAPTION_IG = '''연금보험, 가입 시점 3년 차이가 실제로 얼마나 벌어질까요?

같은 조건(월 80만원, 7년납, 65세 개시)으로 비교해보면:
1. 34세에 가입하면 65세부터 매달 73만원
2. 37세에 가입하면 65세부터 매달 63만원
3. 100세까지 누적으로 보면 3억 1,609만원 vs 2억 7,469만원 — 약 4,100만원 차이

거치 기간이 길수록 최저연금기준금액에 붙는 이자가 더 오래 쌓이는 구조이기 때문입니다. (2026년 8월 공시이율 2.55% 기준 예시금액)

노후 준비를 고민 중이시라면, '언제 시작하느냐'도 중요한 변수라는 점 참고하시길 바랍니다.

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
            nap.log_content(main_id, 'insurance', 'annuity_sales_video', '연금보험 가입시기 비교 릴스',
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
                           'selected_title': '연금보험 가입시기 비교 릴스',
                           'date': datetime.now(KST).strftime('%Y-%m-%d %H:%M')})
            save_ig_log(ig_log)
            print(f'Instagram 완료: {ig_id}')
        else:
            print('Instagram 포스팅 실패')

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == '__main__':
    main()
