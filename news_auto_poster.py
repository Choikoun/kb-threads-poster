#!/usr/bin/env python3
"""
뉴스 자동 포스터 (카테고리별 하루 3회)
- 오전 9시: 법인·사업주
- 오후 12시: 경제·시장
- 오후 6시: 보험·노후·상속
"""
import os, sys, json, time, re, random
from datetime import datetime, timezone, timedelta
import requests
import feedparser
from bs4 import BeautifulSoup
from google import genai
from dotenv import load_dotenv

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

TOKEN       = os.getenv('THREADS_ACCESS_TOKEN')
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
            'https://rss.donga.com/national.xml',            # 동아일보 사회
            'https://www.khan.co.kr/rss/rssdata/society_news.xml',  # 경향신문 사회
        ],
        'keywords': ['법인', '사업주', '대표이사', '세금', '절세', '기업', '창업', '사업자', '세무', '지분',
                     '시행령', '개정', '세법', '법안', '대법원', '공정위', '판결', '표결',
                     '퇴직금', '퇴직급여', '인건비', '근로자', '4대보험', '최저임금', '해고', '연차', '채용', '노무',
                     'MSO', '경영지원회사', '동업', '횡령', '배임', '배신'],
        'angle': '법인 운영, 절세, 지분 설계, 사업주 세금, 직원·인건비 관리 관점. 사업주·법인 대표가 "나 해당되는 거 아냐?" 느끼게. 동업자 간 신의성실 의무 위반(회사 기회 개인적 이용, 횡령·배임)처럼 "친구·동업자라서 더 못 끝내는 딜레마"도 적극적으로 다뤄라.',
        'format_variants': ['반전형', '사례형', '담백형', '번호형'],
        'hashtags': '#법인 #증여',
        'topic_tag': '법인'
    },
    'economy': {
        'name': '경제·시장',
        'feeds': [
            'https://www.yna.co.kr/rss/economy.xml',         # 연합뉴스 경제
            'https://www.mk.co.kr/rss/50200011/',            # 매일경제 증권
            'https://www.newsis.com/RSS/economy.xml',        # 뉴시스 경제
        ],
        'keywords': [],  # 필터 없음 - 경제 전반
        'angle': '경제·시장 이슈가 사업주·법인 대표·자산가의 사업 자금과 자산 운용에 미치는 영향 관점. 독자가 "내 사업/자산에 영향 있겠다" 느끼게.',
        'format_variants': ['반전형', '사례형', '담백형'],
        'hashtags': '#주식 #경제',
        'topic_tag': '경제'
    },
    'insurance': {
        'name': '보험·노후·상속',
        'feeds': [
            'https://www.mk.co.kr/rss/30000001/',            # 매일경제 경제
            'https://www.mk.co.kr/rss/50200030/',            # 매일경제 부동산
            'https://www.yna.co.kr/rss/economy.xml',         # 연합뉴스 경제
            'https://biz.chosun.com/arc/outboundfeeds/rss/?outputType=xml',  # 조선비즈
            'https://rss.donga.com/national.xml',            # 동아일보 사회
            'https://www.khan.co.kr/rss/rssdata/society_news.xml',  # 경향신문 사회
            'https://www.chosun.com/arc/outboundfeeds/rss/category/national/?outputType=xml',  # 조선일보 사회
        ],
        'keywords': ['보험', '연금', '상속', '증여', '노후', '은퇴', '연금저축', 'IRP', '변액', '종신',
                     '시행령', '개정', '고시', '대법원', '금감원', '판결', '약관',
                     '의사', '개원', '원장', '페이닥터', '종합소득세', '고소득',
                     '부동산 증여', '상속세', '증여세', '가업승계', '재산분할', '유언',
                     'MSO', '가족법인', '경영지원회사',
                     '이혼', '효도', '부양', '실버타운', '요양원', '간병', '독거'],
        'angle': '보험, 연금, 상속·증여, 노후 준비, MSO·가족법인 구조 관점. 특히 의사·고소득 전문직이 "나 종합과세 더 내고 있는 거 아냐?" 느끼게. 또한 이혼 시 재산분할, 자식에게 부양받기 싫은 노후 독립성, 가족 간 재산 분쟁처럼 누구나 겪는 감정적 가족관계 불안도 적극적으로 다뤄라 — 역대 최고 성과(34,254·30,734 조회)가 바로 이 앵글(이혼·요양원)에서 나왔다(2026-06-21 확인). 행정 안내·좁은 틈새 단신보다 이런 가족관계 불안 앵글을 우선시할 것.',
        'context': '고소득 전문직(의사 등)은 금융소득이 종합소득에 합산돼 최고세율 적용받기 쉬움. 비과세로 펀드를 운용하면서 자유롭게 입출금·펀드변경(수수료 없이)할 수 있는 구조면 이 종합과세 자체가 빠짐. 관련 뉴스일 때만 이 구조를 상품명 언급 없이 자연스럽게 녹여라.',
        'format_variants': ['반전형', '사례형', '감정인용형', '번호형'],
        'hashtags': '#증여 #상속',
        'topic_tag': '보험'
    },
    'policy': {
        'name': '정책·시행령',
        'feeds': [
            'https://www.yna.co.kr/rss/politics.xml',        # 연합뉴스 정치
            'https://www.yna.co.kr/rss/economy.xml',         # 연합뉴스 경제
            'https://www.mk.co.kr/rss/30000023/',            # 매일경제 정책
            'https://biz.chosun.com/arc/outboundfeeds/rss/?outputType=xml',  # 조선비즈
            'https://rss.donga.com/national.xml',            # 동아일보 사회
            'https://www.khan.co.kr/rss/rssdata/society_news.xml',  # 경향신문 사회
        ],
        'keywords': ['시행령', '개정', '정책', '법안', '국세청', '금융위', '기재부', '세법', '고시',
                     '발표', '시행', '규제', '완화', '강화', '세율', '공제', '한도',
                     '대법원', '헌재', '표결', '판결', '공정위',
                     '지원금', '환급', '보조금', '감면', '바우처'],
        'angle': '정부 정책·시행령·세법 개정이 사업주·법인 대표·자산가 지갑에 미치는 영향 관점. "이거 내 사업/자산에 해당되는 거 아냐?" 느끼게.',
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
        'hashtags': '#세금 #정책',
        'topic_tag': '세금'
    },
    'government': {
        'name': '국무회의·현안',
        'feeds': [
            'https://www.yna.co.kr/rss/politics.xml',        # 연합뉴스 정치
            'https://www.newsis.com/RSS/politics.xml',        # 뉴시스 정치
            'https://www.yna.co.kr/rss/economy.xml',         # 연합뉴스 경제
            'https://www.chosun.com/arc/outboundfeeds/rss/category/national/?outputType=xml',  # 조선일보 사회
        ],
        'keywords': ['국무회의', '대통령', '국무총리', '현안', '정책토론', '장관', '내각', '용산',
                     '국정', '청와대', '관계부처', '당정', '대법원', '헌재', '공정위'],
        'angle': '국무회의·대통령 현안·정부 정책토론이 사업주·법인 대표·자산가의 사업과 자산에 미치는 영향 관점. 정치 얘기 아님. 내 사업과 자산에 어떤 영향인지로만 풀어내기.',
        'format_branch': '''선택한 뉴스가 그날 가장 화제인 정치 발언·논란(대통령/여야 발언, 헌법기관 충돌 등)이고 그 자체로 임팩트가 크면, 초단문 인용형으로 작성:
- 1~2줄: 발언/사실을 그대로 인용하거나 요약
↵빈줄
- 1줄: "대부분은 ~로 보지만, 진짜는 ~다" 식 재해석 한 줄 — 반드시 사업·자산에 미치는 영향으로 연결할 것. 사업·자산과 연결할 수 없는 순수 정치 발언이면 이 뉴스를 선택하지 말고 다른 후보를 골라.
[포인트 공식]·[메인 포스트 구조]의 3단 전개는 이 경우 생략. 댓글 구조는 동일하게 유지.''',
        'youtube_hint': '국무회의 대통령',  # YouTube 검색 힌트 (회의 현장 사진)
        'hashtags': '#부동산 #정책',
        'topic_tag': '시사'
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
        'hashtags': '#오늘 #이슈',
        'topic_tag': '이슈'
    }
}

