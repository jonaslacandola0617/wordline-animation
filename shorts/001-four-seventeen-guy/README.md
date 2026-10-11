# WORDLINE SHORT 001 — THE 4:17 GUY

Runtime target: **9.5 seconds**  
Master: **2160×3840, 30fps, H.264 + AAC**  
Social encode: **1080×1920**

## Locked beat
4:16 office normality → clock changes to 4:17 → ceiling break / THUD → ordinary man lands in chair → one calm sip → FWOOOP straight back through ceiling → typing resumes.

No captions, logo, narration, dialogue, explanation, or extra twist.

## Pipeline
Three.js deterministic scene:
- `window.setTime(t)`
- `window.setFrame(frame)`
- `window.renderFrame()`
- `window.getDuration()`
- `window.getFPS()`
- `window.setMasterQuality()`

Render:
```bash
npm install
npm run render:417
```

The renderer:
1. Serves the repository locally.
2. Opens the scene in headless Chromium.
3. Renders exact 4K PNG frames at 30fps.
4. Builds the 48kHz audio master.
5. Encodes the 4K master with FFmpeg.
6. Creates a 1080×1920 social encode.
7. Extracts representative preview frames.
8. Writes `render/validation.json`.
9. Removes transient frame PNGs after final encoding.

## Source asset policy
The office uses real supplied Wordline OBJ/MTL assets for the hero characters and major furniture. Procedural geometry is limited to the room shell and small missing props such as monitor, keyboard, cup, papers, and diegetic clock.
