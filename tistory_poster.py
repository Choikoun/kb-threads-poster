#!/usr/bin/env python3
"""
티스토리 자동 발행 (Selenium, 네이버 자동화와 같은 크롬 naver_chrome_profile / 9222 포트 사용)
- Claude 확장프로그램 없이 동작 → 확장 연결 끊김/로그인 불일치 문제와 무관
- 입력은 네이버와 같은 naver.txt (제목/키워드/카테고리/태그 헤더 + --- + 본문)
  본문 규칙: **소제목**, [IMG:파일명], bare URL, 마지막 줄 상담링크
- 티스토리 카테고리는 네이버와 이름이 달라 --cat 으로 지정 (예: 법인, 금융지식, 부동산, "재테크,보험")

사용:
  python tistory_poster.py login              # 로그인 확인(풀렸으면 카카오 저장계정 클릭으로 자동 재로그인)
  python tistory_poster.py post <naver.txt> --cat 법인 [--dry]
  (--dry: 본문·이미지·카테고리·태그까지 채우고 발행은 하지 않음)
"""
import sys, os, re, json, time, html
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException

sys.stdout.reconfigure(encoding='utf-8')
import naver_blog_poster as nb

BLOG = 'freedom-of-economic.tistory.com'
NEWPOST = f'https://{BLOG}/manage/newpost'
NAVY, GOLD = '#1B2A4A', '#B8925A'
HERE = os.path.dirname(os.path.abspath(__file__))

BLOCK_FILE_DIALOG = """if(!window.__blk){window.__blk=1;const oc=HTMLInputElement.prototype.click;
HTMLInputElement.prototype.click=function(){if(this.type==='file')return;return oc.apply(this,arguments)};}"""


def _dismiss_alert(driver):
    try:
        driver.switch_to.alert.dismiss()
        return True
    except NoAlertPresentException:
        return False


def _url(driver):
    for _ in range(3):
        try:
            return driver.current_url
        except UnexpectedAlertPresentException:  # '저장된 글이 있습니다. 이어서 작성?' → 취소(새 글)
            _dismiss_alert(driver)
            time.sleep(0.5)
    return driver.current_url


def _logged_in(driver):
    u = _url(driver)
    return '/auth/login' not in u and 'accounts.kakao' not in u


def ensure_login(driver):
    """티스토리 세션쿠키는 크롬 재시작 때마다 풀린다. 카카오 쿠키가 살아 있으면 저장계정 클릭만으로 재로그인(비밀번호 입력 없음)."""
    try:
        driver.get(NEWPOST)
    except UnexpectedAlertPresentException:  # 이전 작성중 화면의 '페이지를 떠나시겠습니까' → 떠나기
        try:
            driver.switch_to.alert.accept()
        except NoAlertPresentException:
            pass
        driver.get(NEWPOST)
    time.sleep(2)
    _dismiss_alert(driver)
    if _logged_in(driver):
        return True
    for b in driver.find_elements(By.CSS_SELECTOR, 'a,button'):
        if '카카오' in b.text:
            b.click()
            break
    time.sleep(4)
    if 'accounts.kakao' in _url(driver):
        acc = driver.find_elements(By.CSS_SELECTOR, 'li a')
        for a in acc:
            if '@' in a.text:
                a.click()
                break
        time.sleep(6)
    if _logged_in(driver):
        return True
    raise RuntimeError('티스토리 로그인이 풀려 있고 자동 재로그인에 실패했어요. 크롬 창에서 카카오 로그인(로그인 상태 유지 체크)을 한 번 해주세요.')


# ---------- 본문 변환 ----------
URL_RE = re.compile(r'^https?://\S+$')
IMG_RE = re.compile(r'^\[IMG:(.+?)\]$')
HEAD_RE = re.compile(r'^\*\*(.+)\*\*$')


