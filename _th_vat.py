import sys
sys.stdout.reconfigure(encoding='utf-8')
import news_auto_poster as n
text = ("개인사업자 부가세는 신고는 2번인데 내는 돈은 최대 4번이야\n\n"
"국세청 안내 기준으로 개인 일반사업자는 7월과 1월에 확정신고를 해. 그런데 4월과 10월에는 예정고지서가 따로 와.\n\n"
"예정고지는 직전 6개월 납부세액의 50%이고, 다음 확정신고 때 이미 낸 세금으로 빠져. 다만 징수할 금액이 50만 원 미만이면 대상에서 빠져.\n\n"
"다음 기한은 2027년 1월 25일이야. 넘기면 무신고 20%, 과소신고 10%, 납부 지연은 1일 22/100,000가 붙을 수 있어.")
comment = "법인·간이·폐업 기한과 가산세 전체 정리는 블로그에 있어\nhttps://blog.naver.com/sobok__biz/224465639630"
n.post_to_threads(text, [comment], image_url=None, topic_tag='부가세')
