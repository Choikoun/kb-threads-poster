#!/usr/bin/env python3
"""이미지 메타데이터(EXIF·GPS·카메라·소프트웨어 태그 등) 제거 — 폴더 안 jpg/png를 픽셀 그대로 다시 저장.
사용: python strip_meta.py <폴더 또는 파일> ...
스톡 사진의 촬영 정보가 남지 않게 하는 위생 처리이며, AI 생성 표시(틱톡·클립 토글)와는 별개로 그대로 켠다."""
import sys, os
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')


def clean(p):
    im = Image.open(p)
    fmt = im.format
    had = bool(im.info.get('exif') or im.info.get('icc_profile') or im.info.get('xmp') or getattr(im, 'text', None))
    out = Image.new(im.mode, im.size); out.putdata(list(im.getdata()))
    if fmt == 'JPEG':
        out.save(p, 'JPEG', quality=95, subsampling=0)
    else:
        out.save(p, fmt)
    return had


for a in sys.argv[1:]:
    ps = [os.path.join(r, f) for r, _, fs in os.walk(a) for f in fs] if os.path.isdir(a) else [a]
    for p in ps:
        if p.lower().endswith(('.jpg', '.jpeg', '.png')):
            print(('정리' if clean(p) else '이미 깨끗'), p)
