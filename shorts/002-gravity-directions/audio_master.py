#!/usr/bin/env python3
"""Original 40s music, layered repo Foley and ambience, and 48k stereo film mix."""
from pathlib import Path
import math,json,subprocess,wave
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"shorts"/"002-gravity-directions"/"audio"
OUT.mkdir(parents=True,exist_ok=True)
SR=48000; N=SR*40
music=np.zeros((N,2),dtype=np.float32)
world=np.zeros_like(music);foley=np.zeros_like(music);fx=np.zeros_like(music)
rng=np.random.default_rng(702)
log=[]

def place(dst,x,t,g=.3):
    start=int(t*SR)
    if start<0 or start>=N:return
    if x.ndim==1:x=np.column_stack([x,x])
    size=min(N-start,len(x))
    if size>0:dst[start:start+size]+=x[:size]*g

def tone(f,d=.3,a=.15,style="pluck"):
    t=np.arange(int(d*SR),dtype=np.float32)/SR
    wave=np.sin(2*np.pi*f*t)+.28*np.sin(4*np.pi*f*t)+.08*np.sin(6*np.pi*f*t)
    if style=="warm":env=np.minimum(1,t/.08)*np.minimum(1,(d-t)/.25)
    elif style=="bass":env=np.minimum(1,t/.01)*np.exp(-t*8/d)
    elif style=="ding":env=np.exp(-t*11/d)
    else:env=np.minimum(1,t/.005)*np.exp(-t*7/d)
    return (wave*env*a).astype(np.float32)

def note(t,f,d=.38,a=.15,style="pluck"):
    place(music,tone(f,d,a,style),t,1.0)

def beat(t,style="hat",vol=.025):
    d=.23 if style=="kick" else .09
    times=np.arange(int(d*SR),dtype=np.float32)/SR
    if style=="kick":z=np.sin(2*np.pi*(90-45*times/d)*times)*np.exp(-times*32)
    else:
        zz=rng.standard_normal(len(times)).astype(np.float32)
        z=np.concatenate([zz[:1],np.diff(zz)])*np.exp(-times*55)
    place(music,z.astype(np.float32),t,vol)

