#!/usr/bin/env python3
"""
퇴직연금세액공제 소재 릴스형 영상 (Instagram Reels 전용, 존댓말)
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

HOOK = '퇴직연금 900만원\n똑같이 채워도'

SCENES = [
    {'image_query': 'businessman calculator retirement planning desk',
     'image_prompt': 'A flat design illustration of a korean businessman calculating retirement savings with a calculator and documents, navy and gold color palette, soft colors'},
    {'image_query': 'percentage tax rate comparison chart',
     'image_prompt': 'A flat design illustration of two scales balancing percentage symbols representing different tax rates, soft colors'},
    {'image_query': 'warning document penalty stamp',
     'image_prompt': 'A flat design illustration of a document with a warning stamp representing early withdrawal penalty, soft colors'},
    {'image_query': 'financial consultant meeting client office',
     'image_prompt': 'A flat design illustration of a financial consultant explaining a retirement plan document to a client across a desk, soft colors'},
]

NARRATION_IG = (
    '연금저축과 IRP를 합쳐 연 900만원을 채우면, 벌어들이는 돈의 규모에 따라 돌려받는 금액이 최대 148만 5천원 또는 118만 8천원으로 갈립니다. '
    '종합소득금액이 4,500만원을 넘는지가 기준선입니다. '
    '사업소득자는 매출이 아니라 경비를 뺀 순수입이 기준이라, 매출이 많아도 경비가 많으면 더 높은 공제율 구간에 남을 수 있습니다. '
    '자세한 계산 구조는 캡션에서 확인해보세요.'
)

CAPTION_IG = '''연금저축과 IRP를 합쳐 연 900만원을 채우면, 벌어들이는 돈의 규모에 따라 돌려받는 금액이 최대 148만 5천원 또는 118만 8천원으로 갈립니다.

1. 종합소득금액 4,500만원(근로자는 총급여 5,500만원)이 세율을 가르는 기준선입니다. 이 선 아래면 16.5%, 넘으면 13.2%가 적용됩니다.
2. 사업소득자는 매출이 아니라 경비를 뺀 순수입이 기준입니다. 매출이 많아도 경비 인정이 많으면 더 유리한 구간에 남을 수 있습니다.
3. 중도에 인출하면 받았던 공제만큼 기타소득세 16.5%를 다시 내야 합니다.

법인 대표라면 급여 외 배당까지 합산돼 기준선을 넘기기 쉬워, 미리 소득 구조를 점검해두시는 게 좋습니다.

자세한 계산 구조는 블로그에 정리해두었습니다.

#퇴직연금세액공제 #IRP세액공제 #연금저축 #노후준비 #재무설계'''


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
                           'selected_title': '퇴직연금세액공제 블로그 유도 릴스',
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
