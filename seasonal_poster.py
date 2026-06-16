#!/usr/bin/env python3
"""
시즌 이슈 자동 포스팅
주요 세금·증여·상속 일정이 7일 이내로 다가오면 자동으로 관련 글 생성·발행
매일 09:00 KST 실행
"""
import os, sys, json, re, time, requests
from datetime import datetime, timedelta, timezone
from google import genai
from dotenv import load_dotenv
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

TOKEN = os.environ['THREADS_ACCESS_TOKEN']
GEMINI_KEY = os.environ['GEMINI_API_KEY']
BASE = 'https://graph.threads.net/v1.0'
KST = timezone(timedelta(hours=9))
LOG_FILE = 'seasonal_log.json'

EVENTS = [
    {"mmdd": "01-01", "window": 10, "topic": "새해 증여 공제 한도 리셋", "angle": "10년 주기 증여 공제가 초기화되는 시점. 증여 계획이 있다면 구조부터 다시 점검해야 하는 이유"},
    {"mmdd": "03-31", "window": 10, "topic": "법인세 신고 마감", "angle": "법인 대표가 법인세 신고 전에 놓치는 구조적 문제들. 신고는 세무사가 하지만 구조 설계는 미리였어야 했다"},
    {"mmdd": "05-01", "window": 7,  "topic": "종합소득세 신고 시작", "angle": "종합소득세 신고 시즌. 소득이 많을수록 구조가 없으면 더 낸다"},
    {"mmdd": "05-31", "window": 7,  "topic": "종합소득세 신고 마감", "angle": "종합소득세 신고 마감 임박. 올해 못 한 건 내년 구조로 만회해야 한다"},
    {"mmdd": "06-01", "window": 7,  "topic": "재산세 과세기준일", "angle": "6월 1일 기준 부동산 소유자에게 재산세 부과. 증여 타이밍이 하루 차이로 달라지는 이유"},
    {"mmdd": "11-15", "window": 10, "topic": "종합부동산세 납부", "angle": "종부세 고지서 나오는 시점. 부동산 자산 구조 재점검이 필요한 이유"},
    {"mmdd": "12-25", "window": 14, "topic": "연말 증여·절세 마지막 기회", "angle": "연말 전에 증여·자산 이전 완료해야 하는 이유. 12월 31일 이후는 다음 해로 밀린다"},
]

def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, encoding='utf-8') as f:
            return json.load(f)
    return []

def save_log(log):
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

def find_upcoming(today):
    upcoming = []
    year = today.year
    for ev in EVENTS:
        mmdd = ev["mmdd"]
        try:
            target = datetime(year, int(mmdd[:2]), int(mmdd[3:]), tzinfo=KST)
        except ValueError:
            continue
        if target < today:
            target = datetime(year + 1, int(mmdd[:2]), int(mmdd[3:]), tzinfo=KST)
        days_left = (target.date() - today.date()).days
        if 0 <= days_left <= ev["window"]:
            upcoming.append({**ev, "days_left": days_left, "target_date": target.strftime('%Y-%m-%d')})
    return upcoming

def already_posted(log, event_key, year):
    return any(e.get("key") == event_key and e.get("year") == year for e in log)

def generate(event):
    client = genai.Client(api_key=GEMINI_KEY)
    days_left = event['days_left']
    timing = "오늘이야" if days_left == 0 else f"{days_left}일 남았어"
    prompt = f"""너는 증여·상속 구조 설계 전문가 Threads 계정이야.
다가오는 세금·자산 이슈: {event['topic']} ({timing})
각도: {event['angle']}

[핵심 원칙]
- 전부 반말
- 완전한 답 주지 말 것. 경각심을 주되 "상황마다 달라", "구조가 먼저야"처럼 열어두기
- 상담/DM 유도 절대 금지
- 훅을 첫 줄에 — 날짜/시즌 맥락을 자연스럽게 녹이되 딱딱하지 않게
- 메인 6~10줄, 반말, 짧고 강하게
- 댓글 2개 (마지막은 양자택일형)

메인 마지막에 `#증여 #상속` 추가.

JSON만 출력:
{{"main": "...", "comments": ["댓글1", "댓글2"]}}"""
    for attempt in range(3):
        try:
            resp = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            m = re.search(r'\{[\s\S]*\}', resp.text.strip())
            if m:
                return json.loads(m.group())
        except Exception as e:
            print(f'생성 오류 (시도 {attempt+1}/3): {e}')
    return None

def post(content):
    r = requests.get(f'{BASE}/me', params={'fields': 'id', 'access_token': TOKEN}, timeout=30)
    uid = r.json()['id']
    r1 = requests.post(f'{BASE}/{uid}/threads',
                       params={'media_type': 'TEXT', 'text': content['main'], 'access_token': TOKEN}, timeout=30)
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
    today = datetime.now(KST)
    upcoming = find_upcoming(today)
    if not upcoming:
        print(f'[{today.strftime("%Y-%m-%d")}] 다가오는 시즌 이슈 없음')
        return

    log = load_log()
    for ev in upcoming:
        key = ev['mmdd']
        year = today.year
        if already_posted(log, key, year):
            print(f'이미 포스팅됨: {ev["topic"]}')
            continue
        print(f'시즌 이슈 감지: {ev["topic"]} ({ev["days_left"]}일 전)')
        content = generate(ev)
        if not content:
            print('생성 실패')
            continue
        print(f'\n메인:\n{content["main"]}\n')
        post_id = post(content)
        log.append({"key": key, "year": year, "topic": ev["topic"], "post_id": post_id,
                    "date": today.strftime('%Y-%m-%d')})
        save_log(log)
        print(f'완료: {ev["topic"]}')
        time.sleep(5)

if __name__ == '__main__':
    main()