# ─── 1. 뉴스 수집 ────────────────────────────────────────────────

def _kw_overlap(t1, t2):
    """두 제목의 한국어 단어 중복 수"""
    w1 = set(re.findall(r'[가-힣]{2,}', t1))
    w2 = set(re.findall(r'[가-힣]{2,}', t2))
    return len(w1 & w2)


SOURCE_MAP = {
    'mk.co.kr': '매일경제', 'yna.co.kr': '연합뉴스',
    'biz.chosun.com': '조선비즈', 'newsis.com': '뉴시스',
    'etnews.com': '전자신문', 'hankyung.com': '한국경제',
    'sbs.co.kr': 'SBS', 'kbs.co.kr': 'KBS',
    'donga.com': '동아일보', 'khan.co.kr': '경향신문', 'chosun.com': '조선일보',
}

def get_source_name(feed_url):
    for key, name in SOURCE_MAP.items():
        if key in feed_url:
            return name
    m = re.search(r'https?://(?:www\.)?([^/]+)', feed_url)
    return m.group(1) if m else '기타'


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
                    'source': get_source_name(url),
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
                        articles.append({'title': title, 'link': link, 'summary': '', 'source': get_source_name(url)})
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

def get_youtube_thumbnail_url(query):
    """YouTube 영상 검색 → hqdefault 썸네일 URL 반환 (imgbb 업로드 없이 직접 사용)"""
    if not YOUTUBE_KEY:
        return None
    try:
        channel = random.choice(['KBS 뉴스', 'SBS 뉴스', 'MBC 뉴스', 'YTN'])
        r = requests.get('https://www.googleapis.com/youtube/v3/search', params={
            'key': YOUTUBE_KEY,
            'q': f'{channel} {query}',
            'part': 'snippet',
            'type': 'video',
            'order': 'relevance',
            'maxResults': 5,
            'relevanceLanguage': 'ko',
            'regionCode': 'KR',
        }, timeout=10)
        items = r.json().get('items', [])
        if not items:
            print('  YouTube 검색 결과 없음')
            return None
        random.shuffle(items)
        video_id = items[0]['id']['videoId']
        url = f'https://i.ytimg.com/vi/{video_id}/hqdefault.jpg'
        print(f'  YouTube URL: {url}')
        return url
    except Exception as e:
        print(f'  YouTube 오류: {e}')
    return None

