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


def dismiss_draft_popup(driver):
    """'작성 중인 글이 있습니다' 팝업(iframe 안) → 취소 눌러 새 글로 시작."""
    btns = [b for b in driver.find_elements(By.CSS_SELECTOR, 'button.se-popup-button-cancel') if b.is_displayed()]
    if btns:
        js_click(driver, btns[0])
        WebDriverWait(driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.se-popup-dim')))
        print('임시저장 팝업 취소함')


def type_title(driver, wait, title):
    title_area = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.se-section-documentTitle')))
    title_area.click()
    time.sleep(0.3)
    driver.switch_to.active_element.send_keys(title)
    time.sleep(0.3)


def focus_body(driver):
    """제목이 아니라 본문 영역(.se-section-text)에 커서를 둔다."""
    paras = driver.find_elements(By.CSS_SELECTOR, '.se-section-text .se-text-paragraph')
    if paras:
        js_click(driver, paras[-1])
        # JS 클릭만으로 캐럿이 안 잡히는 경우 대비: 실제 클릭도 한 번
        try:
            paras[-1].click()
        except Exception:
            pass
    else:
        # 폴백: 제목에서 Enter 치면 본문으로 이동
        driver.switch_to.active_element.send_keys(Keys.ENTER)
    time.sleep(0.3)


def insert_image(driver, wait, image_path):
    img_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.se-image-toolbar-button')))
    img_btn.click()
    time.sleep(0.8)
    file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type=file]')))
    file_input.send_keys(image_path)
    time.sleep(2.5)
    # 이미지 삽입 후 커서를 다음 줄로
    driver.switch_to.active_element.send_keys(Keys.END)


def type_body(driver, wait, lines, base_dir):
    active = lambda: driver.switch_to.active_element
    for line in lines:
        s = line.strip()
        if s.startswith('[IMG:') and s.endswith(']'):
            img = os.path.join(base_dir, s[5:-1].strip())
            if not os.path.exists(img):
                print(f'  이미지 없음, 건너뜀: {img}')
                continue
            insert_image(driver, wait, img)
            active().send_keys('\n')
            continue
        if s == '':
            active().send_keys('\n')
            continue
        if s.startswith('## '):
            active().send_keys(Keys.CONTROL, 'b')
            active().send_keys(s[3:])
            active().send_keys(Keys.CONTROL, 'b')
            active().send_keys('\n')
            continue
        # 인라인 강조: **텍스트** → 굵게
        parts = line.split('**')
        for i, part in enumerate(parts):
            if not part:
                continue
            if i % 2 == 1:
                active().send_keys(Keys.CONTROL, 'b')
                active().send_keys(part)
                active().send_keys(Keys.CONTROL, 'b')
            else:
                active().send_keys(part)
        active().send_keys('\n')
        time.sleep(0.05)


def select_category(driver, wait, name):
    sel = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@class,"selectbox_button")]')))
    sel.click()
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
    box.click()
    for t in tags:
        box.send_keys(t.strip())
        box.send_keys(Keys.ENTER)
        time.sleep(0.2)
    print(f'태그 입력: {tags}')


def check_keyword(meta, lines):
    """롱테일 키워드 원칙 검사: '키워드:'가 제목·첫 두 문장·태그에 들어있는지. 빠지면 경고(발행은 계속)."""
    kw = meta.get('키워드', '').strip()
    if not kw:
        print('⚠️ 글파일에 "키워드:" 가 없어요 — 롱테일 키워드 1개를 정해서 넣어주세요.')
        return
    norm = lambda s: s.replace(' ', '')
    title_ok = norm(kw) in norm(meta.get('제목', ''))
    head = norm(' '.join([l for l in lines if l.strip() and not l.startswith('[IMG')][:2]))
    head_ok = norm(kw) in head
    tags_ok = any(norm(kw) in norm(t) for t in meta.get('태그', '').split(','))
    for name, ok in [('제목', title_ok), ('첫 두 문장', head_ok), ('태그', tags_ok)]:
        print(f"키워드 '{kw}' → {name}: {'OK' if ok else '⚠️ 없음'}")
    generic = [t.strip() for t in meta.get('태그', '').split(',') if t.strip() and len(t.strip()) <= 4]
    if generic:
        print(f'⚠️ 짧은(대형) 태그 감지: {generic} — 구문형 롱테일 태그로 바꾸는 게 원칙이에요.')


def post_to_naver(meta, lines, base_dir, dry=False):
    title = meta.get('제목', '').strip()
    if not title:
        raise ValueError('글파일에 "제목:" 이 없어요.')
    check_keyword(meta, lines)

    driver = get_driver()
    driver.switch_to.new_window('tab')
    driver.get(f'https://blog.naver.com/{BLOG_ID}?Redirect=Write&')
    wait = WebDriverWait(driver, 20)

    wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'mainFrame')))
    time.sleep(2)
    dismiss_draft_popup(driver)

    type_title(driver, wait, title)
    focus_body(driver)
    type_body(driver, wait, lines, base_dir)
    print('본문 작성 완료')
    driver.save_screenshot('debug_body_done.png')

    # 발행 설정 레이어 열기
    wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@class,"publish_btn")]'))).click()
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

    wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@class,"confirm_btn")]'))).click()
    time.sleep(3)
    driver.save_screenshot('debug_final.png')
    driver.switch_to.default_content()
    print('발행 완료! URL:', driver.current_url)


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'help'
    if mode == 'start':
        start_chrome()
    elif mode == 'post' and len(sys.argv) > 2:
        meta, lines, base_dir = parse_post_file(sys.argv[2])
        post_to_naver(meta, lines, base_dir, dry='--dry' in sys.argv)
    else:
        print('사용법: python naver_blog_poster.py start | post <글파일.txt> [--dry]')
