# Worldline Lab — Moon Fall production plan

## World

ASTER QUAY is a purpose-built coastal metropolis: 30 authored procedural buildings, a six-lane waterfront boulevard, pedestrian plaza, market, observatory, monorail, skybridge, ferry terminal, harbor traffic, vegetation, vehicles, articulated crowds, and distant coastal hills. The renderer uses world-space vertices, perspective projection, face shading, atmospheric depth, and depth sorting. Layout and animation are seeded and timeline-driven so preview and export match.

## Shot map

1. **00:00–00:04 — The impossible sky:** street dolly past traffic and market life, bus wipe, tilt to the oversized Moon, two staggered human reactions, rooftop birds scatter.
2. **00:04–00:12 — The approach:** observatory push-in, scientist and rooftop witnesses react, then a street insert catches braking traffic and cold lunar light.
3. **00:12–00:20 — The tides awaken:** harbor lateral track; water draws down, boats pitch, ropes snap, buoy tips, warning lights and first evacuation.
4. **00:20–00:30 — Gravity takes hold:** low street canyon and backwards crowd track; lights sway and fail, vehicles brake and swerve, facade debris falls.
5. **00:30–00:41 — The water returns:** exposed harbor beat, volumetric wall reveal, ferry toss, waterfront evacuation, outer-harbor impact, spray and flood ingress.
6. **00:41–00:52 — No escape:** flooded low-angle avenue, floating taxi, sparks, skybridge failure, cascading blackout, monumental lunar fractures and separated fragments.
7. **00:52–01:02 — The end of the sky:** rooftop crane and pullback to a poster-like tableau containing tiny people, damaged Aster Quay, a giant fractured Moon, fragments, and a second geographic-scale tidal wall.
8. **01:02–01:05 — End card:** established Worldline Lab identity.

## Sound

The soundtrack is fully procedural and rendered offline at 48 kHz: city/harbor/wind ambience, threat drones and rises, varied crowd/footstep/horn/siren textures, wave and destruction events, electrical arcs, cinematic pulses, a controlled near-silence, and final sub impact. It is soft-limited before playback and routed through the same MediaStreamAudioDestinationNode used by export. No external audio assets or licenses are required.

## Export

The page records only the 1080×1920 canvas at 30 fps. It combines one canvas video track with one Web Audio destination track, prefers VP9/Opus with VP8/Opus fallback, requests 16 Mbps video and 192 kbps audio, records through the complete 65-second timeline, patches WebM duration metadata, and downloads `worldline-lab_moon-fall.webm`.
