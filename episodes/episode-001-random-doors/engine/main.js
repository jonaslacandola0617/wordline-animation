import * as THREE from 'three';
import {loadLibrary,createCharacter} from './assets.js';
import {Stage,materials,makeCake,makeDonut,makeDoor,addBox} from './stage.js';
import {buildStory,DURATIONS} from './story.js';
const q=new URLSearchParams(location.search),sceneId=(q.get('scene')||'01').padStart(2,'0'),WIDTH=Number(q.get('width')||1920),HEIGHT=Number(q.get('height')||1080),FPS=30,DURATION=DURATIONS[sceneId];
if(q.has('render'))document.body.classList.add('render');
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true,powerPreference:'high-performance'});renderer.setSize(WIDTH,HEIGHT,false);renderer.setPixelRatio(1);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.02;renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;document.body.prepend(renderer.domElement);
const scene=new THREE.Scene();scene.background=new THREE.Color(0xbfd2de);scene.fog=new THREE.Fog(0xbfd2de,12,28);const camera=new THREE.PerspectiveCamera(43,WIDTH/HEIGHT,.05,120);camera.position.set(2.7,1.9,5.8);camera.lookAt(0,1.25,-1.2);
scene.add(new THREE.HemisphereLight(0xf7f3e9,0x697a86,2.25));const sun=new THREE.DirectionalLight(0xffeed2,4);sun.position.set(5,8,5);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);sun.shadow.camera.left=-8;sun.shadow.camera.right=8;sun.shadow.camera.top=8;sun.shadow.camera.bottom=-8;sun.shadow.camera.far=32;scene.add(sun);const fill=new THREE.DirectionalLight(0xaecdeb,1.45);fill.position.set(-5,4,3);scene.add(fill);
window.__ready=false;window.__loadError=null;
try{
 const lib=await loadLibrary(),stage=new Stage(scene,lib),M=materials();
 const chars={A:createCharacter(scene,lib,'h02','HUMAN_02'),B:createCharacter(scene,lib,'h03','HUMAN_03'),C:createCharacter(scene,lib,'h04','HUMAN_04'),D:createCharacter(scene,lib,'h08','HUMAN_08'),E1:createCharacter(scene,lib,'h01','HUMAN_01'),E2:createCharacter(scene,lib,'h05','HUMAN_05')};
 const cake=makeCake(scene,M),donut=makeDonut(scene),coffee=new THREE.Group();addBox(coffee,[.18,.22,.16],[0,.11,0],M.white);scene.add(coffee);coffee.visible=false;
 const chainDoors=[makeDoor(scene,M,[-2.65,0,-1.15],.72),makeDoor(scene,M,[0,0,-1.55],.72),makeDoor(scene,M,[2.65,0,-1.15],.72)];
 const wave=new THREE.Group();const water=new THREE.Mesh(new THREE.BoxGeometry(9,5.6,.65),M.water);water.position.y=2.8;wave.add(water);for(let i=0;i<22;i++){const foam=new THREE.Mesh(new THREE.SphereGeometry(.18+.08*(i%3),8,6),M.white);foam.position.set(-4.3+i*.41,5.55+Math.sin(i*.8)*.17,.38);foam.scale.y=.55;wave.add(foam);}wave.position.set(0,0,-7);scene.add(wave);wave.visible=false;
 const ctx={scene,camera,renderer,lib,stage,M,chars,cake,donut,coffee,chainDoors,wave,t:0},update=buildStory(sceneId,ctx);
 window.setTime=t=>{const x=Math.max(0,Math.min(DURATION,Number(t)||0));update(x);renderer.render(scene,camera);return x;};window.setFrame=f=>window.setTime((Number(f)||0)/FPS);window.renderFrame=()=>renderer.render(scene,camera);window.getDuration=()=>DURATION;window.getFPS=()=>FPS;window.setMasterQuality=()=>({width:WIDTH,height:HEIGHT,pixelRatio:1});
 window.__ready=true;document.getElementById('status').textContent='Ready scene '+sceneId;window.setTime(0);
 if(!q.has('render')){const start=performance.now();function loop(now){window.setTime(((now-start)/1000)%DURATION);requestAnimationFrame(loop);}requestAnimationFrame(loop);}
}catch(err){console.error(err);window.__loadError=String(err?.stack||err);document.getElementById('status').textContent='Load error';}
