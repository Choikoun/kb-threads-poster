#!/usr/bin/env python3
"""
뉴스 자동 포스터 (카테고리별 하루 3회)
- 오전 9시: 법인·사업주
- 오후 12시: 경제·시장
- 오후 6시: 보험·노후·상속
"""
import os, sys, json, time, base64, re, random
from datetime import datetime, timezone, timedelta
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

KST = timezone(timedelta(hours=9))
CONTENT_LOG_FILE = 'content_log.json'

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
                     '시행령', '개정', '세법', '법안', '대법원', '공정위', '판결', '표결'],
        'angle': '법인 운영, 절세, 지분 설계, 사업주 세금 관점. 사업주·법인 대표가 "나 해당되는 거 아냐?" 느끼게.',
        'format_variants': ['반전형', '사례형', '담백형'],
        'hashtags': '#법인 #절세'
    },
    'economy': {
        'name': '경제·시장',
        'feeds': [
            'https://www.yna.co.kr/rss/economy.xml',         # 연합뉴스 경제
            'https://www.mk.co.kr/rss/50200011/',            # 매일경제 증권
            'https://www.newsis.com/RSS/economy.xml',        # 뉴시스 경제
        ],
        'keywords': [],  # 필터 없음 - 경제 전반
        'angle': '경제·시장 이슈가 개인 자산과 투자에 미치는 영향 관점. 독자가 "내 돈에 영향 있겠다" 느끼게.',
        'format_variants': ['반전형', '사례형', '담백형'],
        'hashtags': '#주식 #경제'
    },
    'insurance': {
        'name': '보험·노후·상속',
        'feeds': [
            'https://www.mk.co.kr/rss/30000001/',            # 매일경제 경제
            'https://www.yna.co.kr/rss/economy.xml',         # 연합뉴스 경제
            'https://biz.chosun.com/arc/outboundfeeds/rss/?outputType=xml',  # 조선비즈
        ],
        'keywords': ['보험', '연금', '상속', '증여', '노후', '은퇴', '연금저축', 'IRP', '변액', '종신',
                     '시행령', '개정', '고시', '대법원', '금감원', '판결', '약관',
                     '의사', '개원', '원장', '페이닥터', '종합소득세', '고소득'],
        'angle': '보험, 연금, 상속·증여, 노후 준비 관점. 특히 의사·고소득 전문직이 "나 종합과세 더 내고 있는 거 아냐?" 느끼게.',
        'context': '고소득 전문직(의사 등)은 금융소득이 종합소득에 합산돼 최고세율 적용받기 쉬움. 비과세로 펀드를 운용하면서 자유롭게 입출금·펀드변경(수수료 없이)할 수 있는 구조면 이 종합과세 자체가 빠짐. 관련 뉴스일 때만 이 구조를 상품명 언급 없이 자연스럽게 녹여라.',
        'format_variants': ['반전형', '사례형'],
        'hashtags': '#연금 #상속'
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
                     '발표', '시행', '규제', '완화', '강화', '세율', '공제', '한도',
                     '대법원', '헌재', '표결', '판결', '공정위',
                     '지원금', '환급', '보조금', '감면', '바우처'],
        'angle': '정부 정책·시행령·세법 개정이 사업주·자산가·일반인 지갑에 미치는 영향 관점. "이거 나한테 해당되는 거 아냐?" 느끼게.',
        'format_branch': '''선택한 뉴스가 지원금·환급금·보조금·감면 등 "독자가 직접 신청해서 받을 수 있는 혜택" 안내라면, 반전형 대신 안내형으로 작성:
- 1줄: 제도/혜택 한 줄 소개 ("OOO이 이렇게 바뀌었어" 식)
↵빈줄
- 조건을 목록으로 (대상, 소득기준 등)
↵빈줄
- 금액·기간 등 핵심 숫자
↵빈줄
- 신청 방법 (어디서, 어떻게)
↵빈줄
- "모르면 그냥 손해야. 주변에 해당되는 분 있으면 알려줘." 류 공유 유도 마무리
[포인트 공식]·[메인 포스트 구조]는 이 경우 생략. 댓글 구조는 동일하게 유지.''',
        'hashtags': '#세금 #정책'
    },
    'government': {
        'name': '국무회의·현안',
        'feeds': [
            'https://www.yna.co.kr/rss/politics.xml',        # 연합뉴스 정치
            'https://www.newsis.com/RSS/politics.xml',        # 뉴시스 정치
            'https://www.yna.co.kr/rss/economy.xml',         # 연합뉴스 경제
        ],
        'keywords': ['국무회의', '대통령', '국무총리', '현안', '정책토론', '장관', '내각', '용산',
                     '국정', '청와대', '관계부처', '당정', '대법원', '헌재', '공정위'],
        'angle': '국무회의·대통령 현안·정부 정책토론이 사업주·자산가·서민 경제에 미치는 영향 관점. 정치 얘기 아님. 내 돈과 사업에 어떤 영향인지로만 풀어내기.',
        'format_branch': '''선택한 뉴스가 그날 가장 화제인 정치 발언·논란(대통령/여야 발언, 헌법기관 충돌 등)이고 그 자체로 임팩트가 크면, 초단문 인용형으로 작성:
- 1~2줄: 발언/사실을 그대로 인용하거나 요약
↵빈줄
- 1줄: "대부분은 ~로 보지만, 진짜는 ~다" 식 재해석 한 줄
[포인트 공식]·[메인 포스트 구조]의 3단 전개는 이 경우 생략. 댓글 구조는 동일하게 유지.''',
        'youtube_hint': '국무회의 대통령',  # YouTube 검색 힌트 (회의 현장 사진)
        'hashtags': '#부동산 #정책'
    },
    'trend': {
        'name': '오늘의 트렌드',
        'feeds': [
            'https://www.yna.co.kr/rss/economy.xml',         # 연합뉴스 경제
            'https://www.mk.co.kr/rss/50200011/',            # 매일경제 증권
            'https://www.newsis.com/RSS/economy.xml',        # 뉴시스 경제
        ],
        'keywords': [],  # 필터 없음 - 그날 화제 전반
        'angle': '오늘 가장 화제인 트렌드·이슈를 특정 타겟층에 한정하지 않고, 누구나 공감할 수 있게 가볍게 다루는 관점. 출퇴근길에 스치듯 보고 "어 이거 봤어?" 하게.',
        'format_variants': ['담백형'],
        'hashtags': '#오늘 #이슈'
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

def get_trend_headlines(limit=8):
    """content_trends.md에서 핵심 이슈 헤드라인 일부를 컨텍스트로 가져옴"""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'content_trends.md')
    if not os.path.exists(path):
        return ''
    headlines = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            m = re.match(r'-\s+\*\*\[.+?\]\*\*\s+\[(.+?)\]', line.strip())
            if m:
                headlines.append(m.group(1))
            if len(headlines) >= limit:
                break
    return '\n'.join(f'- {h}' for h in headlines)


