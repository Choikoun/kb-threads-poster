#!/usr/bin/env python3
"""쇼핑 글 발행~기록 일괄 실행(2026-11-13). 매일 반복 작업의 토큰을 줄이기 위한 도구.
사전: shop_make.py 로 자산 생성, 글폴더/naver.txt 작성·점검 완료, 쿠팡 링크 삽입 완료.
사용: python shop_run.py <글폴더> [--from 단계] [--only 단계] [--dry]
단계: naver → reel → yt → tt → igth → record   (진행 상태는 글폴더/.run_state.json 에 저장돼 실패해도 이어서 실행)
출력은 한 단계당 한 줄로만 남긴다.
"""
import sys, os, re, json, io, time, subprocess, contextlib
os.environ.setdefault('NAVER_PROFILE_DIR', 'shop_chrome_profile'); os.environ.setdefault('NAVER_DEBUG_PORT', '9223'); os.environ.setdefault('NAVER_BLOG_ID', 'sobok_biz')
sys.stdout.reconfigure(encoding='utf-8')
STEPS = ['naver', 'reel', 'yt', 'tt', 'igth', 'record']
args = [a for a in sys.argv[1:] if not a.startswith('--')]
folder = args[0].rstrip('/\\')
flag = lambda n: sys.argv[sys.argv.index(n) + 1] if n in sys.argv else None
DRY = '--dry' in sys.argv
spec = json.load(open(f'{folder}/spec.json', encoding='utf-8'))
key = spec['key']
SP = f'{folder}/.run_state.json'
st = json.load(open(SP, encoding='utf-8')) if os.path.exists(SP) else {}
save = lambda: json.dump(st, open(SP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def sh(cmd, check=True, timeout=1500):
    r = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
    if check and r.returncode != 0:
        sys.exit(f"실패: {cmd}\n{(r.stdout + r.stderr)[-600:]}")
    return r.stdout + r.stderr


def chrome_up():
    import requests
    try:
        requests.get('http://127.0.0.1:9223/json/version', timeout=4)
        return True
    except Exception:
        return False


def git_push(msg):
    sh('git add -A ' + ' '.join([f'"{folder}"', f'shop_reel_{key}_split_anim.py'] + [f'_cap_{key}_{s}.txt' for s in ('ig', 'tt', 'th', 'th_reply')] + ['shop_posts.json', '.github/workflows/shop_scheduled_posts.yml']), check=False)
    sh(['git', 'commit', '-q', '-m', msg + '\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>'], check=False)
    sh('git pull --rebase --autostash -q', check=False)
    sh('git push -q')


def s_naver():
    if st.get('naver_url'):
        return
    out = sh([sys.executable, 'ai_tell_check.py', f'{folder}/naver.txt'], check=False)
    if '오류 0개' not in out:
        sys.exit('AI 티 점검 오류: ' + out[-300:])
    if not chrome_up():
        sh([sys.executable, 'naver_blog_poster.py', 'start'], timeout=120)
    import naver_blog_poster as nb
    nb.get_driver().set_window_size(1280, 1000)
    meta, lines, base = nb.parse_post_file(f'{folder}/naver.txt')
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        nb.post_to_naver(meta, lines, base, dry=False)
    m = re.search(r'발행 완료! URL: (\S+)', buf.getvalue())
    if not m:
        sys.exit('네이버 발행 확인 실패: ' + buf.getvalue()[-400:])
    st['naver_url'] = m.group(1); save()
    print('naver', st['naver_url'])


def s_reel():
    if st.get('release'):
        return
    git_push(f'{spec["keyword"]} 글 자산 추가')
    before = sh("gh run list --workflow=shop_reel_build.yml --limit 1 --json databaseId -q .[0].databaseId", check=False).strip()
    sh(['gh', 'workflow', 'run', 'shop_reel_build.yml', '-f', f'module=shop_reel_{key}_split_anim', '-f', f'out={folder}/reel_{key}_split.mp4', '-f', 'voice=gemini:Achird'])
    rid = before
    for _ in range(30):
        time.sleep(4)
        rid = sh("gh run list --workflow=shop_reel_build.yml --limit 1 --json databaseId -q .[0].databaseId", check=False).strip()
        if rid and rid != before:
            break
    sh(['gh', 'run', 'watch', rid, '--exit-status'], timeout=900)
    tag = sh("gh release list --limit 1", check=False).split('\t')[0].strip()
    sh(['gh', 'release', 'download', tag, '-p', '*.mp4', '-D', folder, '--clobber'])
    v = f'{folder}/reel_{key}_split.mp4'
    sh(['ffmpeg', '-y', '-loglevel', 'error', '-i', v, '-vf', 'scale=540:960', '-c:v', 'libx264', '-crf', '30', '-preset', 'medium', '-c:a', 'aac', '-b:a', '64k', f'{folder}/reel_{key}_split_tt.mp4'])
    st['release'] = tag; save()
    print('reel', tag)


def cap(n):
    return open(f'_cap_{key}_{n}.txt', encoding='utf-8').read()


def s_yt():
    if st.get('yt_done'):
        return
    c = spec['caption']
    desc = f"{c['headline']}\n{c['detail']}\n\n가격 정리와 링크: {st['naver_url']}\n※ 직접 써본 후기가 아닌 가격 정보 정리예요.\n이 포스팅은 쿠팡 파트너스 활동의 일환으로, 수수료를 제공받습니다.\n\n{c['tags']}\n"
    open(f'_yt_desc_{key}.txt', 'w', encoding='utf-8').write(desc)
    out = sh([sys.executable, 'shop_yt_upload.py', f'{folder}/reel_{key}_split.mp4', spec['yt_title'], f'_yt_desc_{key}.txt'], timeout=900)
    if '게시된 동영상' not in out:
        sys.exit('유튜브 게시 확인 실패: ' + out[-400:])
    m = re.search(r'https://youtube\.com/shorts/[\w-]+', out)
    st['yt_done'] = m.group(0) if m else 'ok'; save()
    print('yt', st['yt_done'])


def s_tt():
    if st.get('tt_done'):
        return
    out = sh([sys.executable, '-W', 'ignore', 'shop_tt_now.py', f'{folder}/reel_{key}_split_tt.mp4', f'_cap_{key}_tt.txt'], timeout=900)
    if 'submit True' not in out:
        sys.exit('틱톡 게시 실패: ' + out[-400:])
    st['tt_done'] = True; save()
    print('tt ok')


def s_igth():
    if st.get('igth_done'):
        return
    url = f"https://github.com/Choikoun/kb-threads-poster/releases/download/{st['release']}/reel_{key}_split.mp4"
    before = sh("gh run list --workflow=shop_scheduled_posts.yml --limit 1 --json databaseId -q .[0].databaseId", check=False).strip()
    sh(['gh', 'workflow', 'run', 'shop_scheduled_posts.yml', '-f', f'item={key}', '-f', f'video_url={url}'])
    rid = before
    for _ in range(30):
        time.sleep(4)
        rid = sh("gh run list --workflow=shop_scheduled_posts.yml --limit 1 --json databaseId -q .[0].databaseId", check=False).strip()
        if rid and rid != before:
            break
    sh(['gh', 'run', 'watch', rid, '--exit-status'], timeout=900)
    st['igth_done'] = True; save()
    print('igth ok')


def s_record():
    p = 'shop_posts.json'
    d = json.load(open(p, encoding='utf-8'))
    d = [x for x in d if x.get('key') != spec['post_key']]
    d.append(dict(key=spec['post_key'], title=spec['title'], naver=st['naver_url'], date=spec['date'], keyword=spec['keyword'], affiliate='쿠팡 1곳',
                  links={'coupang_blog': f'blog_{spec["sub_key"]}'},
                  reel=dict(ig='게시(깃허브)', threads='게시(깃허브)', yt=st.get('yt_done', ''), clip='미등록', tiktok='게시')))
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    git_push(f'{spec["keyword"]} 발행 기록')
    print('record ok')


FN = dict(naver=s_naver, reel=s_reel, yt=s_yt, tt=s_tt, igth=s_igth, record=s_record)
run = STEPS
if flag('--only'):
    run = [flag('--only')]
elif flag('--from'):
    run = STEPS[STEPS.index(flag('--from')):]
if DRY:
    print('실행 예정:', ' → '.join(run), '| 완료 상태:', {k: bool(v) for k, v in st.items()})
    sys.exit()
for s in run:
    FN[s]()
print('전체 완료:', st.get('naver_url'))
