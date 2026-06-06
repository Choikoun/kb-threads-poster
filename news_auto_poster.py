#!/usr/bin/env python3
"""
뉴스 자동 포스터 (카테고리별 하루 3회)
- 오전 9시: 법인·사업주
- 오후 12시: 경제·시장
- 오후 6시: 보험·노후·상속
"""
import os, sys, json, time, base64, re, random
import requests
import feedparser
from bs4 import BeautifulSoup
from google import genai
from dotenv import load_dotenv

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

TOKEN       = os.getenv('THREADS_ACCESS_TOKEN')
IMGBB_KEY   = os.getenv('IMGBB_API_KEY')
GEMINI_KEY  = os.getenv('GEMINI_API_KEY')
YOUTUBE_KEY = os.getenv('YOUTUBE_API_KEY')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0'
}

# ─── 카테고리 설정 ────────────────────────────────────────────────

CATEGORIES = {
    'business': {
        'name': '법인·사업주',
        'feeds': [
            'https://www.mk.co.kr/rss/30000001/',           # 매일경제 경제
            'https://www.newsis.com/RSS/economy.xml',        # 뉴시스 경제
            'https://biz.chosun.com/arc/outboundfeeds/rss/?outputType=xml',  # 조선비즈
        ],
        'keywords': ['법인', '사업주', '대표이사', '세금', '절세', '기업', '창업', '사업자', '세무', '지분',
                     '시행령', '개정', '세법', '법안'],
        'angle': '법인 운영, 절세, 지분 설계, 사업주 세금 관점. 사업주·법인 대표가 "나 해당되는 거 아냐?" 느끼게.'
    },
    'economy': {
        'name': '경제·시장',
        'feeds': [
            'https://www.yna.co.kr/rss/economy.xml',         # 연합뉴스 경제
            'https://www.mk.co.kr/rss/50200011/',            # 매일경제 증권
            'https://www.newsis.com/RSS/economy.xml',        # 뉴시스 경제
        ],
        'keywords': [],  # 필터 없음 - 경제 전반
        'angle': '경제·시장 이슈가 개인 자산과 투자에 미치는 영향 관점. 독자가 "내 돈에 영향 있겠다" 느끼게.'
    },
    'insurance': {
        'name': '보험·노후·상속',
        'feeds': [
            'https://www.mk.co.kr/rss/30000001/',            # 매일경제 경제
            'https://www.yna.co.kr/rss/economy.xml',         # 연합뉴스 경제
            'https://biz.chosun.com/arc/outboundfeeds/rss/?outputType=xml',  # 조선비즈
        ],
        'keywords': ['보험', '연금', '상속', '증여', '노후', '은퇴', '연금저축', 'IRP', '변액', '종신',
                     '시행령', '개정', '고시'],
        'angle': '보험, 연금, 상속·증여, 노후 준비 관점. 독자가 "내 노후·상속 괜찮나?" 느끼게.'
    },
    'policy': {
        'name': '정책·시행령',
        'feeds': [
            'https://www.yna.co.kr/rss/politics.xml',        # 연합뉴스 정치
            'https://www.yna.co.kr/rss/economy.xml',         # 연합뉴스 경제
            'https://www.mk.co.kr/rss/30000023/',            # 매일경제 정책
            'https://biz.chosun.com/arc/outboundfeeds/rss/?outputType=xml',  # 조선비즈
        ],
        'keywords': ['시행령', '개정', '정책', '법안', '국세청', '금융위', '기재부', '세법', '고시',
                     '발표', '시행', '규제', '완화', '강화', '세율', '공제', '한도'],
        'angle': '정부 정책·시행령·세법 개정이 사업주·자산가·일반인 지갑에 미치는 영향 관점. "이거 나한테 해당되는 거 아냐?" 느끼게.'
    },
    'government': {
        'name': '국무회의·현안',
        'feeds': [
            'https://www.yna.co.kr/rss/politics.xml',        # 연합뉴스 정치
            'https://www.newsis.com/RSS/politics.xml',        # 뉴시스 정치
            'https://www.yna.co.kr/rss/economy.xml',         # 연합뉴스 경제
        ],
        'keywords': ['국무회의', '대통령', '국무총리', '현안', '정책토론', '장관', '내각', '용산',
                     '국정', '청와대', '관계부처', '당정'],
        'angle': '국무회의·대통령 현안·정부 정책토론이 사업주·자산가·서민 경제에 미치는 영향 관점. 정치 얘기 아님. 내 돈과 사업에 어떤 영향인지로만 풀어내기.',
        'youtube_hint': '국무회의 대통령'  # YouTube 검색 힌트 (회의 현장 사진)
    }
}

# ─── 1. 뉴스 수집 ────────────────────────────────────────────────

