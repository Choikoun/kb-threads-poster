#!/usr/bin/env python3
"""
매일 23:30 KST — content_log.json으로 당일 포스팅 수 확인
2개 미만이면 GitHub Issue 생성
"""
import os, sys, json, requests
from datetime import datetime, timezone, timedelta
sys.stdout.reconfigure(encoding='utf-8')

KST = timezone(timedelta(hours=9))
CONTENT_LOG = 'content_log.json'
EXPECTED_MIN = 2


def create_issue(title, body=''):
    gh_token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    repo = os.environ.get('GITHUB_REPOSITORY', 'Choikoun/kb-threads-poster')
    if not gh_token:
        print(f'ISSUE (토큰 없음): {title}')
        return
    headers = {'Authorization': f'token {gh_token}', 'Accept': 'application/vnd.github+json'}
    r = requests.post(
        f'https://api.github.com/repos/{repo}/issues',
        headers=headers,
        json={'title': title, 'body': body},
        timeout=30
    )
    print(f'Issue 생성: #{r.json().get("number")} — {title}')


def main():
    now = datetime.now(KST)
    # 23:30 스케줄이 지연돼 자정을 넘기고 실행되면 전날 기준으로 확인 (자정 직후엔 당일 포스팅이 거의 없어 오탐 발생)
    target = now if now.hour >= 4 else now - timedelta(days=1)
    today = target.strftime('%Y-%m-%d')

    if not os.path.exists(CONTENT_LOG):
        create_issue(
            f'⚠️ 포스팅 시스템 이상: content_log.json 없음 ({today})',
            '로그 파일이 없음. 포스팅 시스템 전체 상태 확인 필요.'
        )
        return

    with open(CONTENT_LOG, encoding='utf-8-sig') as f:
        logs = json.load(f)

    today_posts = [p for p in logs if p.get('date', '') == today]
    count = len(today_posts)

    if count < EXPECTED_MIN:
        titles = '\n'.join(
            f"- {p.get('selected_title', p.get('format_variant', '제목없음'))[:50]}"
            for p in today_posts
        ) or '(없음)'
        repo = os.environ.get('GITHUB_REPOSITORY', '')
        create_issue(
            f'⚠️ 포스팅 공백 감지: {today} — {count}개 발행 (최소 {EXPECTED_MIN}개 기대)',
            f'**발행된 포스트 ({count}개):**\n{titles}\n\n'
            f'**예상 슬롯:** 07:30 법인뉴스 / 12:00 경제뉴스 / 21:00 보험뉴스 (+ 화목 14:00 증여상속)\n\n'
            f'**워크플로우 확인:** https://github.com/{repo}/actions'
        )
    else:
        print(f'{today}: {count}개 포스팅 확인 — 정상')


if __name__ == '__main__':
    main()
