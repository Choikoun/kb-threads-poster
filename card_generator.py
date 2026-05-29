"""
카드뉴스 생성기 — 텍스트 기반 Threads 카루셀
"""
from PIL import Image, ImageDraw, ImageFont
import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

# ── 디자인 설정 ──────────────────────────────────────────
SIZE = (1080, 1080)

COLORS = {
    "bg":        "#0A1628",   # 다크 네이비 배경
    "bg_card":   "#0F1F3D",   # 카드 내부 배경 (약간 밝게)
    "accent":    "#F5C842",   # 골드 포인트
    "white":     "#FFFFFF",
    "gray":      "#8B9BB4",   # 보조 텍스트
    "divider":   "#1E3A5F",   # 구분선
}

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

def load_font(weight="regular", size=40):
    paths = {
        "extrabold": os.path.join(FONT_DIR, "NanumGothicExtraBold.ttf"),
        "bold":      os.path.join(FONT_DIR, "NanumGothicBold.ttf"),
        "regular":   os.path.join(FONT_DIR, "NanumGothic.ttf"),
    }
    return ImageFont.truetype(paths.get(weight, paths["regular"]), size)


def hex_to_rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def wrap_text(text, font, max_width, draw):
    """텍스트 자동 줄바꿈"""
    lines = []
    for paragraph in text.split("\n"):
        words = list(paragraph)  # 한국어는 글자 단위
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


def draw_rounded_rect(draw, xy, radius, fill):
    x1, y1, x2, y2 = xy
    fill_rgb = hex_to_rgb(fill)
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill_rgb)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill_rgb)
    draw.ellipse([x1, y1, x1 + 2*radius, y1 + 2*radius], fill=fill_rgb)
    draw.ellipse([x2 - 2*radius, y1, x2, y1 + 2*radius], fill=fill_rgb)
    draw.ellipse([x1, y2 - 2*radius, x1 + 2*radius, y2], fill=fill_rgb)
    draw.ellipse([x2 - 2*radius, y2 - 2*radius, x2, y2], fill=fill_rgb)


def make_card_1_hook(title_big, title_sub, tag=""):
    """카드 1: 훅 — 큰 제목 중앙"""
    img = Image.new("RGB", SIZE, hex_to_rgb(COLORS["bg"]))
    draw = ImageDraw.Draw(img)

    # 상단 포인트 라인
    draw.rectangle([80, 80, 200, 86], fill=hex_to_rgb(COLORS["accent"]))

    # 태그 (선택)
    if tag:
        f_tag = load_font("bold", 28)
        draw.text((80, 100), tag, font=f_tag, fill=hex_to_rgb(COLORS["accent"]))

    # 메인 텍스트
    f_big = load_font("extrabold", 80)
    lines = wrap_text(title_big, f_big, SIZE[0] - 160, draw)
    y = 280
    for line in lines:
        draw.text((80, y), line, font=f_big, fill=hex_to_rgb(COLORS["white"]))
        y += 95

    # 구분선
    draw.rectangle([80, y + 20, 200, y + 26], fill=hex_to_rgb(COLORS["accent"]))

    # 서브 텍스트
    f_sub = load_font("regular", 40)
    sub_lines = wrap_text(title_sub, f_sub, SIZE[0] - 160, draw)
    y = y + 50
    for line in sub_lines:
        draw.text((80, y), line, font=f_sub, fill=hex_to_rgb(COLORS["gray"]))
        y += 52

    # 하단 계정명
    f_account = load_font("bold", 28)
    draw.text((80, SIZE[1] - 80), "@financial_planner0", font=f_account,
              fill=hex_to_rgb(COLORS["gray"]))

    return img


