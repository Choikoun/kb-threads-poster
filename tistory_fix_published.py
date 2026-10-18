#!/usr/bin/env python3
"""이미 발행된 티스토리 글의 표시 결함 보정(2026-10-18 사용자 지적):
 - 본문에 그대로 노출된 별표(**)를 제거
 - '· 문구: https://...' 형태의 출처 줄을 '· <a href>문구</a>' 링크로 변환
이미지·구조·제목은 건드리지 않는다(에디터에서 본문 HTML만 문자열 치환).
사용: python tistory_fix_published.py 311 [304 305 ...]   (--dry 이면 변경 내용만 출력)"""
import sys, re, time
sys.argv_saved = sys.argv[:]
import naver_blog_poster as nb
import tistory_poster as tp
sys.stdout.reconfigure(encoding='utf-8')

SRC = re.compile(r'((?:·|&middot;)\s*)([^<:：\n]+?)\s*[:：]\s*(https?://[^\s<]+)')


def transform(h):
    h = h.replace('**', '')
    h = SRC.sub(lambda m: f'{m.group(1)}<a href="{m.group(3)}" target="_blank" rel="noopener">{m.group(2).strip()}</a>', h)
    return h


def wait_editor(d):
    for _ in range(40):
        time.sleep(1)
        if d.execute_script("return typeof tinymce!=='undefined' && !!tinymce.activeEditor && !!tinymce.activeEditor.getBody()"):
            break
    time.sleep(3)
    tp._dismiss_alert(d)


def fix(d, pid, dry=False):
    d.get(f'https://freedom-of-economic.tistory.com/manage/post/{pid}')
    wait_editor(d)
    cur = d.execute_script("return tinymce.activeEditor.getContent()")
    new = transform(cur)
    n_star = cur.count('**')
    n_src = len(SRC.findall(cur))
    print(f'#{pid}: 별표 {n_star}개, 출처 줄 {n_src}개', '→ 변경 없음' if new == cur else '→ 보정')
    if new == cur or dry:
        return False
    d.execute_script("const ed=tinymce.activeEditor; ed.focus(); ed.setContent(arguments[0]); ed.undoManager.add(); ed.fire('input'); ed.fire('keyup'); ed.fire('change'); ed.nodeChanged(); tinymce.triggerSave();", new)
    time.sleep(1)
    after = d.execute_script("return tinymce.activeEditor.getContent()")
    assert '**' not in after, '별표가 남았음'
    d.find_element(tp.By.ID, 'publish-layer-btn').click()
    time.sleep(1.5)
    d.execute_script("const r=document.querySelector('#open20'); if(r){r.click(); r.dispatchEvent(new Event('change',{bubbles:true}));}")
    time.sleep(0.5)
    d.find_element(tp.By.ID, 'publish-btn').click()
    time.sleep(6)
    return True


if __name__ == '__main__':
    ids = [a for a in sys.argv_saved[1:] if a.isdigit()]
    dry = '--dry' in sys.argv_saved
    d = nb.get_driver()
    tp.ensure_login(d)
    for pid in ids:
        fix(d, pid, dry)
