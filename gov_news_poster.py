#!/usr/bin/env python3
"""
국세청·기재부·법제처 보도자료 + 법률신문·리걸타임즈 RSS 감지 → 즉각 반응 포스팅
세법 개정·세율 변경·공제 한도 + 상법·회사법 판례(정관·의결권·이사회 등) 감지되면
"법이 바뀌었어" 각도로 짧게 발행
"""
import os, sys, json, re, time, requests
from datetime import datetime, timezone, timedelta
sys.stdout.reconfigure(encoding='utf-8')
import feedparser
from google import genai
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.environ['THREADS_ACCESS_TOKEN']
GEMINI_KEY = os.environ['GEMINI_API_KEY']
BASE = 'https://graph.threads.net/v1.0'
KST = timezone(timedelta(hours=9))
GOV_LOG = 'gov_news_log.json'
WINDOW_DAYS = 7

FEEDS = [
    'https://www.nts.go.kr/rss/ntsPressRelease.rss',                                    # 국세청 보도자료
    'https://www.moef.go.kr/com/bbs/BBSList.rss?bbsId=MOSFBBS_000000000029',            # 기획재정부
    'https://www.law.go.kr/rss/lsInfoP.do',                                             # 법제처 법령
    'https://www.yna.co.kr/rss/economy.xml',                                            # 연합뉴스 경제
    'https://www.mk.co.kr/rss/30000001/',                                               # 매경 경제
    'https://biz.chosun.com/arc/outboundfeeds/rss/?outputType=xml',                    # 조선비즈
    'https://www.lawtimes.co.kr/rss/allArticle.xml',                                    # 법률신문 전체기사
    'https://www.legaltimes.co.kr/rss/allArticle.xml',                                  # 리걸타임즈 전체기사
]

TRIGGER_KEYWORDS = [
    '세법 개정', '상속세', '증여세', '가업승계', '소득세법 개정', '세법 시행령',
    '세율 인하', '세율 인상', '공제 한도', '국세기본법', '법인세 개정',
    '최대주주 할증', '상속세율', '세제 개편', '조세특례', '부동산 세제',
    '증여 공제', '세금 완화', '중산층 세금', '상속 공제',
    '정관 변경', '의결권', '이사회', '주주총회', '상법 개정', '회사법',
    '이사 책임', '경영권 분쟁', '주주 권리', '대법원 판결',
]

PROMPT = """너는 한국 Threads에서 활동하는 증여·상속 구조 설계 전문가야.

방금 아래 세법/세제 관련 뉴스가 나왔어:
제목: {title}
내용 요약: {summary}

이 뉴스가 증여·상속·법인 구조 설계에 어떤 의미인지 짧게 포스팅해줘.

[원칙]
- 전부 반말
- 4~6줄, 짧고 강하게
- 첫 줄: "세법이 바뀌었어." 또는 "법이 또 바뀌었어." 등 즉각적인 팩트로 시작
- 법 조항 해설 말고 "미리 알고 있었냐 아니냐의 차이"를 건드릴 것
- 상담/링크 유도 금지
- 특정 종목·자산의 매수/매도/매매 타이밍을 지시하거나 추천하지 않는다 (미등록 투자자문 리스크)
- 마지막에 빈 줄 + `#증여 #상속 #세법개정`

JSON만 출력:
{{"main": "포스트 텍스트\\n\\n#증여 #상속 #세법개정"}}"""

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}


def load_log():
    if os.path.exists(GOV_LOG):
        try:
            with open(GOV_LOG, encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {'posted': []}


def save_log(log):
    with open(GOV_LOG, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def fetch_articles():
    cutoff = (datetime.now(KST) - timedelta(days=WINDOW_DAYS)).strftime('%Y-%m-%d')
    log = load_log()
    posted_urls = {e['url'] for e in log.get('posted', []) if e.get('date', '') >= cutoff}

    results = []
    for feed_url in FEEDS:
        try:
            feed = feedparser.parse(feed_url, request_headers=HEADERS)
            for entry in feed.entries[:20]:
                url = entry.get('link', '')
                title = entry.get('title', '')
                summary = entry.get('summary', entry.get('description', ''))[:300]
                if url in posted_urls:
                    continue
                text = f'{title} {summary}'
                if any(kw in text for kw in TRIGGER_KEYWORDS):
                    results.append({'url': url, 'title': title, 'summary': summary})
        except Exception as e:
            print(f'피드 오류 ({feed_url[:40]}...): {e}')

    return results, log


def generate(title, summary):
    client = genai.Client(api_key=GEMINI_KEY)
    prompt = PROMPT.format(title=title, summary=summary)
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


def post_text(text):
    r = requests.get(f'{BASE}/me', params={'fields': 'id', 'access_token': TOKEN}, timeout=30)
    uid = r.json()['id']
    r1 = requests.post(f'{BASE}/{uid}/threads',
                       params={'media_type': 'TEXT', 'text': text, 'content_warning_type': 'SENSITIVE_MEDIA', 'access_token': TOKEN}, timeout=30)
    time.sleep(4)
    r2 = requests.post(f'{BASE}/{uid}/threads_publish',
                       params={'creation_id': r1.json()['id'], 'access_token': TOKEN}, timeout=30)
    return r2.json().get('id')


def main():
    articles, log = fetch_articles()
    if not articles:
        print('세법 관련 신규 뉴스 없음.')
        return

    article = articles[0]
    print(f'감지: {article["title"][:60]}')

    content = generate(article['title'], article['summary'])
    if not content:
        print('생성 실패')
        return

    print(f'\n{content["main"]}\n')
    post_id = post_text(content['main'])
    print(f'발행 완료: {post_id}')

    log['posted'].append({
        'url': article['url'],
        'title': article['title'],
        'date': datetime.now(KST).strftime('%Y-%m-%d'),
        'post_id': post_id,
    })
    save_log(log)


if __name__ == '__main__':
    main()
