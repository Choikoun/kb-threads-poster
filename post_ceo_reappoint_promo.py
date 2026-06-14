"""
1인법인 대표이사 중임등기 셀프 도구 홍보 포스팅 (1회성)
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import news_auto_poster as nap

MAIN = """1인법인 대표이사
중임등기 어떻게 하냐고
물어보는 사람이 너무 많았어.

매번 설명하기도 그래서
아예 하나 만들었어.

회사 정보만 입력하면
필요한 등기 서류
자동으로 만들어서
zip으로 받을 수 있어.

무료야. 하루 5번까지 써.

https://web-production-92ec7.up.railway.app/public/ceo-reappoint"""

COMMENT1 = """회사명, 등기번호, 발행주식수,
대표이사 정보 같은
기본 정보만 넣으면 돼.

이거로 셀프 중임등기
끝낸 사람들 꽤 있어."""

COMMENT2 = """임기가 지났어도
이걸로 서류는 만들 수 있어.

다만 과태료 대상일 수 있으니
한 번 확인해보는 게 좋아."""

COMMENT3 = """법인 운영하는 이유,
세율 낮아서인 경우 많아.

근데 법인 돈을
개인 통장으로 가져올 때
세금이 한 번 더 붙어.

세율만 보고 만든 법인은
이 단계에서
오히려 손해 보는 경우도 있어.

운영하다 보면
이게 더 큰 문제로
커지는 경우도 있고.

이 법인,
지금 제대로
쓰이고 있는 걸까."""

if __name__ == '__main__':
    main_id = nap.post_to_threads(MAIN, [COMMENT1, COMMENT2, COMMENT3], image_url=None)
    print(f'완료! 메인 포스트 ID: {main_id}')
