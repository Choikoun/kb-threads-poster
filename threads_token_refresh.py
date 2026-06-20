#!/usr/bin/env python3
"""
Threads 액세스 토큰 자동 갱신
만료 전 새 60일짜리 토큰으로 교환 → GitHub Secret 자동 업데이트
"""
import os, sys, requests, base64
sys.stdout.reconfigure(encoding='utf-8')

CURRENT_TOKEN = os.environ['THREADS_ACCESS_TOKEN']
GH_PAT = os.environ['GH_PAT']
REPO = os.environ.get('GITHUB_REPOSITORY', 'Choikoun/kb-threads-poster')


def refresh_token():
    r = requests.get('https://graph.threads.net/refresh_access_token',
                     params={'grant_type': 'th_refresh_token',
                             'access_token': CURRENT_TOKEN}, timeout=30)
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

    pk_resp = requests.get(
        f'https://api.github.com/repos/{REPO}/actions/secrets/public-key',
        headers=headers, timeout=15)
    pk_data = pk_resp.json()

    pk = PublicKey(pk_data['key'].encode(), encoder=Base64Encoder)
    encrypted = SealedBox(pk).encrypt(new_token.encode())
    encrypted_b64 = base64.b64encode(encrypted).decode()

    r = requests.put(
        f'https://api.github.com/repos/{REPO}/actions/secrets/THREADS_ACCESS_TOKEN',
        headers=headers,
        json={'encrypted_value': encrypted_b64, 'key_id': pk_data['key_id']},
        timeout=15)

    if r.status_code in (201, 204):
        print('GitHub Secret 업데이트 완료!')
    else:
        print(f'Secret 업데이트 실패: {r.text}')
        sys.exit(1)


def main():
    print('Threads 토큰 갱신 중...')
    new_token = refresh_token()
    update_github_secret(new_token)


if __name__ == '__main__':
    main()
