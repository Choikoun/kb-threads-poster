#!/usr/bin/env python3
"""티스토리 고정 페이지(소개·면책·문의) 등록 — 익명 운영 유지(실명·소속 회사명 없음).
사용: python tistory_pages_poster.py [소개|면책|문의 ...]  (인자 없으면 3개 모두)
이미 같은 제목의 페이지가 있으면 건너뜀."""
import sys, time
sys.argv_saved = sys.argv[:]
import naver_blog_poster as nb
import tistory_poster as tp
sys.stdout.reconfigure(encoding='utf-8')

LINK = 'https://naver.me/FRLbSbiJ'

PAGES = {
    '소개': ('블로그 소개', """
<h2>이 블로그는 이런 곳입니다</h2>
<p>사업을 하거나 자산을 관리하는 분들이 한 번쯤 부딪히는 돈 문제를 정리하는 정보 블로그입니다. 법인 자금(퇴직금·배당·보험), 증여·상속, 연금과 보험 뉴스를 다룹니다.</p>
<h2>누가 쓰나요</h2>
<p>금융·보험 분야에서 일하는 실무자가 운영합니다. 이름과 소속은 공개하지 않습니다. 광고나 홍보가 아니라 글의 정확성으로 평가받고 싶기 때문입니다.</p>
<h2>글을 쓰는 원칙</h2>
<ol>
<li>국세청, 법령, 금융감독원 같은 공식 자료를 기준으로 씁니다.</li>
<li>확정된 사실과 아직 전망인 내용을 구분해서 씁니다.</li>
<li>계산 사례는 가상 인물과 가정 숫자를 쓰고, 가정이라고 표시합니다.</li>
<li>세법이나 제도가 바뀌면 글을 갱신하고 날짜를 남깁니다.</li>
<li>특정 상품의 가입이나 해지를 권유하지 않습니다.</li>
</ol>
<h2>다루는 주제</h2>
<ul>
<li>법인 자금: 대표이사 퇴직금, 배당, 가지급금, 법인 보험</li>
<li>증여·상속: 증여세율, 공제, 가족 간 자금 이동</li>
<li>연금·보험: 퇴직연금, IRP, 즉시연금, 종신보험과 제도 변화</li>
</ul>
<h2>문의</h2>
<p>글 내용에 대한 정정 요청이나 문의는 <a href="/pages/%EB%AC%B8%EC%9D%98">문의 페이지</a>를 참고해 주세요.</p>
"""),
    '면책': ('면책 고지', """
<h2>정보 제공 목적의 글입니다</h2>
<p>이 블로그의 글은 일반적인 정보 제공을 위한 것이며, 세무·법률·투자·보험 가입에 대한 개별 자문이 아닙니다. 같은 제도라도 개인의 소득, 자산, 가입 시점, 계약 조건에 따라 결과가 달라질 수 있습니다.</p>
<h2>세법과 제도는 바뀝니다</h2>
<p>글에 적힌 세율, 한도, 요건은 작성 시점 기준입니다. 개정되거나 해석이 달라질 수 있으니 실제 신고나 계약 전에는 국세청, 관련 기관, 상품설명서, 세무사 같은 전문가를 통해 최신 내용을 확인하세요.</p>
<h2>사례와 계산에 대해</h2>
<p>글에 나오는 인물(A씨 등)과 숫자는 구조를 설명하기 위한 가정입니다. 실제 상품의 수령액이나 세액과 다를 수 있습니다.</p>
<h2>보도와 전망에 대해</h2>
<p>언론 보도나 업계 전망을 인용한 내용은 확정된 사실이 아닐 수 있고, 글에서 확정과 전망을 구분해 표시합니다.</p>
<h2>상품 권유 금지</h2>
<p>이 블로그는 특정 금융상품의 가입이나 해지를 권유하지 않습니다. 이 글을 근거로 한 결정에 대한 책임은 이용자에게 있습니다.</p>
<h2>외부 링크</h2>
<p>글에 포함된 외부 링크의 내용은 해당 사이트의 책임이며, 링크 이후 이용 중 생기는 문제에 대해 책임지지 않습니다.</p>
"""),
    '문의': ('문의', """
<h2>문의와 정정 요청</h2>
<p>글의 내용이 사실과 다르거나 최신 제도와 다르다고 생각되면 알려 주세요. 확인 후 글을 고치고 수정 날짜를 남깁니다.</p>
<ul>
<li>정정 요청: 해당 글의 댓글로 남겨 주세요.</li>
<li>내 상황에 맞춘 상담이 필요하신 경우: <a href="%s" target="_blank" rel="noopener">상담 신청하기</a></li>
</ul>
<h2>안내</h2>
<p>댓글과 상담 신청으로 받은 개인정보는 문의 응대 외 목적으로 사용하지 않습니다. 개인의 주민등록번호나 계좌번호 같은 민감한 정보는 남기지 마세요.</p>
""" % LINK),
}


def exists(driver, title):
    driver.get('https://freedom-of-economic.tistory.com/manage/pages')
    time.sleep(4)
    rows = driver.execute_script("return [...document.querySelectorAll('tr, li')].map(e=>e.innerText.split(String.fromCharCode(10)).map(x=>x.trim()))")
    return any(title in r and r.index(title) >= 0 and title == t for r in rows for t in r)


def _wait_editor(driver):
    for _ in range(30):
        time.sleep(1)
        if driver.execute_script("return typeof tinymce!=='undefined' && !!tinymce.activeEditor && !!tinymce.activeEditor.getBody()"):
            break
    time.sleep(3)
    tp._dismiss_alert(driver)


def post_page(driver, title, html, page_id=None):
    """새 페이지(page_id 없음) 또는 기존 페이지 수정. 에디터 준비를 기다리고, 본문 입력 후 동기화 이벤트를 발생시켜야 저장된다."""
    url = 'https://freedom-of-economic.tistory.com/manage/page' + (f'/{page_id}' if page_id else '')
    driver.get(url)
    _wait_editor(driver)
    if not page_id:
        tp.set_title(driver, title)
    driver.execute_script("const ed=tinymce.activeEditor; ed.focus(); ed.setContent(arguments[0]); ed.undoManager.add(); ed.fire('input'); ed.fire('keyup'); ed.fire('change'); ed.nodeChanged(); tinymce.triggerSave();", html.strip())
    time.sleep(1)
    driver.find_element(tp.By.ID, 'publish-layer-btn').click()
    time.sleep(1.5)
    driver.execute_script("const r=document.querySelector('#open20'); if(r){r.click(); r.dispatchEvent(new Event('change',{bubbles:true}));}")
    time.sleep(0.5)
    driver.find_element(tp.By.ID, 'publish-btn').click()
    time.sleep(6)


if __name__ == '__main__':
    keys = sys.argv_saved[1:] or list(PAGES)
    d = nb.get_driver()
    tp.ensure_login(d)
    for k in keys:
        title, html = PAGES[k]
        if exists(d, title):
            print('이미 있음, 건너뜀:', title)
            continue
        post_page(d, title, html)
        print('등록 시도:', title, '→ 확인:', exists(d, title))
