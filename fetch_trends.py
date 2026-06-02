"""
매일 실행: 금융/세금/보험 관련 최신 뉴스를 수집해서 content_trends.md에 저장
"""
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import re
import os

KST = timezone(timedelta(hours=9))

# 관련 키워드 필터
KEYWORDS = [
    "상속세", "증여세", "종합소득세", "성실신고", "금융소득종합과세",
    "법인세", "보험", "연금", "절세", "세금", "의사", "개원",
    "법인전환", "가족법인", "배당", "ISA", "IRP", "변액",
    "부동산세", "양도세", "세법개정", "세제개편"
]

# 국무회의 관련 키워드 (별도 섹션으로 표시)
CABINET_KEYWORDS = [
    "국무회의", "대통령", "정부안", "입법예고", "시행령",
    "세법", "금융위", "기재부", "복지부", "고용부",
    "의료", "보험료", "연금개혁", "부동산정책", "규제"
]

# 무료 RSS 피드
RSS_FEEDS = [
    ("한국경제", "https://www.hankyung.com/feed/finance"),
    ("매일경제", "https://www.mk.co.kr/rss/30000001/"),
    ("조선비즈", "https://biz.chosun.com/arc/outboundfeeds/rss/?outputType=xml"),
    ("머니투데이", "https://news.mt.co.kr/mtview.php?type=1&pv=rss"),
    ("보험신보", "https://www.insnews.co.kr/rss/allArticle.xml"),
    ("연합뉴스경제", "https://www.yna.co.kr/rss/economy.xml"),
]

# 정책 뉴스 RSS (국무회의 전용)
POLICY_FEEDS = [
    ("정책브리핑", "https://www.korea.kr/rss/allPolicy.do"),
    ("기획재정부", "https://www.moef.go.kr/nw/nes/rssList.do"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def fetch_rss(name, url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        items = []
        for item in root.iter("item"):
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            pub_date = item.findtext("pubDate", "").strip()
            if title and any(kw in title for kw in KEYWORDS):
                items.append((title, link, pub_date))
        return items[:5]  # 소스당 최대 5개
    except Exception as e:
        print(f"[{name}] RSS 오류: {e}")
        return []


def fetch_policy_rss(name, url):
    """정책 RSS 수집 — 국무회의·정부 안건 전용"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        items = []
        for item in root.iter("item"):
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            pub_date = item.findtext("pubDate", "").strip()
            if title and any(kw in title for kw in CABINET_KEYWORDS + KEYWORDS):
                items.append((title, link, pub_date))
        return items[:5]
    except Exception as e:
        print(f"[{name}] 정책 RSS 오류: {e}")
        return []


def save_trends(all_items, cabinet_items):
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content_trends.md")
    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")

    lines = [
        f"# 최신 트렌드 & 이슈",
        f"*자동 수집: {now}*",
        f"",
        f"콘텐츠 생성 시 아래 이슈를 참고해서 반영해줘.",
        f"",
    ]

    # 국무회의·정부 정책 섹션 (최우선)
    if cabinet_items:
        lines.append("## 🏛️ 국무회의·정부 정책 (콘텐츠 우선 반영)")
        for source, title, link, _ in cabinet_items:
            lines.append(f"- **[{source}]** [{title}]({link})")
        lines.append("")

    # 일반 금융 뉴스
    lines.append("## 📰 금융·세금 트렌드")
    if not all_items:
        lines.append("*오늘 수집된 관련 뉴스 없음*")
    else:
        for source, title, link, _ in all_items:
            lines.append(f"- **[{source}]** [{title}]({link})")

    lines += [
        "",
        "---",
        "## 항상 반영할 주요 정책 (2026 기준)",
        "- 상속세 자녀공제 현행 1인당 5천만원 유지 (5억 개편안 미통과)",
        "- 고배당 기업 배당소득 분리과세 시행 (2026년 1월~)",
        "- 금융소득종합과세 기준 2천만원 유지",
        "- ISA 납입한도 연 4천만원, 비과세 한도 500만원 (서민형 1천만원)",
    ]

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"저장 완료: {output_path} (일반 {len(all_items)}개 / 정책 {len(cabinet_items)}개)")


def main():
    all_items = []
    for name, url in RSS_FEEDS:
        items = fetch_rss(name, url)
        for title, link, pub_date in items:
            all_items.append((name, title, link, pub_date))
        print(f"[{name}] {len(items)}개 수집")

    # 정책·국무회의 뉴스 별도 수집
    cabinet_items = []
    for name, url in POLICY_FEEDS:
        items = fetch_policy_rss(name, url)
        for title, link, pub_date in items:
            cabinet_items.append((name, title, link, pub_date))
        print(f"[{name}] 정책 {len(items)}개 수집")

    save_trends(all_items, cabinet_items)


if __name__ == "__main__":
    main()
