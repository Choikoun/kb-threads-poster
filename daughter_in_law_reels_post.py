#!/usr/bin/env python3
"""
며느리증여 소재 릴스형 영상 (Instagram Reels 전용, 존댓말)
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

HOOK = '며느리 통장으로\n5천만원 보내면?'

SCENES = [
    {'image_query': 'mother and daughter in law kitchen warm',
     'image_prompt': 'A flat design illustration of a korean mother-in-law handing an envelope to her daughter-in-law in a warm kitchen, navy and gold color palette, soft colors'},
    {'image_query': 'family tree relationship diagram',
     'image_prompt': 'A flat design illustration of a family tree diagram with a son and a daughter-in-law connected by a line, soft colors'},
    {'image_query': 'tax notice document calculator',
     'image_prompt': 'A flat design illustration of a tax notice document with a calculator showing a gift tax amount, soft colors'},
    {'image_query': 'financial consultant meeting client office calm',
     'image_prompt': 'A flat design illustration of a financial consultant explaining a document to a client across a desk, soft colors'},
]

NARRATION_IG = (
    '시어머니가 며느리 통장으로 5천만원을 보내면 세금이 얼마나 나올까요. '
    '같은 금액을 아들에게 보내면 공제 5천만원으로 세금이 없지만, 며느리는 기타친족이라 공제가 1천만원뿐입니다. '
    '그래서 남은 4천만원에 10%가 붙어 약 400만원의 증여세가 나옵니다. '
    '자세한 계산 기준은 캡션에서 확인해보세요.'
)

CAPTION_IG = '''시어머니가 며느리 통장으로 5천만원을 보내면 세금이 얼마나 나올까요.

1. 증여재산공제는 받는 사람과의 관계로 갈립니다. 아들 같은 직계비속은 10년간 5천만원, 며느리와 사위는 기타친족이라 1천만원입니다.
2. 5천만원을 보내면 아들은 공제 후 과세표준이 0원이라 세금이 없고, 며느리는 4천만원에 10%가 붙어 약 400만원입니다.
3. 아들 통장을 잠깐 거쳐서 며느리에게 보내는 방식은 실질과세 원칙상 직접 증여로 볼 수 있습니다.

누구 이름으로 어떻게 줄지 미리 계산해보는 게 먼저입니다.

자세한 계산 구조는 블로그에 정리해두었습니다.

#며느리증여 #기타친족공제 #시부모증여세 #증여세 #자녀부부증여'''


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
                           'selected_title': '며느리증여 블로그 유도 릴스',
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
