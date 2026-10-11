# WORDLINE SHORT 001 — The 4:17 Guy

A 9.5-second native-vertical Wordline Animation brainrot test.

## Locked gag

**4:16 → 4:17 → THUD → SIP → FWOOOP → back to work.**

No dialogue. No captions. No logo. No explanation.

## Deterministic API

The scene exposes:
- `setTime(t)`
- `setFrame(frame)`
- `renderFrame()`
- `getDuration()`
- `getFPS()`
- `setMasterQuality()`

## Render

`npm run render:001`

The renderer creates a 2160×3840 PNG sequence, deterministic 48 kHz audio, a 4K H.264 master, a 1080×1920 social encode, preview frames, and ffprobe QA output.
