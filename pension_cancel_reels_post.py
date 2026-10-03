#!/usr/bin/env python3
"""
연금저축해지 소재 릴스형 영상 (Instagram Reels 전용, 존댓말)
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

HOOK = '연금저축 해지하면\n세금이 얼마?'

SCENES = [
    {'image_query': 'worried man calculator documents desk finance',
     'image_prompt': 'A flat design illustration of a worried korean man with a calculator and savings documents at a desk, navy and gold color palette, soft colors'},
    {'image_query': 'piggy bank coins savings',
     'image_prompt': 'A flat design illustration of a piggy bank being opened with coins and a percentage symbol, soft colors'},
    {'image_query': 'tax notice document calculator',
     'image_prompt': 'A flat design illustration of a tax notice document with a calculator showing a tax amount, soft colors'},
    {'image_query': 'financial consultant meeting client office calm',
     'image_prompt': 'A flat design illustration of a financial consultant explaining a document to a client across a desk, soft colors'},
]

NARRATION_IG = (
    '급전이 필요해서 연금저축을 해지하려는 분들이 많습니다. '
    '세액공제를 받은 납입금과 수익은 해지하는 순간 기타소득세 16.5%가 붙습니다. '
    '3,300만원 기준으로 해지하면 세금이 약 545만원, 55세 이후 연금으로 받으면 약 182만원입니다. '
    '자세한 계산 기준은 캡션에서 확인해보세요.'
)

CAPTION_IG = '''급전이 필요해서 연금저축을 해지하려는 분들이 많습니다.

1. 세액공제를 받은 납입 원금과 운용수익을 연금이 아닌 방식으로 꺼내면 기타소득세 16.5%가 붙습니다.
2. 원금 3,000만원에 수익 300만원이 쌓인 계좌라면, 해지 시 세금은 약 545만원이고 55세 이후 연금으로 받으면 약 182만원입니다.
3. 해지 대신 납입유예나 다른 금융회사로의 이전처럼 세제 혜택을 유지하는 방법이 있습니다.

해지 전에 세금 차이부터 확인하는 게 먼저입니다.

자세한 계산 구조는 블로그에 정리해두었습니다.

#연금저축해지 #기타소득세 #연금저축중도인출 #연금수령요건 #노후준비'''


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
                           'selected_title': '연금저축해지 블로그 유도 릴스',
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
