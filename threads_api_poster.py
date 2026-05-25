import json
import os
import time
import logging
import requests
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("poster_log.txt", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

QUEUE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "posts_queue.json")

# 시간대별 타겟 매핑 (KST 기준)
SCHEDULE = {
    0: "의사",
    6: "자산가",
    12: "사업주",
    18: "개인"
}

THREADS_API_BASE = "https://graph.threads.net/v1.0"


def get_env(key):
    val = os.environ.get(key)
    if not val:
        raise ValueError(f"환경변수 {key} 가 설정되지 않았어요.")
    return val


def load_queue():
    with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_queue(data):
    with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_next_post(target):
    data = load_queue()
    for post in data.get(target, []):
        if not post['posted']:
            return post
    return None


def mark_as_posted(target, post_id):
    data = load_queue()
    for post in data.get(target, []):
        if post['id'] == post_id:
            post['posted'] = True
            post['posted_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            break
    save_queue(data)


def post_to_threads(content, access_token, user_id):
    """Threads API로 포스팅"""

    # Step 1: 미디어 컨테이너 생성
    create_url = f"{THREADS_API_BASE}/{user_id}/threads"
    create_params = {
        "media_type": "TEXT",
        "text": content,
        "access_token": access_token
    }

    resp = requests.post(create_url, params=create_params)
    resp.raise_for_status()
    container_id = resp.json().get("id")

    if not container_id:
        raise Exception(f"컨테이너 생성 실패: {resp.text}")

    logger.info(f"컨테이너 생성 완료: {container_id}")

    # Step 2: 잠깐 대기 (API 권장)
    time.sleep(3)

    # Step 3: 게시
    publish_url = f"{THREADS_API_BASE}/{user_id}/threads/publish"
    publish_params = {
        "creation_id": container_id,
        "access_token": access_token
    }

    resp = requests.post(publish_url, params=publish_params)
    resp.raise_for_status()
    post_id = resp.json().get("id")

    logger.info(f"게시 완료! post_id: {post_id}")
    return True


def get_threads_user_id(access_token):
    url = f"{THREADS_API_BASE}/me"
    resp = requests.get(url, params={"access_token": access_token})
    resp.raise_for_status()
    return resp.json().get("id")


def get_current_target():
    """현재 KST 시간에 맞는 타겟 반환"""
    # GitHub Actions는 UTC 기준이므로 UTC+9 변환
    utc_hour = datetime.utcnow().hour
    kst_hour = (utc_hour + 9) % 24

    # 가장 가까운 스케줄 매핑
    for hour, target in SCHEDULE.items():
        if kst_hour == hour:
            return target

    # 환경변수로 직접 지정 가능
    return os.environ.get("TARGET", None)


if __name__ == "__main__":
    access_token = get_env("THREADS_ACCESS_TOKEN")

    # 타겟 결정 (환경변수 우선)
    target = os.environ.get("TARGET") or get_current_target()

    if not target:
        logger.error("타겟을 결정할 수 없어요. TARGET 환경변수를 설정하거나 정해진 시간에 실행해주세요.")
        exit(1)

    logger.info(f"타겟: {target}")

    # 유저 ID 조회
    user_id = get_threads_user_id(access_token)
    logger.info(f"Threads 유저 ID: {user_id}")

    # 다음 포스트 가져오기
    post = get_next_post(target)
    if not post:
        logger.warning(f"[{target}] 큐에 남은 포스트가 없어요. posts_queue.json에 내용을 추가해주세요.")
        exit(0)

    logger.info(f"[{target}] 내용: {post['content'][:50]}...")

    try:
        success = post_to_threads(post['content'], access_token, user_id)
        if success:
            mark_as_posted(target, post['id'])
            logger.info(f"[{target}] ID {post['id']} 게시 완료!")
    except Exception as e:
        logger.error(f"[{target}] 게시 실패: {e}")
        exit(1)
