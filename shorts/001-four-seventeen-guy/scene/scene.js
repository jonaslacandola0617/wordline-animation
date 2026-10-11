import * as THREE from 'three';
import { OBJLoader } from '/node_modules/three/examples/jsm/loaders/OBJLoader.js';
import { MTLLoader } from '/node_modules/three/examples/jsm/loaders/MTLLoader.js';

const DURATION = 9.5;
const FPS = 30;
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xdce6e8);

const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.setSize(window.innerWidth, window.innerHeight, false);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const camera = new THREE.PerspectiveCamera(54, window.innerWidth / window.innerHeight, 0.05, 60);
camera.position.set(0.18, 1.68, -7.9);
const cameraTarget = new THREE.Vector3(0, 1.38, 0.72);
camera.lookAt(cameraTarget);

const hemi = new THREE.HemisphereLight(0xf4fbff, 0x758074, 2.0);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xfff4dc, 4.2);
sun.position.set(-3.5, 6.2, -4.0);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -5;
sun.shadow.camera.right = 5;
sun.shadow.camera.top = 5;
sun.shadow.camera.bottom = -2;
sun.shadow.camera.near = 0.1;
sun.shadow.camera.far = 20;
scene.add(sun);

const fill = new THREE.PointLight(0xcbe7ff, 18, 10, 2);
fill.position.set(2.6, 2.4, -2.2);
scene.add(fill);

const roomMat = new THREE.MeshStandardMaterial({ color: 0xe9e5dc, roughness: 0.86 });
const floorMat = new THREE.MeshStandardMaterial({ color: 0xa8a79f, roughness: 0.9 });
const trimMat = new THREE.MeshStandardMaterial({ color: 0x5e666b, roughness: 0.7 });
const darkMat = new THREE.MeshStandardMaterial({ color: 0x202427, roughness: 0.82 });
const whiteMat = new THREE.MeshStandardMaterial({ color: 0xf5f2e9, roughness: 0.85 });
const glassMat = new THREE.MeshStandardMaterial({ color: 0xaed4e3, roughness: 0.22, metalness: 0.0, transparent: true, opacity: 0.56 });
const paperMat = new THREE.MeshStandardMaterial({ color: 0xece8d9, roughness: 1.0 });
const waterMat = new THREE.MeshStandardMaterial({ color: 0x8fd0df, roughness: 0.13, transparent: true, opacity: 0.72 });

function box(w,h,d,mat,x,y,z){
  const m = new THREE.Mesh(new THREE.BoxGeometry(w,h,d), mat);
  m.position.set(x,y,z); m.castShadow = true; m.receiveShadow = true; scene.add(m); return m;
}
function cyl(rt, rb, h, seg, mat, x,y,z){
  const m = new THREE.Mesh(new THREE.CylinderGeometry(rt,rb,h,seg), mat);
  m.position.set(x,y,z); m.castShadow = true; m.receiveShadow = true; scene.add(m); return m;
}

// Room shell
box(5.8, 0.12, 5.9, floorMat, 0, -0.06, 0.55);
box(5.8, 3.1, 0.12, roomMat, 0, 1.5, 3.43);
box(0.12, 3.1, 5.9, roomMat, -2.84, 1.5, 0.55);
box(0.12, 3.1, 5.9, roomMat, 2.84, 1.5, 0.55);

// Ceiling with a deliberate removable center tile above the empty chair
const holeX = 0.0, holeZ = 0.92, holeW = 0.82;
box(2.45, 0.10, 5.9, whiteMat, -1.67, 3.02, 0.55);
box(2.45, 0.10, 5.9, whiteMat,  1.67, 3.02, 0.55);
box(holeW, 0.10, 3.02, whiteMat, 0, 3.02, -1.00);
box(holeW, 0.10, 2.05, whiteMat, 0, 3.02,  2.00);
const intactTile = box(0.80, 0.095, 0.80, whiteMat, holeX, 3.015, holeZ);
const holeDark = box(0.80, 0.035, 0.80, darkMat, holeX, 3.055, holeZ);
holeDark.visible = false;

// Window strips, ordinary daytime office
for (let i=0;i<3;i++){
  const win = box(0.035, 0.72, 1.05, glassMat, -2.765, 2.0, -0.85 + i*1.35);
  win.rotation.y = Math.PI/2;
}
box(0.09, 3.0, 0.09, trimMat, -2.72, 1.5, -0.22);
box(0.09, 3.0, 0.09, trimMat, -2.72, 1.5, 1.14);

