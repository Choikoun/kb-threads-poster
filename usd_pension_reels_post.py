#!/usr/bin/env python3
"""
달러통장 소재 릴스형 영상 (Instagram Reels 전용, 존댓말)
- 상품명·회사명 없이 달러 변액연금의 구조만 다룸 (사용자 지시 10-06)
- video_poster.py 파이프라인(장면합성·TTS·ffmpeg) 재사용, 상담링크는 항상 댓글에만
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

HOOK = '달러통장에 3년째\n그 달러, 일하고 있나요?'

SCENES = [
    {'image_query': 'us dollar banknotes close up desk',
     'image_prompt': 'A flat design illustration of us dollar bills on a desk, navy and gold color palette, soft colors'},
    {'image_query': 'calculator documents finance planning',
     'image_prompt': 'A flat design illustration of a calculator and a table of percentages, soft colors'},
    {'image_query': 'senior couple relaxing home calm retirement',
     'image_prompt': 'A flat design illustration of a calm senior couple at home, soft colors'},
    {'image_query': 'financial consultant meeting client office calm',
     'image_prompt': 'A flat design illustration of a financial consultant explaining a document to a client across a desk, soft colors'},
]

NARRATION_IG = (
    '달러통장은 달러를 담아두는 통장이라 이자가 낮고, 환차익에는 세금이 없지만 이자에는 15.4%가 붙습니다. '
    '달러로 넣고 달러로 운용하고 달러로 평생 받는 연금 구조도 있습니다. '
    '가입나이별 지급률은 40세 3.5%에서 75세 4.9%까지 올라갑니다. '
    '다만 원금 손실과 환율 손실은 계약자 몫이어서, 곧 쓸 돈과 오래 둘 돈을 나눠 봐야 합니다. '
    '자세한 숫자는 캡션에서 확인해보세요.'
)

CAPTION_IG = '''달러통장에 넣어둔 달러, 쓸 돈과 둘 돈을 나눠 보셨나요?

1. 달러통장은 입출금용입니다. 환차익은 비과세이고 이자에만 15.4%가 붙습니다.
2. 달러로 넣고 달러로 운용하고 달러로 받는 일시납 연금 구조가 있습니다. 가입나이별 지급률은 40세 3.5%에서 75세 4.9%입니다.
3. 변액이라 원금 손실이 생길 수 있고, 환율 손실도 계약자 몫입니다.

내 나이에 몇 퍼센트가 적용되는지, 몇 살부터 얼마를 받는지는 나이와 금액에 따라 달라집니다.

자세한 구조는 블로그에 정리해두었습니다. 이 내용은 가입을 권유하는 것이 아니며, 가입 전에는 상품설명서와 약관을 확인하시기 바랍니다.

#달러통장 #달러연금 #외화보험 #변액연금 #사업주'''


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
                           'selected_title': '달러통장 블로그 유도 릴스',
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
