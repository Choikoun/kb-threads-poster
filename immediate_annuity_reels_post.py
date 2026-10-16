#!/usr/bin/env python3
"""
즉시연금1억 소재 릴스형 영상 (Instagram Reels 전용, 존댓말)
- 사실 출처: 소득세법 시행령 저축성보험 보험차익 비과세 요건(일시납 1억·10년), 보험저널 보도(2027 공시이율). 상담링크는 댓글에만
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

HOOK = '목돈 1억 즉시연금에 넣으면\n월 얼마 받을까?'

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
    '목돈 1억을 즉시연금 상속형에 넣고 이자만 받으면, 이율 3퍼센트 가정으로 월 25만 원입니다. '
    '실제로는 사업비와 환급 재원이 빠져서 이보다 적습니다. '
    '비과세는 일시납 1억 원 이하, 10년 이상 유지가 조건이고, 이 1억은 여러 보험사 가입분을 합쳐서 봅니다. '
    '수령 방식은 종신형, 확정기간형, 상속형 세 가지라서 같은 1억도 월 수령액이 달라집니다. '
    '내년 평균공시이율은 2.50퍼센트에서 2.25퍼센트로 낮아진다고 보도됐습니다.'
)

CAPTION_IG = '''목돈 1억을 즉시연금에 넣으면 매달 얼마를 받을까요?

1. 상속형으로 1억을 넣고 공시이율 3%를 단순 가정하면 연 300만 원, 월 25만 원입니다. 실제 월 수령액은 사업비와 환급 재원이 빠져 이보다 적습니다.
2. 비과세 조건은 일시납 합계 1억 원 이하, 10년 이상 유지입니다. 여러 보험사 가입분을 합쳐서 판단합니다.
3. 수령 방식은 종신형, 확정기간형, 상속형 세 가지이고 상속형이 월 수령액이 가장 적습니다.
4. 보도에 따르면 2027년 평균공시이율은 2.50%에서 2.25%로 낮아집니다.

가입 시점에 따라 요건이 다를 수 있으니 상품설명서와 보험사 안내를 확인하세요. 자세한 내용은 블로그에 정리해두었습니다. 특정 상품 가입을 권유하지 않습니다.

#즉시연금 #즉시연금1억 #일시납연금보험 #비과세 #노후준비'''


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
                           'selected_title': '즉시연금1억 블로그 유도 릴스',
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
