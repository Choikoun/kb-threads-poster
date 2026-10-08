#!/usr/bin/env python3
"""구글 서치콘솔 'URL 검사 → 색인 생성 요청' 자동화 (티스토리 새 글 색인 가속). 자동화 크롬의 구글 로그인 사용.
사용: python gsc_index_request.py 290 291 295 ...   (티스토리 글 번호; 하루 약 10건 한도)"""
import naver_blog_poster as nb, time, sys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'https://freedom-of-economic.tistory.com/'
IDX = 'https://search.google.com/search-console/index?resource_id=https%3A%2F%2Ffreedom-of-economic.tistory.com%2F'


def request(d, num):
    d.get(IDX); time.sleep(6)
    box = d.find_element(By.CSS_SELECTOR, 'input[role=combobox]')
    box.click(); box.send_keys(f'{BASE}{num}'); time.sleep(.5); box.send_keys(Keys.ENTER); time.sleep(16)
    t = d.execute_script("return document.body.innerText")
    if 'URL이 Google에 등록되어 있음' in t:
        return '이미 색인됨'
    btn = [e for e in d.find_elements(By.XPATH, "//*[normalize-space(text())='색인 생성 요청']") if e.is_displayed()]
    if not btn:
        return '요청 버튼 없음'
    btn[0].click()
    for _ in range(30):
        time.sleep(4)
        t = d.execute_script("return document.body.innerText")
        if '색인 생성이 요청됨' in t or '색인 생성 요청됨' in t:
            r = '요청 완료'
            break
        if '할당량' in t:
            r = '일일 할당량 초과'
            break
    else:
        r = '결과 미확인'
    for b in d.find_elements(By.XPATH, "//*[normalize-space(text())='확인' or normalize-space(text())='닫기']"):
        try:
            if b.is_displayed():
                b.click(); break
        except Exception:
            pass
    return r


if __name__ == '__main__':
    d = nb.get_driver()
    for n in sys.argv[1:]:
        print(n, request(d, n), flush=True)
        time.sleep(3)
