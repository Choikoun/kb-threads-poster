"""
뉴스 헤드라인 카드 생성기
RSS에서 가져온 기사 제목을 시각적 카드로 만들어 Threads에 포스팅
"""
from PIL import Image, ImageDraw, ImageFont
import os, time, requests, textwrap
from dotenv import load_dotenv
load_dotenv()

SIZE = (1080, 1080)
COLORS = {
    "bg":      "#0A1628",
    "accent":  "#F5C842",
    "white":   "#FFFFFF",
    "gray":    "#8B9BB4",
    "news_bg": "#0F1F3D",
    "divider": "#1E3A5F",
}
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
THREADS_API_BASE = "https://graph.threads.net/v1.0"
CONSULTATION_LINK = "지금 내 상황이 궁금하다면 → bit.ly/44CqhMr"


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def load_font(weight="regular", size=40):
    paths = {
        "extrabold": os.path.join(FONT_DIR, "NanumGothicExtraBold.ttf"),
        "bold":      os.path.join(FONT_DIR, "NanumGothicBold.ttf"),
        "regular":   os.path.join(FONT_DIR, "NanumGothic.ttf"),
    }
    return ImageFont.truetype(paths.get(weight, paths["regular"]), size)


def wrap_text(text, font, max_width, draw):
    lines = []
    for paragraph in text.split("\n"):
        current = ""
        for char in paragraph:
            test = current + char
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] > max_width and current:
                lines.append(current)
                current = char
            else:
                current = test
        if current:
            lines.append(current)
    return lines


def create_news_card(source, headline, date, commentary):
    """
    뉴스 헤드라인 카드 생성
    source: "한국경제", "보험신보" 등
    headline: 기사 제목
    date: "2026.06.03"
    commentary: 한 줄 코멘트
    """
    img = Image.new("RGB", SIZE, hex_to_rgb(COLORS["bg"]))
    draw = ImageDraw.Draw(img)

    # 상단 골드 라인
    draw.rectangle([80, 80, 200, 86], fill=hex_to_rgb(COLORS["accent"]))

    # 뉴스 소스 뱃지
    f_source = load_font("bold", 28)
    source_text = f"📰  {source}"
    draw.text((80, 100), source_text, font=f_source, fill=hex_to_rgb(COLORS["accent"]))

    # 날짜
    f_date = load_font("regular", 26)
    draw.text((80, 140), date, font=f_date, fill=hex_to_rgb(COLORS["gray"]))

    # 구분선
    draw.rectangle([80, 185, SIZE[0]-80, 188], fill=hex_to_rgb(COLORS["divider"]))

    # 헤드라인
    f_headline = load_font("extrabold", 58)
    lines = wrap_text(headline, f_headline, SIZE[0] - 160, draw)
    y = 220
    for line in lines:
        draw.text((80, y), line, font=f_headline, fill=hex_to_rgb(COLORS["white"]))
        y += 72

    # 구분선2
    draw.rectangle([80, y + 30, SIZE[0]-80, y + 33], fill=hex_to_rgb(COLORS["divider"]))

    # 코멘트 — 길이에 맞게 폰트 크기 자동 조정
    comment_len = len(commentary)
    if comment_len <= 20:
        font_size, line_gap = 52, 65
    elif comment_len <= 40:
        font_size, line_gap = 44, 58
    elif comment_len <= 80:
        font_size, line_gap = 38, 52
    else:
        font_size, line_gap = 32, 46

    f_comment = load_font("bold", font_size)
    comment_lines = wrap_text(commentary, f_comment, SIZE[0] - 160, draw)
    cy = y + 60
    for line in comment_lines:
        draw.text((80, cy), line, font=f_comment, fill=hex_to_rgb(COLORS["accent"]))
        cy += line_gap

    # 하단 계정명
    f_account = load_font("bold", 28)
    draw.text((80, SIZE[1] - 80), "@financial_planner0", font=f_account,
              fill=hex_to_rgb(COLORS["gray"]))

    return img


def upload_to_imgbb(image_path):
    api_key = os.environ.get("IMGBB_API_KEY")
    import base64
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    resp = requests.post("https://api.imgbb.com/1/upload",
                         data={"key": api_key, "image": encoded})
    resp.raise_for_status()
    return resp.json()["data"]["url"]


def post_news_card(source, headline, date, commentary, caption, target="개인"):
    """뉴스 카드 생성 → 업로드 → Threads 포스팅"""
    token = os.environ.get("THREADS_ACCESS_TOKEN")
    user_id = requests.get(f"{THREADS_API_BASE}/me",
                           params={"access_token": token}).json().get("id")

    # 카드 생성
    card = create_news_card(source, headline, date, commentary)
    os.makedirs("news_cards", exist_ok=True)
    card_path = f"news_cards/news_{int(time.time())}.jpg"
    card.save(card_path, "JPEG", quality=95)
    print(f"카드 생성: {card_path}")

    # imgBB 업로드
    image_url = upload_to_imgbb(card_path)
    print(f"업로드 완료: {image_url}")

    # Threads 포스팅
    c = requests.post(f"{THREADS_API_BASE}/{user_id}/threads",
        params={"media_type": "IMAGE", "image_url": image_url,
                "text": caption, "access_token": token})
    c.raise_for_status()
    container_id = c.json().get("id")
    time.sleep(3)

    pub = requests.post(f"{THREADS_API_BASE}/{user_id}/threads_publish",
        params={"creation_id": container_id, "access_token": token})
    pub.raise_for_status()
    post_id = pub.json().get("id")
    print(f"게시 완료: {post_id}")

    # 첫 댓글
    time.sleep(3)
    cr = requests.post(f"{THREADS_API_BASE}/{user_id}/threads",
        params={"media_type": "TEXT", "text": CONSULTATION_LINK,
                "reply_to_id": post_id, "access_token": token})
    cid = cr.json().get("id")
    time.sleep(2)
    requests.post(f"{THREADS_API_BASE}/{user_id}/threads_publish",
        params={"creation_id": cid, "access_token": token})
    print("첫 댓글 완료")

    return post_id


# ── 테스트 ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")

    # 카드 미리보기 테스트
    card = create_news_card(
        source="한국경제",
        headline="삼성전자 시총 2000조 돌파, 글로벌 톱10",
        date="2026.06.03",
        commentary="수익 났을 때 세금 준비가 먼저야."
    )
    card.save("news_cards/test_card.jpg", "JPEG", quality=95)
    print("테스트 카드 생성 완료: news_cards/test_card.jpg")