def _posts():
    try:
        with open(os.path.join(HERE, 'blog_posts.json'), encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def _internal_link(url):
    """네이버 내부링크 → 같은 글의 티스토리 주소 + 글 제목 앵커."""
    for p in _posts():
        if p.get('naver') == url and p.get('tistory'):
            return p['tistory'], p.get('title') or '관련 글 보기'
    return None, None


def _para(text_lines):
    parts = []
    for ln in text_lines:
        parts.extend(nb._group_sentences(ln))
    body = '<br>'.join(html.escape(p) for p in parts)
    body = re.sub(r'^(\d{1,2})[.)]\s+', lambda m: (nb.CIRCLED[int(m.group(1)) - 1] if 1 <= int(m.group(1)) <= 12 else m.group(1) + ')') + ' ', body)
    return f'<p data-ke-size="size16">{body}</p>'


def build_html(lines):
    """lines → (html, [이미지 파일명...]). 이미지는 @@IMG:n@@ 자리표시자로 두고 업로드 후 교체."""
    blocks, cur = [], []
    for raw in lines:
        s = raw.strip()
        if not s:
            if cur:
                blocks.append(cur)
                cur = []
            continue
        cur.append(s)
    if cur:
        blocks.append(cur)

    last_img = max((i for i, b in enumerate(blocks) if len(b) == 1 and IMG_RE.match(b[0])), default=-1)
    out, imgs = [], []
    for i, b in enumerate(blocks):
        if len(b) == 1 and IMG_RE.match(b[0]):
            imgs.append(IMG_RE.match(b[0]).group(1))
            out.append(f'<p data-ke-size="size16">@@IMG:{len(imgs) - 1}@@</p>')
            continue
        # 마지막 이미지 뒤: [마무리 훅 박스] + [상담 문구+URL 버튼]
        if i > last_img >= 0:
            is_cta = any(URL_RE.match(x) and 'naver.me' in x for x in b)
            if is_cta:
                text = [x for x in b if not URL_RE.match(x)]
                url = [x for x in b if URL_RE.match(x)][0]
                out.append(_para(text))
                out.append(f'<p data-ke-size="size16" style="text-align:center;"><a href="{url}" target="_blank" rel="noopener" '
                           f'style="display:inline-block;background:{NAVY};color:#fff;padding:12px 22px;border-radius:6px;'
                           f'text-decoration:none;font-weight:bold;">상담 신청하기</a></p>')
            else:
                inner = _para(b).replace('<p data-ke-size="size16">', '<p data-ke-size="size16" style="margin:0;">', 1)
                out.append(f'<div style="background:#F7F5F0;border-left:4px solid {GOLD};padding:16px 18px;border-radius:4px;margin:8px 0 18px;">{inner}</div>')
            continue
        if len(b) >= 1 and HEAD_RE.match(b[0]):
            h = HEAD_RE.match(b[0]).group(1)
            out.append(f'<h3 data-ke-size="size23" style="color:{NAVY};border-left:4px solid {GOLD};padding-left:10px;"><b>{html.escape(h)}</b></h3>')
            b = b[1:]
            if not b:
                continue
        # URL 줄: 내부링크/외부링크
        text, links = [], []
        for x in b:
            if URL_RE.match(x):
                links.append(x)
            else:
                text.append(x)
        if text:
            out.append(_para(text))
        for u in links:
            t_url, t_title = _internal_link(u)
            if t_url:
                out.append(f'<p data-ke-size="size16">👉 <a href="{t_url}" target="_blank" rel="noopener">{html.escape(t_title)}</a></p>')
            elif 'naver.me' in u:
                out.append(f'<p data-ke-size="size16" style="text-align:center;"><a href="{u}" target="_blank" rel="noopener" '
                           f'style="display:inline-block;background:{NAVY};color:#fff;padding:12px 22px;border-radius:6px;'
                           f'text-decoration:none;font-weight:bold;">상담 신청하기</a></p>')
            else:
                out.append(f'<p data-ke-size="size16"><a href="{u}" target="_blank" rel="noopener">{html.escape(u)}</a></p>')
    return '\n'.join(out), imgs


# ---------- 에디터 조작 ----------
def set_title(driver, title):
    driver.execute_script(
        "const t=document.querySelector('#post-title-inp');"
        "Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(t,arguments[0]);"
        "t.dispatchEvent(new Event('input',{bubbles:true}));t.dispatchEvent(new Event('change',{bubbles:true}));", title)


def set_body(driver, body_html):
    driver.execute_script("tinymce.activeEditor.setContent(arguments[0]); tinymce.activeEditor.fire('change');", body_html)
    time.sleep(1)


def upload_image(driver, path, idx):
    driver.execute_script(BLOCK_FILE_DIALOG)
    btn = [e for e in driver.find_elements(By.CSS_SELECTOR, 'div[aria-label="첨부"]') if e.is_displayed()]
    if not btn:
        raise RuntimeError('첨부 버튼을 못 찾았어요(창 크기 확인).')
    btn[0].click()
    time.sleep(0.8)
    ok = driver.execute_script("""const it=[...document.querySelectorAll('.mce-tistory-attach-item')];
const t=it.find(e=>e.innerText.includes('사진')); if(!t) return false;
for(const ty of ['mousedown','mouseup','click']) t.dispatchEvent(new MouseEvent(ty,{bubbles:true,cancelable:true,view:window})); return true;""")
    if not ok:
        raise RuntimeError('첨부 메뉴의 사진 항목을 못 찾았어요.')
    time.sleep(0.8)
    inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type=file]')
    if not inputs:
        raise RuntimeError('파일 input이 생성되지 않았어요.')
    inputs[-1].send_keys(path)
    fname = os.path.basename(path)
    for _ in range(40):
        time.sleep(0.5)
        done = driver.execute_script("""const d=tinymce.activeEditor.getDoc();
const f=[...d.querySelectorAll('figure img')].filter(i=>i.getAttribute('data-filename')===arguments[0]&&!i.closest('figure').dataset.placed);
return f.length>0;""", fname)
        if done:
            break
    else:
        raise RuntimeError(f'이미지 업로드 확인 실패: {fname}')
    moved = driver.execute_script("""const d=tinymce.activeEditor.getDoc();
const imgs=[...d.querySelectorAll('figure img')].filter(i=>i.getAttribute('data-filename')===arguments[0]&&!i.closest('figure').dataset.placed);
const fig=imgs[imgs.length-1].closest('figure');
const ph=[...d.querySelectorAll('p')].find(p=>p.textContent.trim()==='@@IMG:'+arguments[1]+'@@');
if(!ph) return false;
fig.dataset.placed='1'; fig.remove(); ph.replaceWith(fig);
return true;""", fname, idx)
    if not moved:
        raise RuntimeError(f'이미지 자리표시자 교체 실패: {fname}')
    time.sleep(0.5)


