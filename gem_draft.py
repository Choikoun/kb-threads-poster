#!/usr/bin/env python3
"""
Gemini Gem("SEO블로그 제작 gem")으로 블로그 초안 생성 (자동화 크롬 9222, 구글 로그인 유지됨)
사용: python gem_draft.py "키워드" [out.txt] [--extra "추가 조건"] [--facts-file 사실자료.txt] [--custom]
- 모델을 3.1 Pro로 바꿔서 실행 (Flash-Lite는 분량·품질 부족)
- 결과는 초안일 뿐: 세법·보험 숫자는 반드시 검산 후 naver.txt로 정리할 것 (메모리 feedback_blog_gem_workflow)
"""
import sys, time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import naver_blog_poster as nb

sys.stdout.reconfigure(encoding='utf-8')
GEM = 'https://gemini.google.com/gem/20d720618964'
MASK = '--mask' in sys.argv
NOPRO = '--nopro' in sys.argv
MASK_MAP = [('가업승계', 'GS'), ('증여', 'ZY'), ('상속', 'SS')]
MASK_LEGEND = ('[용어 표기 규칙] 이 요청에서 ZY는 부모 등이 재산을 무상으로 넘겨주는 것(증여)을, SS는 사망으로 재산이 넘어가는 것(상속)을, GS는 가업을 물려주는 것을 뜻하는 약어입니다. '
               '글에서도 이 약어를 그대로(ZY, SS, GS, 예: ZY세, ZY재산공제) 쓰고 풀어쓰지 마세요.')


def mask(t):
    for a, b in MASK_MAP:
        t = t.replace(a, b)
    return t


def unmask(t):
    for a, b in MASK_MAP:
        t = t.replace(b, a)
    return t


CUSTOM = '--custom' in sys.argv  # 재무 글용 기본조건 대신 --extra/--facts-file 내용만 사용(다른 주제 글)

BASE_COND = ("[작성 조건] 모바일에서 편하게 읽히고 훑어만 봐도 핵심이 이해되게 쓴다. "
             "1) 결론부터: 도입 2~3문장에 이 글이 답하는 질문과 핵심 결론(기준 숫자)을 먼저 제시, 긴 인사말·배경 설명으로 시작 금지. "
             "2) 문단은 짧게: 한 문단에 핵심 하나, 1~3문장. 모든 문장을 한 줄씩 끊지는 말 것. "
             "3) 소제목만 읽어도 흐름이 보이게: 내용이 바뀔 때마다 짧고 구체적인 소제목(추상적 '주의사항' 금지, 예: '가입 전에 확인할 세 가지'). 6~7개. "
             "4) 내용에 맞는 형식: 설명은 짧은 문단, 여러 조건·확인 항목은 목록(순서 있으면 번호), 표는 꼭 필요한 비교에만 쓰고 가로로 긴 표는 피할 것. "
             "5) 굵게 표시는 핵심 결론과 꼭 기억할 표현만. 문단 전체 굵게, 이모지·강조 남발 금지. "
             "6) 쉽게 쓰되 정확하게: 전문용어는 처음 나올 때 쉬운 말로 풀고, 반복 설명·의미 없는 연결 문장은 줄이되 중요한 조건·예외·위험을 생략하거나 단정적으로 바꾸지 말 것. 사실자료에 없는 사실·사례를 임의로 추가하지 말 것. "
             "마지막에 '핵심 정리'를 3개 이내 항목으로 넣고, 그 뒤에 독자에게 질문을 던지는 후킹 한 문장으로 끝낼 것. 차분하고 신뢰감 있는 문체. "
             "분량 공백 제외 3,500자 안팎, 대상은 사업주·자산가, 숫자가 들어간 구체적 계산 사례 1~2개(가상 인물 A씨, 가정임을 명시). "
             "출처 표기, 각주, 인용 마커, '집품' 같은 군더더기 금지. 확실하지 않은 세법·보험 수치는 쓰지 말고 현행 기준만 사용. "
             "특정 보험사·상품명 언급 금지, 가입 권유 금지, 거친 표현 금지. 상담 링크 자리표시자는 쓰지 말 것. "
             "[말투] AI가 쓴 티가 나지 않게: 'A가 아니라 B입니다' 대조 공식으로 도입을 열지 말고 질문이나 구체적 상황으로 열 것. "
             "'~입니다'를 중심으로 하되 '~죠', '~거든요', '~더라고요' 같은 구어를 문단당 한 번쯤 섞고, 문장 길이를 일부러 들쭉날쭉하게(아주 짧은 문장도 섞기). "
             "'~하는 것이 먼저입니다', '각별히 주목', '하늘과 땅 차이', '~를 고민하시는 분들이라면', '~에 대해 알아보겠습니다' 같은 정형 문구 금지. "
             "면책 문구는 글 끝에 한 번만. 모든 항목을 '· 항목: 설명' 병렬 목록으로 만들지 말고 일부는 줄글로 풀 것.")


