#!/usr/bin/env python3
"""저작권 문제 없는 배경음악 직접 합성(코드로 만든 오리지널, 외부 음원 미사용) → assets_safe/*.wav
사용: python gen_bgm.py  (3곡, 각 64초 루프). 부드러운 패드 + 잔잔한 아르페지오, 드럼 없음."""
import numpy as np, wave, os
SR = 44100
OUT = 'assets_safe'
os.makedirs(OUT, exist_ok=True)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def pad(freq, dur, amp=0.18):
    t = np.arange(int(dur * SR)) / SR
    s = np.zeros_like(t)
    for det, a in ((0.0, 1.0), (0.004, 0.6), (-0.004, 0.6)):
        f = freq * (1 + det)
        s += a * (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.12 * np.sin(2 * np.pi * 3 * f * t))
    a_t, r_t = min(1.2, dur * 0.35), min(1.4, dur * 0.4)
    env = np.ones_like(t)
    na, nr = int(a_t * SR), int(r_t * SR)
    env[:na] = np.linspace(0, 1, na) ** 1.5
    env[-nr:] = np.linspace(1, 0, nr) ** 1.5
    return amp * s / 2.5 * env


def pluck(freq, dur=1.2, amp=0.12):
    t = np.arange(int(dur * SR)) / SR
    s = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * 2 * freq * t)
    return amp * s * np.exp(-t * 3.2) * np.minimum(1, t * 200)


def make(name, bpm, prog, scale_shift=0, seed=0, bars_total=32):
    rng = np.random.default_rng(seed)
    beat = 60.0 / bpm
    bar = 4 * beat
    total = bars_total * bar
    out = np.zeros(int(total * SR) + SR * 3)
    for b in range(bars_total):
        chord = prog[b % len(prog)]
        t0 = int(b * bar * SR)
        for n in chord:
            p = pad(midi(n + scale_shift), bar + 0.8)
            out[t0:t0 + len(p)] += p
        # 잔잔한 아르페지오(8분음표, 살짝 확률적으로 건너뛰어 기계적인 느낌 줄이기)
        notes = [n + 12 + scale_shift for n in chord]
        for k in range(8):
            if rng.random() < 0.82:
                nt = notes[(k * 2 + b) % len(notes)] + (12 if k % 4 == 3 else 0)
                tt = t0 + int((k * beat / 2 + rng.normal(0, 0.006)) * SR)
                pl = pluck(midi(nt))
                if tt >= 0:
                    out[tt:tt + len(pl)] += pl
    out = out[:int(total * SR)]
    # 루프 이음새 페이드
    fade = int(1.5 * SR)
    out[:fade] *= np.linspace(0, 1, fade)
    out[-fade:] *= np.linspace(1, 0, fade)
    out = out / (np.max(np.abs(out)) + 1e-9) * 0.7
    pcm = (out * 32767).astype(np.int16)
    with wave.open(os.path.join(OUT, name + '.wav'), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    print(name, round(total, 1), '초')


# 코드 진행(MIDI 음): C-Am-F-G, F-G-Em-Am, Am-F-C-G 변형(7th 포함)
P1 = [[48, 55, 59, 64], [45, 52, 55, 60], [41, 48, 52, 57], [43, 50, 55, 59]]
P2 = [[41, 48, 52, 57], [43, 50, 55, 59], [40, 47, 52, 55], [45, 52, 55, 60]]
P3 = [[45, 52, 55, 60], [41, 48, 52, 57], [48, 55, 59, 64], [43, 50, 55, 59]]
make('calm_a', 84, P1, 0, 1)
make('calm_b', 76, P2, 2, 2)
make('calm_c', 90, P3, -2, 3)
