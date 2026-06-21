#!/usr/bin/env python3
"""
외부 댓글 → 새 포스트 초안 자동 생성
최근 외부 댓글 중 질문형/흥미로운 것을 골라 새 포스팅 초안을 Gemini로 만든다.
결과는 post_drafts.json에 저장 + GitHub Issue 생성 (사용자가 직접 검토 후 포스팅)
"""
import os, sys, json, re, time, requests
sys.stdout.reconfigure(encoding='utf-8')
from google import genai
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.environ['THREADS_ACCESS_TOKEN']
GEMINI_KEY = os.environ['GEMINI_API_KEY']
BASE = 'https://graph.threads.net/v1.0'
SELF = 'financial_planner0'
DRAFTS_FILE = 'post_drafts.json'
MAX_POSTS = 30   # 최근 포스트 수
MAX_DEPTH = 4    # 답글 탐색 깊이


def api_get(url, params, retries=2):
    for attempt in range(retries + 1):
        try:
            return requests.get(url, params=params, timeout=30).json()
        except requests.exceptions.RequestException:
            if attempt == retries:
                raise
            time.sleep(2)


def get_replies(comment_id):
    data = api_get(f'{BASE}/{comment_id}/replies',
        {'fields': 'id,text,username,timestamp', 'access_token': TOKEN})
    return data.get('data', [])


def collect_external(comment, depth=0):
    if depth >= MAX_DEPTH:
        return [comment]
    own = [c for c in get_replies(comment['id']) if c.get('username') == SELF]
    if not own:
        return [comment]
    result = []
    for o in own:
        for gc in get_replies(o['id']):
            if gc.get('username') != SELF:
                result.extend(collect_external(gc, depth + 1))
    return result


def is_interesting(text):
    """질문형이거나 설계 관련 키워드가 있는 댓글 필터"""
    if not text or len(text.strip()) < 10:
        return False
    question_marks = '?' in text or '？' in text
    keywords = ['증여', '상속', '법인', '가지급금', '절세', '퇴직금', '배우자',
                '자녀', '부동산', '연금', '차용', '공제', '어떻게', '어떤',
                '왜', '언제', '뭐가', '차이', '방법', '맞나요', '맞나',
                '되나요', '되나', '가능']
    has_keyword = any(k in text for k in keywords)
    return question_marks or has_keyword


DRAFT_PROMPT = """너는 한국 Threads에서 활동하는 증여·상속 구조 설계 전문가야.
세무사·법무사가 아니야. "도구보다 목적과 구조가 먼저"가 이 계정의 각도야.

아래 댓글이 독자가 실제로 남긴 질문/반응이야:
---
원본 포스트 일부: {post_preview}
댓글 내용: {comment_text}
---

이 댓글에서 영감을 받아 새로운 포스팅 초안을 작성해줘.
댓글에 직접 답하는 게 아니라, 댓글이 건드린 주제를 더 넓은 시각으로 풀어내는 새 글이야.

[핵심 원칙]
- 전부 반말
- 완전한 답 주지 말 것. 경각심·인사이트를 건드리되 "상황마다 달라", "구조가 먼저야"처럼 열어두어 독자 스스로 상담 욕구가 생기도록.
- 상담/DM/링크 유도 절대 금지. 화두만 던지고 끝낸다.
- 특정 종목·자산의 매수/매도/매매 타이밍을 지시하거나 추천하지 않는다 (미등록 투자자문 리스크). 구조적 인식까지만 다루고 투자행동 지시는 하지 않는다.
- 훅을 첫 줄에 — 반전 사례, 펀치라인, 경각심 중 하나로 시작
- 메인 포스트: 6~10줄. 짧고 강하게. 한 줄 15~25자 수준.
- 마지막에 빈 줄 하나 + `#증여 #상속`

[포맷]
반전형 또는 감정인용형 중 더 자연스러운 것으로.

[댓글 2개]
- 댓글1: 추가 맥락 2~3줄 (반말)
- 댓글2: 양자택일형 질문 2줄 (반말, 예: "A야, B야?")

JSON만 출력:
{{
  "main": "메인 포스트\n\n#증여 #상속",
  "comments": ["댓글1", "댓글2"],
  "draft_title": "이 초안을 한 줄로 요약하면 (내부 라벨용, 독자에게 안 보임)"
}}"""


