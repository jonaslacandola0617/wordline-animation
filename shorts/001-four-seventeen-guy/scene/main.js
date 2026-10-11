import * as THREE from 'three';
import { OBJLoader } from '/node_modules/three/examples/jsm/loaders/OBJLoader.js';
import { MTLLoader } from '/node_modules/three/examples/jsm/loaders/MTLLoader.js';

const WIDTH = 2160;
const HEIGHT = 3840;
const FPS = 30;
const DURATION = 9.5;

const renderer = new THREE.WebGLRenderer({
  antialias: true,
  alpha: false,
  preserveDrawingBuffer: true,
  powerPreference: 'high-performance'
});
renderer.setSize(WIDTH, HEIGHT, false);
renderer.setPixelRatio(1);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.04;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xd8d1c7);
scene.fog = new THREE.Fog(0xd8d1c7, 10, 20);

const camera = new THREE.PerspectiveCamera(41, WIDTH / HEIGHT, 0.05, 100);
const cameraBase = new THREE.Vector3(3.15, 2.48, 7.1);
const cameraTarget = new THREE.Vector3(0.0, 1.42, -0.72);
camera.position.copy(cameraBase);
camera.lookAt(cameraTarget);

const hemi = new THREE.HemisphereLight(0xf8f2e7, 0x78838a, 2.15);
scene.add(hemi);

const key = new THREE.DirectionalLight(0xfff1d5, 4.1);
key.position.set(4.8, 7.5, 5.2);
key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
key.shadow.camera.near = 0.1;
key.shadow.camera.far = 30;
key.shadow.camera.left = -7;
key.shadow.camera.right = 7;
key.shadow.camera.top = 7;
key.shadow.camera.bottom = -7;
scene.add(key);

const fill = new THREE.DirectionalLight(0xbfd8ea, 1.7);
fill.position.set(-5.5, 4.5, 2);
scene.add(fill);

const warmWhite = new THREE.MeshStandardMaterial({ color: 0xe9e3d9, roughness: 0.90 });
const floorMat = new THREE.MeshStandardMaterial({ color: 0xb9aa9c, roughness: 0.96 });
const wallMat = new THREE.MeshStandardMaterial({ color: 0xe4ddd3, roughness: 0.95 });
const ceilingMat = new THREE.MeshStandardMaterial({ color: 0xf1ede7, roughness: 0.93 });
const darkMat = new THREE.MeshStandardMaterial({ color: 0x30373c, roughness: 0.78 });
const paperMat = new THREE.MeshStandardMaterial({ color: 0xf4f0e8, roughness: 0.90 });
const planterMat = new THREE.MeshStandardMaterial({ color: 0xa06f58, roughness: 0.90 });
const leafMat = new THREE.MeshStandardMaterial({ color: 0x668b69, roughness: 0.94 });
const glassMat = new THREE.MeshPhysicalMaterial({
  color: 0x9dc8d8, roughness: 0.25, transparent: true, opacity: 0.52, depthWrite: false
});

function box(name, size, pos, mat, cast=true, receive=true) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(...size), mat);
  m.name = name;
  m.position.set(...pos);
  m.castShadow = cast;
  m.receiveShadow = receive;
  scene.add(m);
  return m;
}

// Architectural shell only; actual furniture and humans come from the supplied Wordline asset packs.
box('floor', [6.7,0.10,7.4], [0,-0.05,-0.45], floorMat, false, true);
box('back-wall', [6.7,3.35,0.12], [0,1.675,-3.72], wallMat, false, true);
box('left-wall', [0.12,3.35,7.4], [-3.35,1.675,-0.45], wallMat, false, true);
box('right-wall', [0.12,3.35,7.4], [3.35,1.675,-0.45], wallMat, false, true);

// Window with real depth/frame and a calm daytime backdrop.
box('window-frame', [2.45,1.78,0.08], [-1.72,2.02,-3.625], darkMat, true, true);
const windowGlass = new THREE.Mesh(new THREE.PlaneGeometry(2.27,1.60), glassMat);
windowGlass.position.set(-1.72,2.02,-3.57);
scene.add(windowGlass);
const sky = new THREE.Mesh(
  new THREE.PlaneGeometry(2.17,1.50),
  new THREE.MeshBasicMaterial({ color: 0xa9c9d7 })
);
sky.position.set(-1.72,2.02,-3.60);
scene.add(sky);

