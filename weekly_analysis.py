"""
주간 조회수 분석 — 매주 상위 포스팅 확인 + 재발행 후보 추적 + Gemini 전략 인사이트
"""
import sys, os, json, re, time, requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from google import genai
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

BASE = "https://graph.threads.net/v1.0"
REBLOG_FILE = "reblog_candidates.json"
CONTENT_LOG_FILE = "content_log.json"
FOLLOWER_HISTORY_FILE = "follower_history.json"
KST = timezone(timedelta(hours=9))


def load_content_log():
    if os.path.exists(CONTENT_LOG_FILE):
        with open(CONTENT_LOG_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []


def get_followers_count(user_id, token):
    resp = requests.get(f"{BASE}/{user_id}/threads_insights",
                        params={"metric": "followers_count", "access_token": token}, timeout=15)
    if not resp.ok:
        return None
    data = resp.json().get("data", [])
    if not data:
        return None
    return data[0].get("total_value", {}).get("value")


def log_follower_count(count):
    history = []
    if os.path.exists(FOLLOWER_HISTORY_FILE):
        with open(FOLLOWER_HISTORY_FILE, encoding="utf-8") as f:
            history = json.load(f)
    today = datetime.now(KST).strftime("%Y-%m-%d")
    if history and history[-1]["date"] == today:
        history[-1]["followers"] = count
    else:
        history.append({"date": today, "followers": count})
    with open(FOLLOWER_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    return history


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

    # 팔로워 수 추적
    followers = get_followers_count(user_id, token)
    if followers is not None:
        history = log_follower_count(followers)
        print(f"\n👥 팔로워: {followers:,}명")
        if len(history) >= 2:
            prev = history[-2]
            diff = followers - prev["followers"]
            sign = "+" if diff >= 0 else ""
            print(f"   ({prev['date']} 대비 {sign}{diff}명)")

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

    format_weights = {}
    if groups:
        print(f"\n🧪 포맷별 성과 (카테고리 / 포맷 / 건수 / 평균조회 / 평균좋아요)")
        for (category, variant), items in sorted(groups.items()):
            avg_views = sum(i["views"] for i in items) / len(items)
            avg_likes = sum(i["likes"] for i in items) / len(items)
            print(f"  {category} / {variant}: {len(items)}건, 평균조회 {avg_views:,.0f}, 평균좋아요 {avg_likes:,.1f}")
            format_weights.setdefault(category, {})[variant] = round(avg_views, 1)
        with open('format_weights.json', 'w', encoding='utf-8') as f:
            json.dump(format_weights, f, ensure_ascii=False, indent=2)
        print(f"  → format_weights.json 업데이트 완료")

    # content_log.json에 인게이지먼트 데이터 반영
    insights_map = {r['id']: r for r in results}
    updated = False
    for entry in content_log:
        pid = entry.get('post_id')
        if pid and pid in insights_map:
            r = insights_map[pid]
            if entry.get('views') != r['views'] or 'likes' not in entry:
                entry['views'] = r['views']
                entry['likes'] = r.get('likes', 0)
                entry['replies'] = r.get('replies', 0)
                updated = True
    if updated:
        with open(CONTENT_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(content_log, f, ensure_ascii=False, indent=2)
        print(f'  → content_log.json 인게이지먼트 데이터 갱신')

    # 인게이지먼트 심층 분석
    qualified = [r for r in results if r['views'] >= 100]
    if qualified:
        print(f'\n💡 인게이지먼트 심층 분석')
        like_rated = sorted(qualified, key=lambda r: r['likes'] / r['views'], reverse=True)
        print(f'\n  👍 좋아요율 TOP 5 (좋아요/조회수):')
        for r in like_rated[:5]:
            rate = r['likes'] / r['views'] * 100
            print(f'  {rate:.1f}% | 조회 {r["views"]:,} | 좋아요 {r["likes"]} | {r["text"][:30]}...')
        reply_rated = sorted(qualified, key=lambda r: r['replies'] / r['views'], reverse=True)
        print(f'\n  💬 댓글율 TOP 5 (댓글/조회수):')
        for r in reply_rated[:5]:
            rate = r['replies'] / r['views'] * 100
            print(f'  {rate:.2f}% | 조회 {r["views"]:,} | 댓글 {r["replies"]} | {r["text"][:30]}...')

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

    # 인기글 후속 자동 생성·발행
    gemini_key = os.environ.get('GEMINI_API_KEY')
    if gemini_key and results:
        avg_views = sum(r["views"] for r in results) / len(results) if results else 0
        hot = [r for r in results if r["views"] >= max(avg_views * 3, 500) and r.get("full_text")]
        if hot:
            top = hot[0]
            print(f"\n🔥 인기글 후속 자동 생성: 조회 {top['views']:,} | {top['text']}...")
            try:
                client = genai.Client(api_key=gemini_key)
                followup_prompt = f"""너는 증여·상속 구조 설계 전문가 Threads 계정이야.
아래 글이 이번 주 조회수 {top['views']:,}회로 크게 반응이 왔어.

[원본 글]
{top['full_text'][:300]}

이 글과 연결되지만 다른 각도의 후속 글을 써줘.
- 원본 글의 주제/훅을 반복하지 않음
- 원본이 건드린 경각심을 한 단계 더 깊이 파고들거나 반대 시나리오를 보여줌
- 전부 반말, 메인 6~10줄
- 댓글 2개 (마지막은 양자택일형)

JSON만 출력:
{{"main": "...", "comments": ["댓글1", "댓글2"]}}"""
                resp = client.models.generate_content(model='gemini-2.5-flash', contents=followup_prompt)
                m = re.search(r'\{[\s\S]*\}', resp.text.strip())
                if m:
                    content = json.loads(m.group())
                    print(f"\n후속 글:\n{content['main']}\n")
                    new_id = repost_text(content['main'], token, user_id)
                    if new_id:
                        for c in content.get('comments', []):
                            rc = requests.post(f"{BASE}/{user_id}/threads",
                                               params={"media_type": "TEXT", "text": c, "reply_to_id": new_id, "access_token": token}, timeout=30)
                            time.sleep(3)
                            requests.post(f"{BASE}/{user_id}/threads_publish",
                                          params={"creation_id": rc.json().get("id"), "access_token": token}, timeout=30)
                            time.sleep(2)
                        print(f"  ✅ 후속 글 발행 완료: {new_id}")
            except Exception as e:
                print(f"후속 글 생성 실패: {e}")
        else:
            print(f"\n🔥 후속 자동화 기준 미달 (평균 조회 {avg_views:,.0f}회, 기준 {max(avg_views*3,500):,.0f}회)")

    # Gemini 전략 인사이트
    gemini_key = os.environ.get('GEMINI_API_KEY')
    if gemini_key and results:
        try:
            top5 = results[:5]
            summary = '\n'.join([
                f"{i+1}. [{r['date']}] 조회 {r['views']:,} | 좋아요 {r['likes']} | 댓글 {r['replies']}\n   \"{r['text']}...\""
                for i, r in enumerate(top5)
            ])
            prompt = f"""너는 증여·상속 구조 설계 전문가 Threads 계정의 콘텐츠 전략가야.
이번 주 TOP 5 포스팅 성과 데이터:

{summary}

이 데이터를 보고 다음 주 콘텐츠 전략을 3가지 제안해줘.
각 제안은:
- 어떤 각도/주제로 쓸지
- 왜 이번 성과 데이터에서 그 판단이 나왔는지
- 구체적인 첫 줄(훅) 예시 1개

전부 반말. 200자 이내로 간결하게."""
            client = genai.Client(api_key=gemini_key)
            resp = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            print(f"\n🤖 다음 주 콘텐츠 전략 (Gemini 인사이트)")
            print(f"{'-'*60}")
            print(resp.text.strip())
        except Exception as e:
            print(f'\nGemini 인사이트 생성 실패: {e}')

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    run_analysis()
