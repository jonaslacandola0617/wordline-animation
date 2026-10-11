import * as THREE from 'three';
import {cloneDeep} from './assets.js';
export const clamp01=x=>Math.max(0,Math.min(1,x));
export function smooth(a,b,x){const t=clamp01((x-a)/(b-a));return t*t*(3-2*t);}
export const lerp=(a,b,t)=>a+(b-a)*t;
export function materials(){return{
 wall:new THREE.MeshStandardMaterial({color:0xe8e3da,roughness:.92}),wallBlue:new THREE.MeshStandardMaterial({color:0xcbd8e3,roughness:.92}),
 floor:new THREE.MeshStandardMaterial({color:0xa99d91,roughness:.95}),wood:new THREE.MeshStandardMaterial({color:0x8b644f,roughness:.88}),
 dark:new THREE.MeshStandardMaterial({color:0x26313a,roughness:.78}),metal:new THREE.MeshStandardMaterial({color:0x7d8589,roughness:.62,metalness:.12}),
 sand:new THREE.MeshStandardMaterial({color:0xdac38c,roughness:1}),water:new THREE.MeshPhysicalMaterial({color:0x4f91b6,roughness:.25,transparent:true,opacity:.88}),
 concrete:new THREE.MeshStandardMaterial({color:0x777b80,roughness:.98}),tile:new THREE.MeshStandardMaterial({color:0xe5e9ea,roughness:.82}),
 coral:new THREE.MeshStandardMaterial({color:0xff6b6b,roughness:.75}),yellow:new THREE.MeshStandardMaterial({color:0xffd166,roughness:.75}),
 blue:new THREE.MeshStandardMaterial({color:0x4da3ff,roughness:.72}),navy:new THREE.MeshStandardMaterial({color:0x162a46,roughness:.80}),
 white:new THREE.MeshStandardMaterial({color:0xf5f7fb,roughness:.82})
};}
export function addBox(parent,size,pos,mat,cast=true){const m=new THREE.Mesh(new THREE.BoxGeometry(...size),mat);m.position.set(...pos);m.castShadow=cast;m.receiveShadow=true;parent.add(m);return m;}
export function addCylinder(parent,r1,r2,h,pos,mat,seg=16){const m=new THREE.Mesh(new THREE.CylinderGeometry(r1,r2,h,seg),mat);m.position.set(...pos);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m;}
function addText(parent,text,pos,scale=1){const c=document.createElement('canvas');c.width=1024;c.height=256;const x=c.getContext('2d');x.fillStyle='#162a46';x.fillRect(0,0,1024,256);x.fillStyle='#ffd166';x.font='800 120px Arial';x.textAlign='center';x.textBaseline='middle';x.fillText(text,512,130);const tex=new THREE.CanvasTexture(c);tex.colorSpace=THREE.SRGBColorSpace;const p=new THREE.Mesh(new THREE.PlaneGeometry(2.4*scale,.60*scale),new THREE.MeshBasicMaterial({map:tex}));p.position.set(...pos);parent.add(p);}
function shell(g,M,theme){addBox(g,[7.8,.10,6.4],[0,-.05,-.2],theme==='beach'?M.sand:(theme==='parking'||theme==='rooftop'?M.concrete:M.floor),false);if(!['beach','rooftop','parking'].includes(theme)){addBox(g,[2.62,3.2,.12],[-2.59,1.6,-2.65],theme==='office'?M.wallBlue:M.wall,false);addBox(g,[2.62,3.2,.12],[2.59,1.6,-2.65],theme==='office'?M.wallBlue:M.wall,false);addBox(g,[2.36,.48,.12],[0,2.96,-2.65],theme==='office'?M.wallBlue:M.wall,false);}}
export function makeDoor(parent,M,pos=[0,0,-2.56],scale=1){const g=new THREE.Group();g.position.set(...pos);g.scale.setScalar(scale);parent.add(g);addBox(g,[.18,2.75,.18],[-1.10,1.375,0],M.dark);addBox(g,[.18,2.75,.18],[1.10,1.375,0],M.dark);addBox(g,[2.38,.18,.18],[0,2.72,0],M.dark);const pivot=new THREE.Group();pivot.position.set(-1,0,0);g.add(pivot);addBox(pivot,[2,2.55,.11],[1,1.275,0],M.wood);const knob=addCylinder(pivot,.045,.045,.08,[1.74,1.28,.09],M.metal,12);knob.rotation.x=Math.PI/2;return{group:g,pivot,setOpen(p){pivot.rotation.y=-1.48*clamp01(p);}};}
function cloneTo(g,src,pos,ry=0,s=1){const o=cloneDeep(src);o.position.set(...pos);o.rotation.y=ry;o.scale.setScalar(s);g.add(o);return o;}
function buildTheme(theme,lib,M){const g=new THREE.Group();shell(g,M,theme);
 if(theme==='apartment'||theme==='party'){cloneTo(g,lib.table,[-1.65,0,-.65],0,.78);cloneTo(g,lib.fridge,[2.65,0,-1.45],Math.PI,.92);cloneTo(g,lib.shelf,[2.55,0,.85],-Math.PI/2,.95);if(theme==='party'){for(let i=0;i<8;i++)addCylinder(g,.13,.13,.26,[-2.6+i*.72,2.52+Math.sin(i)*.14,-2.42],[M.coral,M.yellow,M.blue][i%3],14);addText(g,'HAPPY BIRTHDAY',[0,2.45,-2.56],.82);}}
 else if(theme==='office'){for(const x of[-2,0,2]){cloneTo(g,lib.desk,[x,0,-.35],0,.85);cloneTo(g,lib.officeChair,[x,0,.45],Math.PI,.88);}cloneTo(g,lib.shelf,[3.2,0,-2.1],-Math.PI/2,.9);}
 else if(theme==='restaurant'||theme==='kitchen'){cloneTo(g,lib.restaurantTable,[-1.8,0,-.6],0,.95);cloneTo(g,lib.restaurantTable,[1.7,0,-.5],0,.95);cloneTo(g,lib.fridge,[2.8,0,-1.75],Math.PI,.88);addBox(g,[3.9,.65,.76],[0,.36,-2.15],M.metal);}
 else if(theme==='bathroom'){for(let x=-2.6;x<=2.6;x+=1.3)addBox(g,[.07,2.1,1.45],[x,1.05,-1.35],M.tile);addBox(g,[1.25,.78,.52],[2.5,.39,.1],M.white);}
 else if(theme==='laundromat'){for(let x=-2.7;x<=2.7;x+=1.1){addBox(g,[.92,1.12,.72],[x,.56,-1.65],M.white);const ring=new THREE.Mesh(new THREE.TorusGeometry(.28,.045,10,24),M.dark);ring.position.set(x,.58,-1.27);g.add(ring);}}
 else if(theme==='parking'){for(const x of[-3,-1,1,3])addBox(g,[.34,3,.34],[x,1.5,-1.4],M.concrete);for(const x of[-2,0,2])addBox(g,[.10,.012,3.5],[x,.02,-.2],M.yellow,false);}
 else if(theme==='rooftop'){addBox(g,[7.8,.82,.18],[0,.41,-2.72],M.concrete);for(let i=0;i<9;i++)addBox(g,[1,1.7+(i%4)*.55,1],[-5+i*1.35,(1.7+(i%4)*.55)/2,-7-(i%3)*.6],[M.navy,M.wallBlue,M.coral][i%3]);}
 else if(theme==='beach'){addBox(g,[12,.08,7],[0,-.02,-1],M.sand,false);const w=new THREE.Mesh(new THREE.PlaneGeometry(16,7),M.water);w.rotation.x=-Math.PI/2;w.position.set(0,.02,-5.2);g.add(w);cloneTo(g,lib.umbrella,[2,0,-1.45],0,.8);}
 else if(theme==='bus'){cloneTo(g,lib.bus,[0,-.05,-5.2],Math.PI/2,.36);addBox(g,[8,.08,5],[0,-.04,-5],M.concrete,false);}
 else if(theme==='convenience'){for(const x of[-2.5,0,2.5]){addBox(g,[1.3,1.85,.45],[x,.925,-1.6],M.white);for(let y=.4;y<1.7;y+=.4)addBox(g,[1.22,.05,.6],[x,y,-1.6],M.dark);}}
 else if(theme==='hotel'){addBox(g,[7.8,.08,7],[0,-.03,-.1],new THREE.MeshStandardMaterial({color:0x8d4f48,roughness:.98}),false);for(const x of[-2.9,-1.45,1.45,2.9])addBox(g,[.88,2.15,.10],[x,1.08,-2.58],M.wood);}
 else if(theme==='stairwell'){for(let i=0;i<9;i++)addBox(g,[2.8,.18,.48],[1.1,i*.18,-2.1+i*.43],M.concrete);}
 return g;
}
export class Stage{constructor(scene,lib){this.scene=scene;this.M=materials();this.sourceRoot=new THREE.Group();this.destRoot=new THREE.Group();scene.add(this.sourceRoot,this.destRoot);this.source={};this.dest={};const themes=['apartment','party','office','restaurant','kitchen','bathroom','laundromat','parking','rooftop','beach','bus','convenience','hotel','stairwell'];for(const t of themes){const a=buildTheme(t,lib,this.M);a.visible=false;this.sourceRoot.add(a);this.source[t]=a;const b=buildTheme(t,lib,this.M);b.position.z=-3;b.scale.setScalar(.92);b.visible=false;this.destRoot.add(b);this.dest[t]=b;}this.door=makeDoor(scene,this.M);}
 showSource(n){for(const[k,g]of Object.entries(this.source))g.visible=k===n;}showDest(n){for(const[k,g]of Object.entries(this.dest))g.visible=k===n;}}
export function makeCake(scene,M){const g=new THREE.Group();scene.add(g);const cream=new THREE.MeshStandardMaterial({color:0xf8e3d2,roughness:.78}),icing=new THREE.MeshStandardMaterial({color:0xffb8c8,roughness:.72});addCylinder(g,.62,.62,.30,[0,.15,0],cream,24);addCylinder(g,.48,.48,.29,[0,.44,0],cream,24);addCylinder(g,.33,.33,.28,[0,.72,0],cream,24);addCylinder(g,.64,.64,.055,[0,.31,0],icing,24);addCylinder(g,.50,.50,.055,[0,.59,0],icing,24);addCylinder(g,.35,.35,.055,[0,.87,0],icing,24);g.scale.setScalar(.78);g.visible=false;return g;}
export function setCakeState(cake,state){cake.rotation.z=[0,.025,.055,.095,.13][state]||0;}
export function makeDonut(scene){const g=new THREE.Group(),d=new THREE.Mesh(new THREE.TorusGeometry(.16,.075,10,24),new THREE.MeshStandardMaterial({color:0xb97445,roughness:.78}));d.rotation.x=Math.PI/2;g.add(d);scene.add(g);g.visible=false;return g;}
