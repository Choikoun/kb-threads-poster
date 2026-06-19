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
        with open(CONTENT_LOG_FILE, encoding="utf-8-sig") as f:
            return json.load(f)
    return []


def get_follower_demographics(user_id, token):
    """팔로워 100명 이상일 때 국가·나이·성별 분포 반환"""
    result = {}
    for breakdown in ['country', 'age', 'gender']:
        resp = requests.get(f"{BASE}/{user_id}/threads_insights",
                            params={"metric": "follower_demographics",
                                    "breakdown": breakdown,
                                    "access_token": token}, timeout=15)
        if not resp.ok:
            continue
        data = resp.json().get("data", [])
        if not data:
            continue
        breakdown_data = data[0].get("total_value", {}).get("breakdowns", [])
        if not breakdown_data:
            continue
        results_list = breakdown_data[0].get("results", [])
        result[breakdown] = sorted(results_list, key=lambda x: x.get("value", 0), reverse=True)
    return result


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


def remix_text(original_text, gemini_key):
    """원본 글을 새 훅으로 리믹스 — 같은 인사이트, 다른 각도"""
    try:
        client = genai.Client(api_key=gemini_key)
        prompt = f"""너는 증여·상속 구조 설계 전문가 Threads 계정이야.
아래 글이 2달 전에 반응이 좋았어.
같은 핵심 인사이트를 유지하면서, 완전히 다른 첫 줄(훅)과 다른 표현으로 리믹스해줘.

[원본]
{original_text[:500]}

[조건]
- 전부 반말
- 메인 6~10줄
- 원본 첫 줄과 전혀 다른 방식으로 시작 (반전/사례/숫자/경각심 중 택1)
- 원본의 핵심 메시지는 유지하되 예시나 표현은 바꿔
- 해시태그는 원본 마지막 줄 그대로 유지
- 상담/DM 유도 절대 금지

메인 포스트 텍스트만 출력. JSON 없이."""
        resp = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return resp.text.strip()
    except Exception as e:
        print(f'  리믹스 생성 실패: {e}')
        return None


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

    # 팔로워 추이 (최근 14일)
    if os.path.exists(FOLLOWER_HISTORY_FILE):
        with open(FOLLOWER_HISTORY_FILE, encoding='utf-8') as f:
            fh = json.load(f)
        if len(fh) >= 2:
            recent = fh[-14:]
            print(f"\n📈 팔로워 추이 (최근 {len(recent)}일)")
            for i, entry in enumerate(recent):
                bar_diff = ""
                if i > 0:
                    diff = entry['followers'] - recent[i-1]['followers']
                    bar_diff = f"  (+{diff})" if diff > 0 else f"  ({diff})" if diff < 0 else "  (=)"
                print(f"  {entry['date']}: {entry['followers']:,}명{bar_diff}")
            total_diff = recent[-1]['followers'] - recent[0]['followers']
            sign = "+" if total_diff >= 0 else ""
            print(f"  → 기간 합계: {sign}{total_diff}명")

    # 팔로워 데모그래픽 (100명 이상일 때만)
    if followers and followers >= 100:
        demo = get_follower_demographics(user_id, token)
        if demo:
            print(f"\n🌍 팔로워 데모그래픽")
            if 'country' in demo:
                top_countries = demo['country'][:5]
                print(f"  국가: " + " | ".join(f"{d.get('dimension_values',['?'])[0]} {d.get('value',0)}명" for d in top_countries))
            if 'age' in demo:
                print(f"  나이: " + " | ".join(f"{d.get('dimension_values',['?'])[0]}대 {d.get('value',0)}명" for d in demo['age']))
            if 'gender' in demo:
                label = {'M': '남성', 'F': '여성', 'U': '미확인'}
                print(f"  성별: " + " | ".join(f"{label.get(d.get('dimension_values',['?'])[0], d.get('dimension_values',['?'])[0])} {d.get('value',0)}명" for d in demo['gender']))

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

    # 소스별 성과 분석
    source_groups = {}
    for entry in content_log:
        src = entry.get('source', '')
        if not src:
            continue
        r = results_by_id.get(entry.get('post_id'))
        if not r:
            continue
        source_groups.setdefault(src, []).append(r['views'])
    if source_groups:
        print(f'\n📰 뉴스 소스별 평균 조회수')
        source_avgs = {s: sum(v) / len(v) for s, v in source_groups.items()}
        for src, avg in sorted(source_avgs.items(), key=lambda x: -x[1]):
            count = len(source_groups[src])
            bar = '█' * min(int(avg / 500), 15)
            print(f'  {src}: 평균 {avg:,.0f} ({count}건) {bar}')
        source_weights = {s: round(avg, 1) for s, avg in source_avgs.items()}
        source_weights['updated'] = datetime.now(KST).strftime('%Y-%m-%d')
        with open('source_weights.json', 'w', encoding='utf-8') as f:
            json.dump(source_weights, f, ensure_ascii=False, indent=2)
        max_avg = max(source_avgs.values())
        low_sources = [s for s, v in source_avgs.items() if v < max_avg * 0.6]
        if low_sources:
            print(f'  → 저성과 소스: {", ".join(low_sources)} (다음 포스팅 프롬프트에 자동 반영)')
        print(f'  → source_weights.json 저장')

    # 포스팅 길이별 성과 분석
    length_groups = {}
    for entry in content_log:
        lc = entry.get('line_count', 0)
        if not lc:
            continue
        r = results_by_id.get(entry.get('post_id'))
        if not r:
            continue
        bucket = f'{lc}줄' if lc <= 9 else '10줄+'
        length_groups.setdefault(bucket, []).append(r['views'])
    if len(length_groups) >= 2:
        print(f'\n📏 포스팅 길이별 평균 조회수 (해시태그 제외 기준)')
        length_avgs = {b: sum(v) / len(v) for b, v in length_groups.items()}
        for bucket, avg in sorted(length_avgs.items(), key=lambda x: -x[1]):
            count_b = len(length_groups[bucket])
            bar = '█' * min(int(avg / 500), 15)
            print(f'  {bucket}: 평균 {avg:,.0f} ({count_b}건) {bar}')
        best_len = max(length_avgs, key=lambda b: length_avgs[b])
        print(f'  → 최적 길이: {best_len}')

    # 시간대별 성과 분석
    hour_groups = {}
    for entry in content_log:
        hour = entry.get('hour')
        if hour is None:
            continue
        r = results_by_id.get(entry.get('post_id'))
        if not r:
            continue
        hour_groups.setdefault(hour, []).append(r['views'])

    if len(hour_groups) >= 3:
        print(f'\n⏰ 시간대별 평균 조회수 (KST)')
        sorted_hours = sorted(hour_groups.keys())
        for h in sorted_hours:
            views = hour_groups[h]
            avg = sum(views) / len(views)
            bar = '█' * min(int(avg / 500), 20)
            print(f'  {h:02d}:00 | 평균 {avg:,.0f} ({len(views)}건) {bar}')
        best_hour = max(hour_groups, key=lambda h: sum(hour_groups[h]) / len(hour_groups[h]))
        worst_hour = min(hour_groups, key=lambda h: sum(hour_groups[h]) / len(hour_groups[h]))
        print(f'  → 최고 시간대: {best_hour:02d}:00 KST | 최저: {worst_hour:02d}:00 KST')

    # 팔로워 급증일 ↔ 포스팅 상관관계
    if os.path.exists(FOLLOWER_HISTORY_FILE):
        with open(FOLLOWER_HISTORY_FILE, encoding='utf-8') as f:
            fh_data = json.load(f)
        growth_days = {}
        for i in range(1, len(fh_data)):
            diff = fh_data[i]['followers'] - fh_data[i - 1]['followers']
            if diff >= 5:
                growth_days[fh_data[i]['date']] = diff
        if growth_days and content_log:
            log_by_date = {}
            for entry in content_log:
                d = entry.get('date')
                if d:
                    log_by_date.setdefault(d, []).append(entry)
            matched = [(date, gain, log_by_date[date])
                       for date, gain in sorted(growth_days.items(), key=lambda x: -x[1])
                       if date in log_by_date]
            if matched:
                print(f'\n🔗 팔로워 급증일 포스팅 상관관계 (+5명 이상)')
                for date, gain, posts in matched[:5]:
                    print(f'  [{date}] +{gain}명 증가')
                    for p in posts:
                        r = results_by_id.get(p.get('post_id'), {})
                        views = r.get('views', p.get('views'))
                        v_str = f'조회 {views:,}' if isinstance(views, int) else '조회 ?'
                        title = (p.get('selected_title') or p.get('category', '?'))[:30]
                        print(f'    └ {title} | {v_str} | {p.get("format_variant", "?")}')

    # 팔로워 이탈일 포스팅 상관관계
    if os.path.exists(FOLLOWER_HISTORY_FILE):
        with open(FOLLOWER_HISTORY_FILE, encoding='utf-8') as f:
            fh_fall = json.load(f)
        fall_days = {}
        for i in range(1, len(fh_fall)):
            diff = fh_fall[i]['followers'] - fh_fall[i - 1]['followers']
            if diff <= -2:
                fall_days[fh_fall[i]['date']] = diff
        if fall_days:
            log_by_date_f = {}
            for entry in content_log:
                d = entry.get('date')
                if d:
                    log_by_date_f.setdefault(d, []).append(entry)
            fall_matched = [(date, diff, log_by_date_f.get(date, []))
                            for date, diff in sorted(fall_days.items(), key=lambda x: x[1])]
            print(f'\n⚠️ 팔로워 이탈일 ({len(fall_days)}일, -2명 이상)')
            for date, diff, posts in fall_matched:
                print(f'  [{date}] {diff}명 감소')
                if posts:
                    for p in posts:
                        r = results_by_id.get(p.get('post_id'), {})
                        views = r.get('views', p.get('views'))
                        v_str = f'조회 {views:,}' if isinstance(views, int) else '조회 ?'
                        title = (p.get('selected_title') or p.get('category', '?'))[:30]
                        print(f'    └ {title} | {v_str} | {p.get("format_variant", "?")}')
                else:
                    print(f'    └ 포스팅 없음 (또는 content_log 미기록)')

    # 프로필 방문 추이 & 포스팅 상관관계 (상담 링크 유입 간접 측정)
    if os.path.exists(FOLLOWER_HISTORY_FILE):
        with open(FOLLOWER_HISTORY_FILE, encoding='utf-8') as f:
            fh_pv = json.load(f)
        pv_by_date = {e['date']: e['profile_views'] for e in fh_pv if e.get('profile_views') is not None}
        if pv_by_date:
            avg_pv = sum(pv_by_date.values()) / len(pv_by_date)
            print(f'\n👁️ 프로필 방문 추이 (상담 링크 유입 간접 지표, 평균 {avg_pv:.0f}회/일)')
            log_by_date_pv = {}
            for entry in content_log:
                d = entry.get('date')
                if d:
                    log_by_date_pv.setdefault(d, []).append(entry)
            for date, pv in sorted(pv_by_date.items())[-7:]:
                marker = '↑' if pv > avg_pv * 1.3 else ' '
                posts_on = log_by_date_pv.get(date, [])
                titles = ', '.join((p.get('selected_title') or p.get('category', '?'))[:18] for p in posts_on[:2])
                post_str = f' | {titles}' if titles else ''
                print(f'  {marker} [{date}] 방문 {pv}회{post_str}')
            high_pv = {d: v for d, v in pv_by_date.items() if v > avg_pv * 1.3}
            if high_pv:
                print(f'\n  📌 방문 급증일 상위 포스팅:')
                for date in sorted(high_pv, key=lambda d: -high_pv[d])[:3]:
                    posts = log_by_date_pv.get(date, [])
                    print(f'  [{date}] 방문 {high_pv[date]}회')
                    for p in posts:
                        title = (p.get('selected_title') or p.get('category', '?'))[:35]
                        print(f'    └ {title}')

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
        remix_key = os.environ.get('GEMINI_API_KEY')
        print(f"\n🔄 재발행 리믹스 {len(due)}개:")
        for r in due:
            full_text = r.get("full_text")
            if not full_text:
                print(f"  → {r['text']}... — full_text 없어서 건너뜀")
                continue
            post_text = full_text
            if remix_key:
                remixed = remix_text(full_text, remix_key)
                if remixed:
                    post_text = remixed
                    print(f"  리믹스 생성 완료")
                else:
                    print(f"  리믹스 실패 — 원본으로 재발행")
            new_id = repost_text(post_text, token, user_id)
            if new_id:
                r["reposted"] = True
                r["reposted_id"] = new_id
                r["reposted_date"] = today
                r["remixed"] = bool(remix_key and remixed)
                print(f"  ✅ {'리믹스' if r['remixed'] else '원본'} 재발행 완료 ({new_id}): {r['text']}... (원본 조회 {r['views']:,})")
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

    # 저성과 포스트 Gemini 자동 진단
    if gemini_key and results:
        qualified_bottom = [r for r in results if r.get('views', 0) >= 10]
        if len(qualified_bottom) >= 3:
            bottom3 = sorted(qualified_bottom, key=lambda x: x['views'])[:3]
            avg_v = sum(r['views'] for r in results) / len(results)
            bottom_summary = '\n'.join([
                f"{i+1}. [{r['date']}] 조회 {r['views']:,} | 좋아요 {r['likes']} | 댓글 {r['replies']}\n   \"{r['text']}...\""
                for i, r in enumerate(bottom3)
            ])
            bottom_prompt = f"""너는 증여·상속 구조 설계 전문가 Threads 계정의 콘텐츠 전략가야.
이번 주 전체 평균 조회수는 {avg_v:,.0f}회야.
아래 3개 포스팅은 조회수가 가장 낮았어.

{bottom_summary}

각 포스팅이 왜 저조했는지 한 가지씩 분석해줘.
훅이 약한지, 주제 각도가 흔한지, 가독성이 떨어지는지 등 구체적인 원인 진단.
200자 이내, 전부 반말, 번호 붙여서."""
            try:
                client_b = genai.Client(api_key=gemini_key)
                resp_b = client_b.models.generate_content(model='gemini-2.5-flash', contents=bottom_prompt)
                print(f'\n📉 저성과 포스트 Gemini 진단 (조회수 하위 3개)')
                print(f'{"-"*60}')
                print(resp_b.text.strip())
            except Exception as e:
                print(f'저성과 분석 실패: {e}')

    # 훅 패턴 분석 & 학습
    if gemini_key and len(results) >= 5:
        hook_data = []
        for r in results[:15]:
            first_line = r.get('full_text', '').split('\n')[0].strip()
            if first_line:
                hook_data.append({'first_line': first_line[:60], 'views': r['views']})
        if hook_data:
            posts_summary = '\n'.join([
                f"{i+1}. 조회 {d['views']:,}: {d['first_line']}"
                for i, d in enumerate(hook_data)
            ])
            hook_prompt = f"""아래 Threads 포스팅들의 첫 줄을 보고 훅 유형을 분류해줘.

유형 (하나만 선택):
- 반전형: 일반적 통념을 뒤집는 사실
- 숫자형: 구체적 수치/통계로 시작
- 경각심형: 위험·손해·경고로 시작
- 사례형: 구체적 사람/상황 사례로 시작
- 질문형: 독자에게 직접 질문

[포스팅 목록]
{posts_summary}

JSON 배열만 출력 (다른 텍스트 없이):
[{{"num": 1, "type": "반전형"}}, ...]"""
            try:
                client_h = genai.Client(api_key=gemini_key)
                resp_h = client_h.models.generate_content(model='gemini-2.5-flash', contents=hook_prompt)
                m_h = re.search(r'\[[\s\S]*\]', resp_h.text.strip())
                if m_h:
                    classifications = json.loads(m_h.group())
                    hook_views = {}
                    for item in classifications:
                        num = item.get('num', 0) - 1
                        hook_type = item.get('type', '')
                        if 0 <= num < len(hook_data) and hook_type:
                            hook_views.setdefault(hook_type, []).append(hook_data[num]['views'])
                    if hook_views:
                        hook_weights = {t: round(sum(v) / len(v), 1) for t, v in hook_views.items()}
                        hook_weights['updated'] = datetime.now(KST).strftime('%Y-%m-%d')
                        with open('hook_weights.json', 'w', encoding='utf-8') as f:
                            json.dump(hook_weights, f, ensure_ascii=False, indent=2)
                        print(f'\n🎣 훅 패턴 분석 (평균 조회수)')
                        for t, avg in sorted(
                            ((t, v) for t, v in hook_weights.items() if t != 'updated'),
                            key=lambda x: -x[1]
                        ):
                            count = len(hook_views[t])
                            print(f'  {t}: 평균 {avg:,.0f}회 ({count}건)')
                        best_hook = max((t for t in hook_weights if t != 'updated'), key=lambda t: hook_weights[t])
                        print(f'  → 최고 훅: {best_hook} → hook_weights.json 저장 (다음 포스팅에 자동 반영)')
            except Exception as e:
                print(f'훅 패턴 분석 실패: {e}')

    # 카테고리별 최적 포스팅 시간 → slot_config.json 자동 업데이트
    SLOT_DEFAULTS = {'business': 7, 'economy': 12, 'insurance': 21, 'policy': 15, 'government': 20, 'trend': 7}
    cat_hour_perf = {}
    for entry in content_log:
        cat = entry.get('category', '')
        hour = entry.get('hour')
        pid = entry.get('post_id')
        if not cat or hour is None or not pid:
            continue
        r = results_by_id.get(pid)
        if not r:
            continue
        cat_hour_perf.setdefault(cat, {}).setdefault(hour, []).append(r['views'])

    if cat_hour_perf:
        slot_config = {}
        if os.path.exists('slot_config.json'):
            with open('slot_config.json', encoding='utf-8') as f:
                slot_config = json.load(f)
        updated = False
        print(f'\n⏰ 카테고리별 최적 포스팅 시간 분석 (A/B 슬롯)')
        for cat, hour_data in cat_hour_perf.items():
            if len(hour_data) < 2:
                continue
            best_h = max(hour_data, key=lambda h: sum(hour_data[h]) / len(hour_data[h]))
            best_avg = sum(hour_data[best_h]) / len(hour_data[best_h])
            cur_h = slot_config.get(cat, SLOT_DEFAULTS.get(cat, best_h))
            cur_views = hour_data.get(cur_h, [0])
            cur_avg = sum(cur_views) / max(len(cur_views), 1)
            marker = '↑' if best_h != cur_h else ' '
            print(f'  {marker} {cat}: 현재 {cur_h:02d}:00 (평균 {cur_avg:,.0f}) → 최적 {best_h:02d}:00 (평균 {best_avg:,.0f})')
            if abs(best_h - cur_h) >= 2:
                slot_config[cat] = best_h
                updated = True
        if updated:
            with open('slot_config.json', 'w', encoding='utf-8') as f:
                json.dump(slot_config, f, ensure_ascii=False, indent=2)
            print(f'  → slot_config.json 업데이트 (2시간 이상 차이 나는 카테고리 조정)')

    # 댓글 유발 포스팅 패턴 분석
    MIN_VIEWS = 30
    commented = [r for r in results if r.get('replies', 0) > 0 and r.get('views', 0) >= MIN_VIEWS]
    uncommented = [r for r in results if r.get('replies', 0) == 0 and r.get('views', 0) >= MIN_VIEWS]

    if commented and uncommented:
        cl_map = {e.get('post_id'): e.get('category', '?') for e in content_log}
        print(f'\n💬 댓글 유발 포스팅 패턴 (조회 {MIN_VIEWS} 이상 기준)')
        print(f'  댓글 있음: {len(commented)}건 | 댓글 없음: {len(uncommented)}건')

        cat_counts = {}
        for r in commented:
            c = cl_map.get(r['id'], '?')
            cat_counts[c] = cat_counts.get(c, 0) + 1
        top_cats = sorted(cat_counts.items(), key=lambda x: -x[1])[:3]
        print(f'  댓글 있는 포스트 카테고리 TOP3: {", ".join(f"{c}({n})" for c, n in top_cats)}')

        if gemini_key:
            c_sample = commented[:3]
            u_sample = uncommented[:3]
            c_texts = '\n'.join([f'- (조회 {r["views"]}, 댓글 {r["replies"]}) {r["text"][:60]}...' for r in c_sample])
            u_texts = '\n'.join([f'- (조회 {r["views"]}, 댓글 0) {r["text"][:60]}...' for r in u_sample])
            pattern_prompt = f"""이 Threads 계정(증여·상속·법인 구조 설계 전문가)의 포스팅을 비교해줘.

[댓글이 달린 포스팅]
{c_texts}

[댓글이 없는 포스팅]
{u_texts}

댓글이 달리게 만드는 요소 3가지를 말해줘.
전부 반말, 150자 이내."""
            try:
                client_p = genai.Client(api_key=gemini_key)
                resp_p = client_p.models.generate_content(model='gemini-2.5-flash', contents=pattern_prompt)
                print(f'  Gemini 분석: {resp_p.text.strip()}')
            except Exception as e:
                print(f'  댓글 패턴 분석 실패: {e}')

    # 인스타그램 카드뉴스 성과 분석
    IG_LOG_FILE = 'instagram_log.json'
    IG_TOKEN = os.environ.get('INSTAGRAM_ACCESS_TOKEN', '')
    BASE_IG = 'https://graph.facebook.com/v21.0'
    IG_METRICS = 'reach,impressions,saved,likes,comments'

    if os.path.exists(IG_LOG_FILE) and IG_TOKEN:
        with open(IG_LOG_FILE, encoding='utf-8') as f:
            ig_log = json.load(f)

        ig_updated = False
        print(f'\n📸 인스타그램 카드뉴스 성과')
        print(f'  {"제목":<30} {"도달":>6} {"저장":>5} {"좋아요":>5} {"댓글":>5}')
        print(f'  {"-"*55}')

        for entry in ig_log:
            pid = entry.get('ig_post_id')
            if not pid:
                continue
            # 이미 측정된 경우 최신 데이터로 갱신
            try:
                r = requests.get(f'{BASE_IG}/{pid}/insights',
                                 params={'metric': IG_METRICS, 'access_token': IG_TOKEN}, timeout=15)
                if r.ok:
                    metrics = {d['name']: d.get('values', [{}])[0].get('value', 0)
                               for d in r.json().get('data', [])}
                    entry['reach'] = metrics.get('reach', 0)
                    entry['impressions'] = metrics.get('impressions', 0)
                    entry['saved'] = metrics.get('saved', 0)
                    entry['likes'] = metrics.get('likes', 0)
                    entry['comments'] = metrics.get('comments', 0)
                    ig_updated = True
                title = (entry.get('selected_title') or '')[:30]
                reach = entry.get('reach', '-')
                saved = entry.get('saved', '-')
                likes = entry.get('likes', '-')
                comments = entry.get('comments', '-')
                print(f'  {title:<30} {str(reach):>6} {str(saved):>5} {str(likes):>5} {str(comments):>5}')
            except Exception as e:
                print(f'  성과 조회 실패 ({pid}): {e}')

        if ig_updated:
            with open(IG_LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(ig_log, f, ensure_ascii=False, indent=2)

            # 저장 수 기준 상위 포스트
            ranked = sorted([e for e in ig_log if e.get('saved', 0) > 0],
                            key=lambda x: -x.get('saved', 0))
            if ranked:
                print(f'\n  💾 저장 수 TOP: {(ranked[0].get("selected_title") or "")[:30]} ({ranked[0]["saved"]}회)')

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    run_analysis()