# ─── 3. 기사 이미지 URL 추출 (YouTube 실패 시 폴백) ─────────────

def get_article_image_url(url):
    """기사 og:image URL 추출 (다운로드·업로드 없이 URL 직접 반환)"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=12, allow_redirects=True)
        soup = BeautifulSoup(r.content, 'html.parser')
        og = soup.find('meta', property='og:image')
        img_url = og['content'] if og and og.get('content') else None
        if not img_url:
            tw = soup.find('meta', attrs={'name': 'twitter:image'})
            img_url = tw['content'] if tw and tw.get('content') else None
        if img_url:
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            print(f'  기사 이미지 URL: {img_url[:80]}')
            return img_url
    except Exception as e:
        print(f'  기사 이미지 URL 오류: {e}')
    return None

def upload_to_github_release(file_path, repo='Choikoun/kb-threads-poster', tag=None):
    """mp4를 GitHub Releases에 업로드하고 공개 다운로드 URL 반환"""
    gh_token = os.environ['GITHUB_TOKEN']
    headers = {
        'Authorization': f'Bearer {gh_token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
    }

    if tag is None:
        tag = f"video-{datetime.now(KST).strftime('%Y%m%d-%H%M%S')}"

    r = requests.post(
        f'https://api.github.com/repos/{repo}/releases',
        headers=headers,
        json={
            'tag_name': tag,
            'name': f'Video {tag}',
            'body': '자동 생성된 비디오 포스트 에셋',
            'draft': False,
            'prerelease': False,
        },
        timeout=30,
    )
    if not r.ok:
        print(f'  릴리스 생성 실패: {r.status_code} {r.text}')
        return None
    release = r.json()
    upload_url_base = release['upload_url'].split('{')[0]

    filename = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        data = f.read()

    upload_headers = dict(headers)
    upload_headers['Content-Type'] = 'video/mp4'
    ur = requests.post(
        upload_url_base,
        headers=upload_headers,
        params={'name': filename},
        data=data,
        timeout=120,
    )
    if not ur.ok:
        print(f'  에셋 업로드 실패: {ur.status_code} {ur.text}')
        return None

    asset = ur.json()
    download_url = asset['browser_download_url']
    print(f'  GitHub Release 업로드 완료: {download_url}')
    return download_url

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
    '반전형': '''1. 숫자/팩트 or 반전 훅 — 한 줄씩 끊어서
↵빈줄
2. "대부분은 모르는" 반전 or 충격 사실 — 각 문장 단독 줄
↵빈줄
3. 묵직한 마무리 한 줄 (이모지 1개 앞에 붙여도 좋음)

예시:
퇴직금,
회사가 당연히 줘야 한다고 생각하지?

⚠️ 5명 중 1명은 못 받고 있어.

받을 수 있는데 모르는 사람이 더 많아.''',

    '사례형': '''1. 구체적 상황·사례로 시작 — 한 줄씩 끊어서
↵빈줄
2. 반전 or 충격 사실 — 각 문장 단독 줄
↵빈줄
3. 묵직한 마무리 한 줄

예시:
어떤 사업주,
퇴직금 정산하고 나서 알았어.

🔑 계약직도 1년 넘으면 퇴직금 대상이야.

미리 알았으면 구조를 달리 짰을 텐데.''',

    '담백형': '''1. 오늘 화제인 트렌드·이슈를 1~2줄로 전달 (한 줄씩 끊어서)
↵빈줄
2. 짧은 한마디 — 반응·소감 톤
↵빈줄
3. 여운 남기듯 마무리. "반전" 구조 강요하지 않음''',

    '감정인용형': '''1. 1인칭 속마음 인용구로 시작 (한 줄)
↵빈줄
2. 그 생각대로 행동하면 마주치는 현실 — 한 줄씩
↵빈줄
3. 구체적 사실·기준 — 숫자 단독 줄
↵빈줄
4. 묵직한 마무리 한 줄''',

    '번호형': '''1. 훅 — "이거 모르면 그냥 손해" 류 한 줄
↵빈줄
2. 번호 매긴 항목 3~5개 — 각 항목 "번호. 구체적 사실/조건" 형식, 항목당 1~2줄
↵빈줄
3. 마무리 한 줄 — 화두 던지고 끝

예시:
법인카드로 처리 가능한 비용, 생각보다 많아.

1. 거래처 식사비 — 한도 내 전액 인정
2. 사무실 비품·소모품 — 즉시 비용 처리
3. 명절 직원 선물 — 1인당 일정액까지 복리후생비

몰랐으면 그냥 세후 지출, 알면 전부 비용 처리야.''',
}

# 담백형·번호형은 ①숫자충격 ②반전 포인트 공식이 안 맞으므로 제외
POINT_FORMULA = '''[포인트 공식 - 반드시 둘 다 섞어]
① 숫자/팩트 충격: 실제 수치, 공식 발표, 통계로 독자 멈추게
② 반전: 대부분이 A라고 알고 있지만 실제는 B

예시 조합:
- "실손 적자 1.8조. / 대부분은 내 보험료가 오르는 이유를 몰라. / 근데 이게 노후 자산을 갉아먹는 구조야."
- "법인 대출 금리가 개인 신용대출보다 2~3배 높아. / 은행이 사장님 모신다고? / 실제론 가장 비싼 고객으로 만드는 거야."
'''


def _choose_format(category, variants):
    weights_file = 'format_weights.json'
    if os.path.exists(weights_file):
        try:
            with open(weights_file, encoding='utf-8') as f:
                weights = json.load(f)
            cat_weights = weights.get(category, {})
            w = [max(cat_weights.get(v, 1.0), 0.1) for v in variants]
            return random.choices(variants, weights=w, k=1)[0]
        except Exception:
            pass
    return random.choice(variants)


def generate_content(articles, category='economy', used_titles=None):
    client = genai.Client(api_key=GEMINI_KEY)
    cat = CATEGORIES.get(category, CATEGORIES['economy'])
    news_list = '\n'.join([f"{i+1}. {a['title']}" for i, a in enumerate(articles[:20])])
    trend_headlines = get_trend_headlines()
    trend_block = f"\n[오늘의 핵심 이슈 - 후속/연결 가능하면 활용]\n{trend_headlines}\n" if trend_headlines else ''
    context_block = f"\n[참고 - 관련 뉴스일 때만 활용]\n{cat['context']}\n" if cat.get('context') else ''
    format_branch_block = f"\n[형식 분기 - 해당되면 사용]\n{cat['format_branch']}\n" if cat.get('format_branch') else ''
    used_block = ''
    if used_titles:
        titles_str = '\n'.join(f'- {t}' for t in used_titles)
        used_block = f"\n[최근 3일 포스팅한 주제 - 절대 금지]\n{titles_str}\n위와 같은 사건·판결·기관 또는 같은 세금 항목(상속세·법인세·종부세 등)을 다룬 뉴스 금지. 완전히 다른 주제를 골라.\n"

    chosen_variant = _choose_format(category, cat.get('format_variants', ['반전형']))
    structure_block = FORMAT_STRUCTURES.get(chosen_variant, FORMAT_STRUCTURES['반전형'])
    point_formula_block = '' if chosen_variant in ('담백형', '번호형') else POINT_FORMULA

    source_hint_block = ''
    if os.path.exists('source_weights.json'):
        try:
            with open('source_weights.json', encoding='utf-8') as f:
                sw = json.load(f)
            src_avgs = {s: v for s, v in sw.items() if s != 'updated'}
            if len(src_avgs) >= 2:
                max_avg = max(src_avgs.values())
                low = [s for s, v in src_avgs.items() if v < max_avg * 0.6]
                if low:
                    source_hint_block = f'\n[저성과 뉴스 소스] {", ".join(low)} → 이 소스 뉴스보다 다른 소스 뉴스를 우선 선택해.\n'
        except Exception:
            pass

    length_hint_block = ''
    if os.path.exists('length_weights.json'):
        try:
            with open('length_weights.json', encoding='utf-8') as f:
                lw = json.load(f)
            best_bucket = lw.get('best_bucket', '')
            if best_bucket:
                length_hint_block = f'\n[이번 주 최고 성과 길이] {best_bucket} (평균 조회 {lw.get("avg_views", 0):,.0f}회) → 특별한 이유가 없다면 해시태그 제외 본문을 이 줄 수에 가깝게 짧게 써.\n'
        except Exception:
            pass

    hook_hint_block = ''
    if os.path.exists('hook_weights.json'):
        try:
            with open('hook_weights.json', encoding='utf-8') as f:
                hw = json.load(f)
            top_hook = max((t for t in hw if t != 'updated'), key=lambda t: hw[t], default=None)
            if top_hook:
                hook_hint_block = f'\n[이번 주 최고 성과 훅 타입] {top_hook} (평균 조회 {hw[top_hook]:,.0f}회) → 가능하면 이 유형으로 첫 줄을 구성해.\n'
        except Exception:
            pass

    follow_cta_block = ''
    extra_roll = random.random()
    if extra_roll < 0.12:
        follow_cta_block = '''
[추가 댓글 - 인스타 크로스 프로모션]
위 댓글들 다음에 댓글을 1개 더 추가해.
인스타그램에도 카드뉴스·릴스로 콘텐츠를 올리고 있다는 걸 자연스럽게 언급하는 한 줄.
반말. "인스타에도 카드뉴스로 정리해서 올려. 거기서도 보고 싶으면 팔로우해놔" 같은 식으로 자연스럽게 변형. 매번 같은 문구 반복하지 않는다.
"@계정명" 같은 핸들은 만들어내지 않는다.
'''
    elif extra_roll < 0.37:
        follow_cta_block = '''
[추가 댓글 - 팔로우 유도]
위 댓글들 다음에 댓글을 1개 더 추가해.
이 글 주제와 자연스럽게 이어지는 톤으로, 팔로우를 유도하는 한 줄.
반말. "이런 얘기 계속 보고 싶으면 팔로우해놔" 같은 직접적 표현도 괜찮고,
주제에 맞게 변형해도 좋음. 매번 같은 문구 반복하지 않는다.
"@계정명" 같은 계정 핸들은 절대 만들어내지 않는다.
'''

    prompt = f"""너는 한국 Threads에서 팔로워를 끌어모으는 금융 전문가야.
