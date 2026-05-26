import json
import os
import time
import argparse
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

THREADS_API_BASE = "https://graph.threads.net/v1.0"
REPLIED_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "replied_comments.json")


def get_env(key):
    val = os.environ.get(key)
    if not val:
        raise ValueError(f"환경변수 {key} 가 설정되지 않았어요. .env 파일을 확인해주세요.")
    return val


def get_threads_user_id(access_token):
    url = f"{THREADS_API_BASE}/me"
    resp = requests.get(url, params={"access_token": access_token})
    resp.raise_for_status()
    return resp.json().get("id")


def post_reply(comment_id, text, access_token, user_id):
    """특정 댓글에 답글 달기"""

    # Step 1: 미디어 컨테이너 생성 (reply_to_id 포함)
    create_url = f"{THREADS_API_BASE}/{user_id}/threads"
    create_params = {
        "media_type": "TEXT",
        "text": text,
        "reply_to_id": comment_id,
        "access_token": access_token
    }

    resp = requests.post(create_url, params=create_params)
    resp.raise_for_status()
    container_id = resp.json().get("id")

    if not container_id:
        raise Exception(f"컨테이너 생성 실패: {resp.text}")

    print(f"컨테이너 생성 완료: {container_id}")

    # Step 2: 잠깐 대기
    time.sleep(3)

    # Step 3: 게시
    publish_url = f"{THREADS_API_BASE}/{user_id}/threads_publish"
    publish_params = {
        "creation_id": container_id,
        "access_token": access_token
    }

    resp = requests.post(publish_url, params=publish_params)
    resp.raise_for_status()
    reply_post_id = resp.json().get("id")

    print(f"답글 게시 완료! reply_post_id: {reply_post_id}")
    return reply_post_id


def mark_as_replied(comment_id, reply_text, reply_post_id):
    """replied_comments.json에 답글 완료 기록"""
    if os.path.exists(REPLIED_FILE):
        with open(REPLIED_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {"replied_ids": [], "history": []}

    if comment_id not in data["replied_ids"]:
        data["replied_ids"].append(comment_id)

    data["history"].append({
        "comment_id": comment_id,
        "reply_text": reply_text,
        "reply_post_id": reply_post_id,
        "replied_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    with open(REPLIED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Threads 댓글에 답글 달기")
    parser.add_argument("--comment_id", required=True, help="답글을 달 댓글의 ID")
    parser.add_argument("--text", required=True, help="답글 내용")
    args = parser.parse_args()

    access_token = get_env("THREADS_ACCESS_TOKEN")
    user_id = get_threads_user_id(access_token)

    print(f"\n댓글 ID: {args.comment_id}")
    print(f"답글 내용: {args.text}")
    print()

    try:
        reply_post_id = post_reply(args.comment_id, args.text, access_token, user_id)
        mark_as_replied(args.comment_id, args.text, reply_post_id)
        print(f"\n✅ 답글 완료! replied_comments.json에 기록됐어.")
    except Exception as e:
        print(f"\n❌ 답글 실패: {e}")
        raise


if __name__ == "__main__":
    main()
