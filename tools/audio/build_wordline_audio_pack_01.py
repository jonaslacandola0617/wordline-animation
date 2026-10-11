#!/usr/bin/env python3
from __future__ import annotations
import json, math, random, shutil, struct, wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "SFX" / "Sounds Effects"
PACK = ROOT / "SFX" / "Wordline_Audio_Pack_01"
SR = 48000

def safe_name(s: str) -> str:
    return "".join(c.lower() if c.isalnum() else "_" for c in s).strip("_")

def category_for(name: str, path: Path) -> str:
    n = name.lower()
    p = str(path).lower()
    if any(k in n for k in ["rain","thunder","forest","birds","park","traffic","crowd","sea","waves","driving"]):
        return "ambience"
    if any(k in n for k in ["alarm","siren","countdown","telephone"]):
        return "alarms"
    if any(k in n for k in ["typing","keyboard","mouse","click","bleep","interface","notification","typewriter","software","loading","technology"]):
        return "technology"
    if any(k in n for k in ["laugh","cheer","applause"]):
        return "reactions"
    if any(k in n for k in ["woosh","whoosh","sweep","rocket","fly_wings","flying_by"]):
        return "movement"
    if any(k in n for k in ["impact","rumble","explosion","breaking","power_up","spaceship"]):
        return "impacts"
    if any(k in n for k in ["game","arcade","casino","mystery","suspense","heartbeat"]):
        return "comedy_stings"
    return "misc"

def write_wav(path: Path, samples, channels=1):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = bytearray()
        for x in samples:
            v = max(-1.0, min(1.0, x))
            frames += struct.pack("<h", int(v * 32767))
        w.writeframes(frames)

def env_decay(t, dur, power=2.2):
    return max(0.0, 1.0 - t/dur) ** power

def noise_burst(dur, seed, low=0.0, high=1.0, tone=None, amp=0.7, attack=0.003):
    rng = random.Random(seed)
    n = int(SR*dur)
    out=[]
    state=0.0
    for i in range(n):
        t=i/SR
        e=min(1.0, t/max(attack,1e-5))*env_decay(t,dur)
        raw=rng.uniform(-1,1)
        state = state*low + raw*(1-low)
        x=state
        if tone:
            x += math.sin(2*math.pi*tone*t)*0.35
        out.append(x*amp*e)
    return out

def sine_hit(dur, freq, amp=0.8, harmonics=(1.0,0.35), pitch_drop=0.0):
    n=int(SR*dur); out=[]
    phase=0.0
    for i in range(n):
        t=i/SR
        f=max(20,freq*(1-pitch_drop*(t/dur)))
        phase += 2*math.pi*f/SR
        e=env_decay(t,dur,2.5)*min(1,t/0.004)
        x=0.0
        for h,a in enumerate(harmonics,1):
            x += math.sin(phase*h)*a
        out.append(x*amp*e/sum(harmonics))
    return out

def mix(*tracks):
    n=max(len(t) for t in tracks)
    out=[0.0]*n
    for tr in tracks:
        for i,x in enumerate(tr): out[i]+=x
    peak=max(1e-9,max(abs(x) for x in out))
    gain=0.92/max(1.0,peak)
    return [x*gain for x in out]

def concat(*tracks, gap=0):
    out=[]
    g=[0.0]*int(SR*gap)
    for i,tr in enumerate(tracks):
        if i and gap: out.extend(g)
        out.extend(tr)
    return out

def filtered_noise(dur, seed, amp=0.5, smooth=0.90):
    rng=random.Random(seed); n=int(SR*dur); out=[]; s=0.0
    for i in range(n):
        t=i/SR
        s=s*smooth+rng.uniform(-1,1)*(1-smooth)
        e=math.sin(math.pi*min(1,t/dur))**1.2
        out.append(s*amp*e)
    return out