아래 뉴스 중 {cat['name']} 독자에게 가장 임팩트 있는 것 하나 골라서 포스트를 작성해줘.
{used_block}
[오늘 뉴스]
{news_list}
{trend_block}
[뉴스 선택 우선순위]
다음 유형의 뉴스가 있으면 최우선으로 선택해:
- 정부기관(국세청·대법원·헌재·공정위·금융위 등) 공식 발표, 판결, 표결 결과
- 구체적 숫자(금액·비율·표결수)가 포함된 사실
- 글로벌 빅테크 리더(CEO 등)의 한국 방문, 재벌 총수와의 회동처럼 화제성 있는 인물 동향 (단순 가십이 아니라 사업적 의미로 재해석할 수 있을 때)
해당하는 뉴스가 없으면 기존 기준대로 가장 임팩트 있는 걸 선택해.

[뉴스 선택 제외 기준]
다음 유형은 다른 후보가 있으면 피해 (후보 전부가 이 유형뿐이면 그중 [작성 각도]와 가장 가까운 걸 선택):
- 단순 행정 안내·공지 (부과·납부·신청 일정 등 절차성 정보뿐, 반전이나 숫자 충격이 없는 것)
- "~할 예정", "~검토 중"처럼 아직 결정·발표되지 않은 예고성 뉴스
- 개별 형사사건 단신(사기·횡령 등)으로 구조적 인사이트 없이 사건 자체만 보도된 것
- {cat['name']} 각도와 직접 관련 없는 뉴스 (단지 같은 RSS 피드에 섞여 들어온 무관한 경제 뉴스)
{source_hint_block}
[작성 각도]
{cat['angle']}
{context_block}
[핵심 원칙 - 반드시 지켜]
- 전부 반말
- 상담/DM/점검 유도 절대 금지. 화두만 던지고 끝낸다.
- 특정 종목·자산의 매수/매도/매매 타이밍을 지시하거나 추천하지 않는다 (미등록 투자자문 리스크). "포트폴리오 재검토할 시기", "수익 극대화 전략" 같은 투자행동 지시형 표현 금지 — "이런 흐름이 있다", "구조가 흔들릴 수 있다"처럼 구조적 인식까지만 다루고, 행동 지시는 하지 않는다.
- 완전한 답 주지 말 것. 경각심·인사이트·잘못된 상식을 건드리되 "상황마다 달라", "구조가 먼저야"처럼 열어두어 독자 스스로 "내 상황은 어떻게 되지?" 상담 욕구가 생기도록.
- 세금 계산·법 조항 해설보다 "미리 구조를 설계하느냐 못 하느냐의 차이" 부각이 이 계정의 포지셔닝.
- [정확성 필수] 세법·제도 개정을 다룰 때, 국회 통과·시행이 확정되지 않은 '개정안/발의/추진 중'인 내용을 이미 확정된 사실("~로 바뀌었다", "~됐다")처럼 단정하지 마라. 뉴스에 '개정안', '추진', '검토', '발의', '입법예고'라는 단어가 있으면 아직 확정 아님 — "개정안이 추진되고 있어", "국회 통과하면 이렇게 바뀌어" 식으로 미확정임을 분명히 하고, 확정된 시행 사실만 확정형으로 써라. (실제 팔로워가 '진짜 결정난 거야?'라고 지적한 오류 재발 방지)
- 한 줄 = 한 문장 or 핵심 단어구. 절대로 한 줄에 두 문장 붙이지 않는다.
- 연속 2줄 이상이면 무조건 빈 줄 하나 삽입 (숨 쉬는 구조)
- 숫자·핵심 사실·반전 문장은 단독 줄에 배치
- 이모지: 전체 포스트에 1~2개. 핵심 줄 앞이나 단락 구분용으로만. 장식용 남발 금지. 사용 예: 💡 ⚠️ 📌 🔑 → 등 의미 있는 것만.
- 모호한 표현 절대 금지: "뭔가 있어", "달라져", "독이다", "조심해", "알아봐야 해" → 구체적으로 써
- 자극적이되 공격적이지 않게. 독자를 비하하거나 몰아붙이는 표현 금지. 기관·구조·현상을 비판하되 독자를 적으로 만들지 않는다.
- ❌ 공격적 (활용형 포함 전부 금지): "바보처럼 당하고 있어", "멍청하게 내고 있지", "털리는 중", "털릴", "털려", "털리고" 등 "털리다" 계열 일체
- ✅ 자극적: "대부분이 이걸 몰라", "이거 해당되는 사람 많을 거야", "은행이 더 벌려는 구조야"

