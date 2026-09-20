#!/usr/bin/env python3
"""
네이버 블로그 자동 발행 (Selenium, 켜져 있는 일반 크롬에 붙는 방식)

⚠️ 네이버 공식 API가 아니라 브라우저를 자동 조작하는 매크로예요.
   이용약관 위반 소지가 있고, 짧은 간격으로 규칙적으로 올리면 블로그 지수가
   떨어질(최적화 이탈) 위험이 있어요. 사용자 책임하에 실행하는 스크립트입니다.

사용법:
1. 크롬 켜기 (최초 1회, 이후엔 켜져 있으면 생략):
     python naver_blog_poster.py start
   → 전용 프로필로 일반 크롬이 뜹니다. 네이버에 직접 로그인하고 창은 닫지 마세요.

2. 발행 설정 화면까지만 확인 (실제 발행 안 함):
     python naver_blog_poster.py post <글파일.txt> --dry

3. 실제 발행:
     python naver_blog_poster.py post <글파일.txt>

글파일 형식:
    제목: 글 제목
    카테고리: 노후준비          (블로그에 있는 카테고리명, 생략 가능)
    태그: 연금보험,노후준비      (쉼표 구분, 생략 가능)
    ---
    본문 줄...
    ## 소제목 줄            (굵게 처리)
    [IMG:01_대표이미지.jpg]   (글파일과 같은 폴더의 이미지를 그 자리에 삽입)
    (빈 줄 = 문단 띄우기)

로그인 정보(아이디/비밀번호)는 이 스크립트가 절대 저장하거나 다루지 않습니다.
"""
import sys, time, os, subprocess

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PROFILE_DIR = os.path.abspath('naver_chrome_profile')
DEBUG_PORT = 9222
BLOG_ID = 'sobok__biz'

CHROME_CANDIDATES = [
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
    os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe'),
]


def find_chrome():
    for p in CHROME_CANDIDATES:
        if os.path.exists(p):
            return p
    raise FileNotFoundError('chrome.exe를 못 찾았어요. CHROME_CANDIDATES에 경로를 추가해주세요.')


def start_chrome():
    chrome = find_chrome()
    os.makedirs(PROFILE_DIR, exist_ok=True)
    subprocess.Popen([
        chrome,
        f'--remote-debugging-port={DEBUG_PORT}',
        f'--user-data-dir={PROFILE_DIR}',
        '--start-maximized',
        'https://nid.naver.com/nidlogin.login',
    ])
    print('크롬 창이 떴어요. 네이버에 직접 로그인하고 창은 닫지 마세요.')
    print('그 다음:  python naver_blog_poster.py post <글파일.txt> [--dry]')


def get_driver():
    options = Options()
    options.add_experimental_option('debuggerAddress', f'127.0.0.1:{DEBUG_PORT}')
    try:
        return webdriver.Chrome(options=options)
    except Exception as e:
        raise RuntimeError('켜져 있는 크롬에 붙지 못했어요. 먼저 python naver_blog_poster.py start 를 실행하세요.') from e


def parse_post_file(path):
    with open(path, encoding='utf-8') as f:
        raw = f.read()
    head, _, body = raw.partition('\n---\n')
    meta = {}
    for line in head.splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            meta[k.strip()] = v.strip()
    base_dir = os.path.dirname(os.path.abspath(path))
    lines = body.strip('\n').split('\n')
    return meta, lines, base_dir


def js_click(driver, el):
    driver.execute_script('arguments[0].click();', el)


def send(driver, *keys):
    """실제 브라우저 포커스로 키를 보낸다. (WebElement.send_keys는 중첩 iframe 구조에서
    조용히 안 먹는 경우가 있어, 전역 ActionChains로 통일)"""
    ActionChains(driver).send_keys(*keys).perform()


def send_chord(driver, modifier, key):
    """Ctrl+B 같은 조합키. ActionChains.send_keys(모디파이어, 키)는 모디파이어를 바로
    떼버려서 조합이 안 먹고 글자가 그대로 입력되는 문제가 있어, key_down/up으로 명시적으로 잡는다."""
    ActionChains(driver).key_down(modifier).send_keys(key).key_up(modifier).perform()


