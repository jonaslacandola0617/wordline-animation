#!/usr/bin/env bash
set -euo pipefail
ROOT="$(pwd)"
EP="$ROOT/shorts/001-four-seventeen-guy"
OUT="$EP/audio/master_audio.wav"
TYPING="$ROOT/SFX/Sounds Effects/Keyboard/Keyboard Typing 3.wav"
IMPACT="$ROOT/SFX/Sounds Effects/MixKit SFX (new)/Suspense/mixkit-cool-impact-movie-trailer-2909.wav"
WHOOSH="$ROOT/SFX/Sounds Effects/MixKit SFX (new)/Wooshes/mixkit-fast-small-sweep-transition-166.wav"

for f in "$TYPING" "$IMPACT" "$WHOOSH"; do
  if [[ ! -f "$f" ]]; then
    echo "Missing required SFX: $f" >&2
    exit 2
  fi
done

ffmpeg -y   -stream_loop -1 -i "$TYPING"   -i "$IMPACT"   -i "$WHOOSH"   -filter_complex "[0:a]atrim=0:9.5,asetpts=PTS-STARTPTS,volume='if(between(t,2.05,3.2),0.035,if(between(t,3.2,7.9),0.060,0.095))':eval=frame,aformat=sample_rates=48000:channel_layouts=stereo[typing];[1:a]atrim=0:0.68,asetpts=PTS-STARTPTS,afade=t=out:st=0.38:d=0.30,volume=0.42,adelay=3540:all=1,aformat=sample_rates=48000:channel_layouts=stereo[impact];[2:a]atrim=0:0.52,asetpts=PTS-STARTPTS,afade=t=out:st=0.31:d=0.20,volume=0.58,adelay=7380:all=1,aformat=sample_rates=48000:channel_layouts=stereo[whoosh];anoisesrc=color=pink:duration=0.26:amplitude=0.030:sample_rate=48000,highpass=f=850,lowpass=f=4100,afade=t=in:d=0.025,afade=t=out:st=0.18:d=0.08,adelay=5280:all=1,aformat=sample_rates=48000:channel_layouts=stereo[sipnoise];sine=frequency=155:duration=0.18:sample_rate=48000,volume=0.020,afade=t=out:st=0.08:d=0.10,adelay=5320:all=1,aformat=sample_rates=48000:channel_layouts=stereo[siptone];[typing][impact][whoosh][sipnoise][siptone]amix=inputs=5:duration=longest:normalize=0,alimiter=limit=0.84,atrim=0:9.5[aout]"   -map "[aout]" -c:a pcm_s24le -ar 48000 "$OUT"

echo "Built $OUT"
