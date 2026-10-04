#!/usr/bin/env python3
"""
사망보험금세금 소재 릴스형 영상 (Instagram Reels 전용, 존댓말)
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

HOOK = '종신보험 20억\n세금이 9억?'

SCENES = [
    {'image_query': 'businessman reviewing insurance documents office',
     'image_prompt': 'A flat design illustration of a korean business owner reviewing an insurance policy document at a desk, navy and gold color palette, soft colors'},
    {'image_query': 'calculator tax documents desk',
     'image_prompt': 'A flat design illustration of a calculator and tax documents on a desk, soft colors'},
    {'image_query': 'family house inheritance planning',
     'image_prompt': 'A flat design illustration of a family standing in front of a house with a document, soft colors'},
    {'image_query': 'financial consultant meeting client office calm',
     'image_prompt': 'A flat design illustration of a financial consultant explaining a document to a client across a desk, soft colors'},
]

NARRATION_IG = (
    '사망보험금 세금은 받는 사람이 아니라 보험료를 낸 사람 기준으로 갈립니다. '
    '본인이 보험료를 내고 본인이 피보험자인 종신보험 20억 원은 전액이 상속재산입니다. '
    '기존 재산이 30억 원이라면 상속세는 약 6억 4천만 원에서 약 15억 4천만 원으로, 9억 원이 늘어납니다. '
    '자녀 이름으로 해뒀어도 보험료를 부모가 냈다면 낸 비율만큼은 상속재산입니다. '
    '자세한 계산은 캡션에서 확인해보세요.'
)

CAPTION_IG = '''사망보험금 세금은 받는 사람이 아니라 보험료를 낸 사람 기준으로 갈립니다.

1. 본인이 보험료를 내고 본인이 피보험자이면 보험금 전액이 상속재산입니다.
2. 기존 재산 30억 원에 종신보험 20억 원이 더해지면 상속세가 약 6억 4천만 원에서 약 15억 4천만 원이 됩니다. 세금이 약 9억 원 늘어나는 계산입니다.
3. 자녀 이름으로 가입했어도 부모가 보험료를 냈다면 낸 비율만큼은 상속재산으로 봅니다.

세금 낼 돈으로 준비한 보험이 오히려 세금을 키우고 있지는 않은지, 증권에서 보험료가 나가는 통장부터 확인해보세요.

자세한 계산 구조는 블로그에 정리해두었습니다.

#사망보험금세금 #종신보험 #상속세 #보험료납부자 #사업주'''


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
                           'selected_title': '사망보험금세금 블로그 유도 릴스',
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
