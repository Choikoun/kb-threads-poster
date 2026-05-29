"""
카드뉴스 Threads 카루셀 포스터
흐름: 카드 생성 → imgBB 업로드 → Threads 카루셀 포스팅
"""
import os
import time
import logging
import requests
from dotenv import load_dotenv
from card_generator import generate_card_set, upload_to_imgbb

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("card_poster_log.txt", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

THREADS_API_BASE = "https://graph.threads.net/v1.0"
CONSULTATION_LINK = "상담 신청 → naver.me/FRLbSbiJ"


def get_env(key):
    val = os.environ.get(key)
    if not val:
        raise ValueError(f"환경변수 {key} 가 설정되지 않았어요.")
    return val


def get_threads_user_id(access_token):
    url = f"{THREADS_API_BASE}/me"
    resp = requests.get(url, params={"access_token": access_token})
    resp.raise_for_status()
    return resp.json().get("id")


def create_carousel_item(user_id, image_url, access_token):
    """카루셀 아이템 컨테이너 생성"""
    url = f"{THREADS_API_BASE}/{user_id}/threads"
    params = {
        "media_type": "IMAGE",
        "image_url": image_url,
        "is_carousel_item": "true",
        "access_token": access_token
    }
    resp = requests.post(url, params=params)
    if not resp.ok:
        logger.error(f"카루셀 아이템 생성 실패: {resp.status_code} - {resp.text}")
    resp.raise_for_status()
    item_id = resp.json().get("id")
    logger.info(f"  카루셀 아이템 생성: {item_id}")
    return item_id


def create_carousel_container(user_id, children_ids, caption, access_token):
    """카루셀 부모 컨테이너 생성"""
    url = f"{THREADS_API_BASE}/{user_id}/threads"
    params = {
        "media_type": "CAROUSEL",
        "children": ",".join(children_ids),
        "text": caption,
        "access_token": access_token
    }
    resp = requests.post(url, params=params)
    if not resp.ok:
        logger.error(f"카루셀 컨테이너 생성 실패: {resp.status_code} - {resp.text}")
    resp.raise_for_status()
    container_id = resp.json().get("id")
    logger.info(f"카루셀 컨테이너 생성: {container_id}")
    return container_id


def publish_carousel(user_id, container_id, access_token):
    """카루셀 게시"""
    url = f"{THREADS_API_BASE}/{user_id}/threads_publish"
    params = {
        "creation_id": container_id,
        "access_token": access_token
    }
    resp = requests.post(url, params=params)
    if not resp.ok:
        logger.error(f"카루셀 게시 실패: {resp.status_code} - {resp.text}")
    resp.raise_for_status()
    post_id = resp.json().get("id")
    logger.info(f"카루셀 게시 완료! post_id: {post_id}")
    return post_id


def post_card_set(card_data, caption, output_dir="cards_output"):
    """
    카드뉴스 전체 파이프라인:
    1. 카드 이미지 생성
    2. imgBB 업로드
    3. Threads 카루셀 포스팅

    Args:
        card_data: generate_card_set에 전달할 카드 데이터 딕셔너리
        caption: 포스팅 본문 텍스트 (카루셀 설명)
        output_dir: 이미지 저장 폴더

    Returns:
        Threads post_id (문자열)
    """
    access_token = get_env("THREADS_ACCESS_TOKEN")
    user_id = get_threads_user_id(access_token)
    logger.info(f"Threads 유저 ID: {user_id}")

    # 1. 카드 이미지 생성
    logger.info("카드 이미지 생성 중...")
    image_paths = generate_card_set(card_data, output_dir=output_dir)
    logger.info(f"  {len(image_paths)}장 생성 완료")

    # 2. imgBB 업로드 → 공개 URL 수집
    logger.info("imgBB 업로드 중...")
    image_urls = []
    for path in image_paths:
        url = upload_to_imgbb(path)
        image_urls.append(url)
        logger.info(f"  업로드 완료: {os.path.basename(path)} → {url}")
        time.sleep(0.5)  # 과부하 방지

    # 3. Threads 카루셀 아이템 컨테이너 생성
    logger.info("Threads 카루셀 아이템 컨테이너 생성 중...")
    children_ids = []
    for url in image_urls:
        item_id = create_carousel_item(user_id, url, access_token)
        children_ids.append(item_id)
        time.sleep(1)  # API 권장 대기

    # 4. 카루셀 부모 컨테이너 생성
    logger.info("카루셀 부모 컨테이너 생성 중...")
    container_id = create_carousel_container(user_id, children_ids, caption, access_token)

    # 5. 잠깐 대기 후 게시 (Threads API 권장)
    logger.info("게시 전 대기 (5초)...")
    time.sleep(5)

    # 6. 게시
    logger.info("카루셀 게시 중...")
    post_id = publish_carousel(user_id, container_id, access_token)

    # 7. 첫 댓글에 상담 링크 달기 (알고리즘 노출 보호)
    logger.info("첫 댓글 달기...")
    time.sleep(3)
    _post_reply(user_id, post_id, CONSULTATION_LINK, access_token)

    return post_id


def _post_reply(user_id, post_id, text, access_token):
    """게시물에 첫 댓글 달기"""
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
        return
    container_id = resp.json().get("id")
    time.sleep(2)

    publish_url = f"{THREADS_API_BASE}/{user_id}/threads_publish"
    resp = requests.post(publish_url, params={"creation_id": container_id, "access_token": access_token})
    if resp.ok:
        logger.info(f"첫 댓글 게시 완료: {resp.json().get('id')}")
    else:
        logger.warning(f"댓글 게시 실패: {resp.status_code} - {resp.text}")


# ── 샘플 카드 데이터 및 캡션 ──────────────────────────────
SAMPLE_CARD_DATA = {
    "tag": "# 상속세 핵심",
    "hook_big": "자산이 많을수록\n세금도 많다?",
    "hook_sub": "반만 맞아. 구조가 없으면 그래.",
    "points": [
        {
            "title": "현금이 없으면 못 낸다",
            "body": "상속세는 6개월 안에\n현금으로 납부해야 해.\n부동산만 있으면\n급매로 팔아야 하는 상황이 생겨."
        },
        {
            "title": "10년 합산이 함정이다",
            "body": "사망 전 10년 이내 증여는\n상속세 계산에 다시 합산돼.\n미리 넘겼다고 안심하면 안 돼."
        },
        {
            "title": "재원은 미리 만드는 것",
            "body": "자산 팔아서 세금 내는 게 아니야.\n살아있을 때\n납부 재원을 따로 설계해두는 거야."
        },
    ],
    "closing": "모르면 그냥 내는 거고,\n알면 구조를 만드는 거야.",
    "cta": "지금 내 상황이 궁금하신가요?"
}

SAMPLE_CAPTION = """상속세, 세율보다 '납부 재원'이 먼저야.

자산가들이 제일 많이 실수하는 게 이거야.
세금 얼마 나오는지만 따지다가
막상 납부할 현금이 없는 상황.

구조를 먼저 만들어야 해.

↓ 카드 넘겨봐"""


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")

    print("카드뉴스 Threads 카루셀 포스팅 시작...")
    try:
        post_id = post_card_set(
            card_data=SAMPLE_CARD_DATA,
            caption=SAMPLE_CAPTION,
            output_dir="cards_sample"
        )
        print(f"\n✓ 포스팅 완료! Threads post_id: {post_id}")
    except Exception as e:
        print(f"\n✗ 오류 발생: {e}")
        raise
