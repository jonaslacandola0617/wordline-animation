#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

ROOT=Path.cwd()
BASE=ROOT/"episodes"/"episode-001-random-doors"
FINAL=BASE/"final"
FINAL.mkdir(parents=True,exist_ok=True)

previews=sorted((BASE/"downloaded").rglob("scene_*_f*.jpg"))
chosen=[]
seen=set()
for p in previews:
    parts=p.stem.split("_")
    if len(parts)<3:
        continue
    sid=parts[1]
    if sid in seen:
        continue
    seen.add(sid)
    chosen.append((sid,p))

chosen.sort(key=lambda x:x[0])
if len(chosen)<11:
    raise SystemExit(f"Expected previews for 11 scenes, found {len(chosen)}")

cell=(320,180)
cols,rows=4,3
sheet=Image.new("RGB",(cols*cell[0],rows*cell[1]),(11,18,32))
draw=ImageDraw.Draw(sheet)

for idx,(sid,p) in enumerate(chosen[:11]):
    im=Image.open(p).convert("RGB")
    im=ImageOps.fit(im,cell,method=Image.Resampling.LANCZOS)
    x=(idx%cols)*cell[0]
    y=(idx//cols)*cell[1]
    sheet.paste(im,(x,y))
    draw.rectangle((x+7,y+7,x+66,y+31),fill=(11,18,32))
    draw.text((x+14,y+11),f"S{sid}",fill=(245,247,251))

out=FINAL/"QA_CONTACT_SHEET.jpg"
sheet.save(out,quality=90,optimize=True)
print(out)
