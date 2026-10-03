#!/usr/bin/env python3
"""
퇴직금정산 소재 릴스형 영상 (Instagram Reels 전용, 존댓말)
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

HOOK = '직원 퇴사하면
퇴직금 언제까지?'

SCENES = [
    {'image_query': 'business owner employee handshake office',
     'image_prompt': 'A flat design illustration of a korean business owner shaking hands with a departing employee in an office, navy and gold color palette, soft colors'},
    {'image_query': 'calendar deadline 14 days',
     'image_prompt': 'A flat design illustration of a calendar with a 14 day deadline circled, soft colors'},
    {'image_query': 'calculator documents payroll',
     'image_prompt': 'A flat design illustration of a calculator and payroll documents on a desk, soft colors'},
    {'image_query': 'financial consultant meeting client office calm',
     'image_prompt': 'A flat design illustration of a financial consultant explaining a document to a client across a desk, soft colors'},
]

NARRATION_IG = (
    '직원이 퇴사하면 퇴직금은 퇴사일로부터 14일 안에 지급해야 합니다. '
    '합의 없이 이 기한을 넘기면 늦은 날수만큼 연 20%의 지연이자가 붙습니다. '
    '월급 400만원으로 3년 일한 직원의 퇴직금은 약 1,174만원이고, 한 달만 늦어도 이자가 약 19만원입니다. '
    '자세한 계산 기준은 캡션에서 확인해보세요.'
)

CAPTION_IG = '''직원이 퇴사하면 퇴직금은 퇴사일로부터 14일 안에 지급해야 합니다.

1. 합의 없이 기한을 넘기면 늦은 날수만큼 연 20%의 지연이자가 붙습니다.
2. 퇴직금은 퇴직 직전 3개월 임금을 기준으로 한 1일 평균임금에 30일을 곱해 근속연수만큼 계산합니다. 상여금과 연차수당도 반영됩니다.
3. 퇴직금은 원칙적으로 직원 본인의 IRP 계좌로 입금해야 합니다.

퇴직금은 쌓이는 동안은 보이지 않다가 퇴사하는 날 한꺼번에 청구서로 옵니다.

자세한 계산 구조는 블로그에 정리해두었습니다.

#퇴직금정산 #퇴직금지급기한 #평균임금 #퇴직연금 #사업주'''


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
                           'selected_title': '퇴직금정산 블로그 유도 릴스',
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