def make_card_point(number, point_title, point_body):
    """카드 2~4: 포인트 카드"""
    img = Image.new("RGB", SIZE, hex_to_rgb(COLORS["bg"]))
    draw = ImageDraw.Draw(img)

    # 번호 배지
    f_num = load_font("extrabold", 100)
    draw.text((80, 80), f"0{number}", font=f_num, fill=hex_to_rgb(COLORS["accent"]))

    # 포인트 제목
    f_title = load_font("extrabold", 62)
    title_lines = wrap_text(point_title, f_title, SIZE[0] - 160, draw)
    y = 240
    for line in title_lines:
        draw.text((80, y), line, font=f_title, fill=hex_to_rgb(COLORS["white"]))
        y += 75

    # 구분선
    draw.rectangle([80, y + 16, 340, y + 22], fill=hex_to_rgb(COLORS["divider"]))

    # 본문
    f_body = load_font("regular", 40)
    body_lines = wrap_text(point_body, f_body, SIZE[0] - 160, draw)
    y = y + 52
    for line in body_lines:
        draw.text((80, y), line, font=f_body, fill=hex_to_rgb(COLORS["gray"]))
        y += 54

    # 하단 계정명
    f_account = load_font("bold", 28)
    draw.text((80, SIZE[1] - 80), "@financial_planner0", font=f_account,
              fill=hex_to_rgb(COLORS["gray"]))

    return img


def make_card_last(closing_line, cta="더 알고 싶으신가요?"):
    """마지막 카드: 마무리 + CTA"""
    img = Image.new("RGB", SIZE, hex_to_rgb(COLORS["accent"]))
    draw = ImageDraw.Draw(img)

    # 배경 포인트 사각형
    draw.rectangle([0, 0, SIZE[0], SIZE[1]], fill=hex_to_rgb(COLORS["bg"]))
    draw.rectangle([0, SIZE[1]-200, SIZE[0], SIZE[1]], fill=hex_to_rgb(COLORS["accent"]))

    # 마무리 문장
    f_close = load_font("extrabold", 58)
    close_lines = wrap_text(closing_line, f_close, SIZE[0] - 160, draw)
    y = 340
    for line in close_lines:
        draw.text((80, y), line, font=f_close, fill=hex_to_rgb(COLORS["white"]))
        y += 72

    # CTA
    f_cta = load_font("bold", 36)
    draw.text((80, SIZE[1] - 160), cta, font=f_cta, fill=hex_to_rgb(COLORS["bg"]))

    # 계정명
    f_account = load_font("extrabold", 32)
    draw.text((80, SIZE[1] - 100), "@financial_planner0", font=f_account,
              fill=hex_to_rgb(COLORS["bg"]))

    return img


def generate_card_set(card_data, output_dir="cards_output"):
    """카드셋 전체 생성
    card_data = {
        "hook_big": "...",
        "hook_sub": "...",
        "tag": "...",
        "points": [
            {"title": "...", "body": "..."},
            ...
        ],
        "closing": "...",
        "cta": "..."
    }
    """
    os.makedirs(output_dir, exist_ok=True)
    paths = []

    # 카드 1 (훅)
    card1 = make_card_1_hook(
        card_data["hook_big"],
        card_data["hook_sub"],
        card_data.get("tag", "")
    )
    p1 = os.path.join(output_dir, "card_01.jpg")
    card1.save(p1, "JPEG", quality=95)
    paths.append(p1)

    # 카드 2~ (포인트)
    for i, pt in enumerate(card_data["points"], start=1):
        card = make_card_point(i, pt["title"], pt["body"])
        p = os.path.join(output_dir, f"card_0{i+1}.jpg")
        card.save(p, "JPEG", quality=95)
        paths.append(p)

    # 마지막 카드
    card_last = make_card_last(
        card_data["closing"],
        card_data.get("cta", "더 알고 싶으신가요?")
    )
    p_last = os.path.join(output_dir, f"card_0{len(card_data['points'])+2}.jpg")
    card_last.save(p_last, "JPEG", quality=95)
    paths.append(p_last)

    return paths


def upload_to_imgbb(image_path):
    """imgBB에 이미지 업로드 후 공개 URL 반환"""
    api_key = os.environ.get("IMGBB_API_KEY")
    if not api_key:
        raise ValueError("IMGBB_API_KEY 환경변수가 없어요.")

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    resp = requests.post(
        "https://api.imgbb.com/1/upload",
        data={"key": api_key, "image": encoded}
    )
    resp.raise_for_status()
    return resp.json()["data"]["url"]


# ── 테스트용 샘플 데이터 ──────────────────────────────────
SAMPLE = {
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


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print("샘플 카드 생성 중...")
    paths = generate_card_set(SAMPLE, output_dir="cards_sample")
    print(f"생성 완료: {len(paths)}장")
    for p in paths:
        print(f"  → {p}")