def select_category(driver, name):
    driver.find_element(By.ID, 'category-btn').click()
    time.sleep(0.8)
    ok = driver.execute_script("""const s=[...document.querySelectorAll('[role=option] span,.mce-menu-item span,#category-list span')]
.find(e=>e.offsetParent&&e.innerText.trim()===arguments[0]); if(!s) return false; s.click(); return true;""", name)
    if not ok:
        cats = driver.execute_script("return [...document.querySelectorAll('#category-list span')].map(e=>e.innerText.trim())")
        raise RuntimeError(f'티스토리 카테고리 "{name}"를 못 찾았어요. 목록: {cats}')
    time.sleep(0.5)


def input_tags(driver, tags):
    inp = driver.find_element(By.ID, 'tagText')
    for t in tags:
        inp.send_keys(t)
        inp.send_keys(Keys.ENTER)
        time.sleep(0.2)


def verify(driver, imgs, expected_h3):
    r = driver.execute_script("""const d=tinymce.activeEditor.getDoc();
return {figs:d.querySelectorAll('figure[data-ke-type=image]').length,ph:(d.body.innerText.match(/@@IMG/g)||[]).length,
h3:d.querySelectorAll('h3').length,len:d.body.innerText.length,last:d.body.lastElementChild.innerText.slice(0,30)}""")
    print('검증:', r)
    if r['figs'] != len(imgs) or r['ph'] or r['h3'] != expected_h3:
        raise RuntimeError(f'본문 검증 실패: {r} (기대 이미지 {len(imgs)}, 소제목 {expected_h3})')


def publish(driver):
    driver.find_element(By.ID, 'publish-layer-btn').click()
    time.sleep(1.5)
    driver.execute_script("const r=document.querySelector('#open20'); r.click(); r.dispatchEvent(new Event('change',{bubbles:true}));")
    time.sleep(0.5)
    label = driver.execute_script("return document.querySelector('#publish-btn').innerText.trim()")
    if '공개 발행' not in label.replace(' ', '') and '발행' not in label:
        raise RuntimeError(f'공개 설정이 안 바뀌었어요(버튼: {label}).')
    driver.find_element(By.ID, 'publish-btn').click()
    for _ in range(30):
        time.sleep(1)
        u = driver.current_url
        if '/manage/newpost' not in u and 'newpost' not in u:
            return u
    raise RuntimeError('발행 후 이동을 확인하지 못했어요.')


def post_to_tistory(meta, lines, base_dir, cat, dry=False):
    driver = nb.get_driver()
    ensure_login(driver)
    time.sleep(1)
    _url(driver)
    body, imgs = build_html(lines)
    for im in imgs:
        if not os.path.exists(os.path.join(base_dir, im)):
            raise FileNotFoundError(os.path.join(base_dir, im))
    set_title(driver, meta['제목'])
    set_body(driver, body)
    for i, im in enumerate(imgs):
        print(f'이미지 {i + 1}/{len(imgs)}: {im}')
        upload_image(driver, os.path.join(base_dir, im), i)
    verify(driver, imgs, body.count('<h3'))
    select_category(driver, cat)
    input_tags(driver, [t.strip() for t in meta.get('태그', '').split(',') if t.strip()])
    if dry:
        print('DRY: 발행 직전까지 채웠어요(발행 안 함).')
        return None
    url = publish(driver)
    print('발행 후 주소:', url)
    return url


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    cmd = sys.argv[1]
    if cmd == 'login':
        d = nb.get_driver()
        print('OK' if ensure_login(d) else 'FAIL')
    elif cmd == 'post':
        path = sys.argv[2]
        cat = sys.argv[sys.argv.index('--cat') + 1]
        meta, lines, base = nb.parse_post_file(path)
        post_to_tistory(meta, lines, base, cat, dry='--dry' in sys.argv)
