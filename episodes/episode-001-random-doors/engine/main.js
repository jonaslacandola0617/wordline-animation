import * as THREE from 'three';
import {loadLibrary,createCharacter} from './assets.js';
import {Stage,materials,makeCake,makeDonut,makeDoor,addBox} from './stage.js';
import {buildStory,DURATIONS} from './story.js';

const q=new URLSearchParams(location.search);
const sceneId=(q.get('scene')||'01').padStart(2,'0');
const WIDTH=Number(q.get('width')||1920),HEIGHT=Number(q.get('height')||1080),FPS=30,DURATION=DURATIONS[sceneId];
if(q.has('render'))document.body.classList.add('render');

const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true,powerPreference:'high-performance'});
renderer.setSize(WIDTH,HEIGHT,false);
renderer.setPixelRatio(1);
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.04;
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
document.body.prepend(renderer.domElement);

const scene=new THREE.Scene();
scene.background=new THREE.Color(0xbfd2de);
scene.fog=new THREE.Fog(0xbfd2de,17,38);

const camera=new THREE.PerspectiveCamera(43,WIDTH/HEIGHT,.05,140);
camera.position.set(2.2,1.8,4.7);
camera.lookAt(0,1.25,-1.25);

scene.add(new THREE.HemisphereLight(0xf7f3e9,0x697a86,1.85));

const sun=new THREE.DirectionalLight(0xffedd3,3.5);
sun.position.set(4.5,7.5,5.5);
sun.castShadow=true;
sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.left=-8;
sun.shadow.camera.right=8;
sun.shadow.camera.top=8;
sun.shadow.camera.bottom=-8;
sun.shadow.camera.near=.1;
sun.shadow.camera.far=36;
scene.add(sun);

const fill=new THREE.DirectionalLight(0xaecdeb,1.20);
fill.position.set(-5,4,3);
scene.add(fill);

const warm=new THREE.PointLight(0xffd9a8,.65,9,2);
warm.position.set(1.8,2.65,1.5);
scene.add(warm);

window.__ready=false;
window.__loadError=null;

try{
  const lib=await loadLibrary();
  const stage=new Stage(scene,lib);
  const M=materials();

  const chars={
    A:createCharacter(scene,lib,'h02','HUMAN_02'),
    B:createCharacter(scene,lib,'h03','HUMAN_03'),
    C:createCharacter(scene,lib,'h04','HUMAN_04'),
    D:createCharacter(scene,lib,'h08','HUMAN_08'),
    E1:createCharacter(scene,lib,'h01','HUMAN_01'),
    E2:createCharacter(scene,lib,'h05','HUMAN_05')
  };

  const cake=makeCake(scene,M);
  const donut=makeDonut(scene);

  const coffee=new THREE.Group();
  addBox(coffee,[.18,.22,.16],[0,.11,0],M.white);
  scene.add(coffee);
  coffee.visible=false;

  const chainDoors=[
    makeDoor(scene,M,[-2.55,0,-2.15],.70),
    makeDoor(scene,M,[0,0,-2.55],.70),
    makeDoor(scene,M,[2.55,0,-2.15],.70)
  ];

  // Curved low-poly wall of water. It lives inside the beach destination,
  // so normal room geometry occludes it everywhere except the open doorway.
  const wave=new THREE.Group();
  const waveGeo=new THREE.PlaneGeometry(13.5,5.2,34,14);
  const pos=waveGeo.attributes.position;
  for(let i=0;i<pos.count;i++){
    const x=pos.getX(i);
    const y=pos.getY(i);
    const ny=(y+2.6)/5.2;
    const curl=1.55*Math.pow(Math.max(0,ny),4);
    const chop=.12*Math.sin(x*1.7+ny*5.2)+.06*Math.sin(x*3.1);
    pos.setZ(i,curl+chop);
  }
  waveGeo.computeVertexNormals();
  const waveBody=new THREE.Mesh(waveGeo,M.water);
  waveBody.castShadow=true;
  waveBody.receiveShadow=true;
  wave.add(waveBody);

  for(let i=0;i<34;i++){
    const foam=new THREE.Mesh(
      new THREE.IcosahedronGeometry(.14+.055*(i%4),1),
      M.white
    );
    foam.position.set(-6.4+i*.39,2.55+Math.sin(i*.75)*.12,1.30+Math.sin(i*.51)*.12);
    foam.scale.set(1.5,.55,1.0);
    foam.castShadow=true;
    wave.add(foam);
  }
  for(let i=0;i<18;i++){
    const spray=new THREE.Mesh(new THREE.IcosahedronGeometry(.055+(i%3)*.025,0),M.white);
    spray.position.set(-5.2+i*.61,2.78+(i%4)*.11,.95+Math.sin(i)*.25);
    wave.add(spray);
  }
  wave.position.set(0,2.45,-5.2);
  wave.visible=false;
  stage.dest.beach.add(wave);

  const ctx={scene,camera,renderer,lib,stage,M,chars,cake,donut,coffee,chainDoors,wave,t:0};
  const update=buildStory(sceneId,ctx);

  window.setTime=t=>{
    const x=Math.max(0,Math.min(DURATION,Number(t)||0));
    update(x);
    renderer.render(scene,camera);
    return x;
  };
  window.setFrame=f=>window.setTime((Number(f)||0)/FPS);
  window.renderFrame=()=>renderer.render(scene,camera);
  window.getDuration=()=>DURATION;
  window.getFPS=()=>FPS;
  window.setMasterQuality=()=>({width:WIDTH,height:HEIGHT,pixelRatio:1});

  window.__ready=true;
  document.getElementById('status').textContent='Ready scene '+sceneId;
  window.setTime(0);

  if(!q.has('render')){
    const start=performance.now();
    function loop(now){
      window.setTime(((now-start)/1000)%DURATION);
      requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);
  }
}catch(err){
  console.error(err);
  window.__loadError=String(err?.stack||err);
  document.getElementById('status').textContent='Load error';
}
