#!/usr/bin/env python3
"""
인스타그램 릴스 포스터
뉴스 기반 세로형 영상(9:16) + TTS → Instagram Reels 발행
매일 20:00 KST, 카테고리는 business 50% + 나머지 5개 균등 10%씩 랜덤 선택
"""
import os, sys, json, time, random, requests, tempfile, shutil
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import news_auto_poster as nap
from video_poster import (
    generate_content, create_scene_frames,
    generate_narration, get_audio_duration, build_video_multi, BGM_PATH,
)

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

TOKEN = os.environ['INSTAGRAM_ACCESS_TOKEN']
IG_USER_ID = os.environ['INSTAGRAM_BUSINESS_ACCOUNT_ID']
BASE_IG = 'https://graph.facebook.com/v21.0'
KST = timezone(timedelta(hours=9))
IG_LOG_FILE = 'instagram_log.json'

CATEGORY_WEIGHTS = {
    'business':   0.5,
    'economy':    0.1,
    'insurance':  0.1,
    'policy':     0.1,
    'government': 0.1,
    'trend':      0.1,
}

CATEGORY_HASHTAGS = {
    'business':   '#법인절세 #사업주 #법인세금 #절세 #자산설계 #세금 #법인운영 #대표이사',
    'economy':    '#경제 #주식 #시장 #투자 #경제뉴스 #재테크 #자산관리 #금융',
    'insurance':  '#보험 #연금 #노후준비 #상속 #증여 #자산설계 #세금 #노후자금',
    'policy':     '#세금 #정책 #세법개정 #시행령 #절세 #세무 #법인세 #소득세',
    'government': '#정책 #경제정책 #부동산 #세금 #정부정책 #자산관리 #시사 #경제',
    'trend':      '#오늘의이슈 #트렌드 #이슈 #경제이슈 #오늘 #뉴스 #화제 #핫이슈',
}


GROWTH_LINES = [
    '저장해두고 나중에 다시 봐.',
    '주변에 비슷한 상황인 사람 있으면 공유해줘.',
    '이런 얘기 계속 보고 싶으면 팔로우해놔.',
    '나중에 또 보고 싶으면 저장해.',
    '관련 있는 사람한테 보내줘.',
    '더 자세한 얘기는 쓰레드에도 있어.',
]


def choose_category():
    categories = list(CATEGORY_WEIGHTS.keys())
    weights = list(CATEGORY_WEIGHTS.values())
    return random.choices(categories, weights=weights, k=1)[0]


def load_ig_log():
    if os.path.exists(IG_LOG_FILE):
        with open(IG_LOG_FILE, encoding='utf-8') as f:
            return json.load(f)
    return []


def save_ig_log(log):
    with open(IG_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def post_reels(video_url, caption):
    # 1. 릴스 컨테이너 생성
    r = requests.post(f'{BASE_IG}/{IG_USER_ID}/media',
                      params={
                          'media_type': 'REELS',
                          'video_url': video_url,
                          'caption': caption,
                          'access_token': TOKEN,
                      }, timeout=30)
    data = r.json()
    container_id = data.get('id')
    if not container_id:
        print(f'컨테이너 생성 실패: {data}')
        return None
    print(f'릴스 컨테이너: {container_id}')

    # 2. 처리 완료 대기 (최대 5분, 10초 간격)
    for attempt in range(30):
        time.sleep(10)
        sr = requests.get(f'{BASE_IG}/{container_id}',
                          params={'fields': 'status_code', 'access_token': TOKEN},
                          timeout=30)
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

    # 3. 발행
    r = requests.post(f'{BASE_IG}/{IG_USER_ID}/media_publish',
                      params={'creation_id': container_id, 'access_token': TOKEN},
                      timeout=30)
    data = r.json()
    ig_id = data.get('id')
    if not ig_id:
        print(f'발행 실패: {data}')
    return ig_id


def main():
    category = sys.argv[1] if len(sys.argv) > 1 else choose_category()
    print(f'=== 인스타그램 릴스 포스터 [{category}] ===')

    articles = nap.get_hot_news(category)
    print(f'뉴스 {len(articles)}개 수집')

    print('Gemini 콘텐츠 생성 중...')
    content = generate_content(articles, category)
    if not content:
        print('콘텐츠 생성 실패 - 종료')
        sys.exit(1)

    print(f"선택 뉴스: {content['selected_title']}")
    print(f"내레이션: {content['narration']}")

    growth_line = random.choice(GROWTH_LINES)
    hashtags = CATEGORY_HASHTAGS.get(category, CATEGORY_HASHTAGS['business'])
    caption = f"{content['caption']}\n\n{growth_line}\n\n{hashtags}"

    tmp_dir = tempfile.mkdtemp()
    try:
        audio_path = os.path.join(tmp_dir, 'narration.mp3')
        video_path = os.path.join(tmp_dir, 'reels.mp4')

        # 장면(3~4컷) 프레임 생성 — 첫 컷은 훅 화면
        print('장면 프레임 생성 중...')
        frames = create_scene_frames(content, out_dir=tmp_dir)
        if not frames:
            print('비주얼 생성 실패 - 종료')
            sys.exit(1)

        print('TTS 생성 중...')
        generate_narration(content['narration'], output_path=audio_path)
        duration = get_audio_duration(audio_path)
        print(f'  {duration:.1f}초')

        print('영상 빌드 중...')
        build_video_multi(frames, audio_path, output_path=video_path, duration=duration, bgm_path=BGM_PATH)

        print('GitHub Release 업로드 중...')
        video_url = nap.upload_to_github_release(video_path)
        if not video_url:
            print('업로드 실패 - 종료')
            sys.exit(1)

        print('Instagram 릴스 발행 중...')
        ig_id = post_reels(video_url, caption)
        if not ig_id:
            print('릴스 발행 실패 - 종료')
            sys.exit(1)

        print(f'완료! Instagram Reels ID: {ig_id}')
        ig_log = load_ig_log()
        ig_log.append({
            'ig_post_id': ig_id,
            'type': 'reels',
            'selected_title': content['selected_title'],
            'date': datetime.now(KST).strftime('%Y-%m-%d %H:%M'),
        })
        save_ig_log(ig_log)

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == '__main__':
    main()
