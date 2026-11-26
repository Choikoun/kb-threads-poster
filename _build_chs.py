import re, json, ast
ID = 'chs'
blk = open('_chs_block.txt', encoding='utf-8').read()
s = open('promo_1022_ig_post.py', encoding='utf-8').read()
assert 'CHS = {' not in s
a = "if __name__ == '__main__':\n    mode = sys.argv[1]"
assert s.count(a) == 1
s = s.replace(a, blk + a)
s = s.replace("('jbn', JBN))", "('jbn', JBN), ('chs', CHS))")
s = s.replace("'jbn': JBN}[mode]", "'jbn': JBN, 'chs': CHS}[mode]")
s = s.replace("'jbn': '종부세납부기간 블로그 요약 카드'}", "'jbn': '종부세납부기간 블로그 요약 카드', 'chs': '출산전후휴가급여 블로그 요약 카드'}")
ast.parse(s)
open('promo_1022_ig_post.py', 'w', encoding='utf-8').write(s)

p = 'timed_social/schedule.json'
d = json.load(open(p, encoding='utf-8'))
d['2026-11-26'] = ID
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

r = open('jbn_anim_reels_post.py', encoding='utf-8').read()
head = r[:r.index('TITLE =')].replace('종부세 납부기간 릴스', '출산전후휴가급여 릴스').replace('종합부동산세법 제16조·제20조·제20조의2, 시행령 제16조', '고용보험법 제75조·제76조, 근로기준법 제74조')
body = """TITLE = '출산전후휴가급여 블로그 유도 릴스(애니메이션)'

SCENES = [
    dict(kind='list', title='출산전후휴가급여', big='휴가 종료일 기준 180일', small='고용보험법 제75조', col=GOLD,
         items=['휴가가 끝난 날 이전 피보험 단위기간', '합산 180일 이상이어야 합니다', '급여는 휴가 시작일 기준 통상임금'],
         say='출산전후휴가급여는 휴가가 끝난 날 이전에 피보험 단위기간이 합산 180일 이상이어야 받을 수 있습니다. 금액은 휴가를 시작한 날 기준 통상임금에 해당하는 금액입니다.'),
    dict(kind='list', title='회사 규모별 일수', big='대기업은 뒤 30일', small='법 제76조 · 필자 계산', col=RED,
         items=['우선지원대상기업은 90일 전체', '그 외는 최초 60일 사업주 유급', '뒤 30일이 급여 대상'],
         say='우선지원대상기업은 휴가 90일 전체가 급여 대상입니다. 그 외 기업은 최초 60일은 사업주가 임금을 주고, 그 뒤 30일만 고용보험 급여 대상입니다.'),
    dict(kind='list', title='신청 기한', big='종료 후 12개월 이내', small='고용보험법 제75조 제2호', col=GREEN,
         items=['휴가 시작 후 1개월부터 신청', '휴가가 끝난 날 이후 12개월 이내', '사업주 금품과 합산이 통상임금 넘으면 감액'],
         say='신청은 휴가를 시작한 날 이후 1개월부터 휴가가 끝난 날 이후 12개월 이내입니다. 사업주에게 받은 금품과 합친 금액이 통상임금을 넘으면 초과분은 빠집니다.'),
    dict(kind='cta', title='저장해두세요', big='우리 회사 몇 일 해당?', small='우선지원대상기업은 고용센터 확인', col=GOLD,
         panel='프로필 링크 → 블로그에 전체 정리',
         say='저장해 두세요. 우리 회사가 우선지원대상기업인지에 따라 급여 일수가 달라집니다. 고용센터에서 확인하셔야 합니다.'),
]

CAPTION = '''출산전후휴가급여, 회사 규모별 급여 일수와 신청 기한을 한 번에 정리했습니다.

1. 고용보험법 제75조: 휴가가 끝난 날 이전 피보험 단위기간이 합산 180일 이상이어야 합니다.
2. 제76조: 우선지원대상기업은 휴가 90일 전체, 그 외는 60일 초과분 최대 30일이 급여 대상입니다.
3. 신청은 휴가 시작 후 1개월부터 휴가가 끝난 날 이후 12개월 이내입니다.

자세한 내용은 블로그에 정리해두었습니다. 내 회사가 우선지원대상기업인지와 지급액은 고용센터에 확인하세요. 특정 상품 가입을 권유하지 않습니다.

#출산전후휴가급여 #출산휴가급여신청 #우선지원대상기업 #고용보험'''


def main():
    K.publish(SCENES, CAPTION, TITLE)


if __name__ == '__main__':
    K.make_video(SCENES, os.environ.get('KB_OUT') or 'npa_anim_test.mp4')
"""
open('chs_anim_reels_post.py', 'w', encoding='utf-8').write(head + body)
ast.parse(open('chs_anim_reels_post.py', encoding='utf-8').read())

t = json.load(open('timed_social/jbn.json', encoding='utf-8'))
t.update({
    "key": "maternity_leave_benefit", "date": "2026-11-26",
    "title_match": "출산전후휴가급여, 대기업은 90일 중 뒤 30일",
    "title": "출산전후휴가급여, 대기업은 90일 중 뒤 30일만 급여로 나오고 신청은 12개월 이내입니다",
    "tistory": "https://freedom-of-economic.tistory.com/347", "topic_tag": "출산휴가",
    "reel_module": "chs_anim_reels_post", "ig_mode": "chs",
    "naver_url": "https://blog.naver.com/sobok__biz/224493086510",
    "threads_text": "대기업 다니는 직장인이 출산휴가 90일을 쓰면 고용보험 급여는 며칠치가 나올까?\n\n우선지원대상기업이 아니면 최초 60일은 회사가 임금을 주고, 뒤 30일만 급여 대상이야. 우선지원대상기업이면 90일 전체가 대상이고.\n\n받으려면 휴가가 끝난 날 이전에 피보험 단위기간이 합산 180일 이상이어야 하고, 신청은 휴가가 끝난 날 이후 12개월 이내야. 우리 회사는 어느 쪽인지 확인해 봤어?",
    "comment": "회사 규모별 일수와 신청 기한은 블로그에 정리해 뒀어 {url}",
})
json.dump(t, open('timed_social/chs.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

c = open('_clip_jbn.py', encoding='utf-8').read()
c = re.sub(r'desc = ".*"\n', 'desc = "출산전후휴가급여는 고용보험법 제75조에 따라 휴가가 끝난 날 이전 피보험 단위기간이 합산 180일 이상이어야 합니다. 제76조에 따라 우선지원대상기업은 휴가 90일 전체, 그 외 기업은 60일을 넘는 일수 중 최대 30일이 급여 대상이고, 신청은 휴가가 끝난 날 이후 12개월 이내입니다. 내 회사 해당 여부와 지급액은 고용센터에 확인하세요. 특정 상품 가입을 권유하지 않습니다. #출산전후휴가급여 #출산휴가급여신청 #고용보험"\n', c)
c = c.replace("'종부세 납부기간은 12월 1일부터 15일'", "'출산전후휴가급여, 대기업은 90일 중 뒤 30일'")
open('_clip_chs.py', 'w', encoding='utf-8').write(c)
print('ok')