// Clock
function makeClockTexture(text){
  const c = document.createElement('canvas'); c.width=768; c.height=320;
  const ctx=c.getContext('2d');
  ctx.fillStyle='#141719'; ctx.fillRect(0,0,c.width,c.height);
  ctx.strokeStyle='#4b5255'; ctx.lineWidth=18; ctx.strokeRect(10,10,c.width-20,c.height-20);
  ctx.font='700 190px monospace'; ctx.textAlign='center'; ctx.textBaseline='middle';
  ctx.fillStyle='#d9f7c0'; ctx.shadowColor='#9ee67a'; ctx.shadowBlur=18;
  ctx.fillText(text,c.width/2,c.height/2+5);
  const tx = new THREE.CanvasTexture(c); tx.colorSpace=THREE.SRGBColorSpace; return {c,ctx,tx};
}
const clockData = makeClockTexture('4:16');
const clockFrame = box(1.22,0.54,0.10,darkMat,-1.62,2.28,3.31);
const clockScreen = new THREE.Mesh(new THREE.PlaneGeometry(1.07,0.39), new THREE.MeshBasicMaterial({map:clockData.tx, side:THREE.DoubleSide}));
clockScreen.position.set(-1.62,2.28,3.245);
clockScreen.rotation.y=Math.PI;
scene.add(clockScreen);
let clockText='4:16';
function setClockText(text){
  if(text===clockText) return; clockText=text;
  const {ctx,c,tx}=clockData; ctx.clearRect(0,0,c.width,c.height);
  ctx.fillStyle='#141719'; ctx.fillRect(0,0,c.width,c.height);
  ctx.strokeStyle='#4b5255'; ctx.lineWidth=18; ctx.strokeRect(10,10,c.width-20,c.height-20);
  ctx.font='700 190px monospace'; ctx.textAlign='center'; ctx.textBaseline='middle';
  ctx.fillStyle='#d9f7c0'; ctx.shadowColor='#9ee67a'; ctx.shadowBlur=18;
  ctx.fillText(text,c.width/2,c.height/2+5); tx.needsUpdate=true;
}

// Procedural small office props only where supplied pack lacks them
function makeMonitor(x,y,z,rotY=0){
  const g=new THREE.Group();
  const frame=new THREE.Mesh(new THREE.BoxGeometry(0.58,0.36,0.055),darkMat); frame.position.y=0.24; g.add(frame);
  const screen=new THREE.Mesh(new THREE.PlaneGeometry(0.51,0.29),new THREE.MeshBasicMaterial({color:0x8db1bc}));
  screen.position.set(0,0.24,-0.029); screen.rotation.y=Math.PI; g.add(screen);
  const stand=new THREE.Mesh(new THREE.BoxGeometry(0.07,0.22,0.07),trimMat); stand.position.y=0.05; g.add(stand);
  const foot=new THREE.Mesh(new THREE.BoxGeometry(0.28,0.025,0.18),trimMat); foot.position.y=-0.06; g.add(foot);
  g.position.set(x,y,z); g.rotation.y=rotY; g.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;}}); scene.add(g); return g;
}
function makeKeyboard(x,y,z,rotY=0){
  const k=box(0.46,0.025,0.17,darkMat,x,y,z); k.rotation.y=rotY; return k;
}
function makePaper(x,y,z,rotY=0){
  const p=box(0.31,0.008,0.22,paperMat,x,y,z); p.rotation.y=rotY; return p;
}

const cup = new THREE.Group();
const cupBody = new THREE.Mesh(new THREE.CylinderGeometry(0.055,0.048,0.12,18,1,true), new THREE.MeshStandardMaterial({color:0xf0f2ef,roughness:0.55}));
cupBody.castShadow=true; cupBody.receiveShadow=true; cup.add(cupBody);
const water = new THREE.Mesh(new THREE.CylinderGeometry(0.049,0.049,0.012,18),waterMat); water.position.y=0.049; cup.add(water);
cup.position.set(0.40,0.84,0.18); scene.add(cup);

const ASSET_ROOT = '/assets/claude%20generated%20assets/';
async function loadOBJ(base, objName, mtlName){
  const mtlLoader = new MTLLoader().setPath(base);
  const mats = await mtlLoader.loadAsync(mtlName); mats.preload();
  const obj = await new OBJLoader().setMaterials(mats).setPath(base).loadAsync(objName);
  obj.traverse(o=>{
    if(o.isMesh){
      o.castShadow=true; o.receiveShadow=true;
      if(Array.isArray(o.material)) o.material.forEach(m=>{ if(m.opacity<1){m.transparent=true;m.depthWrite=false;} });
      else if(o.material && o.material.opacity<1){o.material.transparent=true;o.material.depthWrite=false;}
    }
  });
  return obj;
}

