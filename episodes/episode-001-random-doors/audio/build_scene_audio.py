#!/usr/bin/env python3
from __future__ import annotations
import argparse, asyncio, json, math, struct
from pathlib import Path
from pydub import AudioSegment

ROOT=Path.cwd()
BASE=ROOT/"episodes"/"episode-001-random-doors"
SR=48000

SCENES={"01":25,"02":20,"03":35,"04":30,"05":25,"06":30,"07":15,"08":35,"09":23,"10":20,"11":10}
LINES={
"01":[(3.0,"A","Nope."),(15.0,"D","You still have the cake, right?"),(19.0,"A","Yep."),(20.6,"D","Twenty minutes.")],
"02":[(2.0,"B","Do not close that."),(6.0,"A","Beach?"),(7.0,"B","Beach."),(9.1,"A","I need to get across town."),(12.0,"B","We have infinite doors."),(15.2,"A","That is the opposite of helpful.")],
"03":[(23.0,"A","Closer."),(31.0,"A","Great.")],
"05":[(3.5,"A","How are you this calm?"),(7.5,"C","They stay connected while they're open."),(13.0,"C","You've been closing them?")],
"06":[(20.5,"A","That's it.")],
"07":[(9.0,"B","I had one job.")],
"08":[(8.2,"B","Bus!"),(9.0,"A","Wrong bus!"),(20.2,"A","Seriously?")],
"09":[(11.5,"A","We are literally standing outside her apartment."),(15.6,"D","There you are."),(16.2,"D","I found the hallway ten minutes ago, so I just held the closet open."),(20.4,"C","You two took a while.")],
"10":[(8.4,"D","Perfect."),(15.0,"A","Don't.")],
"11":[(.7,"D","I'll get the plates."),(7.1,"A","Plates?"),(8.0,"D","We're using napkins.")]
}
VOICE_CANDIDATES={
"A":["en-US-GuyNeural","en-US-ChristopherNeural","en-US-EricNeural"],
"B":["en-US-JasonNeural","en-US-ChristopherNeural","en-US-GuyNeural"],
"C":["en-US-DavisNeural","en-US-RogerNeural","en-US-GuyNeural"],
"D":["en-US-JennyNeural","en-US-AriaNeural","en-US-MichelleNeural"]
}
MOOD={"01":"curious","02":"playful","03":"playful","04":"playful_fast","05":"curious","06":"hopeful","07":"tension","08":"playful_fast","09":"comic","10":"warm","11":"warm"}
SFX={
"01":[(.7,"door"),(3.5,"door"),(4.2,"door"),(7.6,"door"),(8.2,"door"),(11.6,"door"),(13.5,"phone")],
"02":[(.3,"door"),(1.1,"body"),(4.9,"door"),(5.0,"latch"),(7.0,"waves")],
"03":[(.6,"door"),(8.0,"door"),(9.5,"door"),(19.0,"door"),(20.5,"door"),(28.2,"door"),(29.7,"door")],
"04":[(.3,"door"),(5.4,"door"),(6.3,"door"),(11.4,"door"),(12.3,"door"),(17.4,"door"),(18.3,"door"),(23.4,"door"),(24.3,"door"),(29.3,"door"),(25.5,"waves")],
"05":[(.2,"door"),(17.0,"tiny")],
"06":[(.4,"door"),(1.2,"door"),(2.0,"door"),(21.0,"success")],
"07":[(5.4,"door"),(7.0,"latch")],
"08":[(.3,"door"),(5.4,"door"),(6.3,"door"),(11.4,"door"),(12.3,"door"),(17.4,"door"),(13.3,"waves"),(18.3,"door"),(23.4,"door"),(24.3,"door"),(28.4,"door"),(29.3,"door"),(34.4,"door")],
"09":[(.3,"door"),(4.5,"door"),(5.3,"door"),(8.5,"door"),(9.3,"door"),(12.5,"door"),(14.8,"door")],
"10":[(4.0,"cup"),(14.8,"tiny")],
"11":[(1.0,"door"),(2.2,"waves"),(6.4,"door")]
}
AMB={"01":"room","02":"room","03":"room","04":"city","05":"office","06":"office","07":"room","08":"city","09":"room","10":"party","11":"party"}
MAP={
"door":["SFX/Wordline_Audio_Pack_01/original/foley/doors/door_close_soft_01.wav"],
"latch":["SFX/Wordline_Audio_Pack_01/original/foley/doors/door_latch_01.wav"],
"body":["SFX/Wordline_Audio_Pack_01/original/impacts/body_thud_soft_01.wav"],
"tiny":["SFX/Wordline_Audio_Pack_01/original/comedy/tiny_bonk_01.wav"],
"success":["SFX/Wordline_Audio_Pack_01/original/comedy/tiny_success_ding_01.wav"],
"cup":["SFX/Wordline_Audio_Pack_01/original/props/cups/cup_setdown_01.wav"],
"phone":["SFX/Sounds Effects/MixKit SFX (new)/Technology/mixkit-vintage-telephone-ringtone-1356.wav"],
"waves":["SFX/Wordline_Audio_Pack_01/curated/ambience/mixkit-close-sea-waves-loop-1195.wav"]
}
AMBS={
"room":["SFX/Sounds Effects/freesound_community-quiet-town-ambience-31063.mp3"],
"office":["SFX/Sounds Effects/Keyboard/Keyboard Typing 2.wav"],
"city":["SFX/Wordline_Audio_Pack_01/curated/ambience/mixkit-city-traffic-background-ambience-2930.wav"],
"party":["SFX/Wordline_Audio_Pack_01/curated/ambience/mixkit-big-crowd-talking-loop-364.wav"]
}