{point_formula_block}
{hook_hint_block}
{length_hint_block}
[메인 포스트 구조 - {chosen_variant}]
{structure_block}
{format_branch_block}
[댓글 구조]
- 댓글 수는 1~3개. 내용 흐름에 맞게 자유롭게 결정. 억지로 3개 채우지 않는다.
- 댓글1: 숫자 단독 줄 + 그 의미 (빈줄 포함, 3~4줄)
- 댓글2 (선택): 핵심 반전 포인트 하나 (빈줄 포함, 3~4줄)
- 마지막 댓글: 양자택일형 질문으로 마무리 (예: "당신은 A야, B야?", "지금 갈아탈 거야, 버틸 거야?")
  - 개방형 질문("어떻게 준비하고 있어?") 금지. 독자가 댓글 하나로 바로 답할 수 있는 두 가지 선택지를 제시.
  - 2~3줄, 전부 반말
{follow_cta_block}
JSON만 출력:
{{
  "selected_title": "선택한 뉴스 제목",
  "youtube_keyword": "YouTube에서 관련 뉴스 영상 찾을 검색어 (한국어 2~4단어, 뉴스 방송에 나올 법한 키워드)",
  "main": "메인 포스트 텍스트",
  "comments": [
    "댓글1",
    "댓글2",
    "댓글3 (마지막 질문, 반드시 반말 — 존댓말 금지)"
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
                sel = result.get('selected_title', '')
                result['source'] = ''
                for a in articles:
                    if sel and (sel[:15] in a['title'] or a['title'][:15] in sel):
                        result['source'] = a.get('source', '')
                        break
                return result
        except Exception as e:
            print(f'Gemini 오류 (시도 {attempt+1}/3): {e}')
            if attempt < 2:
                wait = 20 * (attempt + 1)
                print(f'  {wait}초 후 재시도...')
                time.sleep(wait)
    return None

# ─── 4. Threads 포스팅 ───────────────────────────────────────────

def post_to_threads(main_text, comments, image_url=None, topic_tag=None, content_warning=True):
    me = requests.get('https://graph.threads.net/v1.0/me',
                      params={'fields': 'id', 'access_token': TOKEN}, timeout=30)
    UID = me.json()['id']

    params = {'text': main_text, 'access_token': TOKEN}
    if topic_tag:
        params['topic_tag'] = topic_tag
    if content_warning:
        params['content_warning_type'] = 'SENSITIVE_MEDIA'
    if image_url:
        params['media_type'] = 'IMAGE'
        params['image_url'] = image_url
    else:
        params['media_type'] = 'TEXT'

    r1 = requests.post(f'https://graph.threads.net/v1.0/{UID}/threads', params=params, timeout=30)
    print(f'메인 컨테이너: {r1.json()}')
    time.sleep(4)

    # 이미지 URL 실패 시 텍스트 전용으로 재시도
    if 'id' not in r1.json() and image_url:
        print('이미지 URL 오류 — 텍스트 전용으로 재시도')
        params.pop('image_url', None)
        params['media_type'] = 'TEXT'
        r1 = requests.post(f'https://graph.threads.net/v1.0/{UID}/threads', params=params, timeout=30)
        print(f'텍스트 컨테이너: {r1.json()}')
        time.sleep(4)

    r2 = requests.post(f'https://graph.threads.net/v1.0/{UID}/threads_publish',
                       params={'creation_id': r1.json()['id'], 'access_token': TOKEN}, timeout=30)
    main_id = r2.json()['id']
    print(f'메인 발행: {main_id}')
    time.sleep(3)

    _publish_comments(UID, main_id, comments)

    return main_id


def _publish_comments(UID, main_id, comments):
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


def post_video_to_threads(main_text, comments, video_url, topic_tag=None):
    me = requests.get('https://graph.threads.net/v1.0/me',
                      params={'fields': 'id', 'access_token': TOKEN}, timeout=30)
    UID = me.json()['id']

    params = {
        'text': main_text,
        'media_type': 'VIDEO',
        'video_url': video_url,
        'access_token': TOKEN,
    }
    if topic_tag:
        params['topic_tag'] = topic_tag

    r1 = requests.post(f'https://graph.threads.net/v1.0/{UID}/threads', params=params, timeout=30)
    container_id = r1.json().get('id')
    print(f'메인 컨테이너(VIDEO): {r1.json()}')
    if not container_id:
        print('컨테이너 생성 실패')
        return None

    # 비디오 처리 상태 폴링 (최대 5분, 10초 간격)
    for attempt in range(30):
        time.sleep(10)
        sr = requests.get(f'https://graph.threads.net/v1.0/{container_id}',
                          params={'fields': 'status,error_message', 'access_token': TOKEN},
                          timeout=30)
        sd = sr.json()
        status = sd.get('status')
        print(f'  처리 상태 ({attempt+1}/30): {status}')
        if status == 'FINISHED':
            break
        if status == 'ERROR':
            print(f'  비디오 처리 오류: {sd.get("error_message")}')
            return None
    else:
        print('  비디오 처리 타임아웃')
        return None

    r2 = requests.post(f'https://graph.threads.net/v1.0/{UID}/threads_publish',
                       params={'creation_id': container_id, 'access_token': TOKEN}, timeout=30)
    main_id = r2.json()['id']
    print(f'메인 발행: {main_id}')
    time.sleep(3)

    _publish_comments(UID, main_id, comments)

    return main_id

# ─── 콘텐츠 로그 ──────────────────────────────────────────────────

def log_content(post_id, category, format_variant, selected_title, source='', line_count=0):
    log = []
    if os.path.exists(CONTENT_LOG_FILE):
        with open(CONTENT_LOG_FILE, encoding='utf-8-sig') as f:
            log = json.load(f)
    now = datetime.now(KST)
    log.append({
        'post_id': post_id,
        'category': category,
        'format_variant': format_variant,
        'date': now.strftime('%Y-%m-%d'),
        'hour': now.hour,
        'selected_title': selected_title,
        'source': source,
        'line_count': line_count,
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

    today_str = datetime.now(KST).strftime('%Y-%m-%d')
    cutoff_str = (datetime.now(KST) - timedelta(days=3)).strftime('%Y-%m-%d')
    used_titles = []
    if os.path.exists(CONTENT_LOG_FILE):
        with open(CONTENT_LOG_FILE, encoding='utf-8-sig') as f:
            used_titles = [e['selected_title'] for e in json.load(f)
                          if e.get('date', '') >= cutoff_str and e.get('selected_title')]
    if used_titles:
        print(f'최근 3일 포스팅 주제 {len(used_titles)}개 중복 방지 적용')

    print('\nGemini 컨텐츠 생성 중...')
    content = generate_content(articles, category, used_titles=used_titles)
    if not content:
        print('컨텐츠 생성 실패 - 종료')
        sys.exit(1)

    # 주제 중복 감지 → 재시도
    if used_titles and content.get('selected_title'):
        dup_hits = [t for t in used_titles if _kw_overlap(content['selected_title'], t) >= 3]
        if dup_hits:
            print(f'⚠️ 중복 주제 감지: "{content["selected_title"][:35]}" ↔ "{dup_hits[0][:35]}"')
            print('  다른 주제로 재시도...')
            retry_titles = used_titles + [content['selected_title']]
            content = generate_content(articles, category, used_titles=retry_titles)
            if not content:
                print('재시도 실패 - 종료')
                sys.exit(1)
            print(f'  재선택: {content["selected_title"]}')

    print(f'\n선택된 뉴스: {content["selected_title"]}')
    print(f'메인:\n{content["main"]}\n')
    for i, c in enumerate(content['comments']):
        print(f'댓글{i+1}:\n{c}\n')

    image_url = None
    print('이미지 탐색 중...')

    cat_info = CATEGORIES.get(category, {})
    youtube_hint = cat_info.get('youtube_hint', '')
    search_query = youtube_hint or content.get('youtube_keyword', '') or \
        re.sub(r'[^\w\s]', ' ', content['selected_title']).strip()[:25]

    # 1순위: YouTube 썸네일 URL 직접 사용 (imgbb 불필요)
    print(f'  YouTube 검색: {search_query}')
    image_url = get_youtube_thumbnail_url(search_query)

    # 2순위: 기사 og:image URL 직접 사용
    if not image_url:
        print('  YouTube 없음 → 기사 이미지 URL 시도')
        sel = content['selected_title'][:20]
        for article in articles:
            if sel in article['title'] or article['title'][:20] in sel:
                image_url = get_article_image_url(article['link'])
                if image_url:
                    break
    if not image_url:
        for article in articles[:5]:
            image_url = get_article_image_url(article['link'])
            if image_url:
                break

    if not image_url:
        print('  이미지 없이 진행')

    # A/B 슬롯 실험: slot_config.json의 최적 시간까지 대기
    if os.path.exists('slot_config.json'):
        try:
            with open('slot_config.json', encoding='utf-8') as f:
                sc = json.load(f)
            target_h = sc.get(category)
            if target_h is not None:
                now_h = datetime.now(KST).hour
                wait_secs = (target_h - now_h) * 3600
                if 0 < wait_secs <= 7200:
                    print(f'슬롯 조정: {now_h:02d}:xx → {target_h:02d}:00 KST ({wait_secs//60}분 대기)')
                    time.sleep(wait_secs)
        except Exception as e:
            print(f'슬롯 설정 오류 (무시): {e}')

    print('\nThreads 포스팅 중...')
    main_id = post_to_threads(content['main'], content['comments'], image_url, topic_tag=cat_info.get('topic_tag'))
    print(f'\n완료! 메인 포스트 ID: {main_id}')

    main_line_count = len([l for l in content['main'].split('\n') if l.strip() and not l.strip().startswith('#')])
    log_content(main_id, category, content.get('format_variant', ''), content['selected_title'],
                source=content.get('source', ''), line_count=main_line_count)

if __name__ == '__main__':
    main()