# Original Wordline score: simple pizzicato/plucks with a lightly syncopated beat.
tempo=114; step=60/tempo
chords=[[293.66,369.99,440.0],[246.94,293.66,369.99],[196.,246.94,392.],[220.,277.18,440.]]
for i in range(int(30/step)):
    t=i*step
    if 27.1<t<30:continue
    ch=chords[(i//4)%4]
    note(t,ch[0]/2,.45,.14,"bass")
    note(t,ch[(i//2)%3],.24,.10)
    if i%2==0:note(t+.17,ch[(i+1)%3]*2,.17,.06)
    beat(t,"kick",.06)
    beat(t+step/2,"hat",.017)
for t in np.arange(10.15,19.8,step/2):
    ch=chords[int(t/step/4)%4]
    note(float(t),ch[int(t/step)%3]*2,.22,.055)
# Last-ten-seconds heroic but intentionally sincere build.
for j,at in enumerate([30,33,36]):
    ch=[[293.66,369.99,440],[392,493.88,587.33],[440,554.37,659.25]][j]
    for f in ch:note(at,f,3.6,.071,"warm")
    for i in range(6):
        t=at+i*.50
        if t<39.6:
            note(t,ch[i%3]*1.5,.43,.055)
            beat(t,"kick",.07)
            if i%2:beat(t,"hat",.025)
# Tiny-sip joke: the music almost completely falls away at 27.1 seconds.
a,b,c,d=[int(t*SR) for t in (26.9,27.35,29.3,29.85)]
env=np.ones(N,dtype=np.float32)
env[a:b]=np.linspace(1,.06,b-a,dtype=np.float32)
env[b:c]=.06
env[c:d]=np.linspace(.06,1,d-c,dtype=np.float32)
music*=env[:,None]

def read(rel):
    src=ROOT/rel
    if not src.exists():
        print("OPTIONAL SFX NOT FOUND:",rel)
        return None
    run=subprocess.run(["ffmpeg","-v","error","-i",str(src),"-ar","48000","-ac","2","-f","f32le","pipe:1"],capture_output=True)
    if run.returncode:
        print("FAILED TO DECODE",rel,run.stderr.decode(errors="replace")[-500:]);return None
    arr=np.frombuffer(run.stdout,dtype=np.float32)
    return arr[:len(arr)//2*2].reshape(-1,2)

def cue(dest,rel,t,vol=.2,sec=None):
    wav=read(rel)
    if wav is None:return
    if sec is not None:wav=wav[:int(sec*SR)]
    place(dest,wav,t,vol)
    log.append(dict(time_s=t,file=rel,gain=vol))
P="SFX/Wordline_Audio_Pack_01/"
O=lambda s:P+"original/"+s
C=lambda s:P+"curated/"+s

city=C("ambience/mixkit-city-downtown-crowd-ambience-361.wav")
city_audio=read(city)
if city_audio is not None and len(city_audio):
    times=int(math.ceil(N/len(city_audio)))
    loop=np.tile(city_audio,(times,1))[:N]
    level=np.ones(N,dtype=np.float32)*.075
    level[int(26.8*SR):int(29.9*SR)]*=.23
    level[int(33*SR):]*=np.linspace(1,.25,N-int(33*SR),dtype=np.float32)
    world[:]+=loop*level[:,None]
    log.append(dict(time_s=0,file=city,gain=.075,notes="loop"))

for i,t in enumerate([.10,.37,.70]):
    cue(foley,O("foley/footsteps/footstep_office_%02d.wav"%(i+1)),t,.10)
cue(foley,O("props/cups/cup_pickup_01.wav"),.04,.26)
cue(fx,C("movement/mixkit-cinematic-whoosh-fast-transition-1492.wav"),.34,.33,.70)
cue(foley,O("movement/slide_short_01.wav"),1.25,.19)
cue(fx,"SFX/Sounds Effects/MixKit SFX (new)/mixkit-car-horn-718.wav",1.65,.10,.65)
cue(foley,O("impacts/body_thud_soft_01.wav"),4.62,.25)
cue(fx,C("impacts/mixkit-airplane-flying-by-rumble-1588.wav"),6.30,.12,2.8)
cue(fx,"SFX/Sounds Effects/MixKit SFX (new)/mixkit-small-car-horn-717.wav",7.45,.12,.6)
cue(fx,C("movement/mixkit-fast-rocket-whoosh-1714.wav"),10.12,.17,1.6)
cue(fx,C("movement/mixkit-arrow-whoosh-1491.wav"),13.64,.11,.9)
cue(foley,O("comedy/soft_pop_01.wav"),16.85,.27)
cue(fx,"SFX/Sounds Effects/floraphonic-cartoon-slide-whistle-up-2-176650.mp3",17.0,.12,1.2)
cue(fx,C("movement/mixkit-fast-rocket-whoosh-1714.wav"),20.06,.24,1.7)
cue(foley,O("impacts/body_thud_hard_01.wav"),23.16,.34)
cue(foley,O("comedy/rubber_hit_01.wav"),23.44,.18)
cue(foley,O("impacts/object_drop_small_01.wav"),25.12,.20)
cue(foley,O("props/cups/cup_pickup_01.wav"),25.23,.18)
cue(foley,O("props/liquid/sip_01.wav"),28.06,.29)
cue(fx,C("movement/mixkit-fast-rocket-whoosh-1714.wav"),30.13,.17,1.9)
cue(fx,"SFX/Sounds Effects/MixKit SFX (new)/mixkit-sea-waves-loop-1196.wav",33.1,.20,6.5)
cue(fx,C("impacts/mixkit-airplane-flying-by-rumble-1588.wav"),34.3,.09,4.4)
cue(foley,O("foley/cloth/cloth_shift_01.wav"),38.1,.09)
# Micro-plip before sip.
place(foley,tone(620,.15,.10,"ding"),26.8,1)
# One original, consistent "DING" at each direction change.
for t in [10,20,30]:
    sig=tone(1290,.60,.27,"ding")+tone(1935,.60,.11,"ding")
    place(fx,sig,t,1)
    log.append(dict(time_s=t,file="original 1290Hz+1935Hz chime",gain=1,notes="gravity switch"))

# Deep restrained movement underneath the existing physical SFX.
for at,dur,amp in [(6.7,2.1,.025),(20.3,2.8,.045),(34,5.5,.07)]:
    ts=np.arange(int(dur*SR),dtype=np.float32)/SR
    r=np.sin(2*np.pi*64*ts)*np.sin(np.pi*ts/dur)**2
    place(fx,r,at,amp)

# Exactly 40 seconds: immediate audiovisual end.
fade_end=int(39.62*SR);fade_n=int(.07*SR)
for stem in (music,world,foley,fx):
    stem[fade_end-fade_n:fade_end]*=np.linspace(1,0,fade_n,dtype=np.float32)[:,None]
    stem[fade_end:]=0
mixed=music+world+foley+fx
peak=np.max(np.abs(mixed))
if peak>.96:mixed*=.96/peak

def write(file,arr):
    with wave.open(str(OUT/file),"wb") as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(48000)
        w.writeframes((np.clip(arr,-.999,.999)*32767).astype(np.int16).tobytes())
for name,stem in [("music_stem.wav",music),("world_stem.wav",world),("foley_stem.wav",foley),("effects_stem.wav",fx),("raw_mix.wav",mixed)]:
    write(name,stem)
subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(OUT/"raw_mix.wav"),"-af","loudnorm=I=-14:TP=-1.5:LRA=9","-ar","48000","-ac","2",str(OUT/"master_48k.wav")],check=True)
(OUT/"manifest.json").write_text(json.dumps({
 "duration":40,"sample_rate":48000,
 "music":"original generated instrumental (no unlicensed commercial tracks)",
 "sources":"Mixkit SFX from Wordline repository + Wordline Audio Pack 01 original effects",
 "license_note":"Third-party SFX used within finished films only; do not redistribute standalone sounds",
 "master":"audio/master_48k.wav",
 "stems":["music_stem.wav","world_stem.wav","foley_stem.wav","effects_stem.wav"],
 "cues":log
},indent=2))
print("Finished 48k music + SFX master, cues",len(log))
