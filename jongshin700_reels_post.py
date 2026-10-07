#!/usr/bin/env python3
"""
700종신 판매중지 소재 릴스형 영상 (Instagram Reels 전용, 존댓말)
- Threads는 이미 텍스트로 발행 완료(중복 방지) — 이 스크립트는 IG Reels만 처리
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

HOOK = '700종신 판매중지\n내 계약은 어떻게 될까?'

SCENES = [
    {'image_query': 'insurance contract paperwork pen desk',
     'image_prompt': 'A flat design illustration of an insurance contract document with a stop sign, navy and gold color palette, soft colors'},
    {'image_query': 'calendar deadline seven years',
     'image_prompt': 'A flat design illustration of a calendar highlighting year seven with a percentage chart, soft colors'},
    {'image_query': 'family protection home calm',
     'image_prompt': 'A flat design illustration of a family under an umbrella, soft colors'},
    {'image_query': 'financial consultant meeting client office calm',
     'image_prompt': 'A flat design illustration of a financial consultant explaining a document to a client across a desk, soft colors'},
]

NARRATION_IG = (
    '700종신이 판매중지됐습니다. 이미 가입한 계약은 그대로 유지됩니다. '
    '문제가 된 것은 7년 전에는 환급률이 낮다가 7년 시점에 100%로 오르는 구조입니다. '
    '이 구조에서는 7년이 되는 날 해지가 몰립니다. '
    '하지만 해지하면 낸 돈은 돌려받아도 가족을 위한 사망보장은 그날 사라집니다. '
    '내 증권의 7년 시점 숫자를 캡션에서 확인해보세요.'
)

CAPTION_IG = '''700종신 판매중지, 이미 가입한 계약은 어떻게 될까요?

1. 9월 21일 오후 6시 이후 신규 설계가 중단됐고, 이미 가입한 계약은 그대로 유지됩니다.
2. 당국이 문제 삼은 것은 7년 전에는 0~80%만 돌려주다가 7년 시점에 100%로 오르는 환급 구조와, 사망보험금이 과도하게 불어나는 체증 구조입니다.
3. 7년 시점에 해지하면 낸 돈은 돌려받아도, 종신보험의 사망보장은 그날로 끝납니다.

환급금 숫자만이 아니라, 해지 이후의 보장 계획까지 같이 보셔야 합니다.

자세한 구조는 블로그에 정리해두었습니다. 이 내용은 가입이나 해지를 권유하는 것이 아니며, 증권과 약관을 확인하시기 바랍니다.

#700종신 #종신보험 #단기납종신 #보험해지 #사업주'''


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
                           'selected_title': '700종신 판매중지 블로그 유도 릴스',
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