function findByName(root,name){
  let found=null; root.traverse(o=>{ if(!found && o.name===name) found=o; }); return found;
}
function makePivot(root,names,pivot){
  const p=new THREE.Group(); p.position.copy(pivot); root.add(p);
  for(const n of names){
    const m=findByName(root,n);
    if(m && m.parent===root){
      root.remove(m);
      m.position.sub(pivot);
      p.add(m);
    }
  }
  return p;
}
function rigHuman(root, pivots, prefix){
  const p=v=>new THREE.Vector3(...v);
  const shoulderL=p(pivots.shoulder_L), shoulderR=p(pivots.shoulder_R);
  const hipL=p(pivots.hip_L), hipR=p(pivots.hip_R);
  const armL=makePivot(root,['arm_L','sleeve_L','hand_L'],shoulderL);
  const armR=makePivot(root,['arm_R','sleeve_R','hand_R'],shoulderR);
  const legL=makePivot(root,['leg_L','legwear_L','shoe_L'],hipL);
  const legR=makePivot(root,['leg_R','legwear_R','shoe_R'],hipR);
  const neckY=(shoulderL.y+shoulderR.y)/2+0.12;
  const head=makePivot(root,['neck','head','face','hair'],new THREE.Vector3(0,neckY,0.02));
  return {root,armL,armR,legL,legR,head,prefix};
}

const PIVOTS = {
HUMAN_01:{hip_L:[0.094,0.94,0],hip_R:[-0.094,0.94,0],shoulder_L:[0.23,1.456,0.005],shoulder_R:[-0.23,1.456,0.005]},
HUMAN_02:{hip_L:[0.097,0.873,0],hip_R:[-0.097,0.873,0],shoulder_L:[0.19,1.351,0],shoulder_R:[-0.19,1.351,0]},
HUMAN_03:{hip_L:[0.097,0.972,0],hip_R:[-0.097,0.972,0],shoulder_L:[0.255,1.505,0],shoulder_R:[-0.255,1.505,0]},
HUMAN_04:{hip_L:[0.099,0.899,0],hip_R:[-0.099,0.899,0],shoulder_L:[0.195,1.391,0],shoulder_R:[-0.195,1.391,0]}
};

const pack46 = ASSET_ROOT+'WORLDLINE_LAB_ASSET_PACK_46/models/humans/';
const pack03b = ASSET_ROOT+'WORLDLINE_ASSET_PACK_03B_81/interiors/';
let models={};
let rigs={};
let desks=[],chairs=[];

async function initAssets(){
  const [deskSrc, chairSrc, shelfSrc, h1Src,h2Src,h3Src,h4Src] = await Promise.all([
    loadOBJ(pack03b,'INTERIOR_04_OfficeDesk.obj','INTERIOR_04_OfficeDesk.mtl'),
    loadOBJ(pack03b,'INTERIOR_05_OfficeChair.obj','INTERIOR_05_OfficeChair.mtl'),
    loadOBJ(pack03b,'INTERIOR_06_Shelf.obj','INTERIOR_06_Shelf.mtl'),
    loadOBJ(pack46,'HUMAN_01.obj','HUMAN_01.mtl'),
    loadOBJ(pack46,'HUMAN_02.obj','HUMAN_02.mtl'),
    loadOBJ(pack46,'HUMAN_03.obj','HUMAN_03.mtl'),
    loadOBJ(pack46,'HUMAN_04.obj','HUMAN_04.mtl')
  ]);

  // Central desk/chair for the event
  const d0=deskSrc.clone(true); d0.position.set(0,0,0.15); d0.rotation.y=Math.PI; scene.add(d0); desks.push(d0);
  const c0=chairSrc.clone(true); c0.position.set(0,0,0.93); c0.rotation.y=Math.PI; scene.add(c0); chairs.push(c0);

  // Working side stations using real supplied furniture
  const dL=deskSrc.clone(true); dL.position.set(-1.62,0,0.55); dL.rotation.y=Math.PI; scene.add(dL); desks.push(dL);
  const cL=chairSrc.clone(true); cL.position.set(-1.62,0,1.27); cL.rotation.y=Math.PI; scene.add(cL); chairs.push(cL);
  const dR=deskSrc.clone(true); dR.position.set(1.62,0,0.72); dR.rotation.y=Math.PI; scene.add(dR); desks.push(dR);
  const cR=chairSrc.clone(true); cR.position.set(1.62,0,1.44); cR.rotation.y=Math.PI; scene.add(cR); chairs.push(cR);

  const shelf=shelfSrc.clone(true); shelf.position.set(2.25,0,2.75); shelf.rotation.y=Math.PI; scene.add(shelf);
  models.shelf=shelf;

  // Monitors/keyboards
  const centralMonitor=makeMonitor(-0.43,0.79,-0.03,0);
  centralMonitor.scale.setScalar(0.78);
  makeKeyboard(-0.43,0.795,-0.19,0);
  makePaper(0.48,0.793,0.06,0.08);
  makeMonitor(-1.62,0.79,0.37,0);
  makeKeyboard(-1.62,0.795,0.18,0);
  makeMonitor(1.62,0.79,0.54,0);
  makeKeyboard(1.62,0.795,0.35,0);

  // Ordinary guy in a tie; source asset is HUMAN_03 from the supplied 46-model pack.
  const guy=h3Src.clone(true); guy.position.set(0,-0.43,0.95); guy.rotation.y=Math.PI; scene.add(guy);
  rigs.guy=rigHuman(guy,PIVOTS.HUMAN_03,'HUMAN_03'); guy.visible=false;

  const left=h1Src.clone(true); left.position.set(-1.62,-0.39,1.34); left.rotation.y=Math.PI; scene.add(left);
  rigs.left=rigHuman(left,PIVOTS.HUMAN_01,'HUMAN_01');

  const right=h4Src.clone(true); right.position.set(1.62,-0.37,1.51); right.rotation.y=Math.PI; scene.add(right);
  rigs.right=rigHuman(right,PIVOTS.HUMAN_04,'HUMAN_04');

  const back=h2Src.clone(true); back.position.set(1.82,0,2.65); back.rotation.y=-Math.PI*0.55; back.scale.setScalar(0.98); scene.add(back);
  rigs.back=rigHuman(back,PIVOTS.HUMAN_02,'HUMAN_02');

  // Neutral seated pose for workers
  for(const r of [rigs.left,rigs.right]){
    r.legL.rotation.x=-1.28; r.legR.rotation.x=-1.28;
    r.armL.rotation.x=-1.02; r.armR.rotation.x=-1.02;
  }
}

