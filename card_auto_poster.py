"""
카드뉴스 자동 포스터 — cards_queue.json에서 미발행 카드셋을 꺼내 Threads에 게시
"""
import json
import os
import sys
import logging
from datetime import datetime
from card_poster import post_card_set

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("card_poster_log.txt", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

QUEUE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cards_queue.json")


def load_queue():
    with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_queue(data):
    with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_next_card(target=None):
    """미발행 카드셋 가져오기. target 지정 시 해당 타겟 우선."""
    data = load_queue()
    # 타겟 지정된 경우 먼저 탐색
    if target:
        for card in data:
            if card['target'] == target and not card['posted']:
                return card
    # 타겟 미지정이면 순서대로 첫 미발행 반환
    for card in data:
        if not card['posted']:
            return card
    return None


def mark_as_posted(card_id, threads_post_id):
    data = load_queue()
    for card in data:
        if card['id'] == card_id:
            card['posted'] = True
            card['posted_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            card['threads_post_id'] = threads_post_id
            break
    save_queue(data)


def queue_status():
    """큐 현황 출력"""
    data = load_queue()
    total = len(data)
    posted = sum(1 for c in data if c['posted'])
    logger.info(f"카드뉴스 큐 현황: 전체 {total}개 / 발행완료 {posted}개 / 대기중 {total - posted}개")
    for card in data:
        status = "✓" if card['posted'] else "○"
        logger.info(f"  [{status}] ID {card['id']} ({card['target']}): {card['card_data']['hook_big'][:20].replace(chr(10), ' ')}...")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    # 타겟 환경변수 (선택적)
    target = os.environ.get("CARD_TARGET")

    queue_status()

    card = get_next_card(target)
    if not card:
        logger.warning("큐에 남은 카드뉴스가 없어요. cards_queue.json에 내용을 추가해주세요.")
        sys.exit(0)

    logger.info(f"발행 대상: ID {card['id']} ({card['target']}) — {card['card_data']['hook_big'][:30].replace(chr(10), ' ')}")

    output_dir = f"cards_output/card_set_{card['id']:03d}"

    try:
        post_id = post_card_set(
            card_data=card['card_data'],
            caption=card['caption'],
            output_dir=output_dir
        )
        mark_as_posted(card['id'], post_id)
        logger.info(f"✓ 카드뉴스 발행 완료! ID {card['id']} ({card['target']}) → threads_post_id: {post_id}")
    except Exception as e:
        logger.error(f"✗ 카드뉴스 발행 실패: {e}")
        sys.exit(1)
