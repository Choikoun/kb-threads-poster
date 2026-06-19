#!/usr/bin/env python3
"""
인스타그램 릴스 포스터
뉴스 기반 세로형 영상(9:16) + TTS → Instagram Reels 발행
주 1회 (수요일 20:00 KST)
"""
import os, sys, json, time, requests, tempfile, shutil
from datetime import datetime, timezone, timedelta
from PIL import Image
from dotenv import load_dotenv
import news_auto_poster as nap
from ai_illustration_poster import generate_illustration
from stock_card_poster import search_pexels_photo
from video_poster import (
    generate_content, get_visual_source,
    compose_frame, generate_narration, get_audio_duration, build_video,
)

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

TOKEN = os.environ['INSTAGRAM_ACCESS_TOKEN']
IG_USER_ID = os.environ['INSTAGRAM_BUSINESS_ACCOUNT_ID']
BASE_IG = 'https://graph.facebook.com/v21.0'
KST = timezone(timedelta(hours=9))
IG_LOG_FILE = 'instagram_log.json'

HASHTAGS = '#법인절세 #사업주 #절세 #법인세금 #자산설계 #세금 #증여 #상속 #세금공부 #금융'


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
    category = sys.argv[1] if len(sys.argv) > 1 else 'business'
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

    caption = f"{content['caption']}\n\n{HASHTAGS}"

    tmp_dir = tempfile.mkdtemp()
    try:
        raw_path = os.path.join(tmp_dir, 'raw.jpg')
        frame_path = os.path.join(tmp_dir, 'frame.jpg')
        audio_path = os.path.join(tmp_dir, 'narration.mp3')
        video_path = os.path.join(tmp_dir, 'reels.mp4')

        # 비주얼 생성 (AI 일러스트 / Pexels 교대)
        print('비주얼 생성 중...')
        source = get_visual_source()
        raw = None
        if source == 'illustration':
            print('  AI 일러스트')
            png = os.path.join(tmp_dir, 'ai_raw.png')
            result = generate_illustration(content['image_prompt'], output_path=png)
            if result:
                Image.open(result).convert('RGB').save(raw_path, 'JPEG', quality=95)
                raw = raw_path
        if not raw:
            print(f'  Pexels ({content["image_query"]})')
            raw = search_pexels_photo(content['image_query'], output_path=raw_path, orientation='portrait')
        if not raw:
            print('비주얼 생성 실패 - 종료')
            sys.exit(1)

        print('프레임 합성 중...')
        compose_frame(raw, content['headline'], output_path=frame_path)

        print('TTS 생성 중...')
        generate_narration(content['narration'], output_path=audio_path)
        duration = get_audio_duration(audio_path)
        print(f'  {duration:.1f}초')

        print('영상 빌드 중...')
        build_video(frame_path, audio_path, output_path=video_path, duration=duration)

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
        nap.log_content(ig_id, category, 'reels', content['selected_title'])

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == '__main__':
    main()
