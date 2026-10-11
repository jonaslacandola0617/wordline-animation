import { chromium } from 'playwright';
import { spawn, spawnSync, execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const BASE = path.join(ROOT,'shorts','001-four-seventeen-guy');
const FRAMES = path.join(BASE,'frames');
const PREVIEW = path.join(BASE,'preview');
const OUTPUT = path.join(BASE,'output');
const AUDIO = path.join(BASE,'audio');
const FPS = 30;
const DURATION = 9.5;
const FRAME_COUNT = Math.ceil(FPS * DURATION);
const PORT = 4173;

for (const d of [FRAMES,PREVIEW,OUTPUT]) {
  fs.mkdirSync(d,{recursive:true});
  for (const f of fs.readdirSync(d)) {
    if (f.endsWith('.png') || f.endsWith('.mp4') || f.endsWith('.json') || f.endsWith('.md')) {
      fs.rmSync(path.join(d,f),{force:true});
    }
  }
}

function run(cmd,args,opts={}) {
  console.log('$',cmd,...args);
  const r=spawnSync(cmd,args,{stdio:'inherit',cwd:ROOT,...opts});
  if (r.status!==0) throw new Error(cmd+' failed with '+r.status);
}
function runCapture(cmd,args) {
  return execFileSync(cmd,args,{cwd:ROOT,encoding:'utf8'});
}

run('python3',[path.join(AUDIO,'make_signature.py')]);

const keyboard = path.join(ROOT,'SFX','Sounds Effects','Keyboard','Keyboard Typing 2.wav');
const whoosh = path.join(ROOT,'SFX','Sounds Effects','MixKit SFX (new)','Wooshes','mixkit-air-woosh-1489.wav');
const roomtone = path.join(AUDIO,'roomtone.wav');
const thud = path.join(AUDIO,'signature_thud.wav');
const sip = path.join(AUDIO,'signature_sip.wav');
const masterAudio = path.join(AUDIO,'master.wav');

for (const p of [keyboard,whoosh,roomtone,thud,sip]) {
  if (!fs.existsSync(p)) throw new Error('Missing required audio: '+p);
}

const filter = [
  '[0:a]atrim=0:9.5,volume=0.70[room]',
  '[1:a]asplit=2[k1][k2]',
  '[k1]atrim=start=0:end=2.05,asetpts=PTS-STARTPTS,volume=0.055[k1o]',
  '[k2]atrim=start=8.10:end=9.50,asetpts=PTS-STARTPTS,adelay=8100|8100,volume=0.055[k2o]',
  '[2:a]adelay=3420|3420,volume=0.98[thud]',
  '[3:a]adelay=5250|5250,volume=1.35[sip]',
  '[4:a]atrim=start=0:end=0.70,asetpts=PTS-STARTPTS,adelay=7320|7320,volume=0.72[whoosh]',
  '[room][k1o][k2o][thud][sip][whoosh]amix=inputs=6:duration=first:normalize=0,alimiter=limit=0.92[a]'
].join(';');

run('ffmpeg',[
  '-y',
  '-i',roomtone,
  '-stream_loop','-1','-i',keyboard,
  '-i',thud,
  '-i',sip,
  '-i',whoosh,
  '-filter_complex',filter,
  '-map','[a]',
  '-t','9.5',
  '-ar','48000',
  '-c:a','pcm_s24le',
  masterAudio
]);

const server=spawn('python3',['-m','http.server',String(PORT),'--bind','127.0.0.1'],{
  cwd:ROOT,stdio:['ignore','pipe','pipe']
});
server.stdout.on('data',d=>process.stdout.write('[server] '+d));
server.stderr.on('data',d=>process.stderr.write('[server] '+d));

const sleep=ms=>new Promise(r=>setTimeout(r,ms));
await sleep(800);

let browser;
try {
  browser=await chromium.launch({
    headless:true,
    args:[
      '--use-gl=swiftshader',
      '--enable-webgl',
      '--ignore-gpu-blocklist',
      '--disable-dev-shm-usage',
      '--no-sandbox'
    ]
  });
  const page=await browser.newPage({viewport:{width:2160,height:3840},deviceScaleFactor:1});
  page.on('console',msg=>console.log('[browser]',msg.type(),msg.text()));
  page.on('pageerror',err=>console.error('[browser pageerror]',err));

  await page.goto('http://127.0.0.1:'+PORT+'/shorts/001-four-seventeen-guy/index.html',{
    waitUntil:'networkidle',
    timeout:120000
  });
  await page.waitForFunction(()=>window.__ready===true || !!window.__loadError,null,{timeout:120000});
  const loadError=await page.evaluate(()=>window.__loadError||null);
  if (loadError) throw new Error('Scene load failed: '+loadError);

  const meta=await page.evaluate(()=>({
    duration:window.getDuration(),
    fps:window.getFPS(),
    quality:window.setMasterQuality()
  }));
  console.log('Scene metadata:',meta);
  if (meta.fps!==FPS || Math.abs(meta.duration-DURATION)>0.001) throw new Error('Timeline metadata mismatch');
  if (meta.quality.width!==2160 || meta.quality.height!==3840) throw new Error('Master canvas is not 2160x3840');

  const canvas=page.locator('canvas');
  for (let frame=0;frame<FRAME_COUNT;frame++) {
    await page.evaluate(f=>window.setFrame(f),frame);
    const file=path.join(FRAMES,'frame_'+String(frame).padStart(4,'0')+'.png');
    await canvas.screenshot({path:file,type:'png'});
    if (frame%30===0 || frame===FRAME_COUNT-1) console.log('Rendered',frame+1,'/',FRAME_COUNT);
  }
} finally {
  if (browser) await browser.close();
  server.kill('SIGTERM');
}

const previewFrames = [
  ['00_0.5s',15],
  ['01_2.3s',69],
  ['02_3.4s',102],
  ['03_4.5s',135],
  ['04_5.8s',174],
  ['05_7.7s',231],
  ['06_8.5s',255]
];
for (const [label,n] of previewFrames) {
  fs.copyFileSync(
    path.join(FRAMES,'frame_'+String(n).padStart(4,'0')+'.png'),
    path.join(PREVIEW,label+'.png')
  );
}

const master = path.join(OUTPUT,'WORDLINE_SHORT_001_4K_MASTER.mp4');
const social = path.join(OUTPUT,'WORDLINE_SHORT_001_SOCIAL_1080x1920.mp4');

run('ffmpeg',[
  '-y',
  '-framerate',String(FPS),
  '-i',path.join(FRAMES,'frame_%04d.png'),
  '-i',masterAudio,
  '-c:v','libx264',
  '-preset','slow',
  '-crf','15',
  '-pix_fmt','yuv420p',
  '-c:a','aac',
  '-b:a','320k',
  '-ar','48000',
  '-movflags','+faststart',
  '-shortest',
  master
]);

run('ffmpeg',[
  '-y',
  '-i',master,
  '-vf','scale=1080:1920:flags=lanczos',
  '-c:v','libx264',
  '-preset','slow',
  '-crf','17',
  '-pix_fmt','yuv420p',
  '-c:a','aac',
  '-b:a','256k',
  '-ar','48000',
  '-movflags','+faststart',
  social
]);

function probe(file) {
  return JSON.parse(runCapture('ffprobe',[
    '-v','quiet','-print_format','json','-show_format','-show_streams',file
  ]));
}
const masterProbe=probe(master);
const socialProbe=probe(social);

function validateProbe(label,p,expectedW,expectedH) {
  const v=p.streams.find(s=>s.codec_type==='video');
  const a=p.streams.find(s=>s.codec_type==='audio');
  if (!v || !a) throw new Error(label+' missing video or audio stream');
  if (Number(v.width)!==expectedW || Number(v.height)!==expectedH) throw new Error(label+' wrong resolution');
  if (v.pix_fmt!=='yuv420p') throw new Error(label+' wrong pixel format '+v.pix_fmt);
  if (Number(a.sample_rate)!==48000) throw new Error(label+' wrong audio sample rate');
  const d=Number(p.format.duration);
  if (Math.abs(d-DURATION)>0.15) throw new Error(label+' wrong duration '+d);
}
validateProbe('master',masterProbe,2160,3840);
validateProbe('social',socialProbe,1080,1920);

const qa={
  generated_at:new Date().toISOString(),
  fps:FPS,
  expected_duration_seconds:DURATION,
  frame_count:FRAME_COUNT,
  master:masterProbe,
  social:socialProbe,
  preview_frames:previewFrames.map(([label,frame])=>({label,frame,time:frame/FPS})),
  audio_cues:{
    thud_seconds:3.42,
    sip_seconds:5.25,
    fwooops_seconds:7.32
  },
  inspected_by_pipeline:[
    'scene loaded without browser errors',
    'deterministic setFrame API responded for all frames',
    'all 285 PNG frames rendered',
    'representative preview frames extracted',
    'master contains video+audio',
    'master is 2160x3840 yuv420p',
    'social encode is 1080x1920 yuv420p',
    'audio is 48 kHz'
  ]
};
fs.writeFileSync(path.join(OUTPUT,'QA_REPORT.json'),JSON.stringify(qa,null,2));

const report = [
  '# WORDLINE SHORT 001 — Automated QA',
  '',
  '- Frames rendered: '+FRAME_COUNT,
  '- FPS: '+FPS,
  '- Target duration: '+DURATION+' s',
  '- Master: 2160×3840 H.264 + AAC 48 kHz',
  '- Social: 1080×1920 H.264 + AAC 48 kHz',
  '- Signature timing: THUD 3.42 s / SIP 5.25 s / FWOOOP 7.32 s',
  '',
  'Representative frames are in preview/.',
  '',
  'This report covers deterministic render/encode and stream validation. Visual review of the representative PNGs is still required before release.'
].join('\n');
fs.writeFileSync(path.join(OUTPUT,'QA_REPORT.md'),report);

console.log('Render complete.');
console.log(master);
console.log(social);
