#!/usr/bin/env python3
"""
IRP계좌출금 소재 릴스형 영상 (Instagram Reels 전용, 존댓말)
- 사실 출처: 근로자퇴직급여 보장법 중도인출 사유(금융기관 안내 2026-09), 기타소득세·연금소득세율. 상담링크는 댓글에만
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

HOOK = 'IRP 급하게 해지하면\n세금이 얼마일까?'

SCENES = [
    {'image_query': 'worried person calculating savings documents desk',
     'image_prompt': 'A flat design illustration of a worried person looking at retirement account documents, navy and gold color palette, soft colors'},
    {'image_query': 'calculator documents tax desk',
     'image_prompt': 'A flat design illustration of a calculator and a tax statement on a desk, soft colors'},
    {'image_query': 'house keys moving apartment lease',
     'image_prompt': 'A flat design illustration of house keys and a lease contract, soft colors'},
    {'image_query': 'financial consultant meeting client office calm',
     'image_prompt': 'A flat design illustration of a financial consultant explaining a document to a client across a desk, soft colors'},
]

NARRATION_IG = (
    'IRP에 연 900만 원씩 5년을 넣은 사람이 급하게 해지하면 세금이 742만 원입니다. '
    '그동안 돌려받은 세액공제는 594만 원이라서 환급보다 148만 원을 더 냅니다. '
    '중도인출은 주택 구입, 전세금, 6개월 이상 요양, 회생이나 파산, 재난 피해, 이 다섯 가지 사유에만 됩니다. '
    '사유가 없으면 해지밖에 없고 세액공제 받은 돈에 16.5퍼센트가 붙습니다. '
    '급하지 않다면 55세 이후 연금으로 받는 쪽이 세율이 5.5퍼센트 이하입니다.'
)

CAPTION_IG = '''IRP에 넣어둔 돈을 급하게 꺼내면 세금이 얼마일까요?

1. 중도인출은 법으로 정한 5가지 사유에만 가능합니다. 주택 구입, 전세금, 6개월 이상 요양, 5년 이내 회생·파산, 재난 피해입니다.
2. 사유 없이 해지하면 세액공제 받은 원금과 수익에 기타소득세 16.5%가 붙습니다. 세액공제를 받지 않은 원금은 과세되지 않습니다.
3. 연 900만 원씩 5년(총 4,500만 원) 넣고 공제율 13.2%를 받은 A씨(가정)는 환급 594만 원, 해지 세금 742만 5천 원입니다.
4. 만 55세 이후 연금으로 받으면 연금소득세는 5.5%(70세 이후 4.4%, 80세 이후 3.3%)입니다.

공제율과 실제 세금은 소득과 가입 내역에 따라 다릅니다. 인출 전에는 가입한 금융기관 안내를 확인하세요. 자세한 내용은 블로그에 정리해두었습니다.

#IRP계좌출금 #IRP중도인출 #IRP해지 #연금소득세 #퇴직연금'''


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
                           'selected_title': 'IRP계좌출금 블로그 유도 릴스',
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