def get_hot_news(category='economy'):
    cat = CATEGORIES.get(category, CATEGORIES['economy'])
    print(f'카테고리: {cat["name"]}')
    keywords = cat.get('keywords', [])

    articles = []
    for url in cat['feeds']:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]:
                title = entry.get('title', '')
                title = re.sub(r'\s*-\s*[^-]+$', '', title).strip()
                link = entry.get('link', '')

                # 키워드 필터 (카테고리에 키워드가 있으면 해당 키워드 포함 기사만)
                if keywords and not any(kw in title for kw in keywords):
                    continue

                articles.append({
                    'title': title,
                    'link': link,
                    'summary': entry.get('summary', '')[:200],
                })
        except Exception as e:
            print(f'피드 오류: {e}')

    # 키워드 필터 후 기사 부족하면 전체에서 추가
    if len(articles) < 10 and keywords:
        for url in cat['feeds']:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:10]:
                    title = re.sub(r'\s*-\s*[^-]+$', '', entry.get('title', '')).strip()
                    link = entry.get('link', '')
                    if not any(a['title'] == title for a in articles):
                        articles.append({'title': title, 'link': link, 'summary': ''})
            except:
                pass

    # 중복 제거
    seen = set()
    unique = []
    for a in articles:
        if a['title'] not in seen:
            seen.add(a['title'])
            unique.append(a)
    print(f'뉴스 {len(unique)}개 수집 (키워드 필터: {keywords if keywords else "없음"})')
    return unique[:25]

# ─── 2. YouTube 썸네일 ───────────────────────────────────────────

def get_youtube_thumbnail(query):
    """뉴스 키워드로 YouTube 영상 검색 → 고화질 썸네일 다운로드"""
    if not YOUTUBE_KEY:
        return None
    try:
        channel = random.choice(['KBS 뉴스', 'SBS 뉴스', 'MBC 뉴스', 'YTN'])
        search_q = f'{channel} {query}'
        r = requests.get('https://www.googleapis.com/youtube/v3/search', params={
            'key': YOUTUBE_KEY,
            'q': search_q,
            'part': 'snippet',
            'type': 'video',
            'order': 'relevance',
            'maxResults': 5,
            'relevanceLanguage': 'ko',
            'regionCode': 'KR',
        }, timeout=10)
        data = r.json()
        items = data.get('items', [])
        if not items:
            print(f'  YouTube 검색 결과 없음')
            return None

        # 중복 방지: 결과 셔플 후 순서대로 시도
        random.shuffle(items)
        for item in items:
            video_id = item['id']['videoId']
            for quality in ['maxresdefault', 'hqdefault', 'mqdefault']:
                thumb_url = f'https://i.ytimg.com/vi/{video_id}/{quality}.jpg'
                ir = requests.get(thumb_url, headers=HEADERS, timeout=10)
                if ir.status_code == 200 and len(ir.content) > 5000:
                    print(f'  YouTube 썸네일 ({quality}): {len(ir.content)//1024}KB')
                    return ir.content
    except Exception as e:
        print(f'  YouTube 오류: {e}')
    return None

# ─── 3. 기사 이미지 추출 (YouTube 실패 시 폴백) ──────────────────

def get_article_image(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=12, allow_redirects=True)
        soup = BeautifulSoup(r.content, 'html.parser')

        og = soup.find('meta', property='og:image')
        img_url = og['content'] if og and og.get('content') else None

        if not img_url:
            tw = soup.find('meta', attrs={'name': 'twitter:image'})
            img_url = tw['content'] if tw and tw.get('content') else None

        if not img_url:
            for img in soup.find_all('img', src=True):
                src = img['src']
                if src.startswith('http') and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    img_url = src
                    break

        if not img_url:
            return None

        if img_url.startswith('//'):
            img_url = 'https:' + img_url

        ir = requests.get(img_url, headers=HEADERS, timeout=12)
        if ir.status_code == 200 and len(ir.content) > 50000:  # 50KB 이상만
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

