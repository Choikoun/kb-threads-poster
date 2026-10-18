#!/usr/bin/env python3
"""
Instagram 액세스 토큰 자동 갱신
만료 30일 전 새 60일짜리 토큰으로 교환 → GitHub Secret 자동 업데이트
"""
import os, sys, requests, base64
sys.stdout.reconfigure(encoding='utf-8')

APP_ID = '1488557629676758'
APP_SECRET = os.environ['INSTAGRAM_APP_SECRET']
CURRENT_TOKEN = os.environ['INSTAGRAM_ACCESS_TOKEN']
GH_PAT = os.environ['GH_PAT']
REPO = os.environ.get('GITHUB_REPOSITORY', 'Choikoun/kb-threads-poster')


def refresh_token():
    r = requests.get('https://graph.facebook.com/v21.0/oauth/access_token',
                     params={'grant_type': 'fb_exchange_token',
                             'client_id': APP_ID,
                             'client_secret': APP_SECRET,
                             'fb_exchange_token': CURRENT_TOKEN}, timeout=30)
    if not r.ok:
        print(f'토큰 갱신 실패: {r.text}')
        sys.exit(1)
    data = r.json()
    new_token = data['access_token']
    days = data.get('expires_in', 0) // 86400
    print(f'새 토큰 발급 완료 (유효기간: {days}일)')
    return new_token


def update_github_secret(new_token):
    from nacl.encoding import Base64Encoder
    from nacl.public import PublicKey, SealedBox

    headers = {
        'Authorization': f'Bearer {GH_PAT}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }

    # 공개키 조회
    pk_resp = requests.get(
        f'https://api.github.com/repos/{REPO}/actions/secrets/public-key',
        headers=headers, timeout=15)
    pk_data = pk_resp.json()
    if 'key' not in pk_data:
        print(f'GH_PAT로 secret 공개키 조회 실패: HTTP {pk_resp.status_code} {str(pk_data)[:200]} — GH_PAT 만료/권한 부족 가능(repo 권한 또는 Secrets:write 필요)')
        sys.exit(1)

    # 토큰 암호화
    pk = PublicKey(pk_data['key'].encode(), encoder=Base64Encoder)
    encrypted = SealedBox(pk).encrypt(new_token.encode())
    encrypted_b64 = base64.b64encode(encrypted).decode()

    # Secret 업데이트
    r = requests.put(
        f'https://api.github.com/repos/{REPO}/actions/secrets/INSTAGRAM_ACCESS_TOKEN',
        headers=headers,
        json={'encrypted_value': encrypted_b64, 'key_id': pk_data['key_id']},
        timeout=15)

    if r.status_code in (201, 204):
        print('GitHub Secret 업데이트 완료!')
    else:
        print(f'Secret 업데이트 실패: {r.text}')
        sys.exit(1)


def page_token_for_instagram(user_token):
    """장기 User 토큰으로 /me/accounts 를 조회해 인스타 비즈니스 계정에 연결된 페이지의 Page 토큰을 얻는다.
    장기 User 토큰에서 얻은 Page 토큰은 만료되지 않는다(2026-10-18 User 토큰 60일 만료 사고 대응). 못 찾으면 None."""
    ig_id = os.environ.get('INSTAGRAM_BUSINESS_ACCOUNT_ID', '')
    r = requests.get('https://graph.facebook.com/v21.0/me/accounts',
                     params={'fields': 'id,name,access_token,instagram_business_account{id}',
                             'limit': 100, 'access_token': user_token}, timeout=30)
    if not r.ok:
        print(f'페이지 목록 조회 실패(User 토큰 유지): {r.text[:200]}')
        return None
    pages = r.json().get('data', [])
    print(f'조회된 페이지 {len(pages)}개:', [(pg.get('name'), (pg.get('instagram_business_account') or {}).get('id') == ig_id) for pg in pages])
    try:
        d = requests.get('https://graph.facebook.com/v21.0/debug_token', params={'input_token': user_token, 'access_token': f'{APP_ID}|{APP_SECRET}'}, timeout=30).json().get('data', {})
        print('토큰 권한(scopes):', d.get('scopes'), '/ 만료:', d.get('expires_at'))
    except Exception as e:
        print('debug_token 조회 실패:', e)
    for pg in pages:
        if (pg.get('instagram_business_account') or {}).get('id') == ig_id and pg.get('access_token'):
            print(f"인스타 연결 페이지 확인: {pg.get('name')} (페이지 토큰 사용)")
            return pg['access_token']
    print('인스타 비즈니스 계정에 연결된 페이지를 찾지 못함(User 토큰 유지)')
    return None


def token_expiry(token):
    """debug_token 으로 만료 시각 확인 → (expires_at 초, 0이면 만료 없음) / 실패 시 None"""
    r = requests.get('https://graph.facebook.com/v21.0/debug_token',
                     params={'input_token': token, 'access_token': f'{APP_ID}|{APP_SECRET}'}, timeout=30)
    if not r.ok:
        return None
    return r.json().get('data', {}).get('expires_at')


def main():
    print('Instagram 토큰 갱신 중...')
    user_token = refresh_token()
    final = user_token
    page = page_token_for_instagram(user_token)
    if page:
        exp = token_expiry(page)
        print('페이지 토큰 만료 정보(expires_at, 0이면 무기한):', exp)
        if exp == 0:
            final = page
    if final is user_token:
        print('※ 만료 없는 토큰을 만들지 못해 60일짜리 User 토큰을 저장합니다. 약 55일 뒤 수동 재발급이 필요합니다.')
    ok = update_github_secret(final)
    print('저장한 토큰 종류:', '페이지 토큰(무기한)' if final is not user_token else 'User 장기 토큰(60일)')


if __name__ == '__main__':
    main()
