"""
타래 포스터 — 메인 글 + 연속 댓글로 이어가는 Thread Chain 발행
"""
import os, time, logging, requests
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

BASE = "https://graph.threads.net/v1.0"
TARGET_TAGS = {"의사": "#절세", "자산가": "#상속세", "사업주": "#법인", "개인": "#연금"}


def get_user_id(token):
    return requests.get(f"{BASE}/me", params={"access_token": token}).json().get("id")


def post_text(user_id, text, token, reply_to_id=None):
    params = {"media_type": "TEXT", "text": text, "access_token": token}
    if reply_to_id:
        params["reply_to_id"] = reply_to_id
    resp = requests.post(f"{BASE}/{user_id}/threads", params=params)
    resp.raise_for_status()
    container_id = resp.json().get("id")
    time.sleep(3)
    pub = requests.post(f"{BASE}/{user_id}/threads_publish",
                        params={"creation_id": container_id, "access_token": token})
    pub.raise_for_status()
    return pub.json().get("id")


def post_thread_chain(chain_data, target="개인"):
    """
    chain_data = {
        "main": "첫 번째 글",
        "replies": ["두 번째 글", "세 번째 글", ...]
    }
    """
    token = os.environ.get("THREADS_ACCESS_TOKEN")
    user_id = get_user_id(token)
    tag = TARGET_TAGS.get(target, "")

    # 메인 글
    main_text = chain_data["main"] + (f"\n\n{tag}" if tag else "")
    main_id = post_text(user_id, main_text, token)
    logger.info(f"메인 글 발행: {main_id}")

    # 연속 댓글
    prev_id = main_id
    for i, reply in enumerate(chain_data.get("replies", []), 1):
        time.sleep(5)
        reply_id = post_text(user_id, reply, token, reply_to_id=prev_id)
        logger.info(f"댓글 {i} 발행: {reply_id}")
        prev_id = reply_id

    # 마지막에 상담 링크
    time.sleep(5)
    post_text(user_id, "상담 신청 → https://bit.ly/44CqhMr", token, reply_to_id=main_id)
    logger.info("상담 링크 댓글 완료")

    return main_id


# ── 샘플 타래 데이터 ──────────────────────────────────────
SAMPLE_CHAIN = {
    "main": "법인 슈퍼카 세무조사, 핵심만 정리해줄게.\n\n오늘부터 3편으로 나눠서 올릴게.\n1편 → 비용처리 한도\n2편 → 걸리는 패턴\n3편 → 지금 해야 할 것",
    "replies": [
        "1편. 비용처리 한도.\n\n감가상각비는 연 800만원이야.\n3억짜리 슈퍼카도 매년 800만원씩만 비용 처리돼.\n전액 인정되는 게 아니야.\n\n2편으로 이어서 →",
        "2편. 걸리는 패턴.\n\n주말 가족 나들이,\n골프장 방문,\n유흥업소.\n\n이런 기록이 있으면 그 부분은 사적 사용이야.\n운행일지에 목적, 장소, 참석자 없으면 다 사적으로 봐.\n\n3편으로 이어서 →",
        "3편. 지금 해야 할 것.\n\n운행일지 작성 시작해.\n날짜, 출발지, 목적지, 사용 목적.\n이게 없으면 세무조사에서 답이 없어.\n\n국세청 지금 정조준하고 있어."
    ]
}


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print("타래 포스팅 시작...")
    post_id = post_thread_chain(SAMPLE_CHAIN, target="사업주")
    print(f"완료! main post_id: {post_id}")
