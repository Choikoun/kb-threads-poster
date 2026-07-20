#!/usr/bin/env python3
"""
세제 속보 즉시 포스팅
매 3시간 RSS 체크 → 상속세·증여세·법인세 개정/발표 감지 시 즉시 포스팅
"""
import os, sys, json, re, time, requests, feedparser
from datetime import datetime, timezone, timedelta
from google import genai
from dotenv import load_dotenv
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

TOKEN = os.environ['THREADS_ACCESS_TOKEN']
GEMINI_KEY = os.environ['GEMINI_API_KEY']
BASE = 'https://graph.threads.net/v1.0'
KST = timezone(timedelta(hours=9))
BREAKING_LOG_FILE = 'breaking_log.json'
WINDOW_HOURS = 3.5

# (주제 키워드, 속보 동사 키워드) 쌍
# 주제가 있고 동사도 있을 때, 또는 동사 목록이 비어있으면 주제만으로 감지
BREAKING_PAIRS = [
    ('상속세', ['개정', '개편', '폐지', '완화', '강화', '인하', '인상', '발표']),
    ('증여세', ['개정', '개편', '폐지', '완화', '강화', '인하', '인상', '발표']),
    ('법인세', ['개정', '개편', '인하', '인상', '폐지', '발표']),
    ('종합부동산세', ['폐지', '개편', '개정', '완화', '발표']),
    ('종부세', ['폐지', '개편', '개정', '완화', '발표']),
    ('세법 개정안', []),
    ('세제 개편', []),
    ('기재부', ['상속세', '증여세', '법인세', '세법']),
    ('국세청', ['예규', '고시', '발표', '개정']),
]

RSS_FEEDS = [
    'https://www.hankyung.com/feed/economy',
    'https://rss.etnews.com/Section901.xml',
    'https://www.mk.co.kr/rss/30000001/',
    'https://biz.chosun.com/site/data/rss/rss.xml',
    'https://news.sbs.co.kr/news/SBSNewsRss.do?pmd=Economy',
]


def is_breaking(title):
    for main_kw, verbs in BREAKING_PAIRS:
        if main_kw not in title:
            continue
        if not verbs:
            return True
        if any(v in title for v in verbs):
            return True
    return False


def get_recent_breaking():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=WINDOW_HOURS)
    found = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:20]:
                title = re.sub(r'\s*-\s*[^-]+$', '', entry.get('title', '')).strip()
                published = entry.get('published_parsed') or entry.get('updated_parsed')
                if published:
                    pub_dt = datetime(*published[:6], tzinfo=timezone.utc)
                    if pub_dt < cutoff:
                        continue
                if is_breaking(title):
                    found.append({'title': title, 'link': entry.get('link', '')})
        except Exception as e:
            print(f'피드 오류 ({url[:40]}): {e}')
    seen = set()
    unique = []
    for a in found:
        if a['title'] not in seen:
            seen.add(a['title'])
            unique.append(a)
    return unique


def load_log():
    if os.path.exists(BREAKING_LOG_FILE):
        with open(BREAKING_LOG_FILE, encoding='utf-8') as f:
            return json.load(f)
    return []


def save_log(log):
    with open(BREAKING_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def generate(article):
    client = genai.Client(api_key=GEMINI_KEY)
    prompt = f"""너는 한국 Threads에서 활동하는 증여·상속·법인 구조 설계 전문가야.
방금 세제 관련 속보가 나왔어.

뉴스: {article['title']}

이 뉴스를 보고 사업주·자산가 독자에게 즉각적인 인사이트를 주는 포스팅을 써줘.

[핵심 원칙]
- 전부 반말
- 상담/DM 유도 절대 금지
- 속보 직후 타이밍감을 살려 — "방금 나온 거야", "오늘 발표된 거야" 자연스럽게
- 완전한 답 말고 "이게 바뀌면 내 구조는 어떻게 되지?" 라는 생각이 들도록
- 한 줄 = 한 문장. 연속 2줄이면 빈 줄 삽입
- 메인 6~10줄
- 이모지 1~2개
- 반전형 또는 경각심형 훅으로 시작. 뉴스 제목 직접 인용 말고 핵심만 녹여.

[댓글]
- 댓글1: 이 변화가 실질적으로 어떤 영향인지 2~3줄
- 댓글2: 양자택일형 질문 (2줄, 반말)

마지막에 #세법개정 #절세 해시태그.

JSON만 출력:
{{"main": "...", "comments": ["댓글1", "댓글2"]}}"""

    for attempt in range(3):
        try:
            resp = client.models.generate_content(model='gemini-flash-latest', contents=prompt)
            m = re.search(r'\{[\s\S]*\}', resp.text.strip())
            if m:
                return json.loads(m.group())
        except Exception as e:
            print(f'생성 오류 (시도 {attempt+1}/3): {e}')
            time.sleep(3)
    return None


def post(content):
    r = requests.get(f'{BASE}/me', params={'fields': 'id', 'access_token': TOKEN}, timeout=30)
    uid = r.json()['id']
    r1 = requests.post(f'{BASE}/{uid}/threads',
                       params={'media_type': 'TEXT', 'text': content['main'],
                               'content_warning_type': 'SENSITIVE_MEDIA', 'access_token': TOKEN}, timeout=30)
    time.sleep(4)
    r2 = requests.post(f'{BASE}/{uid}/threads_publish',
                       params={'creation_id': r1.json()['id'], 'access_token': TOKEN}, timeout=30)
    main_id = r2.json()['id']
    print(f'메인 발행: {main_id}')
    time.sleep(3)
    for i, c in enumerate(content.get('comments', [])):
        rc = requests.post(f'{BASE}/{uid}/threads',
                           params={'media_type': 'TEXT', 'text': c, 'reply_to_id': main_id, 'access_token': TOKEN}, timeout=30)
        time.sleep(3)
        rp = requests.post(f'{BASE}/{uid}/threads_publish',
                           params={'creation_id': rc.json()['id'], 'access_token': TOKEN}, timeout=30)
        print(f'댓글{i+1} 발행: {rp.json().get("id")}')
        time.sleep(2)
    return main_id


def main():
    breaking = get_recent_breaking()
    if not breaking:
        print(f'세제 속보 없음 (최근 {WINDOW_HOURS}시간 이내)')
        return

    log = load_log()
    posted_titles = {e['title'] for e in log}

    for article in breaking:
        if article['title'] in posted_titles:
            print(f'이미 포스팅됨: {article["title"]}')
            continue
        print(f'세제 속보 감지: {article["title"]}')
        content = generate(article)
        if not content:
            print('생성 실패')
            continue
        print(f'\n메인:\n{content["main"]}\n')
        main_id = post(content)
        log.append({
            'title': article['title'],
            'post_id': main_id,
            'date': datetime.now(KST).strftime('%Y-%m-%d %H:%M'),
        })
        save_log(log)
        print(f'완료: {article["title"]}')
        break  # 1회 실행에 1건만 포스팅


if __name__ == '__main__':
    main()