const debris=[];
for(let i=0;i<9;i++){
  const m=new THREE.Mesh(new THREE.BoxGeometry(0.16+0.03*(i%3),0.035,0.13+0.02*((i+1)%3)),whiteMat.clone());
  m.castShadow=true; m.receiveShadow=true; m.visible=false; scene.add(m);
  debris.push({
    mesh:m,
    offset:new THREE.Vector3(((i%3)-1)*0.20,0,((Math.floor(i/3))-1)*0.18),
    vel:new THREE.Vector3(((i%3)-1)*0.42, -0.45-0.12*(i%2), ((Math.floor(i/3))-1)*0.34),
    spin:new THREE.Vector3(2.0+i*0.13,1.2+i*0.17,1.8+i*0.11)
  });
}

const launchDust=[];
for(let i=0;i<6;i++){
  const m=new THREE.Mesh(new THREE.BoxGeometry(0.07,0.025,0.06),whiteMat.clone());
  m.castShadow=true; m.visible=false; scene.add(m);
  launchDust.push({mesh:m,ang:i/6*Math.PI*2});
}

function clamp01(x){return Math.max(0,Math.min(1,x));}
function smooth(a,b,t){t=clamp01((t-a)/(b-a)); return t*t*(3-2*t);}
function easeInCubic(x){x=clamp01(x); return x*x*x;}
function lerp(a,b,t){return a+(b-a)*t;}

function setSeated(r, amount){
  const ang=-1.30*amount; r.legL.rotation.x=ang; r.legR.rotation.x=ang;
}
function poseWorkers(t){
  const typing = Math.sin(t*7.0)*0.045;
  const pause = smooth(2.05,2.25,t)*(1-smooth(3.75,4.15,t));
  rigs.left.armL.rotation.x=-1.02 + typing*(1-pause);
  rigs.left.armR.rotation.x=-1.02 - typing*(1-pause);
  rigs.right.armL.rotation.x=-1.02 - typing*0.8*(1-pause);
  rigs.right.armR.rotation.x=-1.02 + typing*0.8*(1-pause);
  rigs.left.head.rotation.x = -0.18*pause;
  rigs.right.head.rotation.x = -0.12*pause;
  rigs.back.root.position.y = 0.008*Math.sin(t*2.1);
  rigs.back.head.rotation.y = 0.05*Math.sin(t*1.6);
}

