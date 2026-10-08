#!/usr/bin/env python3
"""쿠팡 파트너스 Open API (쇼핑 리뷰 계정용) — 키는 .env.shop (gitignore)
search(keyword)   → 상품 검색(이름·가격·이미지·제휴링크(productUrl)·로켓배송 여부)
deeplink(urls)    → 쿠팡 상품 URL을 제휴 단축링크로 변환
사용: python coupang_api.py search 탄소매트"""
import os, sys, time, hmac, hashlib, json, requests
from urllib.parse import urlencode
from dotenv import load_dotenv
load_dotenv('.env.shop')
sys.stdout.reconfigure(encoding='utf-8')
HOST = 'https://api-gateway.coupang.com'
BASE = '/v2/providers/affiliate_open_api/apis/openapi/v1'


def _auth(method, path, query=''):
    dt = time.strftime('%y%m%d', time.gmtime()) + 'T' + time.strftime('%H%M%S', time.gmtime()) + 'Z'
    msg = dt + method + path + query
    sig = hmac.new(os.environ['COUPANG_SECRET_KEY'].encode(), msg.encode(), hashlib.sha256).hexdigest()
    return f"CEA algorithm=HmacSHA256, access-key={os.environ['COUPANG_ACCESS_KEY']}, signed-date={dt}, signature={sig}"


def search(keyword, limit=10):
    path = BASE + '/products/search'
    q = urlencode({'keyword': keyword, 'limit': limit})
    r = requests.get(HOST + path + '?' + q, headers={'Authorization': _auth('GET', path, q), 'Content-Type': 'application/json'}, timeout=20)
    return r.status_code, r.json() if r.headers.get('content-type', '').startswith('application/json') else r.text


def deeplink(urls):
    path = BASE + '/deeplink'
    r = requests.post(HOST + path, headers={'Authorization': _auth('POST', path), 'Content-Type': 'application/json'},
                      data=json.dumps({'coupangUrls': urls}), timeout=20)
    return r.status_code, r.json()


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'search':
        code, j = search(sys.argv[2])
        print(code)
        for p in (j.get('data', {}).get('productData', []) if isinstance(j, dict) else [])[:10]:
            print(p.get('productName'), p.get('productPrice'), 'rocket' if p.get('isRocket') else '', p.get('productUrl'))
        if code != 200: print(str(j)[:300])
