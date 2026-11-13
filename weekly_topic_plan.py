#!/usr/bin/env python3
"""주 1회 주제 후보 일괄 평가 → topic_plan.json (매일은 이 목록에서 고르기만 한다).
사용: python weekly_topic_plan.py [키워드...]   (키워드 생략 시 topic_candidates.txt 한 줄에 하나)
순서: ①이미 발행한 글과 겹치는 키워드 제외(blog_posts.json 제목 대조) ②검색량·문서수·비율 ③비율 상위만 상위10 경쟁 분석(소규모 블로그 수)
기준: 소규모 = 총글 150 미만 또는 개설 1년 미만 또는 이웃 300 미만. 점수 = 비율 우선, 소규모 수로 보정. 출력은 요약 표 한 장."""
import sys, os, json, datetime
sys.stdout.reconfigure(encoding='utf-8')
from keyword_check import search_volume
from kw_research import doc_count
import competitor_check as cc

OUT = 'topic_plan.json'
TOP_ANALYZE = 6


def published_titles():
    d = json.load(open('blog_posts.json', encoding='utf-8'))
    d = d if isinstance(d, list) else d.get('posts', d)
    return [(x['date'], x['title']) for x in d]


def is_small(r):
    try:
        posts = int(r.get('posts') or 0); buddies = int(r.get('buddies') or 0)
    except Exception:
        return False
    fp = r.get('first_post')
    young = False
    if fp:
        try:
            young = (datetime.datetime.now() - datetime.datetime.strptime(fp, '%Y-%m-%d')).days < 365
        except Exception:
            pass
    return posts < 150 or young or buddies < 300


def main():
    kws = sys.argv[1:] or [l.strip() for l in open('topic_candidates.txt', encoding='utf-8') if l.strip()]
    titles = published_titles()
    rows = []
    vol = {}
    for i in range(0, len(kws), 5):
        for r in search_volume(kws[i:i + 5]):
            vol[r['keyword']] = r
    for k in kws:
        dup = [f'{d} {t[:24]}' for d, t in titles if k.replace(' ', '') in t.replace(' ', '')]
        v = vol.get(k.replace(' ', ''))
        total = v['total'] if v else 0
        docs = doc_count(k)
        rows.append({'keyword': k, 'volume': total, 'docs': docs, 'ratio': round(total / docs, 4) if docs else 0, 'published': dup})
    fresh = [r for r in rows if not r['published'] and r['volume'] >= 100]
    fresh.sort(key=lambda r: -r['ratio'])
    for r in fresh[:TOP_ANALYZE]:
        res = cc.run(r['keyword'])
        top = res['top']
        r['small_in_top10'] = sum(1 for x in top if is_small(x))
        r['mine_rank'] = res['mine_rank']
    out = {'date': datetime.date.today().isoformat(), 'rows': rows}
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('키워드 | 검색량 | 문서수 | 비율 | 소규모(10위중) | 비고')
    for r in sorted(rows, key=lambda r: (bool(r['published']), -r['ratio'])):
        note = ('기발행 ' + r['published'][0]) if r['published'] else ('검색량 100 미만 제외' if r['volume'] < 100 else '')
        print(f"{r['keyword']} | {r['volume']} | {r['docs']} | {r['ratio']} | {r.get('small_in_top10', '-')} | {note}")


if __name__ == '__main__':
    main()