function updateGuy(t){
  const g=rigs.guy; if(!g) return;
  const appear=t>=3.16 && t<=7.88;
  g.root.visible=appear;
  if(!appear) return;

  const drop=smooth(3.16,3.56,t);
  const seated=smooth(3.34,3.58,t);
  const launch=easeInCubic((t-7.24)/(7.72-7.24));
  const baseY=-0.43;
  let y=lerp(3.28,baseY,drop);
  if(t>=7.24) y=lerp(baseY,4.05,launch);
  const chairKick = Math.exp(-Math.max(0,t-3.55)*7.0)*Math.sin(Math.max(0,t-3.55)*19.0)*0.10;
  g.root.position.set(0,y,0.95+chairKick);
  setSeated(g,seated*(1-smooth(7.12,7.40,t)));

  // calm, almost no reaction
  g.head.rotation.x = 0.018*Math.sin(t*2.0);

  // right arm rises to accompany the cup; left remains relaxed
  const raise=smooth(4.18,5.10,t)*(1-smooth(5.86,6.45,t));
  g.armR.rotation.x=-1.28*raise;
  g.armR.rotation.z=0.12*raise;
  g.armL.rotation.x=-0.08;

  const deskP=new THREE.Vector3(0.40,0.84,0.18);
  const mouthP=new THREE.Vector3(0.12,1.23,0.58);
  const cp=deskP.clone().lerp(mouthP,raise);
  cup.position.copy(cp);
  cup.rotation.x=-0.28*raise;

  // Chair reacts physically to landing, then settles.
  const c=chairs[0];
  if(c){
    const dt=Math.max(0,t-3.55);
    const impulse = dt<0.85 ? Math.exp(-dt*5.3)*Math.sin(dt*16.5) : 0;
    c.position.z=0.93 + 0.14*Math.max(0,impulse);
    c.position.y=-0.045*Math.max(0,Math.exp(-dt*7.0)*Math.sin(dt*20.0));
  }
}

function updateDebris(t){
  const dt=t-3.18;
  intactTile.visible=t<3.18;
  holeDark.visible=t>=3.18;
  for(let i=0;i<debris.length;i++){
    const d=debris[i], m=d.mesh;
    if(dt<0 || dt>2.1){m.visible=false;continue;}
    m.visible=true;
    m.position.copy(new THREE.Vector3(holeX,3.0,holeZ).add(d.offset));
    m.position.x += d.vel.x*dt;
    m.position.y += d.vel.y*dt - 0.5*5.4*dt*dt;
    m.position.z += d.vel.z*dt;
    if(m.position.y<0.035) m.position.y=0.035;
    m.rotation.set(d.spin.x*dt,d.spin.y*dt,d.spin.z*dt);
  }
  const ldt=t-7.34;
  for(let i=0;i<launchDust.length;i++){
    const d=launchDust[i],m=d.mesh;
    if(ldt<0||ldt>0.8){m.visible=false;continue;}
    m.visible=true;
    const rad=0.18+0.15*ldt;
    m.position.set(Math.cos(d.ang)*rad,3.00-0.8*ldt-1.5*ldt*ldt,holeZ+Math.sin(d.ang)*rad);
    m.rotation.set(ldt*(i+1),ldt*2,ldt*0.7*i);
  }
}

function updateClock(t){ setClockText(t>=2.25?'4:17':'4:16'); }

function updateCamera(t){
  const push = 0.12*smooth(0,2.8,t);
  const impactDt=t-3.54;
  let shake=0;
  if(impactDt>=0 && impactDt<0.34) shake=Math.sin(impactDt*82)*Math.exp(-impactDt*11)*0.028;
  camera.position.set(0.18+shake,1.68+shake*0.45,-7.9+push);
  camera.lookAt(cameraTarget);
}

function update(t){
  updateClock(t);
  poseWorkers(t);
  updateGuy(t);
  updateDebris(t);
  updateCamera(t);
}

window.setTime=(t)=>{update(Math.max(0,Math.min(DURATION,t)));};
window.setFrame=(f)=>window.setTime(f/FPS);
window.renderFrame=()=>renderer.render(scene,camera);
window.getDuration=()=>DURATION;
window.getFPS=()=>FPS;
window.setMasterQuality=()=>{renderer.shadowMap.enabled=true;renderer.toneMappingExposure=1.05;};

window.addEventListener('resize',()=>{
  renderer.setSize(window.innerWidth,window.innerHeight,false);
  camera.aspect=window.innerWidth/window.innerHeight; camera.updateProjectionMatrix();
});

(async()=>{
  try{
    await initAssets();
    window.setTime(0);
    renderer.render(scene,camera);
    window.__ready=true;
  }catch(err){
    console.error(err);
    window.__renderError=String(err?.stack||err);
    window.__ready=false;
  }
})();
