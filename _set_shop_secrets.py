"""쇼핑 인스타그램·스레드 토큰을 .env.shop 에서 읽어 깃허브 저장소 시크릿으로 등록한다(값은 화면에 찍지 않는다).
사용자가 직접 실행: python _set_shop_secrets.py
등록 후 shop_scheduled_posts.yml 이 11-07, 11-08 오전 9시 20분(KST)에 인스타그램·스레드에 올린다."""
import subprocess, sys
from dotenv import dotenv_values
sys.stdout.reconfigure(encoding='utf-8')
E = dotenv_values('.env.shop')
for k in ('SHOP_IG_LOGIN_TOKEN', 'SHOP_IG_USER_ID', 'SHOP_THREADS_ACCESS_TOKEN'):
    v = E.get(k)
    if not v:
        sys.exit(f'{k} 가 .env.shop 에 없음')
    r = subprocess.run(['gh', 'secret', 'set', k, '--body', v], capture_output=True, text=True)
    print(k, 'OK' if r.returncode == 0 else 'FAIL ' + r.stderr.strip()[:100])
