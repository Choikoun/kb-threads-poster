#!/usr/bin/env python3
"""
Gemini Gem("SEO블로그 제작 gem")으로 블로그 초안 생성 (자동화 크롬 9222, 구글 로그인 유지됨)
사용: python gem_draft.py "키워드" [out.txt] [--extra "추가 조건"] [--facts-file 사실자료.txt]
- 모델을 3.1 Pro로 바꿔서 실행 (Flash-Lite는 분량·품질 부족)
- 결과는 초안일 뿐: 세법·보험 숫자는 반드시 검산 후 naver.txt로 정리할 것 (메모리 feedback_blog_gem_workflow)
"""
import sys, time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import naver_blog_poster as nb

sys.stdout.reconfigure(encoding='utf-8')
GEM = 'https://gemini.google.com/gem/20d720618964'

BASE_COND = ("[작성 조건] 분량 공백 제외 4,000자 이상. 서론에서 핵심 결론(기준 숫자)을 먼저 제시. 대상은 사업주·자산가. "
             "숫자가 들어간 구체적 계산 사례를 최소 2개 포함(가상 인물 A씨). 소제목 6~7개를 단정적인 문장으로. "
             "출처 표기, 각주, 인용 마커, '집품' 같은 군더더기 문구는 쓰지 말 것. 확실하지 않은 세법·보험 수치는 쓰지 말고 현행 기준만 사용. "
             "특정 보험사·상품명 언급 금지, 가입 권유 금지. 거친 표현(하수 등) 금지. "
             "마지막은 독자에게 질문을 던지는 후킹 문장으로 끝낼 것. 상담 링크 자리표시자는 쓰지 말 것.")


def draft(keyword, extra=''):
    d = nb.get_driver()
    d.get(GEM)
    time.sleep(4)
    # 모델 3.1 Pro 선택
    d.execute_script("[...document.querySelectorAll('button')].find(b=>b.offsetParent&&/Flash|Pro/.test(b.innerText))?.click()")
    time.sleep(1)
    d.execute_script("[...document.querySelectorAll('button,[role=menuitem]')].find(e=>e.offsetParent&&e.innerText.includes('3.1 Pro'))?.click()")
    time.sleep(1)
    d.get(GEM)
    time.sleep(4)
    prompt = keyword + '\n' + BASE_COND + ((' ' + extra) if extra else '')
    box = d.find_element(By.CSS_SELECTOR, 'div.ql-editor')
    box.click()
    lines = prompt.split('\n')
    for i, l in enumerate(lines):
        box.send_keys(l)
        if i < len(lines) - 1:
            box.send_keys(Keys.SHIFT, Keys.ENTER)
    time.sleep(0.5)
    box.send_keys(Keys.ENTER)
    prev, t = -1, ''
    for _ in range(120):
        time.sleep(5)
        try:
            d.title
        except Exception:
            d = nb.get_driver()
        t = d.execute_script("const m=document.querySelectorAll('model-response,message-content');return m.length?m[m.length-1].innerText:''")
        if len(t) > 1500 and len(t) == prev:
            break
        prev = len(t)
    return t


if __name__ == '__main__':
    kw = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else '_gem_draft.txt'
    extra = sys.argv[sys.argv.index('--extra') + 1] if '--extra' in sys.argv else ''
    if '--facts-file' in sys.argv:  # 사실자료(기사 요약·수치) 파일을 Gem에 넘겨 그 내용만으로 글을 쓰게 함
        facts = open(sys.argv[sys.argv.index('--facts-file') + 1], encoding='utf-8').read().strip().replace('
', ' ')
        extra = (extra + ' ' if extra else '') + ('[사실자료 — 이 자료에 있는 사실·수치만 사용하고, 없는 내용은 지어내지 말 것. 확정되지 않은 사항은 "확정되지 않았다"고 쓸 것] ' + facts)
    text = draft(kw, extra)
    open(out, 'w', encoding='utf-8').write(text)
    print(len(text), '자 →', out)