// Small potted office plant, only because the packs do not contain a correctly-scaled indoor plant.
const pot = new THREE.Mesh(new THREE.CylinderGeometry(0.18,0.22,0.31,10), planterMat);
pot.position.set(2.72,0.155,-3.05); pot.castShadow = true; scene.add(pot);
for (let i=0;i<7;i++) {
  const leaf = new THREE.Mesh(new THREE.ConeGeometry(0.07,0.48,7), leafMat);
  leaf.position.set(2.72 + (i-3)*0.035, 0.46 + Math.abs(i-3)*0.02, -3.05);
  leaf.rotation.z = (i-3)*0.17;
  leaf.castShadow = true;
  scene.add(leaf);
}

// Suspended ceiling. Center tile is the recurring entry hole.
const tileSize = 1.05;
for (let ix=-3; ix<=3; ix++) {
  for (let iz=-3; iz<=3; iz++) {
    const x = ix * tileSize;
    const z = -0.48 + iz * tileSize;
    if (Math.abs(x) < 0.53 && Math.abs(z + 0.48) < 0.53) continue;
    const tile = new THREE.Mesh(new THREE.BoxGeometry(0.99,0.055,0.99), ceilingMat);
    tile.position.set(x,3.24,z);
    tile.receiveShadow = true;
    scene.add(tile);
  }
}
const breakTile = new THREE.Mesh(new THREE.BoxGeometry(0.99,0.055,0.99), ceilingMat);
breakTile.position.set(0,3.24,-0.48);
breakTile.receiveShadow = true;
scene.add(breakTile);

// Subtle ceiling grid strips.
const gridMat = new THREE.MeshStandardMaterial({ color: 0xc8c3bc, roughness: 0.9 });
for (let i=-3;i<=3;i++) {
  box('ceiling-grid-x-'+i,[0.018,0.07,7.30],[i*tileSize+0.52,3.20,-0.45],gridMat,false,true);
  box('ceiling-grid-z-'+i,[6.60,0.07,0.018],[0,3.20,-0.48+i*tileSize+0.52],gridMat,false,true);
}

// Deterministic fragments from the break tile.
function seeded(i) {
  const x = Math.sin(i * 913.17 + 0.431) * 43758.5453123;
  return x - Math.floor(x);
}
const debris = [];
for (let i=0;i<18;i++) {
  const sx = (seeded(i*4)-0.5)*0.84;
  const sz = -0.48 + (seeded(i*4+1)-0.5)*0.84;
  const s = 0.035 + seeded(i*4+2)*0.075;
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(s,s*0.5,s*0.82), ceilingMat);
  mesh.visible = false;
  mesh.castShadow = true;
  scene.add(mesh);
  debris.push({
    mesh,
    start:new THREE.Vector3(sx,3.18,sz),
    vx:(seeded(i+30)-0.5)*0.9,
    vy:0.1+seeded(i+50)*0.8,
    vz:(seeded(i+70)-0.5)*0.9,
    rx:(seeded(i+90)-0.5)*8,
    rz:(seeded(i+110)-0.5)*8
  });
}