def generate_originals():
    items=[]
    def add(cat,name,samples,desc):
        rel=Path("original")/cat/(name+".wav")
        write_wav(PACK/rel,samples)
        items.append({"pack_path":str(rel).replace("\\","/"),"source_type":"wordline_original_generated","license":"Wordline project original","description":desc})
    # footsteps
    for surface,base in [("office",145),("gravel",105)]:
        for i in range(1,5):
            th=sine_hit(0.18,base+i*7,0.55,(1,0.25),0.28)
            grit=noise_burst(0.13,100+i+(0 if surface=="office" else 50),0.84,amp=0.35 if surface=="office" else 0.58)
            add("foley/footsteps",f"footstep_{surface}_{i:02d}",mix(th,grit),f"Stylized {surface} footstep")
    # cloth
    for i in range(1,3):
        add("foley/cloth",f"cloth_shift_{i:02d}",filtered_noise(0.32,210+i,0.62,0.95),"Short clothing movement")
    # chair rolls / squeaks
    for i in range(1,3):
        add("foley/chairs",f"chair_roll_{i:02d}",mix(filtered_noise(0.55,300+i,0.42,0.985),sine_hit(0.22,82+i*4,0.22,(1,0.15),0.1)),"Office chair wheel roll")
        squeak=[]
        n=int(SR*0.36)
        for k in range(n):
            t=k/SR; f=720+180*math.sin(t*11+i); e=math.sin(math.pi*t/0.36)**1.4
            squeak.append(math.sin(2*math.pi*f*t)*0.22*e)
        add("foley/chairs",f"chair_squeak_{i:02d}",squeak,"Short chair squeak")
    # doors
    for i in range(1,3):
        add("foley/doors",f"door_latch_{i:02d}",mix(sine_hit(0.12,520+i*20,0.35,(1,0.2)),noise_burst(0.08,400+i,0.7,amp=0.35)),"Door latch click")
        add("foley/doors",f"door_close_soft_{i:02d}",mix(sine_hit(0.28,95+i*6,0.62,(1,0.4),0.22),noise_burst(0.19,420+i,0.82,amp=0.25)),"Soft interior door close")
    # paper / keys
    for i in range(1,3):
        add("foley/paper",f"paper_rustle_{i:02d}",filtered_noise(0.5,500+i,0.62,0.88),"Paper handling rustle")
        jingles=[]
        for j in range(4):
            tr=sine_hit(0.18,1450+j*310+i*30,0.28,(1,0.45),0.03)
            jingles=concat(jingles,tr,gap=0.018) if jingles else tr
        add("foley/keys",f"keys_jingle_{i:02d}",jingles,"Short key jingle")
    # props
    add("props/cups","cup_pickup_01",mix(sine_hit(0.16,310,0.30,(1,0.2)),noise_burst(0.10,610,0.8,amp=0.14)),"Cup lifted from hard surface")
    add("props/cups","cup_setdown_01",mix(sine_hit(0.20,220,0.42,(1,0.3),0.12),noise_burst(0.12,611,0.82,amp=0.15)),"Cup set on hard surface")
    add("props/cups","glass_tap_01",sine_hit(0.36,1360,0.34,(1,0.50,0.22),0.02),"Small glass tap")
    add("props/phones","phone_pickup_01",mix(sine_hit(0.12,260,0.30,(1,0.18)),noise_burst(0.08,620,0.83,amp=0.12)),"Phone picked up from desk")
    add("props/phones","phone_setdown_01",mix(sine_hit(0.16,190,0.36,(1,0.25),0.1),noise_burst(0.09,621,0.82,amp=0.15)),"Phone set down on desk")
    # comedy
    add("comedy","tiny_bonk_01",mix(sine_hit(0.32,205,0.62,(1,0.4),0.38),sine_hit(0.22,610,0.18,(1,),0.2)),"Small comedic bonk")
    add("comedy","tiny_bonk_02",mix(sine_hit(0.28,242,0.58,(1,0.32),0.3),noise_burst(0.08,701,0.7,amp=0.16)),"Alternate small comedic bonk")
    add("comedy","soft_pop_01",sine_hit(0.12,620,0.48,(1,0.45),0.55),"Soft pop")
    add("comedy","soft_pop_02",sine_hit(0.10,760,0.42,(1,0.38),0.48),"Higher soft pop")
    add("comedy","anticlimax_hit_01",concat(sine_hit(0.22,145,0.55,(1,0.2),0.12),sine_hit(0.7,62,0.38,(1,),0.25),gap=0.03),"Dry anticlimax hit")
    ding=mix(sine_hit(0.7,880,0.45,(1,0.45,0.18)),sine_hit(0.7,1320,0.16,(1,0.3)))
    add("comedy","tiny_success_ding_01",ding,"Tiny success confirmation ding")
    sting=concat(sine_hit(0.18,330,0.28,(1,0.2)),sine_hit(0.5,116,0.34,(1,0.2),0.25),gap=0.05)
    add("comedy","awkward_sting_01",sting,"Awkward pause punctuation")
    add("comedy","rubber_hit_01",mix(sine_hit(0.35,125,0.48,(1,0.25),0.5),sine_hit(0.26,410,0.22,(1,),0.65)),"Rubbery slap/impact")
    add("comedy","tiny_fail_01",concat(sine_hit(0.12,510,0.22,(1,)),sine_hit(0.24,255,0.22,(1,),0.15),gap=0.02),"Tiny failure cue")
    # movement
    add("movement","body_pass_01",filtered_noise(0.32,800,0.58,0.97),"Fast body pass whoosh")
    add("movement","launch_whoosh_soft_01",filtered_noise(0.58,801,0.68,0.985),"Soft fast launch whoosh")
    whistle=[]; n=int(SR*0.65)
    for i in range(n):
        t=i/SR; f=1250-850*(t/0.65); e=math.sin(math.pi*t/0.65)
        whistle.append(math.sin(2*math.pi*f*t)*0.24*e)
    add("movement","fall_whistle_01",whistle,"Stylized falling whistle")
    add("movement","slide_short_01",filtered_noise(0.55,802,0.48,0.94),"Short slide")
    add("movement","skid_short_01",mix(filtered_noise(0.42,803,0.58,0.91),sine_hit(0.24,310,0.13,(1,),0.2)),"Short skid")
    add("movement","spin_whoosh_01",filtered_noise(0.44,804,0.52,0.98),"Spin whoosh")
    # impacts
    add("impacts","body_thud_soft_01",mix(sine_hit(0.55,72,0.66,(1,0.35),0.35),noise_burst(0.22,900,0.86,amp=0.25)),"Soft body thud")
    add("impacts","body_thud_hard_01",mix(sine_hit(0.68,58,0.82,(1,0.38),0.4),noise_burst(0.28,901,0.82,amp=0.38)),"Hard body thud")
    add("impacts","object_drop_small_01",mix(sine_hit(0.28,180,0.46,(1,0.22),0.22),noise_burst(0.14,902,0.78,amp=0.24)),"Small object drop")
    add("impacts","chair_impact_01",mix(sine_hit(0.38,92,0.56,(1,0.28),0.2),noise_burst(0.20,903,0.84,amp=0.22)),"Chair impact / landing support")
    add("impacts","desk_rattle_01",concat(*[mix(sine_hit(0.10,360+i*45,0.18,(1,0.2)),noise_burst(0.06,920+i,0.8,amp=0.10)) for i in range(4)],gap=0.025),"Desk rattle layer")
    # liquid
    sip=filtered_noise(0.45,1001,0.23,0.93)
    sip=mix(sip,sine_hit(0.25,185,0.10,(1,),0.08))
    add("props/liquid","sip_01",sip,"Short sip")
    add("props/liquid","sip_02",mix(filtered_noise(0.38,1002,0.20,0.92),sine_hit(0.21,210,0.09,(1,),0.05)),"Alternate short sip")
    add("props/liquid","gulp_01",concat(mix(filtered_noise(0.22,1003,0.18,0.92),sine_hit(0.14,160,0.12,(1,),0.1)),sine_hit(0.22,120,0.16,(1,),0.25),gap=0.02),"Small gulp")
    add("props/liquid","pour_small_01",filtered_noise(0.85,1004,0.25,0.86),"Small liquid pour")
    return items

