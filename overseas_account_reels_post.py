#!/usr/bin/env python3
"""
해외금융계좌신고 소재 릴스형 영상 (Instagram Reels 전용, 존댓말)
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

HOOK = '해외 계좌 5억원\n신고 안 하면'

SCENES = [
    {'image_query': 'businessman world map globe office finance',
     'image_prompt': 'A flat design illustration of a korean businessman looking at a world map with connected data lines, representing international financial information exchange, navy and gold color palette, soft colors'},
    {'image_query': 'bank statement documents calculator desk',
     'image_prompt': 'A flat design illustration of bank statements, a calculator, and a passport on a desk representing overseas account reporting, soft colors'},
    {'image_query': 'warning alert document stamp',
     'image_prompt': 'A flat design illustration of an official document with a warning stamp and a magnifying glass, representing a tax penalty notice, soft colors'},
    {'image_query': 'tax office consultation korean',
     'image_prompt': 'A flat design illustration of a financial consultant explaining a document to a client across a desk, soft colors'},
]

NARRATION_IG = (
    '해외 예금이나 주식 계좌를 갖고 계신 분들 중, 매년 6월에 신고해야 하는 의무가 있다는 걸 모르고 지나가는 경우가 많습니다. '
    '연중 단 하루라도 잔액이 5억원을 넘긴 적이 있다면, 그 다음 해 6월에 반드시 알려야 합니다. '
    '이제는 금융정보자동교환협정으로 계좌 정보가 국세청에 자동으로 넘어가기 때문에, 신고하지 않으면 나중에라도 드러날 가능성이 높습니다. '
    '자세한 기준과 불이익은 캡션에서 확인해보세요.'
)

CAPTION_IG = '''해외 예금이나 주식 계좌를 갖고 계신 분들 중, 매년 6월에 신고해야 하는 의무가 있다는 걸 모르고 지나가는 경우가 많습니다.

1. 연중 단 하루라도 잔액 합계가 5억원을 넘기면, 그 다음 해 6월에 신고 대상이 됩니다(연말 잔액이 아니라 연중 최고 잔액 기준).
2. 신고하지 않으면 미신고 금액의 최대 20% 과태료, 50억원 초과 시 형사처벌 대상까지 될 수 있습니다.
3. 다만 국세청 통보 전에 스스로 신고하면 과태료를 크게 감경받을 수 있습니다.

금융정보자동교환협정(CRS)으로 100개국 넘는 나라와 매년 계좌 정보를 주고받는 시대라, 신고 여부를 미리 점검해두시는 게 안전합니다.

자세한 계산 구조는 블로그에 정리해두었습니다.

#해외금융계좌신고 #해외계좌신고 #국제조세 #자산관리 #재무설계'''


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
                           'selected_title': '해외금융계좌신고 블로그 유도 릴스',
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