def load(paths):
    for p in paths:
        q=ROOT/p
        if q.exists():
            return AudioSegment.from_file(q).set_frame_rate(SR).set_channels(2)
    return None

def loop(seg,dur):
    out=AudioSegment.silent(duration=0,frame_rate=SR)
    while len(out)<dur:
        out+=seg
    return out[:dur]

def tone(freq,dur,vol=.12,triangle=False):
    data=bytearray()
    n=int(SR*dur)
    for i in range(n):
        t=i/SR
        x=(2*abs(2*((t*freq)%1)-1)-1) if triangle else math.sin(2*math.pi*freq*t)
        env=min(1,t/.02)*max(0,min(1,(dur-t)/.08))
        s=int(max(-1,min(1,x*vol*env))*32767)
        data+=struct.pack("<hh",s,s)
    return AudioSegment(data=data,sample_width=2,frame_rate=SR,channels=2)

def music(dur,mood):
    ms=int(dur*1000)
    track=AudioSegment.silent(duration=ms,frame_rate=SR)
    root={"curious":196,"playful":220,"playful_fast":246.94,"hopeful":174.61,"tension":110,"comic":207.65,"warm":164.81}[mood]
    tempo=126 if "fast" in mood else (112 if mood in ("playful","comic") else 92)
    beat=60/tempo
    chords=[(1,1.25,1.5),(1,1.2,1.498),(1,1.334,1.6),(1,1.25,1.667)]
    t=0;i=0
    while t<dur:
        for m in chords[i%4]:
            track=track.overlay(tone(root*m,min(beat*1.8,1.2),.045 if mood!="warm" else .038,True),position=int(t*1000))
        if mood in ("playful","playful_fast","comic"):
            track=track.overlay(tone(820,.055,.055),position=int(t*1000))
        t+=beat*2;i+=1
    return track-19

async def tts(scene,work):
    status={"engine":"edge-tts","ok":True,"errors":[],"attempts":[]}
    try:
        import edge_tts
    except Exception as e:
        return [],{"engine":"edge-tts","ok":False,"errors":[str(e)],"attempts":[]}
    made=[]
    expected=LINES.get(scene,[])
    for i,(at,role,text) in enumerate(expected):
        p=work/f"{scene}_{i}_{role}.mp3"
        success=False
        line_attempts=[]
        for voice in VOICE_CANDIDATES[role]:
            for attempt in range(1,4):
                try:
                    if p.exists():
                        p.unlink()
                    rate="-8%" if role=="C" else ("+4%" if role=="B" else "+0%")
                    await edge_tts.Communicate(text,voice,rate=rate).save(str(p))
                    if p.exists() and p.stat().st_size>1024:
                        made.append((at,role,text,p))
                        line_attempts.append({"voice":voice,"attempt":attempt,"ok":True})
                        success=True
                        break
                    line_attempts.append({"voice":voice,"attempt":attempt,"ok":False,"error":"empty_or_tiny_output"})
                except Exception as e:
                    line_attempts.append({"voice":voice,"attempt":attempt,"ok":False,"error":str(e)})
                await asyncio.sleep(0.8*attempt)
            if success:
                break
        status["attempts"].append({"role":role,"text":text,"attempts":line_attempts})
        if not success:
            status["ok"]=False
            status["errors"].append(f"{role}:{text}:all voice attempts failed")
    if len(made)!=len(expected):
        status["ok"]=False
    return made,status

async def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--scene",required=True)
    a=ap.parse_args()
    scene=a.scene.zfill(2)
    dur=SCENES[scene]
    ms=dur*1000
    out=BASE/"audio"
    work=out/"tts"
    out.mkdir(parents=True,exist_ok=True)
    work.mkdir(parents=True,exist_ok=True)

    amb=load(AMBS[AMB[scene]]) or AudioSegment.silent(duration=ms,frame_rate=SR)
    amb=loop(amb,ms)-30
    sfx=AudioSegment.silent(duration=ms,frame_rate=SR)

    for at,key in SFX.get(scene,[]):
        seg=load(MAP.get(key,[]))
        if seg is not None:
            sfx=sfx.overlay(seg[:2500]+(-10 if key in ("door","body") else -16),position=int(at*1000))

    mus=music(dur,MOOD[scene])
    made,status=await tts(scene,work)
    if not status["ok"] or len(made)!=len(LINES.get(scene,[])):
        raise RuntimeError("Dialogue generation incomplete for scene "+scene+": "+json.dumps(status))
    dia=AudioSegment.silent(duration=ms,frame_rate=SR)

    for at,role,text,p in made:
        seg=AudioSegment.from_file(p).set_frame_rate(SR).set_channels(2)-3
        dia=dia.overlay(seg,position=int(at*1000))

    if scene=="07":
        mus=mus.fade(to_gain=-24,start=5200,duration=1300).fade(from_gain=-24,start=8800,duration=900)

    mix=amb.overlay(mus).overlay(sfx).overlay(dia)
    for name,seg in [
        (f"scene-{scene}",mix),
        (f"scene-{scene}-dialogue",dia),
        (f"scene-{scene}-sfx",sfx),
        (f"scene-{scene}-music",mus)
    ]:
        seg.export(out/(name+".wav"),format="wav",parameters=["-ar","48000","-ac","2","-c:a","pcm_s24le"])

    manifest={
        "scene":scene,
        "duration":dur,
        "voice_status":status,
        "dialogue":[{"time":x[0],"role":x[1],"text":x[2]} for x in LINES.get(scene,[])],
        "sfx":SFX.get(scene,[]),
        "mood":MOOD[scene]
    }
    (out/f"scene-{scene}-manifest.json").write_text(json.dumps(manifest,indent=2))
    print(json.dumps(manifest,indent=2))

if __name__=="__main__":
    asyncio.run(main())
