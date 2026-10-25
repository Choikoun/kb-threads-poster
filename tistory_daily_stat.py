#!/usr/bin/env python3
"""티스토리 일별 유입 기록 — 검색/SNS/기타 구분, 검색어, 조회 상위 글을 tistory_stats_log.json에 누적.
자동화 크롬(9222)의 티스토리 로그인을 사용한다. 사용: python tistory_daily_stat.py [일수=3]  (어제부터 N일 전까지 갱신)
주의: 통계 trend API는 날짜가 하루 밀려 표기되므로 inflow/topEntry/keyword(날짜 정확)만 쓴다."""
import sys, json, time, os, datetime as dt
sys.stdout.reconfigure(encoding='utf-8')
import naver_blog_poster as nb

B = 'https://freedom-of-economic.tistory.com/manage/v2/statistics/blog/'
FILE = 'tistory_stats_log.json'


def main(days=3):
    d = nb.get_driver()
    if 'tistory.com/manage' not in d.current_url:
        d.get('https://freedom-of-economic.tistory.com/manage/statistics/blog'); time.sleep(6)

    def get(u):
        r = d.execute_async_script("const cb=arguments[arguments.length-1];fetch(arguments[0],{credentials:'include'}).then(r=>r.text()).then(cb).catch(e=>cb('ERR '+e))", u)
        return json.loads(r)['data']

    log = json.load(open(FILE, encoding='utf-8')) if os.path.exists(FILE) else {}
    today = dt.date.today()
    for n in range(0, days + 1):
        day = (today - dt.timedelta(days=n)).isoformat()
        inf = get(B + f'inflow?granularity=day&metric=pv&startDate={day}')['result']
        top = get(B + f'topEntry?metric=pv&startDate={day}&granularity=day')['result']
        kw = get(B + f'keyword?granularity=day&metric=pv&startDate={day}')['result']
        log[day] = {
            'pv': inf['count'], 'search': inf['searchEngine']['total'], 'search_by': inf['searchEngine']['list'],
            'sns': inf['sns']['total'], 'sns_by': inf['sns']['list'], 'etc': inf['ref']['total'],
            'top': [(e['entryId'], e['title'][:30], e['count']) for e in top[:5]],
            'keywords': [(k['keyword'], k['count']) for k in kw],
            'checked': time.strftime('%Y-%m-%d %H:%M'),
        }
    json.dump(dict(sorted(log.items())), open(FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for day in sorted(log)[-(days + 1):]:
        v = log[day]
        print(f"{day} 조회 {v['pv']} | 검색 {v['search']} SNS {v['sns']} 기타 {v['etc']} | 검색어 {v['keywords'][:3]}")


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
