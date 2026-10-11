import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import {spawn} from 'node:child_process';

const argv=process.argv.slice(2);
function opt(k,def){const i=argv.indexOf('--'+k);return i>=0?argv[i+1]:def;}
const MODE=opt('mode','qa'),START=Number(opt('start',0)),END=Number(opt('end',10));
const WIDTH=Number(opt('width',540)),HEIGHT=Number(opt('height',960)),FPS=30;
const FORMAT=opt('format','jpeg');const EXT=FORMAT==='png'?'png':'jpg';
const ROOT=process.cwd();
const BASE=path.join(ROOT,'shorts','002-gravity-directions');
const TAG=MODE==='qa'?'qa':String(START).padStart(2,'0')+'-'+String(END).padStart(2,'0')+'_'+WIDTH;
const OUT=path.join(BASE,'renders',TAG),FRAMES=path.join(OUT,'frames');
fs.mkdirSync(OUT,{recursive:true});fs.mkdirSync(FRAMES,{recursive:true});
const port=4921;
const server=spawn('python3',['-m','http.server',String(port),'--bind','127.0.0.1'],{cwd:ROOT,stdio:'ignore'});
let browser=null;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
try {
  await sleep(1300);
  browser=await chromium.launch({headless:true,args:[
   '--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist','--disable-dev-shm-usage','--no-sandbox'
  ]});
  const page=await browser.newPage({viewport:{width:WIDTH,height:HEIGHT},deviceScaleFactor:1});
  page.on('console',m=>console.log('[browser]',m.type(),m.text()));
  page.on('pageerror',e=>console.error('[error]',e));
  await page.goto('http://127.0.0.1:'+port+'/shorts/002-gravity-directions/index.html?render=1&width='+WIDTH+'&height='+HEIGHT,{waitUntil:'networkidle',timeout:180000});
  await page.waitForFunction(()=>window.__ready===true || window.__loadError!==null,null,{timeout:180000});
  const err=await page.evaluate(()=>window.__loadError);if(err)throw Error('Scene did not load: '+err);
  const canvas=page.locator('#wordline-render');
  let frames=[];
  if(MODE==='qa'){
    const times=[.5,2,4.7,7,9.4,10.5,13.5,17.3,19,20.5,23.6,27.9,30.5,34.3,37.5,39];
    frames=times.map(t=>Math.round(t*FPS));
  }else{
    for(let f=Math.round(START*FPS);f<Math.round(END*FPS);f++)frames.push(f);
  }
  console.log('Rendering '+frames.length+' frames ('+WIDTH+'x'+HEIGHT+') '+MODE);
  for(let j=0;j<frames.length;j++){
    const f=frames[j];
    await page.evaluate(n=>{window.setFrame(n);window.renderFrame();},f);
    const dest=path.join(FRAMES,'frame_'+String(MODE==='qa'?j:f).padStart(5,'0')+'.'+EXT);
    await canvas.screenshot(FORMAT==='png'?{path:dest,type:'png'}:{path:dest,type:'jpeg',quality:90});
    if(j%30===0)console.log('Rendered '+j+'/'+frames.length+' at global frame '+f);
  }
  fs.writeFileSync(path.join(OUT,'manifest.json'),JSON.stringify({mode:MODE,width:WIDTH,height:HEIGHT,fps:FPS,frames:frames.length,first:frames[0],last:frames.at(-1)},null,2));
}finally{
 if(browser)await browser.close();
 server.kill('SIGTERM');
}