function makeClockTexture(text) {
  const c = document.createElement('canvas');
  c.width = 1024; c.height = 360;
  const ctx = c.getContext('2d');
  ctx.fillStyle = '#23282c';
  ctx.fillRect(0,0,c.width,c.height);
  ctx.fillStyle = '#d7e7cb';
  ctx.font = '700 225px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(text,c.width/2,c.height/2+7);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}
const clockBody = new THREE.Mesh(new THREE.BoxGeometry(1.42,0.56,0.12),darkMat);
clockBody.position.set(0.22,2.58,-3.57);
clockBody.castShadow = true;
scene.add(clockBody);
const clockMat = new THREE.MeshBasicMaterial({map:makeClockTexture('4:16')});
const clockFace = new THREE.Mesh(new THREE.PlaneGeometry(1.27,0.43),clockMat);
clockFace.position.set(0.22,2.58,-3.50);
scene.add(clockFace);
let clockState = '4:16';
function setClock(text) {
  if (clockState === text) return;
  clockState = text;
  if (clockMat.map) clockMat.map.dispose();
  clockMat.map = makeClockTexture(text);
  clockMat.needsUpdate = true;
}

const BASE03B='/assets/claude%20generated%20assets/WORLDLINE_ASSET_PACK_03B_81/';
const BASE46='/assets/claude%20generated%20assets/WORLDLINE_LAB_ASSET_PACK_46/models/humans/';

async function loadObjMtl(base,objFile,mtlFile) {
  const mtlLoader=new MTLLoader();
  mtlLoader.setPath(base);
  const mats=await mtlLoader.loadAsync(mtlFile);
  mats.preload();
  const loader=new OBJLoader();
  loader.setMaterials(mats);
  loader.setPath(base);
  const obj=await loader.loadAsync(objFile);
  obj.traverse(o=>{
    if(o.isMesh){
      o.castShadow=true;
      o.receiveShadow=true;
      const materials=Array.isArray(o.material)?o.material:[o.material];
      for(const m of materials){
        if(!m) continue;
        if(m.opacity<1){m.transparent=true;m.depthWrite=false;}
        if('roughness' in m && m.roughness===undefined)m.roughness=0.8;
      }
    }
  });
  return obj;
}

function deepCloneObject(obj){
  const c=obj.clone(true);
  c.traverse(o=>{
    if(o.isMesh){
      o.geometry=o.geometry.clone();
      if(Array.isArray(o.material))o.material=o.material.map(m=>m.clone());
      else if(o.material)o.material=o.material.clone();
    }
  });
  return c;
}

function findNamed(root,name){
  let found=null;
  root.traverse(o=>{if(!found&&o.name===name)found=o;});
  return found;
}

function makeJoint(root,jointName,nodeNames,pivot){
  const nodes=nodeNames.map(n=>findNamed(root,n)).filter(Boolean);
  if(!nodes.length)return null;
  root.updateMatrixWorld(true);
  const g=new THREE.Group();
  g.name=jointName;
  g.position.set(...pivot);
  root.add(g);
  g.updateMatrixWorld(true);
  for(const n of nodes)g.attach(n);
  return g;
}

const humanPivots={
  HUMAN_02:{
    hipL:[0.097,0.873,0],hipR:[-0.097,0.873,0],
    ankleL:[0.104,0.089,0.047],ankleR:[-0.104,0.089,-0.047],
    shoulderL:[0.190,1.351,0],shoulderR:[-0.190,1.351,0],
    wristL:[0.285,0.854,0.017],wristR:[-0.285,0.854,0.111],neck:[0,1.48,0.02]
  },
  HUMAN_03:{
    hipL:[0.097,0.972,0],hipR:[-0.097,0.972,0],
    ankleL:[0.105,0.099,0.052],ankleR:[-0.105,0.099,-0.052],
    shoulderL:[0.255,1.505,0],shoulderR:[-0.255,1.505,0],
    wristL:[0.361,0.951,0.019],wristR:[-0.361,0.951,0.123],neck:[0,1.66,0.02]
  },
  HUMAN_04:{
    hipL:[0.099,0.899,0],hipR:[-0.099,0.899,0],
    ankleL:[0.107,0.092,0.048],ankleR:[-0.107,0.092,-0.048],
    shoulderL:[0.195,1.391,0],shoulderR:[-0.195,1.391,0],
    wristL:[0.293,0.879,0.017],wristR:[-0.293,0.879,0.114],neck:[0,1.52,0.02]
  },
  HUMAN_08:{
    hipL:[0.091,0.914,0],hipR:[-0.091,0.914,0],
    ankleL:[0.099,0.093,0.049],ankleR:[-0.099,0.093,-0.049],
    shoulderL:[0.214,1.416,0],shoulderR:[-0.214,1.416,0],
    wristL:[0.330,0.905,0.027],wristR:[-0.330,0.905,0.127],neck:[0,1.55,0.02]
  }
};

function rigHuman(root,id){
  const p=humanPivots[id]||humanPivots.HUMAN_03;
  const ankleL=makeJoint(root,id+'_ankleL',['shoe_L'],p.ankleL);
  const ankleR=makeJoint(root,id+'_ankleR',['shoe_R'],p.ankleR);
  const hipL=makeJoint(root,id+'_hipL',['leg_L','legwear_L',ankleL?.name].filter(Boolean),p.hipL);
  const hipR=makeJoint(root,id+'_hipR',['leg_R','legwear_R',ankleR?.name].filter(Boolean),p.hipR);
  const wristL=makeJoint(root,id+'_wristL',['hand_L'],p.wristL);
  const wristR=makeJoint(root,id+'_wristR',['hand_R'],p.wristR);
  const shoulderL=makeJoint(root,id+'_shoulderL',['arm_L','sleeve_L',wristL?.name].filter(Boolean),p.shoulderL);
  const shoulderR=makeJoint(root,id+'_shoulderR',['arm_R','sleeve_R',wristR?.name].filter(Boolean),p.shoulderR);
  const head=makeJoint(root,id+'_head',['head','face','hair','glasses','headwear'].filter(Boolean),p.neck);
  return{root,id,ankleL,ankleR,hipL,hipR,wristL,wristR,shoulderL,shoulderR,head};
}

function setRot(j,x=0,y=0,z=0){if(j)j.rotation.set(x,y,z);}
function resetRig(r){
  if(!r)return;
  [r.ankleL,r.ankleR,r.hipL,r.hipR,r.wristL,r.wristR,r.shoulderL,r.shoulderR,r.head]
    .forEach(j=>{if(j)j.rotation.set(0,0,0);});
}
function seatedPose(r){
  setRot(r.hipL,-1.05,0,0.03);
  setRot(r.hipR,-1.05,0,-0.03);
  setRot(r.ankleL,0.72,0,0);
  setRot(r.ankleR,0.72,0,0);
}
function typingPose(r,t,phase=0){
  setRot(r.shoulderL,-0.20+Math.sin(t*8+phase)*0.035,0,0.07);
  setRot(r.shoulderR,-0.22-Math.sin(t*8+phase)*0.035,0,-0.07);
  if(r.head)r.head.rotation.x=0.045+Math.sin(t*0.8+phase)*0.012;
}
function idlePose(r,t,phase=0){
  if(r.head)r.head.rotation.z=Math.sin(t*1.2+phase)*0.012;
}

const desks=[],chairs=[];
let mainChair=null,shelf=null;
const rigs={};
let ready=false;

function addMonitor(pos,rotY=0){
  const g=new THREE.Group();g.position.set(...pos);g.rotation.y=rotY;
  const screen=new THREE.Mesh(new THREE.BoxGeometry(0.52,0.34,0.045),darkMat);screen.position.y=0.23;
  const stem=new THREE.Mesh(new THREE.BoxGeometry(0.05,0.22,0.05),darkMat);stem.position.y=0.06;
  const base=new THREE.Mesh(new THREE.BoxGeometry(0.25,0.035,0.17),darkMat);
  [screen,stem,base].forEach(m=>{m.castShadow=true;m.receiveShadow=true;g.add(m);});
  scene.add(g);return g;
}
function addPaper(pos,rotY=0){
  const p=new THREE.Mesh(new THREE.BoxGeometry(0.32,0.008,0.42),paperMat);
  p.position.set(...pos);p.rotation.y=rotY;p.castShadow=true;scene.add(p);
}

const cupMat=new THREE.MeshStandardMaterial({color:0xe7e2da,roughness:0.68});
const waterMat=new THREE.MeshPhysicalMaterial({color:0x8dc4d9,roughness:0.18,transparent:true,opacity:0.72,depthWrite:false});
const cup=new THREE.Group();
const cupBody=new THREE.Mesh(new THREE.CylinderGeometry(0.075,0.062,0.17,14,1,true),cupMat);
cupBody.position.y=0.085;cupBody.castShadow=true;
const cupWater=new THREE.Mesh(new THREE.CylinderGeometry(0.061,0.061,0.012,14),waterMat);
cupWater.position.y=0.16;
cup.add(cupBody,cupWater);
scene.add(cup);
const cupStart=new THREE.Vector3(-0.33,0.79,0.18);
const cupMouth=new THREE.Vector3(0.06,1.22,-0.26);

async function setupAssets(){
  const [deskSrc,chairSrc,shelfSrc]=await Promise.all([
    loadObjMtl(BASE03B+'interiors/','INTERIOR_04_OfficeDesk.obj','INTERIOR_04_OfficeDesk.mtl'),
    loadObjMtl(BASE03B+'interiors/','INTERIOR_05_OfficeChair.obj','INTERIOR_05_OfficeChair.mtl'),
    loadObjMtl(BASE03B+'interiors/','INTERIOR_06_Shelf.obj','INTERIOR_06_Shelf.mtl')
  ]);

  function addDesk(x,z,ry=0){
    const d=deepCloneObject(deskSrc);d.position.set(x,0,z);d.rotation.y=ry;scene.add(d);desks.push(d);return d;
  }
  function addChair(x,z,ry=0){
    const c=deepCloneObject(chairSrc);c.position.set(x,0,z);c.rotation.y=ry;scene.add(c);chairs.push(c);return c;
  }

  addDesk(0.00,0.05,0);
  addDesk(-1.75,-1.04,0);
  addDesk(1.74,-1.06,0);
  addDesk(-1.70,1.19,0);

  mainChair=addChair(0.00,-0.47,Math.PI);
  addChair(-1.75,-1.52,Math.PI);
  addChair(1.74,-1.54,Math.PI);
  addChair(-1.70,0.71,Math.PI);

  shelf=deepCloneObject(shelfSrc);
  shelf.position.set(2.72,0,-2.95);
  shelf.rotation.y=-Math.PI/2;
  scene.add(shelf);

  addMonitor([0.00,0.79,-0.10],0);
  addMonitor([-1.75,0.79,-1.18],0);
  addMonitor([1.74,0.79,-1.20],0);
  addMonitor([-1.70,0.79,1.02],0);
  addPaper([0.43,0.78,0.20],0.12);
  addPaper([-1.44,0.78,-0.79],-0.16);

  const [h02,h03,h04,h08]=await Promise.all([
    loadObjMtl(BASE46,'HUMAN_02.obj','HUMAN_02.mtl'),
    loadObjMtl(BASE46,'HUMAN_03.obj','HUMAN_03.mtl'),
    loadObjMtl(BASE46,'HUMAN_04.obj','HUMAN_04.mtl'),
    loadObjMtl(BASE46,'HUMAN_08.obj','HUMAN_08.mtl')
  ]);

  const guy=deepCloneObject(h03);
  guy.position.set(0,-0.47,-0.48);
  guy.rotation.y=0;
  scene.add(guy);rigs.guy=rigHuman(guy,'HUMAN_03');guy.visible=false;

  const w1=deepCloneObject(h02);
  w1.position.set(-1.75,-0.39,-1.51);w1.rotation.y=0;scene.add(w1);rigs.w1=rigHuman(w1,'HUMAN_02');

  const w2=deepCloneObject(h04);
  w2.position.set(1.74,-0.40,-1.53);w2.rotation.y=0;scene.add(w2);rigs.w2=rigHuman(w2,'HUMAN_04');

  const w3=deepCloneObject(h08);
  w3.position.set(-1.70,-0.41,0.70);w3.rotation.y=0;scene.add(w3);rigs.w3=rigHuman(w3,'HUMAN_08');

  ready=true;
}

function clamp01(x){return Math.max(0,Math.min(1,x));}
function smoothstep(a,b,x){const t=clamp01((x-a)/(b-a));return t*t*(3-2*t);}
function easeInQuad(t){t=clamp01(t);return t*t;}
function easeInQuart(t){t=clamp01(t);return t*t*t*t;}
function easeOutCubic(t){t=clamp01(t);return 1-Math.pow(1-t,3);}
function lerp(a,b,t){return a+(b-a)*t;}

function updateDebris(t){
  const dt=t-3.18;
  for(let i=0;i<debris.length;i++){
    const d=debris[i],m=d.mesh;
    if(dt<0||dt>1.6){m.visible=false;continue;}
    m.visible=true;
    const q=dt;
    m.position.set(
      d.start.x+d.vx*q,
      d.start.y+d.vy*q-2.8*q*q,
      d.start.z+d.vz*q
    );
    if(m.position.y<0.03)m.position.y=0.03;
    m.rotation.set(d.rx*q,q*(i%3-1)*3.4,d.rz*q);
  }
}

function updateWorkers(t){
  for(const r of [rigs.w1,rigs.w2,rigs.w3]){resetRig(r);seatedPose(r);}
  typingPose(rigs.w1,t,0.3);
  typingPose(rigs.w2,t,1.4);
  typingPose(rigs.w3,t,2.1);

  // Tiny shared anticipation. Nobody panics.
  const look=smoothstep(1.75,2.35,t)*(1-smoothstep(3.42,4.10,t));
  if(rigs.w1.head){
    rigs.w1.head.rotation.x=lerp(0.04,-0.23,look);
    rigs.w1.head.rotation.z=lerp(0,0.06,look);
  }
  if(rigs.w2.head){
    rigs.w2.head.rotation.x=lerp(0.04,-0.15,look);
  }

  // One worker stops typing just before 4:17, then calmly resumes after the exit.
  const pause=smoothstep(2.15,2.55,t)*(1-smoothstep(8.05,8.55,t));
  if(rigs.w1.shoulderL)rigs.w1.shoulderL.rotation.x*=1-pause;
  if(rigs.w1.shoulderR)rigs.w1.shoulderR.rotation.x*=1-pause;
  idlePose(rigs.w3,t,0.4);
}

function updateGuy(t){
  const r=rigs.guy;
  if(!r)return;
  resetRig(r);seatedPose(r);
  const root=r.root;
  const finalY=-0.47;
  const baseZ=-0.48;

  if(t<3.08||t>7.88){
    root.visible=false;
    return;
  }
  root.visible=true;

  if(t<=3.48){
    const p=easeInQuad((t-3.08)/0.40);
    root.position.y=lerp(3.70,finalY,p);
    root.position.z=baseZ;
  }else{
    root.position.y=finalY;
    root.position.z=baseZ;
  }

  // Tiny physical settle after landing.
  if(t>=3.48&&t<3.88){
    const dt=t-3.48;
    root.position.y=finalY + Math.sin(dt*22)*0.055*Math.exp(-dt*7.0);
  }

  // Calm reach/sip/return. Cup moves with the hand path for a readable contact.
  const reach=smoothstep(4.18,4.72,t);
  const toMouth=smoothstep(4.72,5.28,t);
  const hold=1-smoothstep(5.62,6.20,t);
  const up=Math.min(toMouth,hold);
  const returnP=smoothstep(5.65,6.30,t);

  if(r.shoulderR){
    r.shoulderR.rotation.x=-0.10-0.52*reach+0.16*returnP;
    r.shoulderR.rotation.z=-0.09-0.10*reach;
  }
  if(r.wristR)r.wristR.rotation.x=0.12*reach;

  let cpos=cupStart.clone();
  if(t<4.18){
    cpos.copy(cupStart);
  }else if(t<4.72){
    const p=smoothstep(4.18,4.72,t);
    cpos.lerpVectors(cupStart,new THREE.Vector3(-0.06,0.90,-0.10),p);
  }else if(t<5.28){
    const p=smoothstep(4.72,5.28,t);
    cpos.lerpVectors(new THREE.Vector3(-0.06,0.90,-0.10),cupMouth,p);
  }else if(t<5.62){
    cpos.copy(cupMouth);
  }else if(t<6.30){
    const p=smoothstep(5.62,6.30,t);
    cpos.lerpVectors(cupMouth,cupStart,p);
  }else{
    cpos.copy(cupStart);
  }
  cup.position.copy(cpos);
  cup.rotation.z=(t>=4.95&&t<=5.62)?-0.22:0;

  // Ridiculously fast, clean vertical departure.
  if(t>=7.28){
    const p=easeInQuart((t-7.28)/0.60);
    root.position.y=lerp(finalY,4.55,p);
  }
}

function updateChair(t){
  if(!mainChair)return;
  const impact=smoothstep(3.36,3.50,t);
  const settle=smoothstep(3.50,4.05,t);
  mainChair.position.z=-0.47-0.16*impact+0.08*settle;
  mainChair.rotation.z=Math.sin(Math.max(0,t-3.42)*19)*0.018*Math.exp(-Math.max(0,t-3.42)*5);
}

function updateCamera(t){
  // Constant restrained push-in; deterministic micro-impulse at impact only.
  const push=smoothstep(0,DURATION,t);
  camera.position.copy(cameraBase);
  camera.position.z-=0.34*push;
  camera.position.x-=0.12*push;

  const dt=t-3.42;
  if(dt>=0&&dt<0.28){
    const amp=(1-dt/0.28);
    camera.position.x+=Math.sin(dt*92)*0.033*amp;
    camera.position.y+=Math.sin(dt*77+0.8)*0.023*amp;
  }
  camera.lookAt(cameraTarget);
}

function updateScene(t){
  if(!ready)return;
  setClock(t>=2.35?'4:17':'4:16');
  breakTile.visible=t<3.16;
  updateWorkers(t);
  updateGuy(t);
  updateChair(t);
  updateDebris(t);
  updateCamera(t);
}

window.setTime=function(t){
  const time=Math.max(0,Math.min(DURATION,Number(t)||0));
  updateScene(time);
  renderer.render(scene,camera);
  return time;
};
window.setFrame=function(frame){
  return window.setTime((Number(frame)||0)/FPS);
};
window.renderFrame=function(){
  renderer.render(scene,camera);
  return renderer.domElement.toDataURL('image/png');
};
window.getDuration=()=>DURATION;
window.getFPS=()=>FPS;
window.setMasterQuality=()=>({width:WIDTH,height:HEIGHT,pixelRatio:1});
window.__ready=false;

setupAssets().then(()=>{
  cup.position.copy(cupStart);
  updateScene(0);
  renderer.render(scene,camera);
  window.__ready=true;
}).catch(err=>{
  console.error(err);
  window.__loadError=String(err?.stack||err);
});
