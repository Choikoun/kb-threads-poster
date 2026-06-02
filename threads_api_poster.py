import json
import os
import time
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

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

# 시간대별 타겟 매핑 (KST 기준) — 2시간 간격, 08:00~22:00
SCHEDULE = {
    8:  "의사",
    10: "자산가",
    12: "사업주",
    14: "개인",
    16: "의사",
    18: "자산가",
    20: "사업주",
    22: "개인"
}

THREADS_API_BASE = "https://graph.threads.net/v1.0"

# 첫 댓글에 달릴 상담 링크
CONSULTATION_LINK = "상담 신청 → https://bit.ly/44CqhMr"

# 타겟별 토픽 태그 (Threads 알고리즘 노출 강화)
TARGET_TAGS = {
    "의사": "#절세",
    "자산가": "#상속세",
    "사업주": "#법인",
    "개인": "#연금"
}


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
        if not post['posted'] and post.get('approved', False):
            return post
    return None


def mark_as_posted(target, post_id, threads_post_id=None):
    data = load_queue()
    for post in data.get(target, []):
        if post['id'] == post_id:
            post['posted'] = True
            post['posted_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if threads_post_id:
                post['threads_post_id'] = threads_post_id  # 댓글 조회용 ID 저장
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
    publish_url = f"{THREADS_API_BASE}/{user_id}/threads_publish"
    publish_params = {
        "creation_id": container_id,
        "access_token": access_token
    }

    resp = requests.post(publish_url, params=publish_params)
    if not resp.ok:
        logger.error(f"게시 API 응답: {resp.status_code} - {resp.text}")
    resp.raise_for_status()
    post_id = resp.json().get("id")

    logger.info(f"게시 완료! post_id: {post_id}")
    return post_id


def post_reply(post_id, text, access_token, user_id):
    """게시물에 첫 댓글 달기"""
    # Step 1: 댓글 컨테이너 생성
    create_url = f"{THREADS_API_BASE}/{user_id}/threads"
    create_params = {
        "media_type": "TEXT",
        "text": text,
        "reply_to_id": post_id,
        "access_token": access_token
    }

    resp = requests.post(create_url, params=create_params)
    if not resp.ok:
        logger.warning(f"댓글 컨테이너 생성 실패: {resp.status_code} - {resp.text}")
        return None
    container_id = resp.json().get("id")

    time.sleep(2)

    # Step 2: 댓글 게시
    publish_url = f"{THREADS_API_BASE}/{user_id}/threads_publish"
    publish_params = {
        "creation_id": container_id,
        "access_token": access_token
    }

    resp = requests.post(publish_url, params=publish_params)
    if not resp.ok:
        logger.warning(f"댓글 게시 실패: {resp.status_code} - {resp.text}")
        return None

    reply_id = resp.json().get("id")
    logger.info(f"첫 댓글 게시 완료: {reply_id}")
    return reply_id


def get_threads_user_id(access_token):
    url = f"{THREADS_API_BASE}/me"
    resp = requests.get(url, params={"access_token": access_token})
    resp.raise_for_status()
    return resp.json().get("id")


def get_current_target():
    """현재 KST 시간에 맞는 타겟 반환 (GitHub Actions 크론 지연 허용)"""
    # GitHub Actions는 UTC 기준이므로 UTC+9 변환
    utc_hour = datetime.utcnow().hour
    kst_hour = (utc_hour + 9) % 24

    logger.info(f"현재 KST 시각: {kst_hour}시")

    # 정확히 매칭되면 바로 반환
    if kst_hour in SCHEDULE:
        return SCHEDULE[kst_hour]

    # GitHub Actions 크론 지연 대응: 최대 1시간 이전 스케줄까지 허용
    # 스케줄 간격이 2시간이므로 1시간 내에서 찾으면 안전하게 매칭 가능
    for offset in range(1, 2):
        past_hour = (kst_hour - offset) % 24
        if past_hour in SCHEDULE:
            logger.info(f"크론 지연 감지 — {offset}시간 전 스케줄({past_hour}시) 기준으로 실행")
            return SCHEDULE[past_hour]

    return None


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

    # ── 이중 발행 방지: 포스팅 직전 큐를 다시 읽어 중복 체크 ──
    fresh_data = load_queue()
    fresh_post = next((p for p in fresh_data.get(target, []) if p['id'] == post['id']), None)
    if not fresh_post or fresh_post.get('posted'):
        logger.warning(f"[{target}] ID {post['id']} 이미 발행됨 (다른 프로세스에서 처리). 건너뜀.")
        exit(0)

    try:
        # 토픽 태그 추가 (타겟별 1개)
        tag = TARGET_TAGS.get(target, "")
        content_with_tag = f"{post['content']}\n\n{tag}" if tag else post['content']

        threads_post_id = post_to_threads(content_with_tag, access_token, user_id)
        if threads_post_id:
            mark_as_posted(target, post['id'], threads_post_id)
            logger.info(f"[{target}] ID {post['id']} 게시 완료! 태그: {tag} (threads_post_id: {threads_post_id})")

            # 첫 댓글에 상담 링크 달기 (알고리즘 노출 보호)
            time.sleep(3)
            post_reply(threads_post_id, CONSULTATION_LINK, access_token, user_id)

    except Exception as e:
        logger.error(f"[{target}] 게시 실패: {e}")
        exit(1)
