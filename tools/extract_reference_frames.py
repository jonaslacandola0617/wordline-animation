from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".analysis-tools"))

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


REFS = ROOT / "references"
OUT = ROOT / "analysis" / "reference-frames"
PCTS = [0.0, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.985]


def safe_name(path: Path) -> str:
    return path.stem.replace(" ", "_").replace("(", "").replace(")", "")


def frame_at(cap: cv2.VideoCapture, frame_index: int):
    cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, frame_index))
    ok, frame = cap.read()
    return frame if ok else None


def label_frame(frame, label: str, width: int = 300):
    h, w = frame.shape[:2]
    target_h = max(1, round(h * width / w))
    resized = cv2.resize(frame, (width, target_h), interpolation=cv2.INTER_AREA)
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(rgb)
    draw = ImageDraw.Draw(image, "RGBA")
    bar_h = 44
    draw.rectangle((0, image.height - bar_h, image.width, image.height), fill=(7, 9, 8, 220))
    draw.text((10, image.height - 33), label, fill=(242, 239, 232, 255), font=ImageFont.load_default())
    return image


def contact_sheet(items, title: str, columns: int = 4):
    if not items:
        return None
    cell_w = max(item.width for item in items)
    cell_h = max(item.height for item in items)
    rows = math.ceil(len(items) / columns)
    top = 42
    sheet = Image.new("RGB", (cell_w * columns, top + cell_h * rows), (11, 13, 12))
    draw = ImageDraw.Draw(sheet)
    draw.text((12, 14), title, fill=(196, 164, 107), font=ImageFont.load_default())
    for i, item in enumerate(items):
        x = (i % columns) * cell_w
        y = top + (i // columns) * cell_h
        sheet.paste(item, (x, y))
    return sheet


def scene_change_candidates(cap, fps: float, frame_count: int, duration: float):
    interval = 0.5
    times = np.arange(0.0, max(duration - interval, 0.0), interval)
    previous = None
    scored = []
    for t in times:
        idx = min(frame_count - 1, round(t * fps))
        frame = frame_at(cap, idx)
        if frame is None:
            continue
        small = cv2.resize(frame, (96, 160), interpolation=cv2.INTER_AREA)
        lab = cv2.cvtColor(small, cv2.COLOR_BGR2LAB)
        if previous is not None:
            score = float(np.mean(cv2.absdiff(lab, previous)))
            scored.append((score, float(t)))
        previous = lab

    chosen = []
    for score, t in sorted(scored, reverse=True):
        if all(abs(t - existing[1]) >= 1.75 for existing in chosen):
            chosen.append((score, t))
        if len(chosen) >= 8:
            break
    return sorted(chosen, key=lambda pair: pair[1])


def analyze_video(path: Path):
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {path}")

    fps = float(cap.get(cv2.CAP_PROP_FPS))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frame_count / fps if fps else 0.0
    group = path.parent.name
    target = OUT / group / safe_name(path)
    target.mkdir(parents=True, exist_ok=True)

    key_items = []
    key_frames = []
    for pct in PCTS:
        idx = min(frame_count - 1, round((frame_count - 1) * pct))
        frame = frame_at(cap, idx)
        if frame is None:
            continue
        seconds = idx / fps if fps else 0.0
        name = f"p{round(pct * 100):03d}_{seconds:06.2f}s.jpg"
        cv2.imwrite(str(target / name), frame, [cv2.IMWRITE_JPEG_QUALITY, 93])
        key_items.append(label_frame(frame, f"{round(pct * 100)}%  {seconds:.1f}s"))
        key_frames.append({"percent": pct, "seconds": seconds, "file": name})

    changes = scene_change_candidates(cap, fps, frame_count, duration)
    change_items = []
    change_frames = []
    for rank, (score, seconds) in enumerate(changes, start=1):
        idx = min(frame_count - 1, round(seconds * fps))
        frame = frame_at(cap, idx)
        if frame is None:
            continue
        name = f"change_{rank:02d}_{seconds:06.2f}s.jpg"
        cv2.imwrite(str(target / name), frame, [cv2.IMWRITE_JPEG_QUALITY, 93])
        change_items.append(label_frame(frame, f"{seconds:.1f}s  delta {score:.1f}"))
        change_frames.append({"seconds": seconds, "score": score, "file": name})

    key_sheet = contact_sheet(key_items, f"{group}/{path.name} — timeline")
    if key_sheet:
        key_sheet.save(target / "timeline-contact-sheet.jpg", quality=94)
    change_sheet = contact_sheet(change_items, f"{group}/{path.name} — strongest changes")
    if change_sheet:
        change_sheet.save(target / "change-contact-sheet.jpg", quality=94)

    cap.release()
    return {
        "group": group,
        "file": path.name,
        "width": width,
        "height": height,
        "fps": fps,
        "frame_count": frame_count,
        "duration_seconds": duration,
        "key_frames": key_frames,
        "change_frames": change_frames,
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for path in sorted(REFS.glob("*/*.mp4")):
        print(f"Analyzing {path.relative_to(ROOT)}", flush=True)
        results.append(analyze_video(path))
    (OUT / "metadata.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {len(results)} video analyses to {OUT}")


if __name__ == "__main__":
    main()
