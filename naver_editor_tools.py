#!/usr/bin/env python3
"""네이버 스마트에디터 ONE 툴바 도구 사용 모듈 (사용자 요청 2026-10-18: 편집기 도구를 써서 보기 좋게).
원고 표기법(naver.txt)
  **소제목**          한 줄 전체가 ** 로 감싸진 줄 → 문단 서식 '소제목'(제목 구조·큰 글씨)
  > 문장              연속된 줄 → 인용구 박스(인용구 2: 세로선). 요약·핵심 정리·훅 박스용
  [구분선]            한 줄 → 구분선
  ==강조할 말==       노란 배경(#fff8b2) 강조. 글당 최대 3곳 권장
  [표시문구](주소)    링크(출처는 주소를 노출하지 말고 제목에 링크)
인라인 별표 강조(**문장 중간**)는 쓰지 않는다(ai_tell_check 가 오류 처리).
"""
import re, time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import naver_blog_poster as nb

HILITE = '#fff8b2'
TOKEN_RE = re.compile(r'(\*\*[^*]+\*\*|==[^=]+==|\[[^\]]+\]\(https?://[^)\s]+\))')
HEAD_FULL = re.compile(r'^\*\*([^*]+)\*\*$')
LINK_RE = re.compile(r'^\[([^\]]+)\]\((https?://[^)\s]+)\)$')


def tb(driver, cls, wait=0.8):
    b = driver.find_element(By.CSS_SELECTOR, 'button.' + cls)
    nb.js_click(driver, b)
    time.sleep(wait)


def select_back(driver, n):
    ac = ActionChains(driver)
    ac.key_down(Keys.SHIFT)
    for _ in range(n):
        ac.send_keys(Keys.ARROW_LEFT)
    ac.key_up(Keys.SHIFT).perform()
    time.sleep(0.3)


def _click_swatch(driver, color=None, none=False):
    js = ("const want=arguments[0], none=arguments[1];"
          "const bs=[...document.querySelectorAll('button.se-color-palette')].filter(x=>x.offsetParent);"
          "const b=none? bs.find(x=>x.className.includes('no-color')) : bs.find(x=>x.getAttribute('data-color')===want);"
          "if(b){b.click();return true;} return false;")
    ok = driver.execute_script(js, color, none)
    time.sleep(0.5)
    return ok


def highlight_last(driver, n):
    """방금 입력한 n글자에 노란 배경. 이후 입력이 배경을 이어받지 않게 커서 위치의 배경색은 해제."""
    select_back(driver, n)
    tb(driver, 'se-background-color-toolbar-button', 0.8)
    if not _click_swatch(driver, HILITE):
        raise RuntimeError('배경색 팔레트에서 강조색을 못 찾음')
    nb.send(driver, Keys.ARROW_RIGHT)
    time.sleep(0.2)
    tb(driver, 'se-background-color-toolbar-button', 0.6)
    _click_swatch(driver, none=True)


def link_last(driver, n, url):
    """방금 입력한 n글자에 링크."""
    select_back(driver, n)
    tb(driver, 'se-link-toolbar-button', 1.0)
    inp = driver.find_element(By.CSS_SELECTOR, 'input.se-custom-layer-link-input')
    inp.click()
    inp.send_keys(url)
    time.sleep(0.4)
    tb(driver, 'se-custom-layer-link-apply-button', 1.0)
    nb.send(driver, Keys.ARROW_RIGHT)
    time.sleep(0.2)


def type_inline(driver, line):
    """한 줄을 입력. ==강조==, [문구](주소), (레거시) **굵게** 토큰 처리. 줄바꿈은 호출 쪽에서."""
    for tok in TOKEN_RE.split(line):
        if not tok:
            continue
        if tok.startswith('==') and tok.endswith('=='):
            t = tok[2:-2]
            nb.send(driver, t)
            highlight_last(driver, len(t))
        elif LINK_RE.match(tok):
            m = LINK_RE.match(tok)
            nb.send(driver, m.group(1))
            link_last(driver, len(m.group(1)), m.group(2))
        elif tok.startswith('**') and tok.endswith('**'):
            nb.send_chord(driver, Keys.CONTROL, 'b')
            nb.send(driver, tok[2:-2])
            nb.send_chord(driver, Keys.CONTROL, 'b')
        else:
            nb.send(driver, tok)


