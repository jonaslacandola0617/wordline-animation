import fs from 'node:fs';
import path from 'node:path';
import { spawn, spawnSync } from 'node:child_process';
import puppeteer from 'puppeteer';

const ROOT = process.cwd();
const EP = path.join(ROOT, 'shorts/001-four-seventeen-guy');
const FRAMES = path.join(EP, 'render/frames');
const PREVIEW = path.join(EP, 'preview');
const OUTPUTS = path.join(EP, 'render/outputs');
const AUDIO = path.join(EP, 'audio/master_audio.wav');

for (const d of [FRAMES, PREVIEW, OUTPUTS, path.dirname(AUDIO)]) fs.mkdirSync(d,{recursive:true});
for (const f of fs.readdirSync(FRAMES)) if (/^frame_\d+\.png$/.test(f)) fs.rmSync(path.join(FRAMES,f));

const server = spawn(process.platform==='win32'?'npx.cmd':'npx',
  ['http-server','.', '-p','8080','-c-1','--silent'],
  {cwd:ROOT,stdio:['ignore','pipe','pipe']}
);
let serverErr='';
server.stderr.on('data',d=>serverErr+=String(d));
await new Promise(r=>setTimeout(r,1800));

let browser;
try {
  browser = await puppeteer.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--enable-webgl',
      '--ignore-gpu-blocklist',
      '--use-angle=swiftshader',
      '--disable-dev-shm-usage',
      '--hide-scrollbars'
    ]
  });
  const page = await browser.newPage();
  await page.setViewport({width:2160,height:3840,deviceScaleFactor:1});
  page.on('console', msg => console.log('[browser]', msg.type(), msg.text()));
  page.on('pageerror', err => console.error('[pageerror]', err));

  await page.goto('http://127.0.0.1:8080/shorts/001-four-seventeen-guy/scene/index.html', {waitUntil:'networkidle0', timeout:120000});
  await page.waitForFunction(() => window.__ready===true || window.__renderError, {timeout:120000});
  const err = await page.evaluate(()=>window.__renderError||null);
  if (err) throw new Error(err);

  const {duration,fps} = await page.evaluate(()=>({duration:window.getDuration(),fps:window.getFPS()}));
  const count = Math.round(duration*fps);
  console.log(`Rendering ${count} frames at ${fps}fps, 2160x3840`);

  const canvas = await page.$('canvas');
  if (!canvas) throw new Error('Canvas not found');

  for (let i=0;i<count;i++) {
    await page.evaluate((f)=>{ window.setFrame(f); window.renderFrame(); }, i);
    const target=path.join(FRAMES,`frame_${String(i).padStart(4,'0')}.png`);
    await canvas.screenshot({path:target,type:'png'});
    if (i%30===0 || i===count-1) console.log(`frame ${i+1}/${count}`);
  }

  const previewTimes=[0.5,2.3,3.4,4.5,5.8,7.5,8.5];
  for(const t of previewTimes){
    const f=Math.max(0,Math.min(count-1,Math.round(t*fps)));
    const src=path.join(FRAMES,`frame_${String(f).padStart(4,'0')}.png`);
    const dst=path.join(PREVIEW,`t_${t.toFixed(1).replace('.','_')}s.png`);
    fs.copyFileSync(src,dst);
  }
} finally {
  if (browser) await browser.close();
  server.kill('SIGTERM');
}

function run(cmd,args,opts={}) {
  console.log('$',cmd,args.join(' '));
  const r=spawnSync(cmd,args,{cwd:ROOT,stdio:'inherit',...opts});
  if(r.status!==0) throw new Error(`${cmd} failed with exit code ${r.status}`);
}

run('bash',[path.join(EP,'audio/build_audio.sh')]);

const master=path.join(OUTPUTS,'WORDLINE_SHORT_001_4_17_GUY_4K_MASTER.mp4');
const social=path.join(OUTPUTS,'WORDLINE_SHORT_001_4_17_GUY_SOCIAL_1080x1920.mp4');

run('ffmpeg',[
  '-y','-framerate','30','-i',path.join(FRAMES,'frame_%04d.png'),
  '-i',AUDIO,
  '-c:v','libx264','-preset','slow','-crf','15','-pix_fmt','yuv420p',
  '-c:a','aac','-b:a','320k','-ar','48000','-shortest','-movflags','+faststart',master
]);

run('ffmpeg',[
  '-y','-i',master,'-vf','scale=1080:1920:flags=lanczos',
  '-c:v','libx264','-preset','slow','-crf','16','-pix_fmt','yuv420p',
  '-c:a','aac','-b:a','256k','-ar','48000','-movflags','+faststart',social
]);

const probe=spawnSync('ffprobe',[
  '-v','error','-show_entries','format=duration:stream=index,codec_name,codec_type,width,height,r_frame_rate,sample_rate,channels',
  '-of','json',master
],{encoding:'utf8'});
if(probe.status!==0) throw new Error('ffprobe failed');
const validation={
  rendered_at:new Date().toISOString(),
  frame_count:fs.readdirSync(FRAMES).filter(x=>/^frame_\d+\.png$/.test(x)).length,
  master:path.relative(ROOT,master),
  social:path.relative(ROOT,social),
  ffprobe:JSON.parse(probe.stdout),
  preview_frames:fs.readdirSync(PREVIEW).filter(x=>x.endsWith('.png')).sort()
};
fs.writeFileSync(path.join(EP,'render/validation.json'),JSON.stringify(validation,null,2));
console.log(JSON.stringify(validation,null,2));

// Frames are intentionally deleted after final encode to keep the artifact small.
for (const f of fs.readdirSync(FRAMES)) if (/^frame_\d+\.png$/.test(f)) fs.rmSync(path.join(FRAMES,f));
console.log('Render complete.');
