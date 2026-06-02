"""
매일 트렌드 수집 후 일일 브리핑 생성
content_trends.md → daily_briefing.md (보기 좋은 요약본)
"""
import os, re
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

def generate_briefing():
    trends_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content_trends.md")
    briefing_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "daily_briefing.md")

    if not os.path.exists(trends_path):
        return

    with open(trends_path, encoding="utf-8") as f:
        content = f.read()

    # 기사 파싱
    articles = re.findall(r'- \*\*\[(.+?)\]\*\* \[(.+?)\]\((.+?)\)', content)

    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")

    # 섹션별 분류
    insurance = [(s,t,l) for s,t,l in articles if s in ['보험신보']]
    domestic = [(s,t,l) for s,t,l in articles if s in ['한국경제','매일경제','조선비즈','연합뉴스경제','뉴시스경제']]
    global_news = [(s,t,l) for s,t,l in articles if s in ['한국경제국제','매일경제국제','조선비즈국제','인베스팅닷컴']]
    stock = [(s,t,l) for s,t,l in articles if s in ['매일경제증권']]
    policy = [(s,t,l) for s,t,l in articles if '정책' in s or '기재부' in s]

    lines = [
        f"# 📰 일일 브리핑",
        f"*{now}*",
        f"",
        f"---",
    ]

    if insurance:
        lines += [f"\n## 🔖 보험 동향"]
        for s, t, l in insurance[:5]:
            lines.append(f"- [{t}]({l})")

    if domestic:
        lines += [f"\n## 💰 국내 경제·금융"]
        for s, t, l in domestic[:5]:
            lines.append(f"- [{t}]({l})")

    if stock:
        lines += [f"\n## 📈 주식·시장"]
        for s, t, l in stock[:5]:
            lines.append(f"- [{t}]({l})")

    if global_news:
        lines += [f"\n## 🌏 글로벌 경제·정세"]
        for s, t, l in global_news[:5]:
            lines.append(f"- [{t}]({l})")

    if policy:
        lines += [f"\n## 🏛️ 정부·정책"]
        for s, t, l in policy[:5]:
            lines.append(f"- [{t}]({l})")

    lines += [
        f"\n---",
        f"*총 {len(articles)}개 기사 수집됨*"
    ]

    with open(briefing_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"브리핑 생성 완료: {len(articles)}개 기사 → {briefing_path}")


if __name__ == "__main__":
    generate_briefing()
