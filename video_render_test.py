"""build_video_multi 렌더 검증용(게시 없음) — 합성 프레임·무음 톤으로 필터 그래프가 도는지 확인."""
import sys, os, subprocess, tempfile
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
import video_poster as vp
d = tempfile.mkdtemp()
fr = []
for i, c in enumerate([(30, 40, 90), (90, 60, 30), (30, 90, 60), (80, 30, 80)]):
    p = os.path.join(d, f'f{i}.jpg'); Image.new('RGB', (1080, 1920), c).save(p); fr.append(p)
aud = os.path.join(d, 'a.mp3')
subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'sine=frequency=300:duration=12', '-q:a', '5', aud], check=True, capture_output=True)
ph = [{'start': 0, 'end': 3, 'text': '직원이 퇴사하면'}, {'start': 3, 'end': 6, 'text': '14일 안에 지급'},
      {'start': 6, 'end': 9, 'text': '연 20% 지연이자'}, {'start': 9, 'end': 12, 'text': '저장해두세요'}]
out = os.path.join(d, 'o.mp4')
vp.build_video_multi(fr, aud, output_path=out, duration=12.0, phrases=ph, work_dir=d)
r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out], capture_output=True, text=True)
print('OK duration', r.stdout.strip(), 'size', os.path.getsize(out))
