import sys
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from youtube_transcript_api import YouTubeTranscriptApi

sys.stdout.reconfigure(encoding='utf-8')

KTV_CHANNEL_ID = 'UCIMOytYIzaUpoAM2bpT4JZQ'
KST = timezone(timedelta(hours=9))

# 국무회의/정부 발표 관련 키워드
KEYWORDS = ['국무회의', '대통령', '지시', '브리핑', '정부', '장관', '발표', '회의', '대책']

OUTPUT_FILE = 'ktv_briefing.md'


def get_latest_videos(limit=15):
    """KTV RSS에서 최신 영상 가져오기"""
    url = f'https://www.youtube.com/feeds/videos.xml?channel_id={KTV_CHANNEL_ID}'
    r = requests.get(url, timeout=10)
    tree = ET.fromstring(r.text)
    ns = {
        'atom': 'http://www.w3.org/2005/Atom',
        'yt': 'http://www.youtube.com/xml/schemas/2015'
    }
    entries = tree.findall('atom:entry', ns)
    videos = []
    for e in entries[:limit]:
        title = e.find('atom:title', ns).text
        vid_id = e.find('yt:videoId', ns).text
        published = e.find('atom:published', ns).text[:10]
        videos.append({'title': title, 'id': vid_id, 'date': published})
    return videos


def filter_relevant(videos):
    """오늘 날짜 + 관련 키워드 필터링"""
    today = datetime.now(KST).strftime('%Y-%m-%d')
    relevant = []
    for v in videos:
        if v['date'] != today:
            continue
        if any(kw in v['title'] for kw in KEYWORDS):
            relevant.append(v)
    return relevant


def get_transcript(vid_id):
    """자막 추출"""
    try:
        ytt = YouTubeTranscriptApi()
        t = ytt.fetch(vid_id, languages=['ko'])
        snippets = list(t)
        text = ' '.join([x.text if hasattr(x, 'text') else x['text'] for x in snippets])
        return text[:3000]  # 앞 3000자
    except Exception as e:
        return f'[자막 없음: {e}]'


def summarize_issue(title, transcript):
    """핵심 이슈 추출 (제목 + 자막 앞부분 기반)"""
    # 자막이 없으면 제목만
    if '자막 없음' in transcript:
        return f'**{title}**\n자막 미제공'

    # 자막 앞 500자에서 핵심 문장 추출
    summary = transcript[:500].replace('\n', ' ').strip()
    return f'**{title}**\n{summary}...'


def main():
    now_kst = datetime.now(KST).strftime('%Y-%m-%d %H:%M KST')
    print(f'KTV 모니터링 시작: {now_kst}')

    videos = get_latest_videos()
    relevant = filter_relevant(videos)

    if not relevant:
        print('오늘 관련 영상 없음')
        # 브리핑 파일에 빈 섹션
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(f'# 🏛️ KTV 국무회의 브리핑\n*{now_kst}*\n\n오늘 관련 영상 없음\n')
        return

    print(f'오늘 관련 영상 {len(relevant)}개')

    issues = []
    for v in relevant:
        print(f'  처리 중: {v["title"]}')
        transcript = get_transcript(v['id'])
        issue = {
            'title': v['title'],
            'url': f'https://youtu.be/{v["id"]}',
            'transcript_preview': transcript[:500]
        }
        issues.append(issue)

    # 브리핑 파일 저장
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f'# 🏛️ KTV 국무회의 브리핑\n*{now_kst}*\n\n---\n\n')
        for issue in issues:
            f.write(f'## {issue["title"]}\n')
            f.write(f'🔗 {issue["url"]}\n\n')
            f.write(f'{issue["transcript_preview"]}...\n\n---\n\n')

    print(f'브리핑 저장 완료: {OUTPUT_FILE}')

    # JSON도 저장 (자동화 활용용)
    with open('ktv_latest.json', 'w', encoding='utf-8') as f:
        json.dump(issues, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
