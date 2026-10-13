#!/usr/bin/env python3
"""채널·글별로 구분되는 쿠팡 파트너스 링크 생성 (수익 페이지의 채널별 집계용)
사용: python shop_links.py <채널> <글키> <쿠팡 상품 URL> [...]
  채널: blog | threads | ig      글키: 영문·숫자·_ (예: gitden)  → subId = <채널>_<글키>
예) python shop_links.py blog gitden https://www.coupang.com/vp/products/9744199289
"""
import sys
import coupang_api as c
sys.stdout.reconfigure(encoding='utf-8')
CHANNELS = ('blog', 'threads', 'ig')


def make(urls, channel, key):
    assert channel in CHANNELS, f'채널은 {CHANNELS} 중 하나'
    code, j = c.deeplink(urls, sub_id=f'{channel}_{key}')
    return [d['shortenUrl'] for d in j.get('data', [])] if code == 200 else []


if __name__ == '__main__':
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    for u, s in zip(sys.argv[3:], make(sys.argv[3:], sys.argv[1], sys.argv[2])):
        print(s, '←', u)
