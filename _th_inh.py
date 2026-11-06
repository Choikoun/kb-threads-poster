import sys
sys.stdout.reconfigure(encoding='utf-8')
import news_auto_poster as n
text = ("자녀 상속세 면제 한도는 자녀 수가 아니라 배우자가 있느냐로 갈려\n\n"
"국세청 안내 기준으로 일괄공제는 5억 원이고 자녀공제는 1인당 5천만 원이야. 자녀가 5명이어도 기초공제 2억에 2.5억을 더하면 4.5억이라 일괄공제가 더 커.\n\n"
"배우자가 있으면 배우자공제가 최소 5억 원이라 일괄공제와 합쳐 10억, 없으면 5억이 출발점이야. 순금융재산 공제와 동거주택 공제는 그 위에 더해질 수 있어.\n\n"
"사전증여가 있으면 공제 상한이 달라질 수 있으니 세무 전문가와 확인해.")
comment = "공제 항목별 요건과 상한 전체 정리는 블로그에 있어\nhttps://blog.naver.com/sobok__biz/224466906754"
n.post_to_threads(text, [comment], image_url=None, topic_tag='상속세')