FORMAT_STRUCTURES = {
    '반전형': '''1. 숫자/팩트 or 반전 훅 (1~2줄)
↵빈줄
2. "대부분은 모르는" 반전 or 충격 사실 (1~2줄)
↵빈줄
3. 묵직한 마무리 한 줄''',
    '사례형': '''1. 구체적 상황·사례로 시작 (1~2줄). "OO씨", "어떤 사업주", "한 고객" 등 실제 인물처럼 보이는 예시나 흔한 상황 묘사
↵빈줄
2. "대부분은 모르는" 반전 or 충격 사실 (1~2줄)
↵빈줄
3. 묵직한 마무리 한 줄''',
    '담백형': '''1. 오늘 화제인 트렌드·이슈를 자극적 수사나 반전 틀 없이 1~2줄로 그대로 전달
↵빈줄
2. 거기에 짧은 한마디 - 정보 전달이 아니라 가벼운 반응·소감 톤으로 (예: "이거 진짜 체감되네")
↵빈줄
3. 결론이나 교훈으로 정리하지 않고, 여운 남기듯 마무리. "반전" 구조 강요하지 않음''',
}

# 담백형은 ①숫자충격 ②반전 포인트 공식이 안 맞으므로 제외
POINT_FORMULA = '''[포인트 공식 - 반드시 둘 다 섞어]
① 숫자/팩트 충격: 실제 수치, 공식 발표, 통계로 독자 멈추게
② 반전: 대부분이 A라고 알고 있지만 실제는 B

예시 조합:
- "실손 적자 1.8조. / 대부분은 내 보험료가 오르는 이유를 몰라. / 근데 이게 노후 자산을 갉아먹는 구조야."
- "법인 대출 금리가 개인 신용대출보다 2~3배 높아. / 은행이 사장님 모신다고? / 실제론 가장 비싼 고객으로 만드는 거야."
'''


