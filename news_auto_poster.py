#!/usr/bin/env python3
"""
뉴스 자동 포스터
- Google News RSS에서 오늘의 핫 뉴스 수집
- Gemini로 바이럴 컨텐츠 생성
- 뉴스 이미지 다운로드 → imgbb 업로드
- Threads 메인 포스트 + 댓글 스레드 자동 포스팅
"""
import os, sys, json, time, base64, re
import requests
import feedparser
from bs4 import BeautifulSoup
from google import genai
from dotenv import load_dotenv

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

TOKEN     = os.getenv('THREADS_ACCESS_TOKEN')
IMGBB_KEY = os.getenv('IMGBB_API_KEY')
GEMINI_KEY= os.getenv('GEMINI_API_KEY')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0'
}

# ─── 1. 뉴스 수집 ────────────────────────────────────────────────

def get_hot_news():
    feeds = [
        'https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko',
        'https://news.google.com/rss/search?q=경제+주식+부동산+세금+법인&hl=ko&gl=KR&ceid=KR:ko',
        'https://news.google.com/rss/search?q=사업+기업+정책+금융&hl=ko&gl=KR&ceid=KR:ko',
    ]
    articles = []
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                title = entry.get('title', '')
                # 구글 뉴스 제목에서 언론사 제거 ( - 조선일보 형식)
                title = re.sub(r'\s*-\s*[^-]+$', '', title).strip()
                articles.append({
                    'title': title,
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', '')[:200],
                })
        except Exception as e:
            print(f'피드 오류: {e}')
    # 중복 제거
    seen = set()
    unique = []
    for a in articles:
        if a['title'] not in seen:
            seen.add(a['title'])
            unique.append(a)
    return unique[:20]

# ─── 2. 기사 이미지 추출 ─────────────────────────────────────────

def get_article_image(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=12, allow_redirects=True)
        actual_url = r.url
        print(f'  기사 URL: {actual_url[:80]}')

        soup = BeautifulSoup(r.content, 'html.parser')

        # og:image 우선
        og = soup.find('meta', property='og:image')
        img_url = og['content'] if og and og.get('content') else None

        # 없으면 twitter:image
        if not img_url:
            tw = soup.find('meta', attrs={'name': 'twitter:image'})
            img_url = tw['content'] if tw and tw.get('content') else None

        # 없으면 첫 번째 큰 img
        if not img_url:
            for img in soup.find_all('img', src=True):
                src = img['src']
                if src.startswith('http') and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    img_url = src
                    break

        if not img_url:
            print('  이미지 URL 없음')
            return None

        # 상대경로 처리
        if img_url.startswith('//'):
            img_url = 'https:' + img_url

        ir = requests.get(img_url, headers=HEADERS, timeout=12)
        if ir.status_code == 200 and len(ir.content) > 8000:
            print(f'  이미지 다운로드: {len(ir.content)//1024}KB')
            return ir.content
    except Exception as e:
        print(f'  이미지 오류: {e}')
    return None

def upload_to_imgbb(img_bytes):
    img_b64 = base64.b64encode(img_bytes).decode()
    r = requests.post('https://api.imgbb.com/1/upload', data={
        'key': IMGBB_KEY,
        'image': img_b64,
    }, timeout=30)
    d = r.json()
    if d.get('success'):
        url = d['data']['url']
        print(f'  imgbb 업로드 완료: {url}')
        return url
    print(f'  imgbb 실패: {d}')
    return None

# ─── 3. Gemini 컨텐츠 생성 ───────────────────────────────────────

