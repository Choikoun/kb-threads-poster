#!/usr/bin/env python3
"""쿠팡 파트너스 수익 리포트 (Open API reports) — 채널/글별(subId) 집계
사용: python coupang_report.py [시작YYYYMMDD] [종료YYYYMMDD]   (기본: 최근 30일)
- 클릭·주문·취소·수수료를 subId별로 합산. 취소분은 차감. subId가 비어 있으면 '(없음)'으로 묶임
- 새 링크는 coupang_api.deeplink(urls, sub_id='blog_글키')로 만들면 글별로 구분됨
"""
import sys, requests
from datetime import datetime, timedelta
from collections import defaultdict
import coupang_api as c
sys.stdout.reconfigure(encoding='utf-8')


def get(ep, s, e):
    p = c.BASE + '/reports/' + ep
    q = f'startDate={s}&endDate={e}'
    r = requests.get(c.HOST + p + '?' + q, headers={'Authorization': c._auth('GET', p, q), 'Content-Type': 'application/json'}, timeout=30)
    j = r.json()
    return j.get('data', []) if j.get('rCode') == '0' else []


CH = {'blog': '블로그', 'threads': '쓰레드', 'ig': '인스타그램'}


def channel_of(sub):
    """subId 접두어로 채널 구분: blog_* / threads_* / ig_* , 없으면 미구분"""
    return next((v for k, v in CH.items() if (sub or '').startswith(k + '_')), '미구분')


def iso(d):
    return f'{d[:4]}-{d[4:6]}-{d[6:]}'


def export(s, e, outdir):
    """수익 페이지용 JSON 두 개 생성: coupang_daily.json, coupang_orders.json"""
    import json
    daily = [{'date': iso(x['date']), 'channel': channel_of(x.get('subId')), 'subId': x.get('subId') or '(없음)',
              'click': x.get('click', 0), 'order': x.get('order', 0), 'cancel': x.get('cancel', 0),
              'gmv': x.get('gmv', 0), 'commission': x.get('commission', 0)} for x in get('commission', s, e)]
    orders = [{'date': iso(o['date']), 'type': '주문', 'channel': channel_of(o.get('subId')), 'product': o['productName'],
               'category': o.get('categoryName', ''), 'gmv': o['gmv'], 'commission': o['commission']} for o in get('orders', s, e)]
    orders += [{'date': iso(o['date']), 'type': '취소', 'channel': channel_of(o.get('subId')), 'product': o['productName'],
                'category': o.get('categoryName', ''), 'gmv': o['gmv'], 'commission': o['commission']} for o in get('cancels', s, e)]
    json.dump(daily, open(outdir + '/coupang_daily.json', 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(orders, open(outdir + '/coupang_orders.json', 'w', encoding='utf-8'), ensure_ascii=False)
    return len(daily), len(orders)


if __name__ == '__main__':
    if len(sys.argv) > 3 and sys.argv[1] == '--export':
        print(export(sys.argv[3], datetime.now().strftime('%Y%m%d'), sys.argv[2]))
        sys.exit()
    e = sys.argv[2] if len(sys.argv) > 2 else datetime.now().strftime('%Y%m%d')
    s = sys.argv[1] if len(sys.argv) > 1 else (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
    agg = defaultdict(lambda: {'click': 0, 'order': 0, 'cancel': 0, 'gmv': 0.0, 'commission': 0.0})
    for row in get('commission', s, e):
        a = agg[channel_of(row.get('subId'))]
        a['click'] += row.get('click', 0); a['order'] += row.get('order', 0); a['cancel'] += row.get('cancel', 0)
        a['gmv'] += row.get('gmv', 0); a['commission'] += row.get('commission', 0)
    print(f'기간 {s}~{e}  (수수료는 취소 차감 후 순액)')
    print(f"{'subId':<22}{'클릭':>6}{'주문':>6}{'취소':>6}{'결제액':>12}{'수수료':>10}")
    tot = [0, 0, 0, 0.0, 0.0]
    for k, a in sorted(agg.items()):
        print(f"{k:<22}{a['click']:>6}{a['order']:>6}{a['cancel']:>6}{a['gmv']:>12,.0f}{a['commission']:>10,.0f}")
        tot = [tot[0] + a['click'], tot[1] + a['order'], tot[2] + a['cancel'], tot[3] + a['gmv'], tot[4] + a['commission']]
    print(f"{'합계':<22}{tot[0]:>6}{tot[1]:>6}{tot[2]:>6}{tot[3]:>12,.0f}{tot[4]:>10,.0f}")
    print('\n[주문 상세]')
    for o in get('orders', s, e):
        print(o['date'], o.get('subId') or '(없음)', o['productName'][:28], f"{o['gmv']:,.0f}원 → {o['commission']:,.0f}원")
    for o in get('cancels', s, e):
        print(o['date'], '취소', o['productName'][:28], f"{o['commission']:,.0f}원")