def draft(keyword, extra=''):
    d = nb.get_driver()
    d.get(GEM)
    time.sleep(4)
    # 모델 3.1 Pro 선택 (--nopro: 전환 생략. Pro가 보험·세금 주제를 거절하는 경우가 있어 기본 모델로 시도)
    if not NOPRO:
        d.execute_script("[...document.querySelectorAll('button')].find(b=>b.offsetParent&&/Flash|Pro/.test(b.innerText))?.click()")
        time.sleep(1)
        d.execute_script("[...document.querySelectorAll('button,[role=menuitem]')].find(e=>e.offsetParent&&e.innerText.includes('3.1 Pro'))?.click()")
        time.sleep(1)
        d.get(GEM)
        time.sleep(4)
    prompt = keyword + '\n' + (extra if CUSTOM else BASE_COND + ((' ' + extra) if extra else ''))
    box = d.find_element(By.CSS_SELECTOR, 'div.ql-editor')
    box.click()
    lines = prompt.split('\n')
    for i, l in enumerate(lines):
        box.send_keys(l)
        if i < len(lines) - 1:
            box.send_keys(Keys.SHIFT, Keys.ENTER)
    time.sleep(0.5)
    box.send_keys(Keys.ENTER)
    prev, t, stable = -1, '', 0
    for i in range(120):
        time.sleep(5)
        try:
            d.title
        except Exception:
            d = nb.get_driver()
        t = d.execute_script("const m=document.querySelectorAll('model-response,message-content');return m.length?m[m.length-1].innerText:''")
        stable = stable + 1 if (len(t) == prev and len(t) > 0) else 0
        if len(t) > 1500 and stable >= 1:
            break
        if 0 < len(t) < 400 and stable >= 3 and i >= 5:  # 짧은 응답이 멈춰 있으면 거절/오류 응답 → 오래 기다리지 말고 즉시 반환
            print('Gem 거절/짧은 응답:', t[:80])
            break
        prev = len(t)
    return unmask(t) if MASK else t


if __name__ == '__main__':
    kw = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else '_gem_draft.txt'
    extra = sys.argv[sys.argv.index('--extra') + 1] if '--extra' in sys.argv else ''
    if '--facts-file' in sys.argv:  # 사실자료(기사 요약·수치) 파일을 Gem에 넘겨 그 내용만으로 글을 쓰게 함
        facts = ' '.join(open(sys.argv[sys.argv.index('--facts-file') + 1], encoding='utf-8').read().split())
        extra = (extra + ' ' if extra else '') + ('[사실자료 — 이 자료에 있는 사실·수치만 사용하고, 없는 내용은 지어내지 말 것. 확정되지 않은 사항은 "확정되지 않았다"고 쓸 것] ' + facts)
    text = draft(kw, extra)
    for _try in range(4):  # 거절은 확률적(같은 입력도 되다 안 되다 함) → 새 대화로 재시도
        if len(text) >= 400:
            break
        print('재시도', _try + 1)
        time.sleep(3)
        text = draft(kw, extra)
    open(out, 'w', encoding='utf-8').write(text)
    print(len(text), '자 →', out)
