import {chromium} from 'playwright';
import {spawn,spawnSync} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
const sceneId=(process.argv[2]||'01').padStart(2,'0');
const width=Number(process.env.RENDER_WIDTH||1920),height=Number(process.env.RENDER_HEIGHT||1080);
const ROOT=process.cwd(),BASE=path.join(ROOT,'episodes','episode-001-random-doors'),out=path.join(BASE,'renders',sceneId),frames=path.join(out,'frames'),preview=path.join(out,'preview');
fs.rmSync(out,{recursive:true,force:true});fs.mkdirSync(frames,{recursive:true});fs.mkdirSync(preview,{recursive:true});
const port=4300+Number(sceneId),server=spawn('python3',['-m','http.server',String(port),'--bind','127.0.0.1'],{cwd:ROOT,stdio:['ignore','pipe','pipe']});
await new Promise(r=>setTimeout(r,800));let browser;
try{
 browser=await chromium.launch({headless:true,args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist','--disable-dev-shm-usage','--no-sandbox']});
 const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
 page.on('console',m=>console.log('[browser]',m.type(),m.text()));page.on('pageerror',e=>console.error('[pageerror]',e));
 await page.goto('http://127.0.0.1:'+port+'/episodes/episode-001-random-doors/index.html?render=1&scene='+sceneId+'&width='+width+'&height='+height,{waitUntil:'networkidle',timeout:120000});
 await page.waitForFunction(()=>window.__ready===true||!!window.__loadError,null,{timeout:120000});
 const err=await page.evaluate(()=>window.__loadError||null);if(err)throw new Error(err);
 const meta=await page.evaluate(()=>({duration:window.getDuration(),fps:window.getFPS(),quality:window.setMasterQuality()})),count=Math.round(meta.duration*meta.fps);
 console.log('scene',sceneId,meta,'frames',count);const canvas=page.locator('canvas'),picks=new Set([Math.round(count*.08),Math.round(count*.34),Math.round(count*.60),Math.round(count*.86)]);
 for(let f=0;f<count;f++){
   await page.evaluate(x=>{window.setFrame(x);window.renderFrame();},f);
   const file=path.join(frames,'frame_'+String(f).padStart(5,'0')+'.jpg');
   await canvas.screenshot({path:file,type:'jpeg',quality:93});
   if(picks.has(f))fs.copyFileSync(file,path.join(preview,'scene_'+sceneId+'_f'+String(f).padStart(5,'0')+'.jpg'));
   if(f%120===0)console.log('scene',sceneId,'frame',f,'/',count);
 }
 const audio=path.join(BASE,'audio','scene-'+sceneId+'.wav'),mp4=path.join(out,'scene-'+sceneId+'.mp4');
 const r=spawnSync('ffmpeg',['-y','-framerate','30','-i',path.join(frames,'frame_%05d.jpg'),'-i',audio,'-c:v','libx264','-preset','medium','-crf','16','-pix_fmt','yuv420p','-r','30','-c:a','aac','-b:a','256k','-ar','48000','-movflags','+faststart','-shortest',mp4],{stdio:'inherit'});
 if(r.status!==0)throw new Error('ffmpeg encode failed');
 fs.rmSync(frames,{recursive:true,force:true});
 fs.writeFileSync(path.join(out,'render.json'),JSON.stringify({scene:sceneId,...meta,frames:count,resolution:[width,height]},null,2));
}finally{if(browser)await browser.close();server.kill('SIGTERM');}