def dismiss_draft_popup(driver):
    """'작성 중인 글이 있습니다' 팝업(iframe 안) → 취소 눌러 새 글로 시작."""
    btns = [b for b in driver.find_elements(By.CSS_SELECTOR, 'button.se-popup-button-cancel') if b.is_displayed()]
    if btns:
        js_click(driver, btns[0])
        WebDriverWait(driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.se-popup-dim')))
        print('임시저장 팝업 취소함')


def click_and_type(driver, locate_fn, text, check_fn, label='영역', tries=4):
    """locate_fn()으로 매 시도마다 요소를 새로 찾아 클릭 후 text 입력, check_fn()으로 실제 반영 확인 — 조용한 실패 시 재시도.
    (편집 영역이 중첩 iframe이라 activeElement 비교로는 포커스를 검증할 수 없어, 입력 결과로 검증한다.)"""
    for attempt in range(tries):
        if not driver.execute_script('return document.hasFocus()'):
            print(f'  [{label}] 창이 포커스를 못 받은 상태 — Page.bringToFront 재시도')
            driver.execute_cdp_cmd('Page.bringToFront', {})
            time.sleep(0.5)
        el = locate_fn()
        try:
            el.click()
        except Exception:
            js_click(driver, el)
        time.sleep(0.3)
        active_desc = driver.execute_script(
            'var a=document.activeElement; return a.tagName+"."+a.className+" hasFocus="+document.hasFocus();')
        current = check_fn()
        print(f'  [{label} 시도{attempt+1}] active={active_desc!r} 상태: {current!r}')
        if attempt > 0:
            send(driver, Keys.CONTROL, 'a')
            send(driver, Keys.DELETE)
            time.sleep(0.2)
        send(driver, text)
        time.sleep(0.3)
        result = check_fn()
        if text[:5] in (result or ''):
            return
        print(f'  {label} 입력 반영 확인 실패 ({result!r}), 재시도 {attempt+1}/{tries}')
        time.sleep(1.5 * (attempt + 1))  # 점점 더 길게 대기 (에디터 준비 지연 대응)
    driver.save_screenshot(f'debug_type_fail_{label}.png')
    raise RuntimeError(f'{label}이 실제로 입력되지 않았어요 (debug_type_fail_{label}.png 확인)')


def type_title(driver, wait, title):
    locate = lambda: wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.se-section-documentTitle')))
    click_and_type(driver, locate, title,
                  lambda: locate().text.strip(), 'title')


def focus_body(driver):
    """제목이 아니라 본문 영역(.se-section-text)에 커서를 둔다. (최종 반영 여부는 이후 본문 타이핑 결과로 검증)"""
    paras = driver.find_elements(By.CSS_SELECTOR, '.se-section-text .se-text-paragraph')
    if not paras:
        send(driver, Keys.ENTER)
        time.sleep(0.3)
        return
    safe_click(driver, paras[-1])
    time.sleep(0.3)


def insert_image(driver, wait, image_path):
    img_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.se-image-toolbar-button')))
    js_click(driver, img_btn)
    time.sleep(0.3)
    try:
        img_btn.click()
    except Exception:
        pass
    try:
        file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type=file]')))
    except Exception:
        driver.save_screenshot('debug_image_click_failed.png')
        raise
    file_input.send_keys(image_path)
    time.sleep(2.5)
    # 이미지 삽입 후 커서를 다음 줄로
    send(driver, Keys.END)


def type_body(driver, wait, lines, base_dir):
    for line in lines:
        s = line.strip()
        if s.startswith('[IMG:') and s.endswith(']'):
            img = os.path.join(base_dir, s[5:-1].strip())
            if not os.path.exists(img):
                print(f'  이미지 없음, 건너뜀: {img}')
                continue
            insert_image(driver, wait, img)
            send(driver, '\n')
            continue
        if s == '':
            send(driver, '\n')
            continue
        if s.startswith('## '):
            send_chord(driver, Keys.CONTROL, 'b')
            send(driver, s[3:])
            send_chord(driver, Keys.CONTROL, 'b')
            send(driver, '\n')
            continue
        # 인라인 강조: **텍스트** → 굵게
        parts = line.split('**')
        for i, part in enumerate(parts):
            if not part:
                continue
            if i % 2 == 1:
                send_chord(driver, Keys.CONTROL, 'b')
                send(driver, part)
                send_chord(driver, Keys.CONTROL, 'b')
            else:
                send(driver, part)
        send(driver, '\n')
        if 'http://' in line or 'https://' in line:
            # URL은 SmartEditor가 잠시 뒤 링크 카드로 자동 변환함 — 그 전에 다음 줄이
            # 같은 줄로 붙어버리는 경우가 있어 변환이 끝날 시간을 준다.
            time.sleep(1.2)
        else:
            time.sleep(0.05)


