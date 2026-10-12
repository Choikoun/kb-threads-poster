#!/usr/bin/env python3
"""
증여세율표 소재 릴스형 영상 (Instagram Reels 전용, 존댓말)
- 사실 출처: 국세청 안내(세율·증여재산공제·혼인출산공제), 상속세 및 증여세법. 상담링크는 댓글에만
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

HOOK = '자녀에게 1억 증여\n세금은 얼마일까?'

SCENES = [
    {'image_query': 'parent and adult child talking home table documents',
     'image_prompt': 'A flat design illustration of a parent and an adult child talking at a table with documents, navy and gold color palette, soft colors'},
    {'image_query': 'calculator documents tax desk',
     'image_prompt': 'A flat design illustration of a calculator and a tax rate table on a desk, soft colors'},
    {'image_query': 'family wedding baby congratulations',
     'image_prompt': 'A flat design illustration of a newlywed couple and a baby with a gift box, soft colors'},
    {'image_query': 'financial consultant meeting client office calm',
     'image_prompt': 'A flat design illustration of a financial consultant explaining a document to a client across a desk, soft colors'},
]

NARRATION_IG = (
    '증여세율 10퍼센트에서 50퍼센트는 증여한 금액이 아니라 공제를 뺀 과세표준에 적용됩니다. '
    '성년 자녀가 처음 1억 원을 받으면 공제 5천만 원을 빼고 남은 5천만 원에 10퍼센트라 세금은 500만 원입니다. '
    '3억 원은 4천만 원, 5억 원은 8천만 원으로 금액은 세 배인데 세금은 여덟 배가 됩니다. '
    '결혼이나 출산 후 2년 안에 증여받으면 공제가 1억 원 더해져 최대 1억 5천만 원까지 공제됩니다. '
    '10년 안에 받은 증여가 있는지 먼저 확인해보세요.'
)

CAPTION_IG = '''자녀에게 1억 원을 증여하면 세금은 얼마일까요?

1. 증여세율 10~50%는 증여액이 아니라 공제를 뺀 과세표준에 적용됩니다.
2. 성년 자녀가 처음 받는 경우(공제 5천만 원): 1억 원은 500만 원, 3억 원은 4,000만 원, 5억 원은 8,000만 원입니다. 신고세액공제 전 금액이며 구조를 설명하기 위한 계산입니다.
3. 혼인·출산 후 2년 안에 직계존속에게 받으면 1억 원이 추가로 공제되어 성년 자녀는 최대 1억 5천만 원까지 공제됩니다(2024년 이후 증여분).

공제는 10년 단위로 합산됩니다. 최근 10년 안에 받은 증여가 있는지 먼저 확인하세요.

자세한 계산은 블로그에 정리해두었습니다. 세법은 개정될 수 있으니 신고 전에는 국세청 안내나 세무전문가 확인이 필요합니다.

#증여세율표 #증여세 #증여재산공제 #혼인출산공제 #사업주'''


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
                           'selected_title': '증여세율표 블로그 유도 릴스',
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
