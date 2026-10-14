#!/usr/bin/env python3
"""
단기납종신 판매중단 이후 소재 릴스형 영상 (Instagram Reels 전용, 존댓말)
- 사실 출처: 보험저널 보도(2026-09-22, 10-13), 보험업감독업무시행세칙 제5-19조·별표18. 확정/전망 구분. 상담링크는 댓글에만
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

HOOK = '700종신 다음은\n단기납종신일까?'

SCENES = [
    {'image_query': 'insurance documents desk consultation calm',
     'image_prompt': 'A flat design illustration of insurance documents on a desk with a calendar, navy and gold color palette, soft colors'},
    {'image_query': 'calendar year 2027 planning documents',
     'image_prompt': 'A flat design illustration of a calendar page and a downward arrow chart, soft colors'},
    {'image_query': 'business owner reviewing contract office',
     'image_prompt': 'A flat design illustration of a business owner reviewing a contract at an office desk, soft colors'},
    {'image_query': 'financial consultant meeting client office calm',
     'image_prompt': 'A flat design illustration of a financial consultant explaining a document to a client across a desk, soft colors'},
]

NARRATION_IG = (
    '금융당국의 즉시 판매중단 권고는 700종신에만 적용됐고 단기납종신은 대상에서 빠졌습니다. '
    '700종신은 납입 중에 환급률이 원금에 닿는 구조이고, 단기납은 대부분 납입이 끝난 뒤에 닿습니다. '
    '하지만 2027년에는 공시이율이 2.50퍼센트에서 2.25퍼센트로 내려가고 수수료 4년 분급도 시행됩니다. '
    '2027년 1월에 환급 구조가 개정될 수 있다는 건 업계 전망이지 확정이 아닙니다. '
    '원금 도달 시점이 납입 중인지 완료 후인지 설계서에서 먼저 확인해보세요.'
)

CAPTION_IG = '''700종신 판매중단 이후 단기납종신은 어떻게 될까요?

1. 즉시 판매중단은 700종신만 해당됩니다. 단기납종신과 건강종신은 제외됐습니다.
2. 700종신은 납입 중에, 단기납종신은 대부분 납입이 끝난 뒤에 환급률이 원금에 도달합니다.
3. 2027년에는 평균공시이율이 2.50%에서 2.25%로 내려가고, 판매수수료 4년 분급과 계약체결비용 한도가 시행됩니다.

2027년 1월 환급구조 개정 가능성은 업계 전망이며 확정이 아닙니다.

가입 전에는 원금 도달 시점, 가입 목적, 납입 여력을 설계서로 먼저 확인하세요. 자세한 내용은 블로그에 정리해두었습니다. 보도 내용을 정리한 것이며 특정 상품 가입을 권유하지 않습니다.

#단기납종신 #700종신 #종신보험 #무저해지 #사업주'''


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
                           'selected_title': '단기납종신 판매중단 이후 블로그 유도 릴스',
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