def generate_draft(post_preview, comment_text):
    client = genai.Client(api_key=GEMINI_KEY)
    prompt = DRAFT_PROMPT.format(
        post_preview=post_preview[:80],
        comment_text=comment_text[:200]
    )
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


def load_existing_drafts():
    if os.path.exists(DRAFTS_FILE):
        try:
            with open(DRAFTS_FILE, encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_drafts(drafts):
    with open(DRAFTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(drafts, f, ensure_ascii=False, indent=2)


def create_github_issue(drafts_added):
    gh_token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    repo = os.environ.get('GITHUB_REPOSITORY', 'Choikoun/kb-threads-poster')
    if not gh_token or not drafts_added:
        return
    body_parts = [f'## 댓글 기반 포스팅 초안 ({len(drafts_added)}개)\n',
                  '`post_drafts.json`에 저장됨. 마음에 드는 초안 번호를 댓글로 남기거나 직접 수정 후 포스팅.\n']
    for i, d in enumerate(drafts_added, 1):
        body_parts.append(f'### 초안 {i}: {d.get("draft_title", "")}')
        body_parts.append(f'**원본 댓글:** {d["source_comment"][:80]}')
        body_parts.append(f'\n**메인 글:**\n```\n{d["draft"]["main"]}\n```')
        body_parts.append(f'**댓글1:** {d["draft"]["comments"][0] if d["draft"].get("comments") else ""}')
        body_parts.append(f'**댓글2:** {d["draft"]["comments"][1] if len(d["draft"].get("comments", [])) > 1 else ""}\n---')
    body = '\n'.join(body_parts)
    from datetime import datetime
    title_date = datetime.now().strftime('%Y-%m-%d')
    headers = {'Authorization': f'token {gh_token}', 'Accept': 'application/vnd.github+json'}
    requests.post(
        f'https://api.github.com/repos/{repo}/issues',
        headers=headers,
        json={'title': f'📝 포스팅 초안 ({title_date})', 'body': body, 'labels': ['draft']},
        timeout=30
    )


def main():
    user_id = api_get(f'{BASE}/me', {'access_token': TOKEN}).get('id')
    resp = api_get(f'{BASE}/{user_id}/threads',
        {'fields': 'id,text,timestamp', 'limit': MAX_POSTS, 'access_token': TOKEN})
    posts = resp.get('data', [])

    existing_drafts = load_existing_drafts()
    existing_comment_ids = {d['source_comment_id'] for d in existing_drafts}

    candidates = []
    for post in posts:
        pid = post['id']
        post_text = post.get('text', '')
        ext_top = [r for r in get_replies(pid) if r.get('username') != SELF]
        for e in ext_top:
            for c in collect_external(e):
                cid = c.get('id')
                ctext = c.get('text', '')
                if cid not in existing_comment_ids and is_interesting(ctext):
                    candidates.append({
                        'comment_id': cid,
                        'comment_text': ctext,
                        'post_preview': post_text[:80],
                        'timestamp': c.get('timestamp', ''),
                    })

    if not candidates:
        print('초안 생성할 댓글 없음.')
        return

    # 최대 3개만 처리
    candidates = candidates[:3]
    print(f'초안 생성 대상 댓글: {len(candidates)}개')

    new_drafts = []
    for cand in candidates:
        print(f'생성 중: {cand["comment_text"][:50]}...')
        draft = generate_draft(cand['post_preview'], cand['comment_text'])
        if draft:
            entry = {
                'source_comment_id': cand['comment_id'],
                'source_comment': cand['comment_text'],
                'source_post_preview': cand['post_preview'],
                'created_at': cand['timestamp'],
                'draft': draft,
                'draft_title': draft.get('draft_title', ''),
                'status': 'pending',
            }
            new_drafts.append(entry)
            print(f'  → "{draft.get("draft_title", "")}" 초안 생성')

    if new_drafts:
        all_drafts = existing_drafts + new_drafts
        save_drafts(all_drafts)
        print(f'{len(new_drafts)}개 초안 저장 완료')
        create_github_issue(new_drafts)
    else:
        print('생성된 초안 없음.')


if __name__ == '__main__':
    main()
