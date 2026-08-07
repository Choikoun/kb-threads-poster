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
FORMAT_POOL_FILE = "format_pool.json"
KST = timezone(timedelta(hours=9))

# news_auto_poster.py에 하드코딩된 정적 포맷 (이름 충돌 방지용 — import하면 feedparser 등 의존성이 끌려와 목록만 유지)
STATIC_FORMATS = ['반전형', '사례형', '담백형', '감정인용형', '번호형', '스토리형', '한줄형']
MAX_ACTIVE_DYNAMIC = 3  # 동시 활성 동적 포맷 상한


def refresh_format_pool(groups):
    """매주 새 포맷 1개 발명 + 저성과 포맷 은퇴 → format_pool.json.
    고정 포맷 풀은 돌려쓰다 보면 결국 또 획일화된다는 사용자 지적(2026-07-27)에 따른 자동 순환 장치.
    news_auto_poster._choose_format가 이 풀의 active 포맷을 로테이션에 합류시킨다."""
    gemini_key = os.environ.get('GEMINI_API_KEY')
    if not gemini_key:
        return

    pool = {'formats': {}}
    if os.path.exists(FORMAT_POOL_FILE):
        try:
            with open(FORMAT_POOL_FILE, encoding='utf-8') as f:
                pool = json.load(f)
        except Exception:
            pass
    pool.setdefault('formats', {})

    print(f"\n🧬 포맷 풀 갱신 (동적 포맷 발명·은퇴)")

    # 1) 이번 주 데이터로 동적 포맷 성과 집계
    dyn_stats = {}
    for (cat, variant), items in groups.items():
        if variant in pool['formats']:
            s = dyn_stats.setdefault(variant, {'views': 0, 'n': 0})
            s['views'] += sum(i['views'] for i in items)
            s['n'] += len(items)
    all_views = [i['views'] for items in groups.values() for i in items]
    overall_avg = (sum(all_views) / len(all_views)) if all_views else 0

    # 2) 성과 기반 은퇴: 5건 이상 게시됐는데 전체 평균의 35% 미만
    for name, s in dyn_stats.items():
        fmt = pool['formats'].get(name)
        if fmt and fmt.get('status') == 'active' and s['n'] >= 5 and overall_avg > 0:
            avg = s['views'] / s['n']
            if avg < overall_avg * 0.35:
                fmt['status'] = 'retired'
                fmt['retired'] = datetime.now(KST).strftime('%Y-%m-%d')
                fmt['retired_reason'] = f"{s['n']}건 평균 {avg:,.0f}회 — 전체 평균({overall_avg:,.0f})의 {avg/overall_avg*100:.0f}%"
                print(f"  📉 은퇴: {name} ({fmt['retired_reason']})")

    # 3) 새 포맷 발명 (Gemini)
    active = {n: f for n, f in pool['formats'].items() if f.get('status') == 'active'}
    existing_names = STATIC_FORMATS + list(pool['formats'].keys())
    active_desc = '\n'.join(f"- {n}: {f.get('why', '')}" for n, f in active.items()) or '(없음)'
    top_lines = []
    for (cat, variant), items in sorted(groups.items(), key=lambda kv: -max(i['views'] for i in kv[1]))[:5]:
        best = max(items, key=lambda i: i['views'])
        top_lines.append(f"- [{variant}] {best['views']:,}회: {best['text'][:60]}")

    prompt = f"""너는 한국 Threads에서 법인·세금·자산 설계 전문가 계정의 콘텐츠 포맷 디자이너야.
이 계정은 뉴스 기반 텍스트 포스팅을 하루 수차례 발행하는데, 포맷이 반복되면 독자가 지루해하므로 매주 새 포맷을 하나씩 로테이션에 투입한다.

[이미 존재하는 포맷 이름 - 이름과 구조 모두 겹치면 안 됨]
{', '.join(existing_names)}
(반전형=통념 뒤집기, 사례형=인물 사례, 담백형=이슈 전달+소감, 감정인용형=1인칭 속마음 인용, 번호형=번호 리스트, 스토리형=시간순 미니 서사, 한줄형=1~3줄 초단문)

[현재 활성 동적 포맷]
{active_desc}

[이번 주 성과 참고 - 어떤 글이 터졌는지]
{chr(10).join(top_lines) if top_lines else '(데이터 없음)'}

위와 구조적으로 확실히 다른, 스크롤을 멈추게 할 새 포맷 1개를 발명해라.
- Threads는 텍스트 네이티브 플랫폼 — 시각 장치 없이 문장 배치·리듬·화법만으로 주목을 끌어야 함
- 참고할 만한 방향(이 중에서 골라도 되고 완전히 새로 만들어도 됨): 대화 재연(두 사람 대화 인용), 타임라인형(연도·날짜 나열로 변화 보여주기), 체크리스트 아닌 오답노트형(틀린 통념을 X표로), 숫자 대비형(두 숫자만 극명하게 대비), 역발상 제목형(모두가 A라 할 때 B라고 첫 줄에 선언), 편지형, 실황 중계형
- structure는 다른 작가가 그대로 따라 쓸 수 있는 지시문 3~6줄로 (기존 포맷 지시문처럼 "1. ~ / 2. ~" 또는 서술형)
- 반말·상담유도 금지·이모지 절약 같은 계정 규칙은 시스템이 따로 강제하니 구조 설계에만 집중

JSON만 출력:
{{"name": "한글 2~4자+형 (기존 이름 금지)", "structure": "작성 지시문", "categories": ["business","economy","insurance","policy","government" 중 어울리는 것들], "why": "왜 주목을 끄는지 한 줄"}}"""

    try:
        client = genai.Client(api_key=gemini_key)
        resp = client.models.generate_content(model='gemini-flash-lite-latest', contents=prompt)
        m = re.search(r'\{[\s\S]*\}', resp.text.strip())
        new_fmt = json.loads(m.group(), strict=False) if m else None
    except Exception as e:
        print(f'  포맷 발명 실패: {e}')
        new_fmt = None

    valid_cats = {'business', 'economy', 'insurance', 'policy', 'government', 'trend'}
    if new_fmt:
        name = (new_fmt.get('name') or '').strip()
        structure = (new_fmt.get('structure') or '').strip()
        cats = [c for c in (new_fmt.get('categories') or []) if c in valid_cats]
        if name and structure and cats and name not in existing_names:
            pool['formats'][name] = {
                'structure': structure,
                'categories': cats,
                'why': (new_fmt.get('why') or '').strip(),
                'created': datetime.now(KST).strftime('%Y-%m-%d'),
                'status': 'active',
            }
            print(f"  🆕 신규 포맷: {name} → {', '.join(cats)}")
            print(f"     {pool['formats'][name]['why']}")
        else:
            print(f"  신규 포맷 검증 실패 (이름 중복/필드 누락) — 이번 주는 추가 없음")

    # 4) 활성 상한 초과 시 가장 오래된 것부터 은퇴 (성과 데이터 있는 저성과 우선)
    active = {n: f for n, f in pool['formats'].items() if f.get('status') == 'active'}
    while len(active) > MAX_ACTIVE_DYNAMIC:
        def _avg(nm):
            s = dyn_stats.get(nm)
            return (s['views'] / s['n']) if s and s['n'] else float('inf')
        victim = min(active, key=lambda nm: (_avg(nm), active[nm].get('created', '')))
        pool['formats'][victim]['status'] = 'retired'
        pool['formats'][victim]['retired'] = datetime.now(KST).strftime('%Y-%m-%d')
        pool['formats'][victim].setdefault('retired_reason', '활성 상한 초과 — 로테이션 자리 확보')
        print(f"  📉 은퇴(상한 초과): {victim}")
        active.pop(victim)

    with open(FORMAT_POOL_FILE, 'w', encoding='utf-8') as f:
        json.dump(pool, f, ensure_ascii=False, indent=2)
    print(f"  → {FORMAT_POOL_FILE} 저장 (활성 동적 포맷 {len(active)}개)")


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
        resp = client.models.generate_content(model='gemini-flash-lite-latest', contents=prompt)
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

            # 퍼널 지표 — 허영 지표(조회수)가 아니라 "결국 상담"으로 가는 중간 계단 추적 (2026-08-08 신설)
            total_views = sum(r.get('views', 0) for r in results)
            total_likes = sum(r.get('likes', 0) for r in results)
            total_replies = sum(r.get('replies', 0) for r in results)
            print(f"\n🔻 퍼널 지표 (도달 → 관심 → 관계)")
            if total_views:
                print(f"  조회 1,000회당 팔로워 순증: {total_diff / (total_views / 1000):.2f}명  (분석 게시물 조회 합계 {total_views:,} 기준)")
                print(f"  전체 좋아요율: {total_likes / total_views * 100:.3f}% | 전체 댓글율: {total_replies / total_views * 100:.3f}%")
            print(f"  ※ 체크리스트 자동 DM 발송 수·클릭률은 ManyChat 대시보드에서 수동 확인 (무료 티어 월 25명 한도 주의)")

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
        refresh_format_pool(groups)

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
        with open('length_weights.json', 'w', encoding='utf-8') as f:
            json.dump({
                'best_bucket': best_len,
                'avg_views': round(length_avgs[best_len], 1),
                'all': {b: round(v, 1) for b, v in length_avgs.items()},
                'updated': datetime.now(KST).strftime('%Y-%m-%d'),
            }, f, ensure_ascii=False, indent=2)
        print(f'  → length_weights.json 저장')

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

    # 재발행 후보 (조회수 300 이상) — 논란으로 조회수 오른 글은 excluded_posts.json으로 영구 차단
    excluded_ids = set()
    if os.path.exists('excluded_posts.json'):
        try:
            with open('excluded_posts.json', encoding='utf-8') as f:
                excluded_ids = {e['id'] for e in json.load(f).get('excluded', [])}
        except Exception:
            pass
    reblog = load_reblog()
    existing_ids = {r["id"] for r in reblog}
    new_candidates = []
    for r in results:
        if r["views"] >= 300 and r["id"] not in existing_ids and r["id"] not in excluded_ids:
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
- 댓글 2개 (마지막 마무리 방식을 매번 다르게 — 양자택일형은 30% 이하로만, 나머지는 자기 판단 던지기·되묻는 질문·후속 예고 중 하나)

