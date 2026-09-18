#!/usr/bin/env python3
"""
블로그 글 ↔ Threads 포스팅 연결
- blog_posts.json 에 발행된 블로그 글을 key 별로 등록해두면,
  같은 key 를 가진 Threads 소재가 나갈 때 댓글로 블로그 링크를 하나 더 단다.
- 링크는 본문이 아니라 댓글에만 (도달 영향 최소화), 주제가 정확히 맞을 때만.
- URL 이 비어 있으면(아직 미발행) 아무것도 붙이지 않는다.
"""
import os, json

BLOG_POSTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blog_posts.json')


def _load():
    if not os.path.exists(BLOG_POSTS_FILE):
        return []
    with open(BLOG_POSTS_FILE, encoding='utf-8') as f:
        return json.load(f)


def get_blog_url(key, prefer='naver'):
    for p in _load():
        if p.get('key') == key:
            return p.get(prefer) or p.get('tistory') or p.get('naver') or None
    return None


def blog_comment(key):
    """Threads 댓글용 문구(반말). 매칭되는 발행 글이 없으면 None."""
    url = get_blog_url(key)
    if not url:
        return None
    return f'이 얘기 숫자까지 자세히 정리해둔 글 → {url}'


def log_source(key):
    """content_log.json 의 source 필드에 넣을 마커 — 주간분석에서 블로그링크 유무별 도달 비교용."""
    return f'blog:{key}' if get_blog_url(key) else ''
