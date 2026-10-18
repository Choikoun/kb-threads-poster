#!/usr/bin/env python3
"""KB 블로그 유도 릴스 애니메이션 어댑터 — shop_anim(쇼핑 세션 엔진)의 부품을 가져다 쓰되
배경은 상품 사진 대신 그라데이션, 하단 고지는 KB용. shop_anim.py 는 수정하지 않는다.

장면(dict) 종류:
  hook : 배너(제목+카운트업 숫자) + 막대 비교 → kind='hook', title, count=(목표,'접미사'), small, rows=[(라벨,값,색)], gap
  bars : 배너(큰 글자) + 막대 비교               → kind='bars', title, big, small, rows, gap, fmt(값→문자열)
  list : 배너 + 체크리스트(최대 3줄)            → kind='list', title, big, small, items
  cta  : 북마크 + 안내 패널                      → kind='cta', title, big, small, panel
모든 장면: say(내레이션), col(강조색). 환경변수 KB_PREVIEW=1 이면 장면별 마지막 프레임 PNG만 저장(_tmp_vid/prev*.png).
주의: ffmpeg는 GitHub Actions 에서만 가능. 장면별 TTS를 쓰므로 REEL_SAVE_CTA 는 해제하고(마지막 cta 장면 대본에 '저장'을 직접 쓴다).
"""
import os, sys
os.environ.pop('REEL_SAVE_CTA', None)
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image, ImageDraw
import shop_anim as A
from shop_anim import c, ease, W, H, NAVY, GOLD, RED, GREEN
from card_generator import load_font

FOOT = '정보 정리용 · 가상 사례이며 세법과 제도는 바뀔 수 있습니다'
_bg = {}


def kb_bg(i, extra=1.12):
    """장면 번호별 그라데이션 배경(큰 이미지, A.bg_frame 으로 줌 크롭)"""
    k = i % 3
    if k in _bg:
        return _bg[k]
    top, bot = [('#0F1A33', '#1B2A4A'), ('#13223F', '#243B63'), ('#0F1A33', '#2A2F57')][k]
    bw, bh = int(W * extra), int(H * extra)
    im = Image.new('RGB', (bw, bh))
    d = ImageDraw.Draw(im)
    t0, t1 = c(top), c(bot)
    for y in range(bh):
        r = y / (bh - 1)
        d.line([(0, y), (bw, y)], fill=tuple(int(t0[j] + (t1[j] - t0[j]) * r) for j in range(3)))
    _bg[k] = im
    return im