def generate_content(articles, category='economy'):
    client = genai.Client(api_key=GEMINI_KEY)
    cat = CATEGORIES.get(category, CATEGORIES['economy'])
    news_list = '\n'.join([f"{i+1}. {a['title']}" for i, a in enumerate(articles[:20])])
    trend_headlines = get_trend_headlines()
    trend_block = f"\n[오늘의 핵심 이슈 - 후속/연결 가능하면 활용]\n{trend_headlines}\n" if trend_headlines else ''
    context_block = f"\n[참고 - 관련 뉴스일 때만 활용]\n{cat['context']}\n" if cat.get('context') else ''
    format_branch_block = f"\n[형식 분기 - 해당되면 사용]\n{cat['format_branch']}\n" if cat.get('format_branch') else ''

    chosen_variant = random.choice(cat.get('format_variants', ['반전형']))
    structure_block = FORMAT_STRUCTURES.get(chosen_variant, FORMAT_STRUCTURES['반전형'])
    point_formula_block = '' if chosen_variant == '담백형' else POINT_FORMULA

    prompt = f"""너는 한국 Threads에서 팔로워를 끌어모으는 금융 전문가야.
아래 뉴스 중 {cat['name']} 독자에게 가장 임팩트 있는 것 하나 골라서 포스트를 작성해줘.

[오늘 뉴스]
{news_list}
{trend_block}
[뉴스 선택 우선순위]
다음 유형의 뉴스가 있으면 최우선으로 선택해:
- 정부기관(국세청·대법원·헌재·공정위·금융위 등) 공식 발표, 판결, 표결 결과
- 구체적 숫자(금액·비율·표결수)가 포함된 사실
해당하는 뉴스가 없으면 기존 기준대로 가장 임팩트 있는 걸 선택해.

[작성 각도]
{cat['angle']}
{context_block}
[핵심 원칙 - 반드시 지켜]
- 전부 반말
- 상담/DM/점검 유도 절대 금지. 화두만 던지고 끝낸다.
- 한 줄 10~20자. 짧게 끊어지게.
- 아이디어 바뀔 때 빈 줄 삽입 (가독성)
- 숫자·핵심 사실은 단독 줄에 배치
- 모호한 표현 절대 금지: "뭔가 있어", "달라져", "독이다", "조심해", "알아봐야 해" → 구체적으로 써
- 자극적이되 공격적이지 않게. 독자를 비하하거나 몰아붙이는 표현 금지. 기관·구조·현상을 비판하되 독자를 적으로 만들지 않는다.
- ❌ 공격적 (활용형 포함 전부 금지): "바보처럼 당하고 있어", "멍청하게 내고 있지", "털리는 중", "털릴", "털려", "털리고" 등 "털리다" 계열 일체
- ✅ 자극적: "대부분이 이걸 몰라", "이거 해당되는 사람 많을 거야", "은행이 더 벌려는 구조야"

{point_formula_block}
[메인 포스트 구조 - {chosen_variant}]
{structure_block}
{format_branch_block}
[댓글 구조]
- 댓글 수는 1~3개. 내용 흐름에 맞게 자유롭게 결정. 억지로 3개 채우지 않는다.
- 댓글1: 숫자 단독 줄 + 그 의미 (빈줄 포함, 3~4줄)
- 댓글2 (선택): 핵심 반전 포인트 하나 (빈줄 포함, 3~4줄)
- 마지막 댓글: 양자택일형 질문으로 마무리 (예: "당신은 A인가요, B인가요?", "지금 갈아타실 건가요, 버티실 건가요?")
  - 개방형 질문("어떻게 준비하고 계신가요?") 금지. 독자가 댓글 하나로 바로 답할 수 있는 두 가지 선택지를 제시.
  - 2~3줄, 마지막만 존댓말

JSON만 출력:
{{
  "selected_title": "선택한 뉴스 제목",
  "youtube_keyword": "YouTube에서 관련 뉴스 영상 찾을 검색어 (한국어 2~4단어, 뉴스 방송에 나올 법한 키워드)",
  "main": "메인 포스트 텍스트",
  "comments": [
    "댓글1",
    "댓글2",
    "댓글3 (마지막 질문만 존댓말)"
  ],
  "format_variant": "{chosen_variant}"
}}"""

    for attempt in range(3):
        try:
            resp = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            raw = resp.text.strip()
            m = re.search(r'\{[\s\S]*\}', raw)
            if m:
                result = json.loads(m.group())
                hashtags = cat.get('hashtags', '')
                if hashtags and 'main' in result:
                    result['main'] = result['main'].rstrip() + f'\n\n{hashtags}'
                result.setdefault('format_variant', chosen_variant)
                return result
        except Exception as e:
            print(f'Gemini 오류 (시도 {attempt+1}/3): {e}')
            if attempt < 2:
                wait = 20 * (attempt + 1)
                print(f'  {wait}초 후 재시도...')
                time.sleep(wait)
    return None

