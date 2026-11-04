import sys
sys.stdout.reconfigure(encoding='utf-8')
import news_auto_poster as n
text = ("67년생이면 올해가 국민연금 조기수령 나이 만 59세가 되는 해야\n\n"
"공단 안내에서 1965~68년생은 노령연금 64세, 조기노령연금 59세야. 67년생은 2026년에 59세, 2031년에 64세가 돼.\n\n"
"조기노령연금은 가입기간 10년 이상이고 소득이 있는 업무에 종사하지 않아야 해. 월평균소득금액이 A값 3,193,511원을 넘으면 소득이 있는 업무로 봐.\n\n"
"64세 이후에도 5년 동안은 소득이 약 519만 원 이상이면 감액될 수 있어. 내 지급률과 금액은 공단에서 확인해.")
comment = "연도별 시점과 감액 기준 전체 정리는 블로그에 있어\nhttps://blog.naver.com/sobok__biz/224464466282"
n.post_to_threads(text, [comment], image_url=None, topic_tag='국민연금')
