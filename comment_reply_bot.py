#!/usr/bin/env python3
"""
댓글 → 자동 1장 답글 봇 (Threads)

reply_bot_posts.json 에 등록된 내 게시물의 댓글을 읽어, 숫자가 있는 댓글에
계산 결과 이미지를 답글로 달아준다. 30분마다 GitHub Actions에서 실행.

핸들러:
  inheritance — "재산 15억 부채 2억 배우자 자녀2" → 상속세 대략 1장 (deliverables/inheritance_estimate.py)
                현행법 확정 구조만 사용. 설계서가 필요한 보험 숫자(연금 수령액 등)는 자동 계산하지 않는다.

상태: reply_bot_state.json (답글 단 댓글 id 목록) — 워크플로우가 커밋.
사용: python comment_reply_bot.py [--dry]   (--dry: 답글 안 달고 파싱·렌더만)
"""
import os, sys, re, json, time, requests
from dotenv import load_dotenv
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'deliverables'))

TOKEN = os.environ['THREADS_ACCESS_TOKEN']
BASE = 'https://graph.threads.net/v1.0'
SELF = 'financial_planner0'
POSTS_FILE = 'reply_bot_posts.json'
STATE_FILE = 'reply_bot_state.json'
CONSULT_LINK = 'https://naver.me/FRLbSbiJ'
MAX_REPLIES_PER_RUN = 10


# ─── 파싱 ────────────────────────────────────────────────────────
def parse_money(s):
    """'15억' '3억5천' '15억 2000만' '5000만원' '2억원' → 만원 단위 int. 실패 시 None"""
    s = s.replace(',', '').replace(' ', '')
    total = 0; found = False
    m = re.search(r'(\d+(?:\.\d+)?)억', s)
    if m:
        total += float(m.group(1)) * 10000; found = True
        s = s[m.end():]
    m = re.search(r'(\d+(?:\.\d+)?)천', s)
    if m:
        total += float(m.group(1)) * 1000; found = True
        s = s[m.end():]
    m = re.search(r'(\d+(?:\.\d+)?)만', s)
    if m:
        total += float(m.group(1)); found = True
    return int(round(total)) if found else None


def parse_inheritance(text):
    """댓글 텍스트 → {'assets','debts','spouse','children'} 또는 None(재산 못 읽으면)"""
    t = text.replace('，', ',')
    assets = None
    for key in ['재산', '자산', '총재산']:
        m = re.search(key + r'\s*[:은는]?\s*([\d.,억천만원\s]+)', t)
        if m:
            assets = parse_money(m.group(1))
            if assets: break
    if not assets:
        # 키워드 없이 '15억' 하나만 있는 경우
        nums = re.findall(r'\d+(?:\.\d+)?억(?:\s*\d+천)?(?:\s*\d+만)?', t)
        if len(nums) == 1 and not re.search(r'부채|빚|채무|대출', t):
            assets = parse_money(nums[0])
    if not assets:
        return None
    debts = 0
    m = re.search(r'(?:부채|빚|채무|대출)\s*[:은는]?\s*([\d.,억천만원\s]+)', t)
    if m:
        debts = parse_money(m.group(1)) or 0
    spouse = bool(re.search(r'배우자|아내|남편|와이프|부인', t)) and not re.search(r'배우자\s*(없|x|X|무)', t)
    children = 0
    KNUM = {'한': 1, '하나': 1, '두': 2, '둘': 2, '세': 3, '셋': 3, '네': 4, '넷': 4}
    m = re.search(r'(?:자녀|자식|아이|애|아들|딸)\s*[:은는이가]?\s*(\d+|하나|둘|셋|넷|한|두|세|네)', t)
    if m:
        v = m.group(1); children = int(v) if v.isdigit() else KNUM[v]
    elif re.search(r'(?:자녀|자식|아이)\s*(?:없|x|X|무)', t):
        children = 0
    elif re.search(r'아들|딸', t):
        children = len(re.findall(r'아들|딸', t))
    return {'assets': assets, 'debts': debts, 'spouse': spouse, 'children': children}