def heading(driver, text):
    """문단 서식 '소제목'으로 입력. 다음 문단은 자동으로 본문으로 돌아온다."""
    tb(driver, 'se-text-format-toolbar-button', 0.8)
    ok = driver.execute_script(
        "const e=[...document.querySelectorAll('button,li,span')].filter(x=>x.offsetParent&&(x.innerText||'').trim()==='소제목')[0];"
        "if(e){e.click();return true;} return false;")
    time.sleep(0.8)
    if not ok:
        raise RuntimeError("문단 서식 '소제목' 항목을 못 찾음")
    nb.send(driver, text)
    nb.send(driver, Keys.ENTER)
    time.sleep(0.4)


def divider(driver):
    tb(driver, 'se-insert-horizontal-line-default-toolbar-button', 1.0)


def quote_box(driver, block_lines, style='quotation_line'):
    """인용구 박스. 뒤에 빈 문단을 먼저 만들어 두어야 아래로 빠져나올 수 있다.
    현재 커서는 비어 있는 새 문단이어야 한다. 본문 마지막 줄에서 ArrowDown 2번(출처칸 → 다음 문단)."""
    nb.send(driver, Keys.ENTER)
    time.sleep(0.3)
    nb.send(driver, Keys.ARROW_UP)
    time.sleep(0.3)
    tb(driver, 'se-insert-quotation-default-toolbar-button', 1.2)
    tb(driver, f'se-quotation-{style}-toolbar-button', 1.0)
    for i, ln in enumerate(block_lines):
        if i:
            nb.send(driver, Keys.ENTER)
        # 인용구 안에서는 툴바가 인용구 전용이라 배경색·링크 버튼이 없다 → 표기만 걷어내고 평문으로 입력
        type_inline(driver, nb._plain(ln))
    nb.send(driver, Keys.ARROW_DOWN)
    time.sleep(0.3)
    nb.send(driver, Keys.ARROW_DOWN)
    time.sleep(0.4)


def _count(driver):
    return driver.execute_script("return document.querySelectorAll('.se-component').length")


def set_line_height(driver, pct=180, debug=False):
    """본문 전체에 줄간격 적용(마지막에 한 번). 선택 → 줄간격 버튼 → 옵션."""
    paras = driver.find_elements(By.CSS_SELECTOR, '.se-section-text .se-text-paragraph')
    if not paras:
        return
    n0 = _count(driver)
    time.sleep(1.0)
    if debug: print('LH0 컴포넌트', n0)
    nb.safe_click(driver, paras[0])
    if debug: print('LH1 클릭 후', _count(driver))
    nb.send_chord(driver, Keys.CONTROL, 'a')
    time.sleep(0.4)
    if debug: print('LH2 전체선택 후', _count(driver))
    tb(driver, 'se-line-height-toolbar-button', 0.9)
    if debug: print('LH3 버튼 후', _count(driver), driver.execute_script("return [...document.querySelectorAll('button,li')].filter(x=>x.offsetParent&&/^1[5-9]0%$|^2[01]0%$/.test((x.innerText||'').trim())).length"))
    ok = driver.execute_script(
        "const t=arguments[0];"
        "const e=[...document.querySelectorAll('button,li,span')].filter(x=>x.offsetParent&&(x.innerText||'').trim()===t)[0];"
        "if(e){e.click();return true;} return false;", f'{pct}%')
    time.sleep(0.6)
    if debug: print('LH4 옵션 클릭 후', _count(driver), ok)
    nb.send(driver, Keys.ARROW_RIGHT)
    if debug: print('LH5 끝', _count(driver))
    if _count(driver) < n0:
        raise RuntimeError(f'줄간격 적용 중 본문 컴포넌트가 줄었습니다({n0}→{_count(driver)}) — 발행 중단')
    return ok
