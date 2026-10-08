#!/usr/bin/env python3
"""
퇴직연금 디폴트옵션 소재 릴스형 영상 (Instagram Reels 전용, 존댓말)
- 사실 출처: 고용노동부 2026-02-27 발표(2025년 말 기준), 뉴시스 보도
- 상품·회사명 없음, 상담링크는 항상 댓글에만
"""
import os, sys, json, tempfile, shutil
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

from video_poster import (
    create_scene_frames, generate_narration_timed, make_subtitle_phrases,
    get_audio_duration, build_video_multi, pick_bgm,
)
from annuity_video_poster import post_reels, load_ig_log, save_ig_log
import news_auto_poster as nap

KST = timezone(timedelta(hours=9))

HOOK = '직원이 지시 안 하면\n퇴직금 어디로 갈까?'

SCENES = [
    {'image_query': 'small business owner meeting employees office',
     'image_prompt': 'A flat design illustration of a business owner looking at retirement pension notices on a meeting room table, navy and gold color palette, soft colors'},
    {'image_query': 'calendar two weeks deadline',
     'image_prompt': 'A flat design illustration of a calendar with a two week countdown, soft colors'},
    {'image_query': 'percentage chart bars office',
     'image_prompt': 'A flat design illustration of a bar chart where one bar is much larger than the others, soft colors'},
    {'image_query': 'financial consultant meeting client office calm',
     'image_prompt': 'A flat design illustration of a financial consultant explaining a document to a client across a desk, soft colors'},
]

NARRATION_IG = (
    '직원이 퇴직연금 운용 지시를 하지 않으면 2주 뒤 미리 동의해 둔 디폴트옵션으로 자동 운용됩니다. '
    '2025년 말 기준 이렇게 운용되는 적립금 53조 3천억 원 가운데 85.4%가 수익률 2.63%의 안정형에 있습니다. '
    '같은 해 중립투자형은 10.81%였지만, 과거 수익률이 미래를 보장하지는 않습니다. '
    '사업장 규약에 어떤 운용 방법이 올라가 있는지 대표님은 알고 계신가요? 자세한 내용은 캡션에서 확인해보세요.'
)

CAPTION_IG = '''직원이 퇴직연금 운용 지시를 안 하면, 퇴직금은 어디로 갈까요?

1. 새로 입금된 퇴직금은 2주 동안 운용 지시가 없으면 디폴트옵션으로 운용됩니다. 기존 상품 만기 후에는 4주 뒤 통지, 2주 뒤 적용(약 6주)입니다.
2. 2025년 말 디폴트옵션 적립금 53.3조 원 중 85.4%가 수익률 2.63%의 안정형에 있습니다. 같은 해 중립투자형은 10.81%, 적극투자형은 14.93%였습니다. (고용노동부 발표, 과거 수익률이며 미래를 보장하지 않습니다)
3. 사업장이 제도를 도입하려면 사전지정운용방법을 최대 3개까지 골라 퇴직연금규약에 반영해야 합니다.

대표님 회사의 규약에는 어떤 방법이 올라가 있나요?

자세한 내용은 블로그에 정리해두었습니다. 이 내용은 특정 상품의 선택이나 가입을 권유하는 것이 아닙니다.

#퇴직연금디폴트옵션 #퇴직연금 #DC형 #사업주 #노후준비'''


def main():
    tmp_dir = tempfile.mkdtemp()
    try:
        print('장면 프레임 생성 중...')
        frames = create_scene_frames({'hook': HOOK, 'scenes': SCENES}, out_dir=tmp_dir, use_scene_text=False)
        if not frames:
            print('비주얼 생성 실패 - 종료')
            sys.exit(1)
        bgm = pick_bgm()

        print('=== Instagram Reels 영상 생성 ===')
        audio_ig = os.path.join(tmp_dir, 'narration_ig.mp3')
        _, boundaries_ig = generate_narration_timed(NARRATION_IG, output_path=audio_ig)
        phrases_ig = make_subtitle_phrases(boundaries_ig)
        duration_ig = get_audio_duration(audio_ig)
        video_ig = os.path.join(tmp_dir, 'video_ig.mp4')
        build_video_multi(frames, audio_ig, output_path=video_ig, duration=duration_ig,
                          bgm_path=bgm, phrases=phrases_ig, work_dir=tmp_dir)

        video_url_ig = nap.upload_to_github_release(video_ig)
        if not video_url_ig:
            print('IG 영상 업로드 실패 - 종료')
            sys.exit(1)

        ig_id = post_reels(video_url_ig, CAPTION_IG)
        if ig_id:
            ig_log = load_ig_log()
            ig_log.append({'ig_post_id': ig_id, 'type': 'reels',
                           'selected_title': '퇴직연금디폴트옵션 블로그 유도 릴스',
                           'date': datetime.now(KST).strftime('%Y-%m-%d %H:%M')})
            save_ig_log(ig_log)
            print(f'Instagram 완료: {ig_id}')
        else:
            print('Instagram 포스팅 실패')
            sys.exit(1)

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == '__main__':
    main()