def bars2(im, rows, y0, p, fmt=None, gap=None, hi=None):
    """shop_anim.bars 와 같은 모양이지만 값 표기 함수(fmt)를 받는다 — 퍼센트·소수 표시용"""
    fmt = fmt or (lambda v: f'{int(v):,}')
    e = ease(p)
    A.panel(im, [50, y0 - 30, W - 50, y0 + 100 * len(rows) + 50], a=min(1.0, e * 2))
    d = ImageDraw.Draw(im)
    mx = max(v for _, v, _ in rows)
    x0, wmax = 330, 600
    for k, (lab, v, col) in enumerate(rows):
        y = y0 + k * 100 + 30
        on = hi is None or hi == k
        col_ = c(col) if on else tuple(int(t * 0.45 + 28) for t in c(col))
        d.text((70, y), lab, font=load_font('bold', 30), fill=c('#FFFFFF') if on else c('#8A91A3'), anchor='lm')
        q = ease(p * 1.1 - k * 0.12)
        w = int(wmax * v / mx * q)
        if w > 6:
            d.rounded_rectangle([x0, y - 24, x0 + w, y + 24], radius=12, fill=col_)
            if w > 150:
                d.text((x0 + w - 14, y), fmt(v * q), font=load_font('extrabold', 30), fill=c('#FFFFFF'), anchor='rm')
            else:  # 짧은 막대는 숫자를 막대 오른쪽 바깥에
                d.text((x0 + w + 16, y), fmt(v * q), font=load_font('extrabold', 30), fill=c('#FFFFFF'), anchor='lm')
    if gap and p > 0.7:
        d.text((W // 2, y0 + 100 * len(rows) + 5), gap, font=load_font('extrabold', 36), fill=c('#FFD27A'), anchor='mm')


def render(sc, i, p, t, t01, work):
    im = A.bg_frame(kb_bg(i), t01, 1 if i % 2 == 0 else -1)
    k = sc['kind']
    col = sc.get('col', GOLD)
    if k == 'hook':
        # 첫 프레임부터 결과 숫자가 보이도록 배너 등장·카운트업을 35% 지점부터 시작(스터디: 훅 장면 첫 프레임=결과 숫자)
        A.banner(im, sc['title'], '', sc.get('small', ''), col, 0.35 + 0.65 * p, countup=sc.get('count'))
        bars2(im, sc['rows'], 700, max(0.0, (t - 0.6) / 1.4), sc.get('fmt'), sc.get('gap'), sc.get('hi'))
    elif k == 'bars':
        A.banner(im, sc['title'], sc.get('big', ''), sc.get('small', ''), col, p)
        bars2(im, sc['rows'], 700, max(0.0, (t - 0.4) / 1.4), sc.get('fmt'), sc.get('gap'), sc.get('hi'))
    elif k == 'list':
        A.banner(im, sc['title'], sc.get('big', ''), sc.get('small', ''), col, p)
        A.checklist(im, sc['items'], 700, max(0.0, (t - 0.5) / 1.8))
    else:  # cta
        A.banner(im, sc['title'], sc.get('big', ''), sc.get('small', ''), col, p)
        A.bookmark(im, max(0.0, (t - 0.2) / 0.8), t)
        if t > 0.8 and sc.get('panel'):
            A.panel(im, [90, 1110, W - 90, 1230], alpha=225)
            ImageDraw.Draw(im).text((W // 2, 1170), sc['panel'], font=load_font('bold', 42), fill=(255, 255, 255), anchor='mm')
    ImageDraw.Draw(im).text((W // 2, 1790), FOOT, font=load_font('regular', 26), fill=c('#B8BECC'), anchor='mm')
    return im


def preview(scenes, seconds=3.0, d='_tmp_kb'):
    """TTS·ffmpeg 없이 장면별 PNG만 저장(_tmp_kb/). 쇼핑 미리보기 폴더(_tmp_vid)와 섞이지 않게 별도 폴더 사용.
    t=seconds 시점(애니메이션이 거의 끝난 상태)과 t=0.5초 시점(등장 중)을 같이 뽑는다."""
    os.makedirs(d, exist_ok=True)
    for i, sc in enumerate(scenes):
        for tag, t in (('end', seconds), ('mid', 0.5)):
            render(sc, i, min(1.0, t / 0.8), t, min(1.0, t / seconds), None).save(f'{d}/prev{i}_{tag}.png')
    print('미리보기 저장:', d)


def make_video(scenes, out):
    if os.environ.get('KB_PREVIEW'):
        return preview(scenes)
    A.run(scenes, render, out)


def publish(scenes, caption, title, hook_check=True):
    """영상 생성 → GitHub release 업로드 → 인스타 릴스 게시 → instagram_log 기록 (기존 *_reels_post.py 와 같은 흐름)"""
    import tempfile, shutil
    from datetime import datetime, timezone, timedelta
    from annuity_video_poster import post_reels, load_ig_log, save_ig_log
    import news_auto_poster as nap
    KST = timezone(timedelta(hours=9))
    if hook_check and not scenes[-1]['say'].count('저장'):
        raise SystemExit('마지막 장면 대본에 저장 유도 문구가 없습니다')
    tmp = tempfile.mkdtemp()
    try:
        out = os.path.join(tmp, 'kb_anim.mp4')
        make_video(scenes, out)
        url = nap.upload_to_github_release(out)
        if not url:
            print('영상 업로드 실패 - 종료'); sys.exit(1)
        ig_id = post_reels(url, caption)
        if not ig_id:
            print('Instagram 포스팅 실패'); sys.exit(1)
        log = load_ig_log()
        log.append({'ig_post_id': ig_id, 'type': 'reels', 'selected_title': title, 'engine': 'kb_anim',
                    'date': datetime.now(KST).strftime('%Y-%m-%d %H:%M')})
        save_ig_log(log)
        print(f'Instagram 완료: {ig_id}')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
