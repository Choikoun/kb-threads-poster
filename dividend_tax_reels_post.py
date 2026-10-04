#!/usr/bin/env python3
"""
배당소득세 소재 릴스형 영상 (Instagram Reels 전용, 존댓말)
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

HOOK = '배당 1억\n세금이 1,200만 원 차이?'

SCENES = [
    {'image_query': 'business owner reviewing financial statements office',
     'image_prompt': 'A flat design illustration of a korean business owner reviewing financial statements at a desk, navy and gold color palette, soft colors'},
    {'image_query': 'calculator tax documents desk',
     'image_prompt': 'A flat design illustration of a calculator and tax documents on a desk, soft colors'},
    {'image_query': 'family together home planning',
     'image_prompt': 'A flat design illustration of a family of four sitting together with documents, soft colors'},
    {'image_query': 'financial consultant meeting client office calm',
     'image_prompt': 'A flat design illustration of a financial consultant explaining a document to a client across a desk, soft colors'},
]

NARRATION_IG = (
    '이자와 배당을 합친 금융소득이 연 2천만 원 이하면 15.4% 원천징수로 세금이 끝납니다. '
    '2천만 원을 넘기면 넘긴 금액만 다른 소득과 합쳐져 종합과세되고, 지방소득세까지 포함하면 최고 49.5%입니다. '
    '법인 대표가 배당 1억 원을 혼자 받으면 세금이 약 3,100만 원, 가족 4명이 나눠 받으면 약 1,900만 원입니다. '
    '자세한 계산은 캡션에서 확인해보세요.'
)

CAPTION_IG = '''금융소득이 연 2천만 원을 넘는지가 배당소득세의 경계선입니다.

1. 2천만 원 이하는 15.4% 원천징수로 세금이 끝납니다.
2. 2천만 원을 넘긴 금액만 다른 소득과 합쳐져 종합과세되고, 지방소득세까지 더하면 최고 49.5%입니다.
3. 법인 대표가 배당 1억 원을 혼자 받으면 약 3,100만 원, 가족 4명이 나눠 받으면 약 1,900만 원이 세금입니다. 대표 다른 소득 과세표준 1.5억 가정의 단순 계산입니다.

배당은 얼마를 받느냐보다 누가 받느냐가 먼저입니다. 그렇다고 꺼내지 않고 쌓아두면 주식 평가액이 올라 나중에 증여세와 상속세로 돌아옵니다.

자세한 계산 구조는 블로그에 정리해두었습니다.

#배당소득세 #금융소득종합과세 #법인배당 #배당세액공제 #사업주'''


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
                           'selected_title': '배당소득세 블로그 유도 릴스',
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
