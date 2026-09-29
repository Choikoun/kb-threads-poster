#!/usr/bin/env python3
"""
특수관계인저가양도 소재 릴스형 영상 (Instagram Reels 전용, 존댓말)
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

HOOK = '가족끼리 싸게 팔면\n걸리는 기준선'

SCENES = [
    {'image_query': 'family real estate contract signing'},
    {'image_query': 'parent adult child discussing paperwork'},
    {'image_query': 'calculator documents house price'},
    {'image_query': 'tax office consultation'},
]

NARRATION_IG = (
    '부모가 자녀에게 시세보다 싸게 집을 팔면 세금을 아낄 수 있다고 생각하실 수 있습니다. '
    '하지만 정확한 기준선을 모르고 넘으면 증여세와 양도소득세를 동시에 맞을 수 있습니다. '
    '시가와 거래가액의 차이가 시가의 30퍼센트 또는 3억원 중 적은 금액을 넘으면 그 초과분에 증여세가 매겨집니다. '
    '자세한 계산 구조는 캡션에서 확인해보세요.'
)

CAPTION_IG = '''부모가 자녀에게 시세보다 싸게 집을 팔면 세금을 아낄 수 있다고 생각하실 수 있습니다.

정확한 기준선을 모르고 넘으면 증여세와 양도소득세를 동시에 맞을 수 있습니다.

1. 시가와 거래가액의 차이가 시가의 30% 또는 3억원 중 적은 금액을 넘으면 그 초과분에 증여세가 매겨집니다.
2. 판 사람에게는 양도소득세도 실제 거래가액이 아니라 시가를 기준으로 다시 계산됩니다(부당행위계산부인).
3. 증여세 기준(30%·3억원)과 양도세 재계산 기준(5%·3억원)이 서로 다르다는 점도 헷갈리기 쉬운 부분입니다.

자세한 계산 구조는 블로그에 정리해두었습니다.

#특수관계인저가양도 #증여세 #양도소득세 #부동산세금 #재무설계'''


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
                           'selected_title': '특수관계인저가양도 블로그 유도 릴스',
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
