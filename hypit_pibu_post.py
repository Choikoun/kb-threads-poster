#!/usr/bin/env python3
"""hypit로 만든 직장피부양자 릴스(SunHi 음성)를 이미 올라간 릴리스 영상 주소로 인스타 릴스에 게시. 구조 실험용(조회 비교는 목소리가 달라 참고만)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from datetime import datetime, timezone, timedelta
from annuity_video_poster import post_reels, load_ig_log, save_ig_log
import pibu_anim_reels_post as P

URL = 'https://github.com/Choikoun/kb-threads-poster/releases/download/video-20261104-113252/pibu_v4_sunhi.mp4'
TITLE = '직장피부양자뜻 hypit 무료 릴스(SunHi 음성, 구조 실험)'


def main():
    ig_id = post_reels(URL, P.CAPTION)
    if not ig_id:
        print('Instagram 포스팅 실패'); sys.exit(1)
    log = load_ig_log()
    log.append({'ig_post_id': ig_id, 'type': 'reels', 'selected_title': TITLE, 'engine': 'hypit',
                'date': datetime.now(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M')})
    save_ig_log(log)
    print(f'Instagram 완료: {ig_id}')


if __name__ == '__main__':
    main()