def safe_click(driver, el):
    try:
        el.click()
    except Exception:
        js_click(driver, el)


def select_category(driver, wait, name):
    sel = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@class,"selectbox_button")]')))
    safe_click(driver, sel)
    time.sleep(0.8)
    opts = [e for e in driver.find_elements(By.XPATH, f'//*[normalize-space(text())="{name}"]') if e.is_displayed()]
    if not opts:
        driver.save_screenshot('debug_category_notfound.png')
        raise RuntimeError(f'카테고리 "{name}"를 목록에서 못 찾았어요 (debug_category_notfound.png 확인)')
    js_click(driver, opts[0])
    time.sleep(0.5)
    print(f'카테고리 선택: {name}')


def input_tags(driver, wait, tags):
    box = wait.until(EC.presence_of_element_located(
        (By.XPATH, '//input[contains(@placeholder,"태그")] | //textarea[contains(@placeholder,"태그")]')))
    safe_click(driver, box)
    for t in tags:
        box.send_keys(t.strip())
        box.send_keys(Keys.ENTER)
        time.sleep(0.2)
    print(f'태그 입력: {tags}')


def check_keyword(meta, lines, base_dir=None):
    """SEO 검사: 키워드가 제목·첫 두 문장·태그·본문 전체에 들어있는지 + 이미지 파일명에 키워드가 있는지.
    빠지면 경고만 하고 발행은 계속 진행한다."""
    kw = meta.get('키워드', '').strip()
    if not kw:
        print('⚠️ 글파일에 "키워드:" 가 없어요 — 롱테일 키워드 1개를 정해서 넣어주세요.')
        return
    norm = lambda s: s.replace(' ', '')
    body_lines = [l for l in lines if l.strip() and not l.strip().startswith('[IMG')]
    title_ok = norm(kw) in norm(meta.get('제목', ''))
    head = norm(' '.join(body_lines[:2]))
    head_ok = norm(kw) in head
    tags_ok = any(norm(kw) in norm(t) for t in meta.get('태그', '').split(','))
    full_body = norm(' '.join(body_lines))
    occurrences = full_body.count(norm(kw))
    for name, ok in [('제목', title_ok), ('첫 두 문장', head_ok), ('태그', tags_ok)]:
        print(f"키워드 '{kw}' → {name}: {'OK' if ok else '⚠️ 없음'}")
    print(f"키워드 '{kw}' → 본문 전체 등장 횟수: {occurrences}회" + ('' if occurrences >= 3 else ' ⚠️ 3회 미만 (자연스럽게 2~3번 더 넣는 걸 권장)'))
    generic = [t.strip() for t in meta.get('태그', '').split(',') if t.strip() and len(t.strip()) <= 4]
    if generic:
        print(f'⚠️ 짧은(대형) 태그 감지: {generic} — 구문형 롱테일 태그로 바꾸는 게 원칙이에요.')

    # 이미지 파일명 SEO 체크 (네이버는 alt 텍스트를 파일명 그대로 가져다 씀 — 09-19 확인)
    img_names = [l.strip()[5:-1].strip() for l in lines if l.strip().startswith('[IMG:') and l.strip().endswith(']')]
    if img_names:
        kw_no_space = norm(kw)
        no_kw = [n for n in img_names if kw_no_space not in norm(n)]
        if no_kw:
            print(f"⚠️ 파일명에 키워드가 없는 이미지: {no_kw} — 네이버는 alt 텍스트를 파일명 그대로 쓰니, 파일명에 키워드를 넣는 걸 권장해요.")