# ─── 핸들러 ──────────────────────────────────────────────────────
def handle_inheritance(text):
    """→ (image_path, reply_text) 또는 None"""
    p = parse_inheritance(text)
    if not p:
        return None
    from inheritance_estimate import render, estimate, fmt
    e = estimate(p)
    label = f"댓글 기준 · 재산 {fmt(p['assets'])}" + (f" · 부채 {fmt(p['debts'])}" if p['debts'] else '')
    png, _ = render({**p, 'label': label, 'prepared_by': '재무설계 상담'}, out_dir='reply_bot_tmp')
    reply = (f"재산 {fmt(p['assets'])}"
             + (f"·부채 {fmt(p['debts'])}" if p['debts'] else '')
             + f"·배우자 {'있음' if p['spouse'] else '없음'}·자녀 {p['children']}명 기준으로 대략 계산하면\n"
             f"예상 상속세 약 {fmt(e['tax_after'])}이야. (일괄공제·배우자공제·누진세율만 반영, 추가 공제는 미반영)\n\n"
             f"이 숫자 줄이는 방향까지 내 상황 1장으로 정리 원하면 → {CONSULT_LINK}")
    return png, reply


HANDLERS = {'inheritance': handle_inheritance}


# ─── Threads API ─────────────────────────────────────────────────
def get_uid():
    return requests.get(f'{BASE}/me', params={'fields': 'id', 'access_token': TOKEN}, timeout=15).json()['id']


def get_replies(post_id):
    r = requests.get(f'{BASE}/{post_id}/replies',
                     params={'fields': 'id,text,username,timestamp', 'access_token': TOKEN}, timeout=30)
    return r.json().get('data', [])


def reply_with_image(uid, comment_id, image_url, text):
    r1 = requests.post(f'{BASE}/{uid}/threads', params={
        'media_type': 'IMAGE', 'image_url': image_url, 'text': text,
        'reply_to_id': comment_id, 'access_token': TOKEN}, timeout=30)
    if 'id' not in r1.json():
        print(f'  답글 컨테이너 실패: {r1.text}'); return None
    time.sleep(8)
    r2 = requests.post(f'{BASE}/{uid}/threads_publish',
                       params={'creation_id': r1.json()['id'], 'access_token': TOKEN}, timeout=30)
    if 'id' not in r2.json():
        print(f'  답글 발행 실패: {r2.text}'); return None
    return r2.json()['id']


# ─── 메인 ────────────────────────────────────────────────────────
def load(path, default):
    if os.path.exists(path):
        with open(path, encoding='utf-8-sig') as f:
            return json.load(f)
    return default


def main(dry=False):
    posts = load(POSTS_FILE, [])
    state = load(STATE_FILE, {'replied': [], 'log': []})
    replied = set(state['replied'])
    if not posts:
        print('등록된 게시물 없음'); return
    uid = None if dry else get_uid()
    done = 0
    for p in posts:
        handler = HANDLERS.get(p['handler'])
        if not handler:
            continue
        for c in get_replies(p['post_id']):
            if c['id'] in replied or c.get('username') == SELF or not c.get('text'):
                continue
            result = handler(c['text'])
            if not result:
                print(f"  숫자 못 읽음, 건너뜀: {c['text'][:40]!r}")
                replied.add(c['id'])   # 다시 시도하지 않음
                continue
            png, text = result
            print(f"  → {c['username']}: {c['text'][:40]!r}\n     {text.splitlines()[1]}")
            if dry:
                print(f'     (dry) 이미지: {png}'); continue
            from card_generator import upload_to_imgbb
            url = upload_to_imgbb(png)
            rid = reply_with_image(uid, c['id'], url, text)
            if rid:
                replied.add(c['id'])
                state['log'].append({'comment_id': c['id'], 'reply_id': rid, 'user': c['username'],
                                     'text': c['text'][:80], 'handler': p['handler'],
                                     'time': time.strftime('%Y-%m-%d %H:%M')})
                done += 1
                print(f'     답글 완료 {rid}')
                if done >= MAX_REPLIES_PER_RUN:
                    break
            time.sleep(3)
    if not dry:
        state['replied'] = sorted(replied)
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    print(f'완료: 답글 {done}건')


if __name__ == '__main__':
    main(dry='--dry' in sys.argv)
