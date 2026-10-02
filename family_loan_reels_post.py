#!/usr/bin/env python3
"""
가족간차용증 소재 릴스형 영상 (Instagram Reels 전용, 존댓말)
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

HOOK = '가족간 차용증\n이자율 하나 잘못쓰면'

SCENES = [
    {'image_query': 'parent child signing document table home',
     'image_prompt': 'A flat design illustration of a korean parent and adult child signing a loan agreement document at a home table, navy and gold color palette, soft colors'},
    {'image_query': 'percentage interest rate calculation document',
     'image_prompt': 'A flat design illustration of a calculator and a document showing an interest rate percentage symbol, soft colors'},
    {'image_query': 'bank transfer record document smartphone',
     'image_prompt': 'A flat design illustration of a bank transfer receipt and a smartphone showing a payment record, soft colors'},
    {'image_query': 'financial consultant meeting client office calm',
     'image_prompt': 'A flat design illustration of a financial consultant explaining a document to a client across a desk, soft colors'},
]

NARRATION_IG = (
    '부모 자식 사이에 돈을 빌려줄 때 차용증만 쓰면 증여세를 피할 수 있다고 알고 있는 경우가 많습니다. '
    '실제로는 세법이 정한 적정이자율 4.6%와 실제 이자의 차액이 연 1천만원을 넘으면 증여세가 붙습니다. '
    '거꾸로 계산하면 무이자로 빌려줘도 되는 금액은 약 2억 1,700만원입니다. '
    '자세한 계산 기준은 캡션에서 확인해보세요.'
)

CAPTION_IG = '''부모 자식 사이에 돈을 빌려줄 때 차용증만 쓰면 증여세를 피할 수 있다고 알고 있는 경우가 많습니다.

1. 세법이 정한 적정이자율은 연 4.6%입니다. 이보다 낮게(또는 무이자로) 빌려주면 적정이자와 실제 이자의 차액을 증여로 봅니다.
2. 이 차액이 연간 1천만원을 넘을 때만 과세됩니다. 거꾸로 계산하면 무이자로 빌려줘도 되는 금액은 약 2억 1,700만원입니다.
3. 차용증을 썼어도 실제 상환 이력(이자·원금)이 없다면 증여로 재분류될 수 있습니다.

문서와 실제 자금 흐름을 일치시키는 게 핵심입니다.

자세한 계산 구조는 블로그에 정리해두었습니다.

#가족간차용증 #차용증이자율 #증여세 #특수관계인 #자금대여'''


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
                           'selected_title': '가족간차용증 블로그 유도 릴스',
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
