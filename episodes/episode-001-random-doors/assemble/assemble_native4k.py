#!/usr/bin/env python3
from pathlib import Path
import json, subprocess

ROOT=Path.cwd()
BASE=ROOT/"episodes"/"episode-001-random-doors"
FINAL=BASE/"final4k"
FINAL.mkdir(parents=True,exist_ok=True)

scenes=[]
for i in range(1,12):
    sid=f"{i:02d}"
    candidates=list((BASE/"downloaded4k").rglob(f"scene-{sid}.mp4"))
    if not candidates:
        raise SystemExit(f"missing native 4K scene {sid}")
    scenes.append(candidates[0])

concat=FINAL/"concat.txt"
concat.write_text("\n".join("file '"+str(p.resolve())+"'" for p in scenes))

joined=FINAL/"WORDLINE_EPISODE_001_RANDOM_DOORS_NATIVE_4K_JOINED.mp4"
subprocess.check_call([
    "ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),
    "-c","copy",str(joined)
])

master=FINAL/"WORDLINE_EPISODE_001_RANDOM_DOORS_NATIVE_4K_MASTER.mp4"
subprocess.check_call([
    "ffmpeg","-y","-i",str(joined),
    "-c:v","libx264","-preset","slow","-crf","16","-pix_fmt","yuv420p",
    "-af","loudnorm=I=-14:TP=-1.0:LRA=9",
    "-c:a","aac","-b:a","320k","-ar","48000","-movflags","+faststart",
    str(master)
])

delivery1080=FINAL/"WORDLINE_EPISODE_001_RANDOM_DOORS_1080P_DELIVERY.mp4"
subprocess.check_call([
    "ffmpeg","-y","-i",str(master),
    "-vf","scale=1920:1080:flags=lanczos",
    "-c:v","libx264","-preset","slow","-crf","17","-pix_fmt","yuv420p",
    "-c:a","aac","-b:a","256k","-ar","48000","-movflags","+faststart",
    str(delivery1080)
])

thumb=FINAL/"thumbnails"
thumb.mkdir(exist_ok=True)
for src,t,name in [
    (scenes[0],2.0,"thumb_01_bus_reveal.jpg"),
    (scenes[1],2.0,"thumb_02_beach_arrival.jpg"),
    (scenes[10],3.4,"thumb_03_tsunami.jpg")
]:
    subprocess.check_call(["ffmpeg","-loglevel","error","-y","-ss",str(t),"-i",str(src),"-frames:v","1","-q:v","2",str(thumb/name)])

probe=json.loads(subprocess.check_output([
    "ffprobe","-v","quiet","-print_format","json","-show_format","-show_streams",str(master)
]))
v=next(x for x in probe["streams"] if x["codec_type"]=="video")
a=next(x for x in probe["streams"] if x["codec_type"]=="audio")
report={
    "status":"PASS",
    "render_mode":"native 4K per scene",
    "duration":float(probe["format"]["duration"]),
    "resolution":[int(v["width"]),int(v["height"])],
    "fps":v.get("avg_frame_rate"),
    "pixel_format":v.get("pix_fmt"),
    "audio_sample_rate":int(a.get("sample_rate",0)),
    "scenes":11
}
if report["resolution"] != [3840,2160]: raise SystemExit("master is not native 3840x2160")
if report["audio_sample_rate"] != 48000: raise SystemExit("audio sample rate is not 48 kHz")
(FINAL/"QA_REPORT_NATIVE4K.json").write_text(json.dumps(report,indent=2))
(FINAL/"QA_REPORT_NATIVE4K.md").write_text("# Episode 001 Native 4K QA\n\n"+json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
