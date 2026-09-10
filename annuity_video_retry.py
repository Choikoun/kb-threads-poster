#!/usr/bin/env python3
"""
이미 업로드된 GitHub Release mp4를 재사용해 Threads/IG 재발행 시도 (진단용)
"""
import sys, json
sys.stdout.reconfigure(encoding='utf-8')

import news_auto_poster as nap
from annuity_video_poster import CAPTION_THREADS, CAPTION_IG, CONSULT_COMMENT_THREADS, post_reels, load_ig_log, save_ig_log
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))
VIDEO_URL_THREADS = 'https://github.com/Choikoun/kb-threads-poster/releases/download/video-20260910-111616/video_threads.mp4'
VIDEO_URL_IG = 'https://github.com/Choikoun/kb-threads-poster/releases/download/video-20260910-111644/video_ig.mp4'


def main():
    main_id = nap.post_video_to_threads(CAPTION_THREADS, [CONSULT_COMMENT_THREADS], VIDEO_URL_THREADS)
    if main_id:
        nap.log_content(main_id, 'insurance', 'annuity_sales_video', '연금보험 가입시기 비교 릴스',
                        line_count=CAPTION_THREADS.count('\n') + 1)
        print(f'Threads 완료: {main_id}')
    else:
        print('Threads 재시도도 실패')

    ig_id = post_reels(VIDEO_URL_IG, CAPTION_IG)
    if ig_id:
        ig_log = load_ig_log()
        ig_log.append({'ig_post_id': ig_id, 'type': 'reels',
                       'selected_title': '연금보험 가입시기 비교 릴스',
                       'date': datetime.now(KST).strftime('%Y-%m-%d %H:%M')})
        save_ig_log(ig_log)
        print(f'Instagram 완료: {ig_id}')
    else:
        print('Instagram 재시도도 실패')


if __name__ == '__main__':
    main()
