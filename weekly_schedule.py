#!/usr/bin/env python3
"""
매주 월요일 08:00 KST — 이번 주 포스팅 스케줄을 GitHub Issue로 생성
"""
import os, sys, requests
from datetime import datetime, timezone, timedelta
sys.stdout.reconfigure(encoding='utf-8')

KST = timezone(timedelta(hours=9))

DAILY_SLOTS = [
    ('06:00', '새벽 인사이트', '증여·상속 구조 원칙 (3줄)'),
    ('07:30', '법인·사업주 뉴스', '오전 비즈니스 뉴스'),
    ('09:00', '시즌 이슈', '해당 이벤트 있을 때만'),
    ('10:00', '세법 뉴스 감지', '국세청·기재부 RSS (해당 시만)'),
    ('12:00', '경제·시장 뉴스', '점심 경제 뉴스'),
    ('16:00', '세법 뉴스 감지', '국세청·기재부 RSS (해당 시만)'),
    ('21:00', '보험·노후·상속 뉴스', '저녁 뉴스'),
    ('21:00', '팔로워 추적', '마일스톤 달성 시만 포스팅'),
    ('23:30', '포스팅 공백 감지', '2개 미만이면 GitHub Issue'),
]

WEEKLY_SLOTS = {
    0: [('14:00', '법인 설계 이야기', '시리즈 법인·승계·동업·매각 포스팅')],  # 월
    1: [('14:00', '증여 설계 이야기', '시리즈 증여·상속 포스팅')],       # 화
    2: [('11:00', '댓글→초안 생성', 'GitHub Issue로 초안 전달'),           # 수
         ('20:00', '주간 재발행', '지난 30일 인기글 TOP1 재발행')],
    3: [('14:00', '증여 설계 이야기', '시리즈 증여·상속 포스팅')],       # 목
    4: [('14:00', '법인 설계 이야기', '시리즈 법인·승계·동업·매각 포스팅')],  # 금
    5: [('20:00', '비디오 포스팅', 'Ken Burns + TTS 영상')],              # 토
    6: [('10:00', '이번 주 TOP 글 요약', '이번 주 조회수 1위 미리보기')], # 일
}

MONTHLY_SLOTS = [
    ('매주 월 07:00', '주간 조회수 분석', '재발행 후보·포맷 가중치·Gemini 인사이트'),
    ('매월 1일 10:00', '월간 하이라이트', '전달 TOP3 포스트 자동 발행'),
]

WEEKDAY_KO = ['월', '화', '수', '목', '금', '토', '일']


def main():
    gh_token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    repo = os.environ.get('GITHUB_REPOSITORY', 'Choikoun/kb-threads-poster')

    today = datetime.now(KST)
    # 이번 주 월~일
    monday = today - timedelta(days=today.weekday())
    week_dates = [monday + timedelta(days=i) for i in range(7)]

    lines = [f'## 이번 주 포스팅 스케줄 ({monday.strftime("%m/%d")} ~ {week_dates[6].strftime("%m/%d")})\n']
    lines.append('### 매일 반복 슬롯')
    lines.append('| 시각 (KST) | 내용 | 비고 |')
    lines.append('|-----------|------|------|')
    for slot, name, note in DAILY_SLOTS:
        lines.append(f'| {slot} | {name} | {note} |')

    lines.append('\n### 요일별 추가 슬롯')
    lines.append('| 날짜 | 요일 | 시각 | 내용 |')
    lines.append('|------|------|------|------|')
    for d in week_dates:
        wd = d.weekday()  # 0=월 ... 6=일
        slots = WEEKLY_SLOTS.get(wd, [])
        for slot, name, _ in slots:
            lines.append(f'| {d.strftime("%m/%d")} | {WEEKDAY_KO[wd]} | {slot} | {name} |')

    lines.append('\n### 정기 분석·이벤트')
    lines.append('| 주기 | 내용 | 비고 |')
    lines.append('|------|------|------|')
    for timing, name, note in MONTHLY_SLOTS:
        lines.append(f'| {timing} | {name} | {note} |')

    lines.append(f'\n---\n_자동 생성: {today.strftime("%Y-%m-%d %H:%M")} KST_')

    body = '\n'.join(lines)
    title = f'📅 이번 주 포스팅 스케줄 ({monday.strftime("%m/%d")} ~ {week_dates[6].strftime("%m/%d")})'

    if not gh_token:
        print(title)
        print(body)
        return

    headers = {'Authorization': f'token {gh_token}', 'Accept': 'application/vnd.github+json'}
    r = requests.post(
        f'https://api.github.com/repos/{repo}/issues',
        headers=headers,
        json={'title': title, 'body': body},
        timeout=30
    )
    print(f'스케줄 Issue 생성: #{r.json().get("number")} — {title}')


if __name__ == '__main__':
    main()