JSON만 출력:
{{"main": "...", "comments": ["댓글1", "댓글2"]}}"""
                resp = client.models.generate_content(model='gemini-flash-lite-latest', contents=followup_prompt)
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
            resp = client.models.generate_content(model='gemini-flash-lite-latest', contents=prompt)
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
                resp_b = client_b.models.generate_content(model='gemini-flash-lite-latest', contents=bottom_prompt)
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
                resp_h = client_h.models.generate_content(model='gemini-flash-lite-latest', contents=hook_prompt)
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
        date_str = entry.get('date', '')
        if not cat or hour is None or not pid:
            continue
        # 주말(금/토/일)은 콘텐츠 종류(감성형) 효과가 시간대 효과와 섞여 들어가므로 제외 —
        # 2026-06-21 확인: 요일별 평균 조회수가 시간대보다 훨씬 크게 갈려서, 안 거르면 시간대 추천이 왜곡됨
        try:
            if datetime.strptime(date_str, '%Y-%m-%d').weekday() in (4, 5, 6):
                continue
        except ValueError:
            pass
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
                resp_p = client_p.models.generate_content(model='gemini-flash-lite-latest', contents=pattern_prompt)
                print(f'  Gemini 분석: {resp_p.text.strip()}')
            except Exception as e:
                print(f'  댓글 패턴 분석 실패: {e}')

    # 인스타그램 카드뉴스 성과 분석
    IG_LOG_FILE = 'instagram_log.json'
    IG_TOKEN = os.environ.get('INSTAGRAM_ACCESS_TOKEN', '')
    BASE_IG = 'https://graph.facebook.com/v21.0'
    # 'impressions'는 최신 API에서 무효 지표라 콤마로 묶어 한 번에 요청하면 전체가 실패함(Threads insights와 동일 이슈) — 지표별 개별 호출로 전환
    IG_METRICS = ['reach', 'saved', 'likes', 'comments']

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
                metrics = {}
                for metric in IG_METRICS:
                    r = requests.get(f'{BASE_IG}/{pid}/insights',
                                     params={'metric': metric, 'access_token': IG_TOKEN}, timeout=15)
                    if r.ok:
                        data = r.json().get('data', [])
                        if data:
                            metrics[metric] = data[0].get('values', [{}])[0].get('value', 0)
                    else:
                        print(f'  지표 조회 실패 ({pid}/{metric}): {r.status_code} {r.text[:150]}')
                if metrics:
                    entry['reach'] = metrics.get('reach', entry.get('reach', 0))
                    entry['saved'] = metrics.get('saved', entry.get('saved', 0))
                    entry['likes'] = metrics.get('likes', entry.get('likes', 0))
                    entry['comments'] = metrics.get('comments', entry.get('comments', 0))
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
