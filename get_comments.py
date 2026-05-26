import json
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

THREADS_API_BASE = "https://graph.threads.net/v1.0"
QUEUE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "posts_queue.json")
COMMENTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "comments_pending.json")
REPLIED_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "replied_comments.json")


def get_env(key):
    val = os.environ.get(key)
    if not val:
        raise ValueError(f"환경변수 {key} 가 설정되지 않았어요. .env 파일을 확인해주세요.")
    return val


def load_replied():
    if not os.path.exists(REPLIED_FILE):
        return set()
    with open(REPLIED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return set(data.get("replied_ids", []))


def get_posted_items():
    """posts_queue.json에서 threads_post_id가 있는 게시된 포스트들을 반환"""
    with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    posted = []
    for target, posts in data.items():
        for post in posts:
            if post.get("posted") and post.get("threads_post_id"):
                posted.append({
                    "target": target,
                    "queue_id": post["id"],
                    "threads_post_id": post["threads_post_id"],
                    "content_preview": post["content"][:50] + "...",
                    "posted_at": post.get("posted_at", "")
                })
    return posted


def fetch_replies(threads_post_id, access_token):
    """특정 게시물의 댓글(1단계 답글) 가져오기"""
    url = f"{THREADS_API_BASE}/{threads_post_id}/replies"
    params = {
        "fields": "id,text,username,timestamp",
        "access_token": access_token
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json().get("data", [])


def main():
    access_token = get_env("THREADS_ACCESS_TOKEN")
    replied_ids = load_replied()

    posted_items = get_posted_items()
    if not posted_items:
        print("아직 threads_post_id가 저장된 게시물이 없어요.")
        print("새 토큰으로 게시한 포스트부터 댓글 추적이 시작됩니다.")
        return

    all_new_comments = []

    print(f"\n{'='*60}")
    print(f"댓글 조회 시작 — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    for item in posted_items:
        post_id = item["threads_post_id"]
        print(f"[{item['target']}] {item['content_preview']}")
        print(f"  threads_post_id: {post_id}")

        try:
            replies = fetch_replies(post_id, access_token)
        except Exception as e:
            print(f"  ⚠️  댓글 조회 실패: {e}\n")
            continue

        new_replies = [r for r in replies if r["id"] not in replied_ids]

        if not new_replies:
            print(f"  새 댓글 없음\n")
            continue

        print(f"  새 댓글 {len(new_replies)}개:")
        for reply in new_replies:
            print(f"    @{reply.get('username', '?')} [{reply['id']}]")
            print(f"    \"{reply.get('text', '')}\"")
            print()
            all_new_comments.append({
                "comment_id": reply["id"],
                "username": reply.get("username", ""),
                "text": reply.get("text", ""),
                "timestamp": reply.get("timestamp", ""),
                "parent_post_id": post_id,
                "parent_target": item["target"],
                "parent_preview": item["content_preview"],
                "suggested_reply": ""  # 여기에 답글 초안을 채워서 사용
            })

    # comments_pending.json 저장
    with open(COMMENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_new_comments, f, ensure_ascii=False, indent=2)

    total = len(all_new_comments)
    if total > 0:
        print(f"{'='*60}")
        print(f"총 {total}개의 새 댓글이 comments_pending.json에 저장됐어요.")
        print(f"Claude에게 공유하면 답글 초안을 작성해줄 거야.")
        print(f"{'='*60}\n")
    else:
        print(f"\n새 댓글이 없어요. 나중에 다시 확인해봐.\n")


if __name__ == "__main__":
    main()
