#!/usr/bin/env python3
"""
인스타그램 카드뉴스 포스터
쓰레드 상위 포스트 → 5장 카드뉴스 → 인스타 캐러셀 발행
주 2회 자동 실행 (화/목 21:00 KST)
"""
import os, sys, json, re, time, requests, tempfile, shutil
from datetime import datetime, timezone, timedelta
from google import genai
from dotenv import load_dotenv
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

from card_generator import generate_card_set, upload_to_imgbb

TOKEN = os.environ['INSTAGRAM_ACCESS_TOKEN']
IG_USER_ID = os.environ['INSTAGRAM_BUSINESS_ACCOUNT_ID']
THREADS_TOKEN = os.environ['THREADS_ACCESS_TOKEN']
GEMINI_KEY = os.environ['GEMINI_API_KEY']

BASE_IG = 'https://graph.facebook.com/v21.0'
BASE_THREADS = 'https://graph.threads.net/v1.0'
KST = timezone(timedelta(hours=9))
CONTENT_LOG_FILE = 'content_log.json'
IG_LOG_FILE = 'instagram_log.json'


def load_ig_log():
    if os.path.exists(IG_LOG_FILE):
        with open(IG_LOG_FILE, encoding='utf-8') as f:
            return json.load(f)
    return []


def save_ig_log(log):
    with open(IG_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def get_top_post():
    """content_log에서 최근 7일 중 아직 인스타에 올리지 않은 최고 조회수 포스트"""
    if not os.path.exists(CONTENT_LOG_FILE):
        return None
    with open(CONTENT_LOG_FILE, encoding='utf-8') as f:
        log = json.load(f)

    ig_log = load_ig_log()
    posted_thread_ids = {e.get('threads_post_id') for e in ig_log}

    cutoff = (datetime.now(KST) - timedelta(days=7)).strftime('%Y-%m-%d')
    recent = [e for e in log
              if e.get('date', '') >= cutoff
              and e.get('post_id') not in posted_thread_ids
              and e.get('post_id')]

    if not recent:
        return None

    best = None
    best_views = -1
    for entry in recent[:15]:
        pid = entry['post_id']
        try:
            r = requests.get(f'{BASE_THREADS}/{pid}/insights',
                             params={'metric': 'views', 'access_token': THREADS_TOKEN}, timeout=10)
            views = 0
            if r.ok:
                data = r.json().get('data', [])
                if data:
                    vals = data[0].get('values', [])
                    views = (vals[0].get('value', 0) if vals
                             else data[0].get('total_value', {}).get('value', 0))
            if views > best_views:
                best_views = views
                best = {**entry, 'views': views}
        except Exception as e:
            print(f'  조회수 확인 실패 ({pid}): {e}')

    return best


def get_post_text(post_id):
    r = requests.get(f'{BASE_THREADS}/{post_id}',
                     params={'fields': 'text', 'access_token': THREADS_TOKEN}, timeout=15)
    if r.ok:
        return r.json().get('text', '')
    return ''


def generate_card_data(post_text):
    client = genai.Client(api_key=GEMINI_KEY)
    prompt = f"""아래 Threads 포스팅을 인스타그램 카드뉴스 데이터로 변환해줘.

원본 포스팅:
{post_text}

[규칙]
- 전부 반말
- 상담/DM 유도 절대 금지
- 짧고 강하게
- 숫자·구체적 기준 살리기

JSON만 출력:
{{
  "hook_big": "훅 한 줄 (20자 이내, 반전형)",
  "hook_sub": "훅 보조 설명 (30자 이내)",
  "tag": "# 주제 태그 (예: # 상속세 핵심)",
  "points": [
    {{"title": "포인트 제목 (15자 이내)", "body": "본문 (줄바꿈 포함 80자 이내)"}},
    {{"title": "포인트 제목 (15자 이내)", "body": "본문 (줄바꿈 포함 80자 이내)"}},
    {{"title": "포인트 제목 (15자 이내)", "body": "본문 (줄바꿈 포함 80자 이내)"}}
  ],
  "closing": "마무리 문장 (30자 이내, 생각하게 만드는 문장)",
  "caption": "인스타 본문 (150자 이내, 핵심 요약)",
  "hashtags": ["증여", "상속", "법인절세", "절세", "자산설계", "사업주", "자산가"]
}}"""

    for attempt in range(3):
        try:
            resp = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            m = re.search(r'\{[\s\S]*\}', resp.text.strip())
            if m:
                return json.loads(m.group())
        except Exception as e:
            print(f'생성 오류 (시도 {attempt+1}/3): {e}')
            time.sleep(3)
    return None


def post_carousel(image_urls, caption):
    # 1. 각 이미지 컨테이너 생성
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

    # 2. 캐러셀 컨테이너 생성
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

    # 3. 발행
    r = requests.post(f'{BASE_IG}/{IG_USER_ID}/media_publish',
                      params={'creation_id': carousel_id,
                              'access_token': TOKEN}, timeout=30)
    if not r.ok:
        print(f'발행 실패: {r.text}')
        return None
    return r.json()['id']


def main():
    print('쓰레드 상위 포스트 조회 중...')
    best = get_top_post()
    if not best:
        print('발행할 포스트 없음 (최근 7일 내 새 포스트 없거나 이미 인스타 발행됨)')
        return

    print(f'선택: {best.get("selected_title", "")} (조회 {best.get("views", 0):,})')

    post_text = get_post_text(best['post_id'])
    if not post_text:
        print('포스트 본문 조회 실패')
        return
    print(f'본문 {len(post_text)}자 조회 완료')

    print('Gemini 카드 데이터 생성 중...')
    card_data = generate_card_data(post_text)
    if not card_data:
        print('카드 데이터 생성 실패')
        return
    print(f'  훅: {card_data["hook_big"]}')

    print('카드 이미지 생성 중...')
    tmp_dir = tempfile.mkdtemp()
    try:
        paths = generate_card_set(card_data, output_dir=tmp_dir)
        print(f'  {len(paths)}장 생성 완료')

        print('imgbb 업로드 중...')
        image_urls = []
        for i, path in enumerate(paths):
            url = upload_to_imgbb(path)
            image_urls.append(url)
            print(f'  카드 {i+1}/{len(paths)} 업로드 완료')
            time.sleep(1)

        hashtags = ' '.join(f'#{t.lstrip("#").strip()}' for t in card_data.get('hashtags', []))
        caption = f'{card_data["caption"]}\n\n{hashtags}'

        print('인스타그램 캐러셀 발행 중...')
        ig_post_id = post_carousel(image_urls, caption)

        if ig_post_id:
            print(f'발행 완료! Instagram Post ID: {ig_post_id}')
            ig_log = load_ig_log()
            ig_log.append({
                'ig_post_id': ig_post_id,
                'threads_post_id': best['post_id'],
                'selected_title': best.get('selected_title', ''),
                'date': datetime.now(KST).strftime('%Y-%m-%d %H:%M'),
                'views_at_selection': best.get('views', 0),
            })
            save_ig_log(ig_log)
        else:
            print('발행 실패')
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == '__main__':
    main()