def post_to_naver(meta, lines, base_dir, dry=False):
    title = meta.get('제목', '').strip()
    if not title:
        raise ValueError('글파일에 "제목:" 이 없어요.')
    check_keyword(meta, lines)

    driver = get_driver()
    driver.switch_to.new_window('tab')
    # 새로 만든 탭은 OS/브라우저 레벨 포커스를 못 받아 클릭해도 실제 입력 포커스로 이어지지 않는
    # 경우가 있었음(document.hasFocus()==true인데도 재현됨) — CDP로 강제 포커스 에뮬레이션.
    driver.execute_cdp_cmd('Emulation.setFocusEmulationEnabled', {'enabled': True})
    driver.get(f'https://blog.naver.com/{BLOG_ID}?Redirect=Write&')
    driver.execute_cdp_cmd('Page.bringToFront', {})
    wait = WebDriverWait(driver, 20)

    wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'mainFrame')))
    time.sleep(2)
    # 툴바 JS(이미지 버튼)까지 로드된 걸 에디터 준비 신호로 사용 — 새 탭은 타이틀 placeholder가
    # 먼저 보여도 contenteditable 바인딩이 늦게 끝나 조용히 타이핑이 안 먹는 경우가 있었음.
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button.se-image-toolbar-button')))
    except Exception:
        pass
    time.sleep(1.5)
    dismiss_draft_popup(driver)
    time.sleep(1)

    type_title(driver, wait, title)
    focus_body(driver)
    type_body(driver, wait, lines, base_dir)
    body_text = driver.find_element(By.CSS_SELECTOR, '.se-section-text').text.strip()
    first_line = next((l.strip() for l in lines if l.strip() and not l.strip().startswith('[IMG')), '')
    if first_line[:10] not in body_text:
        driver.save_screenshot('debug_body_typed_fail.png')
        raise RuntimeError(f'본문이 실제로 입력되지 않았어요 (debug_body_typed_fail.png 확인)')
    print('본문 작성 완료')
    driver.save_screenshot('debug_body_done.png')

    # 발행 설정 레이어 열기
    dims = driver.find_elements(By.CSS_SELECTOR, '.se-popup-dim')
    if any(d.is_displayed() for d in dims):
        print('발행 전 남아있는 팝업 dim 감지 — ESC로 정리')
        driver.switch_to.active_element.send_keys(Keys.ESCAPE)
        time.sleep(0.5)
    publish_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@class,"publish_btn")]')))
    safe_click(driver, publish_btn)
    time.sleep(1.5)

    if meta.get('카테고리'):
        select_category(driver, wait, meta['카테고리'])
    if meta.get('태그'):
        input_tags(driver, wait, [t for t in meta['태그'].split(',') if t.strip()])

    driver.save_screenshot('debug_publish_layer.png')

    if dry:
        print('--dry: 발행 설정 화면까지만 진행했어요 (debug_publish_layer.png 확인). 발행은 안 했습니다.')
        print('이 탭은 그대로 두었으니 확인 후 닫아주세요. (닫으면 임시저장 팝업이 다음에 뜰 수 있음)')
        return

    confirm_candidates = [b for b in driver.find_elements(By.XPATH, '//button[contains(@class,"confirm_btn")]') if b.is_displayed()]
    if not confirm_candidates:
        driver.save_screenshot('debug_confirm_notfound.png')
        raise RuntimeError('최종 발행 버튼(confirm_btn)을 못 찾았어요 (debug_confirm_notfound.png 확인)')
    print(f'최종 발행 버튼 {len(confirm_candidates)}개 감지, 텍스트: {[b.text for b in confirm_candidates]}')
    safe_click(driver, confirm_candidates[0])
    time.sleep(4)
    driver.save_screenshot('debug_final.png')
    # 발행 성공 확인: 에디터 URL이 실제 글 주소(/blogId/postNo)로 바뀌었는지 확인
    for _ in range(6):
        url = driver.current_url
        if driver.current_url.split('?')[0].rstrip('/').split('/')[-1].isdigit():
            break
        time.sleep(1)
    driver.switch_to.default_content()
    final_url = driver.current_url
    if final_url.split('?')[0].rstrip('/').split('/')[-1].isdigit():
        print('발행 완료! URL:', final_url)
    else:
        print(f'⚠️ 발행 확인 안 됨 — URL이 여전히 에디터 화면입니다: {final_url}')
        print('   debug_final.png 확인 필요, 목록에서 실제로 올라갔는지 확인해주세요.')


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'help'
    if mode == 'start':
        start_chrome()
    elif mode == 'post' and len(sys.argv) > 2:
        meta, lines, base_dir = parse_post_file(sys.argv[2])
        post_to_naver(meta, lines, base_dir, dry='--dry' in sys.argv)
    else:
        print('사용법: python naver_blog_poster.py start | post <글파일.txt> [--dry]')