def generate_content(articles, category='economy'):
    client = genai.Client(api_key=GEMINI_KEY)
    cat = CATEGORIES.get(category, CATEGORIES['economy'])
    news_list = '\n'.join([f"{i+1}. {a['title']}" for i, a in enumerate(articles[:20])])

    prompt = f"""너는 한국 Threads에서 팔로워를 끌어모으는 금융 전문가야.
아래 뉴스 중 {cat['name']} 독자에게 가장 임팩트 있는 것 하나 골라서 포스트를 작성해줘.

[오늘 뉴스]
{news_list}

[작성 각도]
{cat['angle']}

[핵심 원칙 - 반드시 지켜]
- 전부 반말
- 상담/DM/점검 유도 절대 금지. 화두만 던지고 끝낸다.
- 한 줄 10~20자. 짧게 끊어지게.
- 아이디어 바뀔 때 빈 줄 삽입 (가독성)
- 숫자·핵심 사실은 단독 줄에 배치
- 모호한 표현 절대 금지: "뭔가 있어", "달라져", "독이다", "조심해", "알아봐야 해" → 구체적으로 써
- 자극적이되 공격적이지 않게. 독자를 비하하거나 몰아붙이는 표현 금지. 기관·구조·현상을 비판하되 독자를 적으로 만들지 않는다.
- ❌ 공격적: "바보처럼 당하고 있어", "멍청하게 내고 있지", "털리는 중"
- ✅ 자극적: "대부분이 이걸 몰라", "이거 해당되는 사람 많을 거야", "은행이 더 벌려는 구조야"

[포인트 공식 - 반드시 둘 다 섞어]
① 숫자/팩트 충격: 실제 수치, 공식 발표, 통계로 독자 멈추게
② 반전: 대부분이 A라고 알고 있지만 실제는 B

예시 조합:
- "실손 적자 1.8조. / 대부분은 내 보험료가 오르는 이유를 몰라. / 근데 이게 노후 자산을 갉아먹는 구조야."
- "법인 대출 금리가 개인 신용대출보다 2~3배 높아. / 은행이 사장님 모신다고? / 실제론 가장 비싼 고객으로 만드는 거야."

[메인 포스트 구조]
1. 숫자/팩트 or 반전 훅 (1~2줄)
↵빈줄
2. "대부분은 모르는" 반전 or 충격 사실 (1~2줄)
↵빈줄
3. 묵직한 마무리 한 줄

[댓글 구조]
- 댓글 수는 1~3개. 내용 흐름에 맞게 자유롭게 결정. 억지로 3개 채우지 않는다.
- 댓글1: 숫자 단독 줄 + 그 의미 (빈줄 포함, 3~4줄)
- 댓글2 (선택): 핵심 반전 포인트 하나 (빈줄 포함, 3~4줄)
- 마지막 댓글: 독자 당사자화 질문으로 마무리 (2~3줄, 마지막만 존댓말)

JSON만 출력:
{{
  "selected_title": "선택한 뉴스 제목",
  "youtube_keyword": "YouTube에서 관련 뉴스 영상 찾을 검색어 (한국어 2~4단어, 뉴스 방송에 나올 법한 키워드)",
  "main": "메인 포스트 텍스트",
  "comments": [
    "댓글1",
    "댓글2",
    "댓글3 (마지막 질문만 존댓말)"
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
    category = sys.argv[1] if len(sys.argv) > 1 else 'economy'
    print(f'=== 뉴스 자동 포스터 시작 [{category}] ===')

    articles = get_hot_news(category)
    print(f'뉴스 {len(articles)}개 수집')
    for a in articles[:5]:
        print(f'  - {a["title"]}')

    print('\nGemini 컨텐츠 생성 중...')
    content = generate_content(articles, category)
    if not content:
        print('컨텐츠 생성 실패 - 종료')
        sys.exit(1)

    print(f'\n선택된 뉴스: {content["selected_title"]}')
    print(f'메인:\n{content["main"]}\n')
    for i, c in enumerate(content['comments']):
        print(f'댓글{i+1}:\n{c}\n')

    image_url = None
    print('이미지 탐색 중...')

    # 1순위: YouTube 썸네일 (뉴스 방송 화면)
    cat_info = CATEGORIES.get(category, {})
    youtube_hint = cat_info.get('youtube_hint', '')  # 카테고리 고정 힌트 (government 등)

    if youtube_hint:
        # government처럼 회의 현장 사진이 필요한 카테고리는 hint 우선
        search_query = youtube_hint
    else:
        search_query = content.get('youtube_keyword', '')
        if not search_query:
            raw_title = content['selected_title']
            search_query = re.sub(r'[^\w\s]', ' ', raw_title).strip()[:25]
    print(f'  YouTube 검색: {search_query}')
    img_bytes = get_youtube_thumbnail(search_query)
    if img_bytes:
        image_url = upload_to_imgbb(img_bytes)

    # 2순위: 기사 og:image (YouTube 실패 시 폴백)
    if not image_url:
        print('  YouTube 실패 → 기사 이미지 시도')
        sel = content['selected_title'][:20]
        for article in articles:
            if sel in article['title'] or article['title'][:20] in sel:
                print(f'  매칭 기사: {article["title"]}')
                img_bytes = get_article_image(article['link'])
                if img_bytes:
                    image_url = upload_to_imgbb(img_bytes)
                break

    if not image_url:
        for article in articles[:5]:
            img_bytes = get_article_image(article['link'])
            if img_bytes:
                image_url = upload_to_imgbb(img_bytes)
                if image_url:
                    break

    if not image_url:
        print('이미지 없이 진행')

    print('\nThreads 포스팅 중...')
    main_id = post_to_threads(content['main'], content['comments'], image_url)
    print(f'\n완료! 메인 포스트 ID: {main_id}')

if __name__ == '__main__':
    main()