def curate_mixkit():
    curated=[]
    roots=[SRC/"MixKit SFX (new)", SRC]
    seen=set()
    for base in roots:
        if not base.exists(): continue
        for p in base.rglob("*"):
            if not p.is_file(): continue
            n=p.name.lower()
            if base==SRC and not n.startswith("mixkit-"): continue
            if "handgun" in n: continue
            if p in seen: continue
            seen.add(p)
            cat=category_for(p.name,p)
            dest=PACK/"curated"/cat/p.name
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(p,dest)
            curated.append({
                "pack_path":str(dest.relative_to(PACK)).replace("\\","/"),
                "source_type":"curated_existing_mixkit",
                "source_repo_path":str(p.relative_to(ROOT)).replace("\\","/"),
                "license":"Mixkit Free License (project-use copy; do not resell as standalone SFX pack)",
                "description":"Curated from existing repository library"
            })
    return curated

def main():
    if PACK.exists():
        shutil.rmtree(PACK)
    PACK.mkdir(parents=True)
    curated=curate_mixkit()
    generated=generate_originals()
    manifest={
        "pack":"WORDLINE AUDIO PACK 01",
        "version":"1.0.0",
        "sample_rate_for_generated_hz":SR,
        "curated_existing_count":len(curated),
        "wordline_original_count":len(generated),
        "total_count":len(curated)+len(generated),
        "purpose":"YouTube-first fun/cinematic low-poly animation: Foley, comedy, movement, ambience, reactions, impacts and disaster support.",
        "redistribution_note":"This pack is for Wordline productions. Do not redistribute third-party curated sounds as a standalone sound-effects product.",
        "items":curated+generated
    }
    (PACK/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    readme=f"""# WORDLINE AUDIO PACK 01

A YouTube-first production pack for Wordline Animation.

- Curated existing Mixkit sounds: **{len(curated)}**
- New Wordline-original generated support sounds: **{len(generated)}**
- Total catalogued sounds: **{len(curated)+len(generated)}**

## Design goal

This pack fixes the main weakness in the older library: it adds **human-scale Foley and layered physical sounds** instead of relying mostly on whooshes, risers, and bass drops.

Use sounds in layers:

1. **World** — room tone / ambience
2. **Physical** — footsteps, chair, cup, cloth, impact
3. **Story/comedy** — only the accent that sells the beat

Do not put a meme sound on every movement.

## Important

The \`curated/\` folder contains project-use copies of Mixkit files already present in the repository. Do not redistribute those as a standalone commercial SFX pack.

The \`original/\` folder contains Wordline-generated utility sounds created by \`tools/audio/build_wordline_audio_pack_01.py\`.

## Music

Full music tracks are intentionally not bundled here. Choose music per episode from YouTube Audio Library first, then document the chosen track in that episode's audio manifest. Wordline should not have one permanent genre; the music follows the story.
"""
    (PACK/"README.md").write_text(readme,encoding="utf-8")
    print(json.dumps({"curated":len(curated),"generated":len(generated),"total":len(curated)+len(generated)},indent=2))

if __name__=="__main__":
    main()
