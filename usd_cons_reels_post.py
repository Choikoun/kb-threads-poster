#!/usr/bin/env python3
"""
달러보험 단점 소재 릴스형 영상 (Instagram Reels 전용, 존댓말)
- 사실 출처: 금감원 2026-06-10 간담회 보도, 약관·사업방법서. 상품·회사명 없음, 상담링크는 댓글에만
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

HOOK = '달러보험 설명 들었는데\n환율 얘기만 기억나요'

SCENES = [
    {'image_query': 'currency exchange rate board dollar won',
     'image_prompt': 'A flat design illustration of a currency exchange board showing dollar and won rates, navy and gold color palette, soft colors'},
    {'image_query': 'calculator documents desk finance',
     'image_prompt': 'A flat design illustration of a calculator and a contract document on a desk, soft colors'},
    {'image_query': 'man reading document carefully coffee table',
     'image_prompt': 'A flat design illustration of a man carefully reading a document, soft colors'},
    {'image_query': 'financial consultant meeting client office calm',
     'image_prompt': 'A flat design illustration of a financial consultant explaining a document to a client across a desk, soft colors'},
]

NARRATION_IG = (
    '금융감독원은 6월 보험사 14곳을 불러 달러보험을 환테크로 오인하지 않도록 환율 위험을 충분히 안내하라고 당부했습니다. '
    '10만 달러를 넣을 때 환율이 1,300원이면 1억 3천만 원, 1,500원이면 1억 5천만 원으로 같은 달러인데 2천만 원 차이가 납니다. '
    '보험사가 정한 환율은 은행 환율과 다를 수 있고, 보험계약대출이 없어 급할 때 뺄 수 있는 돈은 해약환급금의 최대 절반입니다. '
    '환율을 보고 들어갈 돈인지, 10년 넘게 안 써도 되는 돈인지 먼저 확인해보세요.'
)

CAPTION_IG = '''달러보험, 환율 이야기만 듣고 가입하면 놓치는 것들

1. 금융감독원은 2026년 6월 보험사 14곳과의 간담회에서 달러보험을 환테크로 오인하지 않도록 환율 위험을 충분히 안내하라고 당부했습니다.
2. US$100,000를 넣을 때 환율이 1,300원이면 1억 3,000만 원, 1,500원이면 1억 5,000만 원입니다. 구조를 설명하기 위한 가정이며 환율 전망이 아닙니다.
3. 보험사가 정한 환율은 은행 환율과 다를 수 있고, 보험계약대출이 없으며 중도인출은 해약환급금의 최대 50%까지입니다.

이 돈을 10년 넘게 안 써도 되는지가 먼저입니다.

자세한 구조는 블로그에 정리해두었습니다. 이 내용은 특정 상품의 가입이나 해지를 권유하는 것이 아니며, 상품설명서와 약관을 확인하시기 바랍니다.

#달러보험 #달러보험단점 #외화보험 #환율 #사업주'''


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
                           'selected_title': '달러보험단점 블로그 유도 릴스',
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
