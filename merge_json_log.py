#!/usr/bin/env python3
"""
JSON 로그 파일(content_log.json 등) 전용 git 병합 드라이버.
append-only 로그라 두 브랜치가 각자 다른 항목을 추가하면 일반 병합은 충돌나지만,
이건 두 버전을 post_id/ig_post_id 기준으로 union(중복 제거)해서 자동 해결한다.

git이 호출: python merge_json_log.py %O %A %B
  %O = 공통 조상 버전 파일 경로
  %A = 현재(ours) 버전 파일 경로  ← 병합 결과를 여기에 써야 함
  %B = 상대(theirs) 버전 파일 경로
성공 시 exit 0, 자동해결 불가 시 exit 1(그러면 git이 수동 충돌로 표시).
"""
import sys, json


def load(path):
    try:
        with open(path, encoding='utf-8-sig') as f:
            data = json.load(f)
        return data if isinstance(data, list) else None
    except Exception:
        return None


def key(entry):
    # 고유 식별자: post_id > ig_post_id > (전체 내용 튜플)
    return entry.get('post_id') or entry.get('ig_post_id') or json.dumps(entry, sort_keys=True, ensure_ascii=False)


def main():
    if len(sys.argv) < 4:
        return 1
    _o, ours_path, theirs_path = sys.argv[1], sys.argv[2], sys.argv[3]
    ours = load(ours_path)
    theirs = load(theirs_path)
    # 둘 중 하나라도 JSON 배열로 못 읽으면 자동해결 포기 → git 수동 충돌
    if ours is None or theirs is None:
        return 1

    merged = []
    seen = set()
    # ours 순서 유지 후, theirs의 신규 항목만 뒤에 append (append-only 로그 특성)
    for entry in ours + theirs:
        k = key(entry)
        if k in seen:
            continue
        seen.add(k)
        merged.append(entry)

    with open(ours_path, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    return 0


if __name__ == '__main__':
    sys.exit(main())
