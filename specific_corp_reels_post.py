#!/usr/bin/env python3
"""
특정법인증여의제 소재 릴스형 영상 (Instagram Reels 전용, 존댓말)
- Threads는 이미 텍스트로 발행 완료(중복 방지) — 이 스크립트는 IG Reels만 처리
- video_poster.py 파이프라인(장면합성·TTS·ffmpeg) 재사용
- 상담링크는 항상 댓글에만
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

HOOK = '배당 포기했는데\n증여세가 나온다고요?'

SCENES = [
    {'image_query': 'businessman signing dividend document office',
     'image_prompt': 'A flat design illustration of a korean businessman signing a corporate dividend document at a desk, navy and gold color palette, soft colors'},
    {'image_query': 'two companies connection arrow diagram',
     'image_prompt': 'A flat design illustration of two company buildings connected by an arrow representing a shareholder relationship, soft colors'},
    {'image_query': 'tax notice warning document stamp',
     'image_prompt': 'A flat design illustration of an official tax notice document with a warning stamp, soft colors'},
    {'image_query': 'financial consultant meeting client office calm',
     'image_prompt': 'A flat design illustration of a financial consultant explaining a document to a client across a desk, soft colors'},
]

NARRATION_IG = (
    '본인이 받을 배당을 포기하고, 자녀가 지분을 가진 다른 회사가 대신 더 받게 만드는 경우가 있습니다. '
    '직접 거래하지 않았어도, 세법은 그 포기한 몫을 간접적으로 준 것으로 봅니다. '
    '자녀 쪽 회사가 얻은 이익에 지분 비율을 곱한 금액이 1억원을 넘으면, 일반 증여세와 똑같은 누진세율이 적용됩니다. '
    '자세한 계산 기준은 캡션에서 확인해보세요.'
)

CAPTION_IG = '''본인이 받을 배당을 포기하고, 자녀가 지분을 가진 다른 회사가 대신 더 받게 만드는 경우가 있습니다.

1. 지배주주와 특수관계인의 지분 합계가 30% 이상인 회사(특정법인)가 배당·무상제공·저가양수도 등으로 이익을 얻으면, 그 이익의 일부를 지배주주가 준 것으로 간주합니다.
2. 자녀 쪽 회사가 얻은 이익에 지분 비율을 곱한 금액이 1억원을 넘으면 과세 대상입니다.
3. 여기에는 일반 증여세와 동일하게 10%에서 50%까지 누진세율이 적용됩니다.

본인이 직접 거래하지 않았다는 이유로 안전하다고 생각하면 안 되는 영역입니다.

자세한 계산 구조는 블로그에 정리해두었습니다.

#특정법인증여의제 #초과배당증여세 #법인배당 #지배주주 #절세설계'''


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
                           'selected_title': '특정법인증여의제 블로그 유도 릴스',
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
