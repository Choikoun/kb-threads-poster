p='promo_1022_ig_post.py'
s=open(p,encoding='utf-8').read()
B=chr(92)+'n'
block=(
"NPA = {\n"
"    'card_data': {\n"
"        'tag': '# 67년생국민연금수령나이',\n"
"        'hook_big': '67년생 국민연금,BNL올해 59세 조기 신청',\n"
"        'hook_sub': '국민연금공단 노령연금 안내 기준 정리',\n"
"        'points': [\n"
"            {'title': '연도 시계', 'body': '2026년 만 59세 조기 개시,BNL2031년 만 64세 노령연금,BNL연기는 최대 5년.'},\n"
"            {'title': '조기 조건', 'body': '가입 10년 이상,BNL59세 이상,BNL소득이 있는 업무에 종사하지 않을 것.'},\n"
"            {'title': '소득 감액', 'body': '64세 이후 5년 동안BNL월평균소득이 약 519만 원 이상이면BNL연금이 줄 수 있습니다.'},\n"
"            {'title': '연기연금', 'body': '1년마다 7.2%씩 늘지만BNL건강보험료와 세금도BNL함께 확인하세요.'},\n"
"        ],\n"
"        'closing': '내 소득부터BNL먼저 확인해 보세요.',\n"
"        'cta': '프로필 링크 → 블로그에 전체 정리'\n"
"    },\n"
"    'caption': ('67년생이라면 올해가 조기노령연금 개시 나이인 만 59세가 되는 해입니다. 내 월평균소득과 가입기간을 확인해 보셨나요?BNLBNL'\n"
"                '공단 안내에서 1965~68년생은 노령연금 64세, 조기노령연금 59세입니다. 조기노령연금은 가입기간 10년 이상이고 소득이 있는 업무에 종사하지 않아야 하며, 64세 이후에도 5년 동안은 소득에 따라 감액될 수 있습니다.BNLBNL'\n"
"                '내 연금액과 지급률은 국민연금공단에서 확인하세요. 자세한 정리는 블로그에 있습니다.BNLBNL'\n"
"                '#67년생국민연금수령나이 #조기노령연금 #국민연금소득감액 #국민연금'),\n"
"}\n\n"
).replace('BNL',B)
assert "NPA = {" not in s
s=s.replace("if __name__ == '__main__':", block+"if __name__ == '__main__':",1)
for a,b in (("('sgb', SGB)):","('sgb', SGB), ('npa', NPA)):"),
            ("'sgb': SGB}[mode]","'sgb': SGB, 'npa': NPA}[mode]"),
            ("'sgb': '상속재산분할협의서예시 블로그 요약 카드'}","'sgb': '상속재산분할협의서예시 블로그 요약 카드', 'npa': '67년생국민연금수령나이 블로그 요약 카드'}")):
    assert a in s, a
    s=s.replace(a,b,1)
open(p,'w',encoding='utf-8').write(s)
print('patched')
