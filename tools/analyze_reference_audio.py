from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".analysis-tools"))

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont


FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
RATE = 16_000
OUT = ROOT / "analysis" / "reference-audio"


def decode_audio(path: Path):
    command = [
        FFMPEG,
        "-hide_banner",
        "-i",
        str(path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        str(RATE),
        "-f",
        "f32le",
        "pipe:1",
    ]
    proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    stderr = proc.stderr.decode("utf-8", errors="replace")
    if proc.returncode:
        raise RuntimeError(stderr)
    samples = np.frombuffer(proc.stdout, dtype="<f4")
    audio_line = next((line.strip() for line in stderr.splitlines() if "Audio:" in line), "")
    return samples, audio_line


def db(value):
    return float(20 * np.log10(max(float(value), 1e-9)))


def draw_profile(seconds, rms_db, title, path):
    width, height = 1200, 420
    pad_x, pad_top, pad_bottom = 60, 55, 45
    chart_h = height - pad_top - pad_bottom
    image = Image.new("RGB", (width, height), (11, 13, 12))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((18, 18), title, fill=(196, 164, 107), font=font)
    for level in [-48, -36, -24, -12, 0]:
        y = pad_top + (0 - level) / 48 * chart_h
        draw.line((pad_x, y, width - 20, y), fill=(56, 60, 58), width=1)
        draw.text((16, y - 6), f"{level} dB", fill=(124, 137, 123), font=font)
    max_t = max(seconds[-1], 1) if seconds else 1
    points = []
    for t, level in zip(seconds, rms_db):
        x = pad_x + t / max_t * (width - pad_x - 20)
        y = pad_top + (0 - max(-48, min(0, level))) / 48 * chart_h
        points.append((x, y))
    if len(points) > 1:
        draw.line(points, fill=(242, 239, 232), width=3)
    for fraction in [0, .1, .25, .5, .75, .9, 1]:
        x = pad_x + fraction * (width - pad_x - 20)
        draw.line((x, pad_top, x, height - pad_bottom), fill=(196, 164, 107), width=1)
        draw.text((x + 3, height - 30), f"{round(fraction * 100)}%", fill=(196, 164, 107), font=font)
    image.save(path)


def analyze(path: Path):
    samples, audio_line = decode_audio(path)
    duration = len(samples) / RATE
    window = RATE
    seconds = []
    rms_db = []
    peaks_db = []
    for start in range(0, len(samples), window):
        chunk = samples[start : start + window]
        if not len(chunk):
            continue
        seconds.append(start / RATE)
        rms_db.append(db(np.sqrt(np.mean(np.square(chunk)))))
        peaks_db.append(db(np.max(np.abs(chunk))))

    rms_arr = np.array(rms_db)
    peaks_arr = np.array(peaks_db)
    rises = np.diff(rms_arr) if len(rms_arr) > 1 else np.array([])
    top_rises = sorted(
        [{"seconds": float(seconds[i + 1]), "rise_db": float(value)} for i, value in enumerate(rises)],
        key=lambda item: item["rise_db"],
        reverse=True,
    )[:8]
    deciles = []
    for i in range(10):
        lo, hi = duration * i / 10, duration * (i + 1) / 10
        values = [level for t, level in zip(seconds, rms_db) if lo <= t < hi]
        deciles.append(round(float(np.mean(values)), 2) if values else None)

    group = path.parent.name
    stem = path.stem.replace(" ", "_").replace("(", "").replace(")", "")
    target = OUT / group / stem
    target.mkdir(parents=True, exist_ok=True)
    draw_profile(seconds, rms_db, f"{group}/{path.name} — one-second RMS", target / "loudness-profile.png")
    codec_match = re.search(r"Audio:\s*([^\r\n]+)", audio_line)
    return {
        "group": group,
        "file": path.name,
        "duration_seconds": duration,
        "stream_description": codec_match.group(1) if codec_match else audio_line,
        "integrated_rms_dbfs": round(db(np.sqrt(np.mean(np.square(samples)))), 2),
        "peak_dbfs": round(db(np.max(np.abs(samples))), 2),
        "one_second_rms_p10_dbfs": round(float(np.percentile(rms_arr, 10)), 2),
        "one_second_rms_p90_dbfs": round(float(np.percentile(rms_arr, 90)), 2),
        "dynamic_spread_db": round(float(np.percentile(rms_arr, 90) - np.percentile(rms_arr, 10)), 2),
        "rms_by_decile_dbfs": deciles,
        "largest_one_second_rises": top_rises,
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for path in sorted((ROOT / "references").glob("*/*.mp4")):
        print(f"Analyzing audio {path.relative_to(ROOT)}", flush=True)
        results.append(analyze(path))
    (OUT / "audio-metadata.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {len(results)} audio analyses to {OUT}")


if __name__ == "__main__":
    main()
