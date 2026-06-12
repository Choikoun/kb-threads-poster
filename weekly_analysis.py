"""
주간 조회수 분석 — 매주 상위 포스팅 확인 + 재발행 후보 추적
"""
import sys, os, json, time, requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

BASE = "https://graph.threads.net/v1.0"
REBLOG_FILE = "reblog_candidates.json"
CONTENT_LOG_FILE = "content_log.json"
KST = timezone(timedelta(hours=9))


def load_content_log():
    if os.path.exists(CONTENT_LOG_FILE):
        with open(CONTENT_LOG_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []


def get_insights(post_id, token):
    resp = requests.get(f"{BASE}/{post_id}/insights",
                        params={"metric": "views,likes,replies,reposts", "access_token": token}, timeout=15)
    if not resp.ok:
        return {}
    data = {d["name"]: d["values"][0]["value"] for d in resp.json().get("data", []) if d.get("values")}
    return data


def load_reblog():
    if os.path.exists(REBLOG_FILE):
        with open(REBLOG_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_reblog(data):
    with open(REBLOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def repost_text(text, token, user_id):
    """텍스트만 새 포스트로 재발행 (이미지/댓글 없음)"""
    r1 = requests.post(f"{BASE}/{user_id}/threads",
                        params={"media_type": "TEXT", "text": text, "access_token": token}, timeout=30)
    creation_id = r1.json().get("id")
    if not creation_id:
        return None
    time.sleep(4)
    r2 = requests.post(f"{BASE}/{user_id}/threads_publish",
                        params={"creation_id": creation_id, "access_token": token}, timeout=30)
    return r2.json().get("id")


def run_analysis():
    token = os.environ.get("THREADS_ACCESS_TOKEN")
    user_id = requests.get(f"{BASE}/me", params={"access_token": token}, timeout=15).json().get("id")

    resp = requests.get(f"{BASE}/{user_id}/threads",
                        params={"fields": "id,text,timestamp,media_type", "limit": 50, "access_token": token}, timeout=15)
    posts = resp.json().get("data", [])

    results = []
    for post in posts:
        metrics = get_insights(post["id"], token)
        views = metrics.get("views", 0)
        likes = metrics.get("likes", 0)
        replies = metrics.get("replies", 0)
        full_text = post.get("text", "")
        text = full_text[:40].replace("\n", " ")
        ts = post.get("timestamp", "")[:10]
        results.append({"id": post["id"], "date": ts, "text": text, "full_text": full_text,
                        "views": views, "likes": likes, "replies": replies,
                        "media_type": post.get("media_type", "TEXT")})

    results.sort(key=lambda x: x["views"], reverse=True)

    print(f"\n{'='*60}")
    print(f"📊 주간 조회수 분석 — {datetime.now(KST).strftime('%Y-%m-%d')}")
    print(f"{'='*60}")
    print(f"\n🏆 TOP 10 포스팅")
    for i, r in enumerate(results[:10], 1):
        media = "📸" if r["media_type"] == "CAROUSEL_ALBUM" else "📝"
        print(f"{i:2}. {media} [{r['date']}] 조회 {r['views']:,} | 좋아요 {r['likes']} | 댓글 {r['replies']}")
        print(f"    {r['text']}...")

    # 포맷별 성과 분석 (content_log.json 매칭)
    content_log = load_content_log()
    results_by_id = {r["id"]: r for r in results}
    groups = {}
    for entry in content_log:
        r = results_by_id.get(entry.get("post_id"))
        if not r:
            continue
        key = (entry.get("category", "?"), entry.get("format_variant", "?"))
        groups.setdefault(key, []).append(r)

    if groups:
        print(f"\n🧪 포맷별 성과 (카테고리 / 포맷 / 건수 / 평균조회 / 평균좋아요)")
        for (category, variant), items in sorted(groups.items()):
            avg_views = sum(i["views"] for i in items) / len(items)
            avg_likes = sum(i["likes"] for i in items) / len(items)
            print(f"  {category} / {variant}: {len(items)}건, 평균조회 {avg_views:,.0f}, 평균좋아요 {avg_likes:,.1f}")

    # 재발행 후보 (조회수 300 이상)
    reblog = load_reblog()
    existing_ids = {r["id"] for r in reblog}
    new_candidates = []
    for r in results:
        if r["views"] >= 300 and r["id"] not in existing_ids:
            reblog_date = (datetime.now(KST) + timedelta(weeks=8)).strftime("%Y-%m-%d")
            r["reblog_date"] = reblog_date
            reblog.append(r)
            new_candidates.append(r)

    if new_candidates:
        save_reblog(reblog)
        print(f"\n📌 재발행 후보 {len(new_candidates)}개 추가됨")
        for r in new_candidates:
            print(f"  → [{r['reblog_date']}] {r['text']}... (조회 {r['views']:,})")

    # 재발행 시기 된 것들 → 실제 재발행 수행
    today = datetime.now(KST).strftime("%Y-%m-%d")
    due = [r for r in reblog if r.get("reblog_date", "") <= today and not r.get("reposted")]
    if due:
        print(f"\n🔄 재발행 시기 된 포스팅 {len(due)}개:")
        for r in due:
            full_text = r.get("full_text")
            if not full_text:
                print(f"  → {r['text']}... (원본 조회 {r['views']:,}) — full_text 없어서 재발행 건너뜀")
                continue
            new_id = repost_text(full_text, token, user_id)
            if new_id:
                r["reposted"] = True
                r["reposted_id"] = new_id
                r["reposted_date"] = today
                print(f"  ✅ 재발행 완료 (새 ID {new_id}): {r['text']}... (원본 조회 {r['views']:,})")
            else:
                print(f"  ❌ 재발행 실패: {r['text']}...")
            time.sleep(3)
        save_reblog(reblog)
    else:
        print(f"\n🔄 재발행 시기 된 포스팅 없음")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    run_analysis()