# ─── 4. Threads 포스팅 ───────────────────────────────────────────

def post_to_threads(main_text, comments, image_url=None):
    me = requests.get('https://graph.threads.net/v1.0/me',
                      params={'fields': 'id', 'access_token': TOKEN}, timeout=30)
    UID = me.json()['id']

    params = {'text': main_text, 'access_token': TOKEN}
    if image_url:
        params['media_type'] = 'IMAGE'
        params['image_url'] = image_url
    else:
        params['media_type'] = 'TEXT'

    r1 = requests.post(f'https://graph.threads.net/v1.0/{UID}/threads', params=params, timeout=30)
    print(f'메인 컨테이너: {r1.json()}')
    time.sleep(4)

    r2 = requests.post(f'https://graph.threads.net/v1.0/{UID}/threads_publish',
                       params={'creation_id': r1.json()['id'], 'access_token': TOKEN}, timeout=30)
    main_id = r2.json()['id']
    print(f'메인 발행: {main_id}')
    time.sleep(3)

    for i, comment in enumerate(comments):
        rc = requests.post(f'https://graph.threads.net/v1.0/{UID}/threads', params={
            'media_type': 'TEXT',
            'text': comment,
            'reply_to_id': main_id,
            'access_token': TOKEN
        }, timeout=30)
        time.sleep(3)
        rp = requests.post(f'https://graph.threads.net/v1.0/{UID}/threads_publish',
                           params={'creation_id': rc.json()['id'], 'access_token': TOKEN}, timeout=30)
        print(f'댓글{i+1} 발행: {rp.json().get("id")}')
        time.sleep(2)

    return main_id

# ─── 콘텐츠 로그 ──────────────────────────────────────────────────

def log_content(post_id, category, format_variant, selected_title):
    log = []
    if os.path.exists(CONTENT_LOG_FILE):
        with open(CONTENT_LOG_FILE, encoding='utf-8') as f:
            log = json.load(f)
    log.append({
        'post_id': post_id,
        'category': category,
        'format_variant': format_variant,
        'date': datetime.now(KST).strftime('%Y-%m-%d'),
        'selected_title': selected_title,
    })
    with open(CONTENT_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

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

    log_content(main_id, category, content.get('format_variant', ''), content['selected_title'])

if __name__ == '__main__':
    main()