def generate_content(articles):
    client = genai.Client(api_key=GEMINI_KEY)

    news_list = '\n'.join([f"{i+1}. {a['title']}" for i, a in enumerate(articles[:18])])

    prompt = f"""너는 한국 Threads에서 바이럴 컨텐츠를 만드는 금융 크리에이터야.
아래 오늘의 뉴스 중 가장 바이럴 가능성 높은 것 하나 골라서 포스트를 작성해줘.

타겟 독자: 사업주, 자산가, 의사, 개인 투자자

오늘의 뉴스:
{news_list}

[작성 규칙]
- 반말 사용
- 메인 훅: "진짜 이유 N가지" 또는 반전 각도, 호기심 자극
- 각 댓글: 구체적 수치/사실 포함, 5~8줄
- 억지로 보험/상담 연결 금지
- 마지막 댓글에 독자가 생각해볼 포인트로 마무리

JSON만 출력:
{{
  "selected_title": "선택한 뉴스 제목",
  "main": "메인 포스트 텍스트",
  "comments": [
    "댓글1",
    "댓글2",
    "댓글3"
  ]
}}"""

    try:
        resp = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        raw = resp.text.strip()
        m = re.search(r'\{[\s\S]*\}', raw)
        if m:
            return json.loads(m.group())
    except Exception as e:
        print(f'Gemini 오류: {e}')
    return None

# ─── 4. Threads 포스팅 ───────────────────────────────────────────

def post_to_threads(main_text, comments, image_url=None):
    me = requests.get('https://graph.threads.net/v1.0/me',
                      params={'fields': 'id', 'access_token': TOKEN})
    UID = me.json()['id']

    # 메인 포스트
    params = {'text': main_text, 'access_token': TOKEN}
    if image_url:
        params['media_type'] = 'IMAGE'
        params['image_url'] = image_url
    else:
        params['media_type'] = 'TEXT'

    r1 = requests.post(f'https://graph.threads.net/v1.0/{UID}/threads', params=params)
    print(f'메인 컨테이너: {r1.json()}')
    time.sleep(4)

    r2 = requests.post(f'https://graph.threads.net/v1.0/{UID}/threads_publish',
                       params={'creation_id': r1.json()['id'], 'access_token': TOKEN})
    main_id = r2.json()['id']
    print(f'메인 발행: {main_id}')
    time.sleep(3)

    # 댓글 스레드
    for i, comment in enumerate(comments):
        rc = requests.post(f'https://graph.threads.net/v1.0/{UID}/threads', params={
            'media_type': 'TEXT',
            'text': comment,
            'reply_to_id': main_id,
            'access_token': TOKEN
        })
        time.sleep(3)
        rp = requests.post(f'https://graph.threads.net/v1.0/{UID}/threads_publish',
                           params={'creation_id': rc.json()['id'], 'access_token': TOKEN})
        print(f'댓글{i+1} 발행: {rp.json().get("id")}')
        time.sleep(2)

    return main_id

# ─── 메인 ────────────────────────────────────────────────────────

def main():
    print('=== 뉴스 자동 포스터 시작 ===')

    # 1. 뉴스 수집
    articles = get_hot_news()
    print(f'뉴스 {len(articles)}개 수집')
    for a in articles[:5]:
        print(f'  - {a["title"]}')

    # 2. Gemini 컨텐츠 생성
    print('\nGemini 컨텐츠 생성 중...')
    content = generate_content(articles)
    if not content:
        print('컨텐츠 생성 실패 - 종료')
        sys.exit(1)

    print(f'\n선택된 뉴스: {content["selected_title"]}')
    print(f'메인:\n{content["main"]}\n')
    for i, c in enumerate(content['comments']):
        print(f'댓글{i+1}:\n{c}\n')

    # 3. 이미지 찾기
    image_url = None
    print('이미지 탐색 중...')
    for article in articles:
        # 선택된 뉴스와 제목 매칭
        sel = content['selected_title'][:15]
        if sel in article['title'] or article['title'][:15] in sel:
            print(f'  매칭 기사: {article["title"]}')
            img_bytes = get_article_image(article['link'])
            if img_bytes:
                image_url = upload_to_imgbb(img_bytes)
            break

    if not image_url:
        print('이미지 없이 진행')

    # 4. Threads 포스팅
    print('\nThreads 포스팅 중...')
    main_id = post_to_threads(content['main'], content['comments'], image_url)
    print(f'\n완료! 메인 포스트 ID: {main_id}')

if __name__ == '__main__':
    main()
