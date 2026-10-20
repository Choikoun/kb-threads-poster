#!/usr/bin/env python3
"""티스토리·카카오 로그인 유지 도구 (2026-10-20: 크롬 재시작마다 로그인이 풀리던 문제).
원인: 티스토리/카카오 로그인 쿠키(_T_, TSSESSION, _kawlt, _kawltea 등)가 '세션 쿠키'라 크롬이 꺼지면 사라진다.
해결: 로그인된 상태에서 세션 쿠키에 만료일(기본 30일)을 붙여 다시 저장 → 디스크에 영구 저장돼 재시작 후에도 유지.
비밀번호는 다루지 않고, 쿠키는 크롬 프로필(naver_chrome_profile) 안에만 있으며 파일로 내보내지 않는다.
사용: python login_keepalive.py persist | check
한계: 카카오·티스토리 서버가 세션을 만료시키면 소용없다(그때는 사용자가 한 번 로그인)."""
import sys, time
sys.stdout.reconfigure(encoding='utf-8')
DOMAINS = ('tistory.com', 'kakao.com', 'daum.net')
DAYS = 30


def persist(driver, days=DAYS):
    cs = driver.execute_cdp_cmd('Network.getAllCookies', {})['cookies']
    exp = time.time() + days * 86400
    n = 0
    for c in cs:
        if not any(c['domain'].lstrip('.').endswith(d) for d in DOMAINS):
            continue
        if not (c.get('session') or c.get('expires', -1) <= 0):
            continue
        p = {'name': c['name'], 'value': c['value'], 'domain': c['domain'], 'path': c.get('path', '/'),
             'secure': c.get('secure', False), 'httpOnly': c.get('httpOnly', False), 'expires': exp}
        if c.get('sameSite'):
            p['sameSite'] = c['sameSite']
        try:
            if driver.execute_cdp_cmd('Network.setCookie', p).get('success'):
                n += 1
        except Exception:
            pass
    return n


def logged_in(driver):
    driver.get('https://www.tistory.com/')
    time.sleep(2)
    u = driver.current_url
    body = driver.execute_script("return document.body.innerText.slice(0,400)")
    return 'auth/login' not in u and 'accounts.kakao' not in u and '로그인' not in body.split('\n')[0:3].__str__()


if __name__ == '__main__':
    import naver_blog_poster as nb
    d = nb.get_driver()
    if sys.argv[1] == 'persist':
        print('영구화한 세션 쿠키:', persist(d))
    else:
        d.get('https://www.tistory.com/manage/newpost')
        time.sleep(3)
        print('로그인 유지됨' if 'auth/login' not in d.current_url and 'accounts.kakao' not in d.current_url else '로그인 풀림', d.current_url[:60])
