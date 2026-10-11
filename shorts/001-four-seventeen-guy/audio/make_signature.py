#!/usr/bin/env python3
import math, random, wave, struct, os

SR = 48000
OUT = os.path.dirname(__file__)
os.makedirs(OUT, exist_ok=True)

def write_wav(name, samples):
    path = os.path.join(OUT, name)
    peak = max(1e-9, max(abs(x) for x in samples))
    # Keep designed headroom; normalize only if an accidental over occurs.
    gain = min(1.0, 0.92 / peak)
    with wave.open(path, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        for x in samples:
            y = max(-1.0, min(1.0, x * gain))
            w.writeframesraw(struct.pack('<h', int(y * 32767)))
    return path

rng = random.Random(417)

# Room tone: subtle office/HVAC air so the hard silence before impact still feels physical.
dur = 9.5
room = []
lp = 0.0
for n in range(int(SR * dur)):
    t = n / SR
    noise = rng.uniform(-1, 1)
    lp = lp * 0.992 + noise * 0.008
    hum = math.sin(2 * math.pi * 60 * t) * 0.0022 + math.sin(2 * math.pi * 120 * t) * 0.0008
    room.append(lp * 0.014 + hum)
write_wav('roomtone.wav', room)

# Signature THUD: compact physical body/chair impact, not an explosion.
impact = []
lp = 0.0
for n in range(int(SR * 0.72)):
    t = n / SR
    env = math.exp(-t * 8.0)
    body = math.sin(2 * math.pi * (58 - 18 * t) * t) * 0.68 * env
    knock = math.sin(2 * math.pi * 125 * t) * 0.24 * math.exp(-t * 15)
    noise = rng.uniform(-1, 1)
    lp = lp * 0.86 + noise * 0.14
    crack = lp * 0.17 * math.exp(-t * 24)
    impact.append(body + knock + crack)
write_wav('signature_thud.wav', impact)

# Signature SIP: small liquid draw + tiny swallow; intentionally dry and recognizable.
sip = []
lp = 0.0
for n in range(int(SR * 0.52)):
    t = n / SR
    env = math.sin(math.pi * min(1, t / 0.40)) if t < 0.40 else max(0, 1 - (t - 0.40) / 0.12)
    noise = rng.uniform(-1, 1)
    lp = lp * 0.72 + noise * 0.28
    straw = lp * 0.065 * env
    bubble = math.sin(2 * math.pi * (410 + 180 * t) * t) * 0.025 * env
    swallow = math.sin(2 * math.pi * 92 * t) * 0.07 * math.exp(-((t - 0.43) / 0.045) ** 2)
    sip.append(straw + bubble + swallow)
write_wav('signature_sip.wav', sip)

print('Generated deterministic 48 kHz signature audio.')
