import * as THREE from 'three';
import {loadObjMtl,cloneDeep,rigHuman,resetRig} from '/episodes/episode-001-random-doors/engine/assets.js';

const query=new URLSearchParams(location.search);
const WIDTH=Number(query.get('width')||1080);
const HEIGHT=Number(query.get('height')||1920);
const FPS=30, DURATION=40;
const scene=new THREE.Scene();
scene.background=new THREE.Color(0x9bd4f6);
scene.fog=new THREE.FogExp2(0x9bd4f6,0.005);
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true,powerPreference:'high-performance'});
renderer.setSize(WIDTH,HEIGHT,false);renderer.setPixelRatio(1);
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.17;
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.domElement.id='wordline-render';
document.body.prepend(renderer.domElement);
if(query.has('render'))document.body.classList.add('render');
const camera=new THREE.PerspectiveCamera(43,WIDTH/HEIGHT,.12,520);
scene.add(new THREE.HemisphereLight(0xe9f5ff,0x75878d,2.35));
const sun=new THREE.DirectionalLight(0xffe6bc,3.75);
sun.position.set(-16,70,35);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.left=-65;sun.shadow.camera.right=65;sun.shadow.camera.top=65;sun.shadow.camera.bottom=-65;
sun.shadow.camera.far=220;sun.shadow.bias=-0.00018;scene.add(sun);
const fill=new THREE.DirectionalLight(0xa9dfff,1.2);fill.position.set(14,26,12);scene.add(fill);
const m={
  road:new THREE.MeshStandardMaterial({color:0x5d7185,roughness:.97}),
  pavement:new THREE.MeshStandardMaterial({color:0xe8dac6,roughness:.94}),
  lines:new THREE.MeshStandardMaterial({color:0xfbf2d2,roughness:.93}),
  blue:new THREE.MeshStandardMaterial({color:0x4da3ff,roughness:.63}),
  red:new THREE.MeshStandardMaterial({color:0xf46b5a,roughness:.72}),
  yellow:new THREE.MeshStandardMaterial({color:0xffd166,roughness:.72}),
  green:new THREE.MeshStandardMaterial({color:0x4ea978,roughness:.77}),
  white:new THREE.MeshStandardMaterial({color:0xf5f7fb,roughness:.67}),
  cream:new THREE.MeshStandardMaterial({color:0xfce8d3,roughness:.74}),
  cardboard:new THREE.MeshStandardMaterial({color:0xc49b70,roughness:.98}),
  glass:new THREE.MeshPhysicalMaterial({color:0x9bd8f2,metalness:.08,roughness:.16,transparent:true,opacity:.54,depthWrite:false}),
  brown:new THREE.MeshStandardMaterial({color:0x5c3827,roughness:.53}),
  steel:new THREE.MeshStandardMaterial({color:0x929faa,roughness:.52,metalness:.24}),
  ocean:new THREE.MeshStandardMaterial({color:0xffffff,roughness:.42,metalness:.03,flatShading:true,vertexColors:true,side:THREE.DoubleSide}),
  foam:new THREE.MeshStandardMaterial({color:0xe9fbff,roughness:.8})
};
function box(parent,size,pos,mat,cast=true){const obj=new THREE.Mesh(new THREE.BoxGeometry(...size),mat);obj.position.set(...pos);obj.castShadow=cast;obj.receiveShadow=true;parent.add(obj);return obj;}
function cyl(parent,r1,r2,h,pos,mat,seg=12){const obj=new THREE.Mesh(new THREE.CylinderGeometry(r1,r2,h,seg),mat);obj.position.set(...pos);obj.castShadow=true;obj.receiveShadow=true;parent.add(obj);return obj;}
function sphere(parent,r,pos,mat,detail=1){const obj=new THREE.Mesh(new THREE.IcosahedronGeometry(r,detail),mat);obj.position.set(...pos);obj.castShadow=true;obj.receiveShadow=true;parent.add(obj);return obj;}
const smooth=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x);};
const ramp=(t,a,b)=>smooth((t-a)/(b-a));
const lerp=(a,b,u)=>a+(b-a)*u;
const base46='/assets/claude%20generated%20assets/WORLDLINE_LAB_ASSET_PACK_46/models/';
const base03A='/assets/claude%20generated%20assets/WORLDLINE_ASSET_PACK_03A_80/';
const base03B='/assets/claude%20generated%20assets/WORLDLINE_ASSET_PACK_03B_81/';
const base1='/assets/claude%20generated%20assets/WORDLINE_LAB_ASSET_PACK_1/';

const LIBRARY=[
  ['human',base46+'humans/','HUMAN_02'],
  ['pedestrian',base46+'humans/','HUMAN_01'],
  ['businessman',base46+'humans/','HUMAN_04'],
  ['humanB',base46+'humans/','HUMAN_08'],
  ['bus',base03A+'land_vehicles/','LAND_01'],
  ['car1',base46+'cars/','CAR_01'],
  ['car2',base46+'cars/','CAR_02'],
  ['skyscraper',base46+'buildings/','BUILDING_10'],
  ['building1',base46+'buildings/','BUILDING_03'],
  ['building2',base46+'buildings/','BUILDING_07'],
  ['building3',base46+'buildings/','BUILDING_12'],
  ['building4',base46+'buildings/','BUILDING_16'],
  ['streetlight',base1+'props/','WL_Prop_Streetlight_A'],
  ['tree',base1+'vegetation/','WL_Tree_Broadleaf_A'],
  ['umbrella',base03B+'accessories/','ACCESSORY_05_Umbrella'],
  ['boat',base03A+'boats/','BOAT_01']
];
window.__ready=false;window.__loadError=null;
try{
 const values=await Promise.all(LIBRARY.map(async ([key,path,file])=>[key,await loadObjMtl(path,file+'.obj',file+'.mtl')]));
 const lib=Object.fromEntries(values);
 const city=new THREE.Group();scene.add(city);
 // Structural surfaces are supporting geometry, while the buildings, vehicles,
 // trees, streetlight and every character use real catalogued Wordline models.
 box(city,[24,.24,220],[-6.8,-.15,-39],m.road,false);
 box(city,[10,.18,220],[8.2,-.09,-39],m.pavement,false);
 box(city,[9,.18,220],[-24.2,-.09,-39],m.pavement,false);
 for(let z=-104;z<56;z+=12){
   box(city,[.20,.012,4.8],[-6.5,.006,z],m.lines,false);
   for(let x of[-18.7,-14.0]){
     box(city,[.9,.009,1.55],[x,.002,z+3],m.lines,false);
   }
 }
 for(let i=0;i<7;i++)box(city,[13,.012,.58],[-6.7,.006,7+i*1.35],m.lines,false);

 function addModel(key,position,scale=1,rotation=0,container=city){
   const c=cloneDeep(lib[key]);c.position.set(...position);c.scale.setScalar(scale);c.rotation.y=rotation;container.add(c);return c;
 }
 // Physical skyscraper whose x≈4 side acts as the first sideways "ground".
 const tower=addModel('skyscraper',[8.65,0,-7],.35,0);
 const buildingSet=[
   ['building1',[-34,0,-21],.86,0],['building2',[-34,0,-64],.78,.25],
   ['building3',[-33,0,-106],.67,0],['building1',[25,0,-35],.76,.17],
   ['building4',[28,0,-79],.53,0],['building2',[-35,0,27],.65,.08],
   ['building3',[31,0,27],.66,0],['building4',[-39,0,56],.44,0],
   ['building2',[26,0,-132],.86,.28],['building1',[-36,0,-145],1.0,0]
 ];
 buildingSet.forEach(([key,p,s,r])=>addModel(key,p,s,r));
 const lamps=[];
 for(let i=0;i<6;i++){
   const p=[2.2,0,-14-i*16];
   lamps.push(addModel('streetlight',p,1.06,Math.PI/2));
   addModel('tree',[11.2,0,-10-i*21],.86,.65);
 }
 // Only load one set of car models and clone, keeping actual vehicle geometry.
 const cars=[];
 for(let i=0;i<5;i++){
   const c=addModel(i%2?'car1':'car2',[-6.0+(i%2)*-4.5,0,-15-i*21],.92,i%2?Math.PI:0);
   cars.push({mesh:c,start:c.position.clone(),index:i});
 }
 const bus=addModel('bus',[-8,0,-10],.70,Math.PI);
 // The source City Bus uses a blue-steel body material. Keep its actual model,
 // but give the body Wordline's signature unmistakable red paint.
 bus.traverse(o=>{if(!o.isMesh)return;
   const arr=Array.isArray(o.material)?o.material:[o.material];
   for(const mat of arr)if(mat && /blue_steel|coral/i.test(mat.name)){mat.color.set(0xe84c42);mat.roughness=.64;mat.needsUpdate=true;}
 });
 const busWheels=[];bus.traverse(o=>{if(/wheel/i.test(o.name)&&!o.children.some(c=>/wheel/i.test(c.name)))busWheels.push(o);});
 const boat=addModel('boat',[-10,0,-116],.74,Math.PI/2);

 // Character rig and extras. Current A is HUMAN_02, as in the prior short.
 const actorRoot=addModel('human',[0,0,2],1.0,0,scene);
 const hero=rigHuman(actorRoot,'HUMAN_02');
 const extras=[];
 for(let i=0;i<6;i++){
   const mesh=addModel(i%3===0?'pedestrian':i%3===1?'businessman':'humanB',[-3.6-(i%3)*2.2,0,-4.0-i*11],1,0,scene);
   extras.push({mesh,rig:rigHuman(mesh,i%3===0?'HUMAN_01':i%3===1?'HUMAN_04':'HUMAN_08'),start:mesh.position.clone(),i});
 }
 const umbrellaGuyRoot=addModel('businessman',[-2.1,0,-3],1.0,0,scene);
 const umbrellaGuy=rigHuman(umbrellaGuyRoot,'HUMAN_04');
 const umbrella=addModel('umbrella',[0,0,0],.75,0,scene);
 // A genuine simple coffee cup is not in the current low-poly asset catalogs.
 const cup=new THREE.Group();scene.add(cup);cup.scale.setScalar(1.72);
 const shell=new THREE.Mesh(new THREE.CylinderGeometry(.105,.083,.30,16,1,true),m.cream);
 shell.position.y=.15;cup.add(shell);shell.castShadow=true;
 const bottom=cyl(cup,.087,.087,.016,[0,.01,0],m.cream,16);
 const top=cyl(cup,.098,.098,.008,[0,.305,0],m.brown,16);
 const handle=new THREE.Mesh(new THREE.TorusGeometry(.085,.019,6,13,Math.PI*1.65),m.cream);handle.position.set(.125,.18,0);handle.rotation.z=.15;cup.add(handle);
 const coffeeDrops=[];
 for(let i=0;i<23;i++)coffeeDrops.push(sphere(scene,.025+(i%3)*.010,[0,0,0],m.brown,0));
 const finalDrop=sphere(scene,.042,[0,0,0],m.brown,0);

 const boxes=new THREE.Group();boxes.position.set(1.1,0,1.5);scene.add(boxes);boxes.visible=false;
 for(let i=0;i<13;i++){
   const x=((i*7)%9-4)*.30;
   const z=((i*3)%7-3)*.24;
   const y=.20+(i%3)*.26;
   const b=box(boxes,[.52,.43,.48],[x,y,z],m.cardboard,true);
   b.rotation.y=i*.37;
 }
 // Quiet but legible sidewalk attachments for character to grab.
 const pole=addModel('streetlight',[3.0,0,-2],1.0,Math.PI/2,city);

 // Large high-poly-enough wave with volumetric crest, lit faceted surfaces, foam and spray.
 const wave=new THREE.Group();scene.add(wave);
 const W=185,H=83,XX=62,YY=32;
 const positions=[],uvs=[],colors=[],indices=[];
 for(let j=0;j<=YY;j++){
   const v=j/YY, yy=v*H-7;
   for(let i=0;i<=XX;i++){
     const u=i/XX,xx=(u-.5)*W;
     const curl=18*Math.pow(v,6);
     const chop=2.0*Math.sin(xx*.055+v*9)+1.0*Math.sin(xx*.19+v*6);
     positions.push(xx,yy,curl+chop);
     uvs.push(u,v);
     const baseColor=new THREE.Color(0x0c5d91).lerp(new THREE.Color(0x43b9da),v);
     if(v>.76)baseColor.lerp(new THREE.Color(0xa0e7ea),(v-.76)*1.8);
     const streak=(.5+.5*Math.sin(xx*.21+v*53))*Math.max(0,v-.45)*.30;
     baseColor.lerp(new THREE.Color(0xb3f0f1),streak);
     colors.push(baseColor.r,baseColor.g,baseColor.b);
   }
 }
 for(let j=0;j<YY;j++)for(let i=0;i<XX;i++){
   const a=j*(XX+1)+i,b=a+XX+1;
   indices.push(a,b,a+1,b,b+1,a+1);
 }
 const geo=new THREE.BufferGeometry();
 geo.setIndex(indices);geo.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
 geo.setAttribute('uv',new THREE.Float32BufferAttribute(uvs,2));
 geo.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));geo.computeVertexNormals();
 const waveMesh=new THREE.Mesh(geo,m.ocean);waveMesh.castShadow=true;waveMesh.receiveShadow=true;wave.add(waveMesh);
 const foam=[];
 for(let i=0;i<115;i++){
   const x=-88+i*1.54,y=74+Math.sin(i*.32)*2.6,z=21+Math.sin(i*.52)*2.2;
   const f=sphere(wave,.63+(i%5)*.15,[x,y,z],m.foam,i%3===0?1:0);
   f.scale.set(1.85,1.7,1.8);foam.push(f);
 }
 // Irregular whitewater veins on the front surface add depth instead of a flat blue panel.
 for(let i=0;i<94;i++){
   const x=-88+(i*13.47)%176;
   const v=.47+((i*7)%17)/17*.44;
   const yy=v*H-7;
   const z=18*Math.pow(v,6)+2*Math.sin(x*.055+v*9)+Math.sin(x*.19+v*6)+1.4;
   const streak=sphere(wave,.21+(i%4)*.11,[x,yy,z],m.foam,0);
   streak.scale.set(2.1+(i%3)*.6,.65,.53);
   streak.rotation.z=(i%7-3)*.15;
 }
 const spray=[];
 for(let i=0;i<110;i++){
   const sp=sphere(wave,.12+(i%5)*.06,[0,0,0],m.foam,0);
   spray.push(sp);
 }
 // Low scattered clouds frame the sky without obscuring the gag.
 const cloudMat=new THREE.MeshStandardMaterial({color:0xf6fdff,roughness:1});
 const clouds=[];
 for(let i=0;i<10;i++){
   const g=new THREE.Group();
   for(let j=0;j<4;j++)sphere(g,2.0+(j%3)*.55,[(j-1.5)*2.0,(j%2)*.5,0],cloudMat,1);
   g.position.set(-55+i*12,37+(i%4)*8,-60-i*9);
   scene.add(g);clouds.push(g);
 }

 const shotSpecs=[
  [0,1.5,[1.65,2.6,5.6],[.08,1.26,1.6],41],
  [1.5,4,[3.3,4.4,9.5],[2.6,2.9,1.2],43],
  [4,6.35,[1.6,6.1,10.6],[3.4,4,0],45],
  [6.35,8.35,[-2.0,12.0,14.8],[2.0,10,-8],47],
  [8.35,10,[-3.5,11,18],[3.8,7,-8],46],
  [10,13.2,[.5,13.0,10.5],[3.3,9.4,1],39],
  [13.2,16.4,[-5.0,26,25],[2.0,25,-10],48],
  [16.4,18.3,[5.6,8.0,13],[-1.0,6.1,-3],42],
  [18.3,20,[1.0,15.7,10],[3.3,13,1],42],
  [20,23.2,[-4.0,17,23],[2.5,6,-8],49],
  [23.2,26.2,[3.2,2.85,6.0],[1.1,1.2,1.5],44],
  [26.2,30,[2.4,2.4,5.0],[1.2,1.4,1.3],40],
  [30,33.25,[.6,5.0,9.5],[2.8,3.2,0],43],
  [33.25,36.2,[-6.0,16,25],[-12,34,-88],48],
  [36.2,37.7,[2.8,5.0,6.6],[2.55,3.65,1.6],39],
  [37.7,40,[.5,5.0,7.3],[2.65,3.7,-1],48]
 ];

 function heroPose(t){
   resetRig(hero);
   hero.root.visible=true;hero.root.rotation.set(0,0,0);
   hero.root.position.set(0,0,1.6);
   let rot=0;
   if(t<4){
     const p=ramp(t,.23,3.9);
     hero.root.position.set(lerp(0,3.72,p),lerp(0,3.5,p),1.6);
     rot=lerp(0,Math.PI/2,ramp(t,.38,2.2));
     if(hero.shoulderL)hero.shoulderL.rotation.x=-.55;
     if(hero.shoulderR)hero.shoulderR.rotation.x=-1.1;
   }else if(t<10){
     hero.root.position.set(3.72,lerp(3.50,6.8,ramp(t,6,10)),1.6);
     rot=Math.PI/2;
     if(hero.hipL)hero.hipL.rotation.x=.3*Math.sin(t*4);
     if(hero.shoulderR)hero.shoulderR.rotation.x=-1.4;
   }else if(t<20){
     hero.root.position.set(3.72,lerp(6.8,13.3,ramp(t,10,16.2)),1.6);
     rot=lerp(Math.PI/2,0,ramp(t,10,10.8));
     if(hero.shoulderL)hero.shoulderL.rotation.x=-2.3;
     if(hero.shoulderR)hero.shoulderR.rotation.x=-1.25;
     if(hero.hipL)hero.hipL.rotation.x=.28*Math.sin(t*3);
     if(hero.hipR)hero.hipR.rotation.x=-.32*Math.sin(t*3);
   }else if(t<24){
     hero.root.position.set(lerp(3.72,1.18,ramp(t,20.2,23.7)),lerp(13.3,0.45,ramp(t,20.1,23.6)),lerp(1.6,1.5,ramp(t,20,23.4)));
     rot=-.30*Math.sin(t*3);
     if(hero.shoulderL)hero.shoulderL.rotation.x=-1.5;
     if(hero.shoulderR)hero.shoulderR.rotation.x=-1.15;
   }else if(t<30){
     hero.root.position.set(1.18,.07,1.5);
     if(hero.shoulderR)hero.shoulderR.rotation.x=lerp(-.90,-1.55,ramp(t,26,28.3));
     if(hero.head)hero.head.rotation.x=-.08*ramp(t,27.2,28.2);
   }else{
     const p=ramp(t,30,32.8);
     hero.root.position.set(lerp(1.18,3.72,p),lerp(.07,3.55,p),1.5);
     rot=lerp(0,Math.PI/2,p);
     if(hero.shoulderR)hero.shoulderR.rotation.x=lerp(-.9,-1.4,ramp(t,37,38.5));
     if(hero.head)hero.head.rotation.y=lerp(0,-.18,ramp(t,34,35.5));
   }
   hero.root.rotation.z=rot;
   return rot;
 }

 function cupPose(t,rot){
   cup.visible=true;cup.rotation.set(0,0,0);cup.scale.setScalar(1);
   const a=hero.root.position;
   if(t<.4){cup.position.set(a.x-.26,a.y+1.14,a.z+.38);}
   else if(t<10){
     const p=ramp(t,.30,4.2);
     cup.position.set(lerp(-.26,2.78,p),lerp(1.19,7.15,ramp(t,.4,9.1)),1.96);
     cup.rotation.z=.4*Math.sin(t*2.7);
   }else if(t<20){
     cup.position.set(3.36,lerp(8.25,15.5,ramp(t,10,18.9)),1.3);
     cup.rotation.z=.45*Math.sin(t*2.2);
   }else if(t<25){
     cup.position.set(lerp(3.36,1.35,ramp(t,20,24.7)),lerp(15.5,1.55,ramp(t,20.2,24.6)),1.7);
     cup.rotation.z=.75*Math.sin(t*1.6);
   }else if(t<30){
     const p=ramp(t,25,26.0);
     cup.position.set(.91,lerp(1.25,1.32,p)+.27*ramp(t,27.1,28.3),1.97);
     cup.rotation.z=-.35*ramp(t,27.8,28.3);
   }else{
     const p=ramp(t,30,32.8);
     cup.position.set(lerp(.91,2.42,p)-.30*ramp(t,37,38.2),lerp(1.34,3.80,p)+.20*ramp(t,37,38.2),1.99);
     cup.rotation.z=-.10;
   }
   finalDrop.visible=t>=26.45&&t<27.12;
   if(finalDrop.visible){
     const p=ramp(t,26.45,27.1);
     finalDrop.position.set(1.42,lerp(2.6,1.50,p),1.83);
   }
   coffeeDrops.forEach((d,i)=>{
     d.visible=t<1.50;
     if(d.visible){
       const p=ramp(t,.05,1.5),an=i*2.39996;
       d.position.set(.24+p*(1.4+i*.09),1.65+Math.sin(an)*.17+p*(i%5)*.04,1.6+Math.cos(an)*.26);
     }
   });
 }

 const baseBusQuat=new THREE.Quaternion();
 const verticalQ=new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().makeBasis(
   new THREE.Vector3(0,0,-1),new THREE.Vector3(-1,0,0),new THREE.Vector3(0,1,0)
 ));
 function busPose(t){
   bus.visible=t<32;bus.scale.setScalar(.70);
   if(t<4){
     bus.position.set(lerp(-9.4,-2.2,ramp(t,1.0,4.0)),0,-7);
     bus.quaternion.setFromAxisAngle(new THREE.Vector3(0,1,0),Math.PI/2);
   }else if(t<6.4){
     bus.position.set(lerp(-2.2,3.4,ramp(t,4,6.2)),lerp(0,2.0,ramp(t,4,6.1)),-8.2);
     bus.quaternion.copy(baseBusQuat).slerp(verticalQ,ramp(t,4.7,6.25));
   }else if(t<10){
     bus.position.set(3.40,lerp(2,17.8,ramp(t,6.4,10)), -8.2);
     bus.quaternion.copy(verticalQ);
   }else if(t<20){
     bus.position.set(lerp(3.4,.5,ramp(t,10,17)),lerp(17.8,48,ramp(t,10,19.0)),lerp(-8.2,-10.5,ramp(t,10,19)));
     bus.quaternion.copy(verticalQ).slerp(baseBusQuat,ramp(t,10,13));
     bus.rotation.z+=.1*Math.sin(t*2);
   }else{
     const p=ramp(t,20.1,23.25);
     bus.position.set(lerp(.5,-6.2,p),lerp(48,0,p),lerp(-10.5,-6.5,p));
     bus.quaternion.copy(baseBusQuat).slerp(verticalQ,0);
     bus.rotation.y=Math.PI/2;bus.rotation.z=.10*Math.sin((t-20)*8)*Math.max(0,1-ramp(t,22.9,23.8));
   }
   busWheels.forEach((o,i)=>{o.rotation.x=t*8.0;});
 }

 function extrasPose(t){
   extras.forEach(({mesh,rig,start,i})=>{
     resetRig(rig);
     const offset=i*.35;
     if(t<10){
       const p=ramp(t,.40+offset,4.6+offset);
       mesh.position.set(lerp(start.x,3.1+i*.12,p),lerp(0,2.2+i*.8,p),start.z);
       mesh.rotation.z=lerp(0,Math.PI/2,p);
     }else if(t<20){
       mesh.position.set(3.1+i*.15,lerp(2.2+i*.8,12+i*2.7,ramp(t,10,18.5)),start.z);
       mesh.rotation.z=lerp(Math.PI/2,0,ramp(t,10,11));
     }else if(t<30){
       mesh.position.set(lerp(3.1+i*.15,start.x,ramp(t,20,25)),lerp(12+i*2.7,0,ramp(t,20.1,24.6)),start.z);
       mesh.rotation.z=0;
     }else{
       mesh.position.set(lerp(start.x,3.2+i*.2,ramp(t,30,34)),2.0+i*.4,start.z);
       mesh.rotation.z=lerp(0,Math.PI/2,ramp(t,30,33));
     }
     if(rig.shoulderL)rig.shoulderL.rotation.x=-.16*Math.sin(t*3+i);
   });
   umbrellaGuyRoot.visible=t>=16.4 && t<20;
   umbrella.visible=umbrellaGuyRoot.visible;
   if(umbrellaGuyRoot.visible){
     const p=ramp(t,16.45,19.8);
     umbrellaGuyRoot.position.set(-2.2,lerp(0,22,p),-3.2);
     umbrellaGuyRoot.rotation.z=-.2*p;
     umbrella.position.set(-2.1,umbrellaGuyRoot.position.y+2.25,-3.2);
     umbrella.rotation.set(Math.PI*.04,0,0);
   }
 }

 function carsPose(t){
   for(const {mesh,start,index:i} of cars){
     const offset=i*.2;
     if(t<10){
       const p=ramp(t,.55+offset,5.2+offset);
       mesh.position.set(lerp(start.x,3.5,p),lerp(0,1.0+i*.52,p),start.z);
       mesh.rotation.z=lerp(0,Math.PI/2,p);
     }else if(t<20){
       mesh.position.set(3.5,lerp(1.0+i*.52,17+i*4.5,ramp(t,10,19)),start.z);
       mesh.rotation.z=0;
     }else if(t<30){
       mesh.position.set(lerp(3.5,start.x,ramp(t,20,24.5)),lerp(17+i*4.5,0,ramp(t,20.2,24.2)),start.z);
       mesh.rotation.z=0;
     }else{
       mesh.position.set(lerp(start.x,3.5,ramp(t,30,34)),lerp(0,2+i*.52,ramp(t,30,34)),start.z);
       mesh.rotation.z=lerp(0,Math.PI/2,ramp(t,30,33));
     }
   }
 }

 function wavePose(t){
   wave.visible=t>=32.5;
   boat.visible=t>=32.5;
   if(wave.visible){
     const p=ramp(t,32.5,39.7);
     wave.position.set(0,0,lerp(-108,-26,p));
     waveMesh.position.y=Math.sin(t*2.0)*.35;
     foam.forEach((f,i)=>{f.position.y=74+Math.sin(i*.32+t*1.4)*1.9;});
     spray.forEach((sp,i)=>{
       const f=(t*.65+i*.123)%1;
       sp.position.set(-83+(i*17.13)%168+Math.sin(i*.7+t)*1.8,77+(i%13)*.9+f*8,22-(i%7)*.4+f*6);
       sp.scale.setScalar(.6+f*1.5);
     });
     boat.position.set(-10,lerp(2,34,ramp(t,32.5,39.7)),lerp(-103,-38,p));
     boat.rotation.z=.18*Math.sin(t*2);
     boat.rotation.x=.15*Math.cos(t*1.4);
   }
 }
 function cameraPose(t){
   let active=shotSpecs[shotSpecs.length-1];
   for(const spec of shotSpecs){if(t>=spec[0]&&t<spec[1]){active=spec;break;}}
   const [a,b,pos,target,fov]=active;
   camera.fov=fov;camera.updateProjectionMatrix();
   camera.position.set(...pos);
   // Gentle handcrafted camera creep inside each shot.
   const u=(t-a)/(b-a);
   camera.position.z-=.45*u;
   if(t>0&&t<4){camera.position.x+=.3*u;}
   if((t>4&&t<5.0)||(t>20&&t<20.5)){
     const dt=t<5?t-4:t-20;
     camera.position.x+=Math.sin(dt*48)*.045*Math.exp(-dt*6);
   }
   camera.lookAt(...target);
 }
 function setTime(t){
   t=Math.max(0,Math.min(DURATION,t));
   const rot=heroPose(t);
   cupPose(t,rot);
   busPose(t);
   extrasPose(t);
   carsPose(t);
   wavePose(t);
   boxes.visible=t>=20.0&&t<30.0;
   boxes.rotation.z=t>23.4?.09*Math.sin(t*4)*Math.exp(-(t-23.4)):0;
   cameraPose(t);
   renderer.render(scene,camera);
   return t;
 }
 window.setTime=setTime;
 window.setFrame=frame=>setTime(frame/FPS);
 window.renderFrame=()=>renderer.render(scene,camera);
 window.getDuration=()=>DURATION;
 window.getFPS=()=>FPS;
 window.setMasterQuality=()=>({width:WIDTH,height:HEIGHT,pixelRatio:1});
 window.__ready=true;
 document.getElementById('notice').textContent='Wordline 002 ready';
 setTime(0);
 if(!query.has('render')){
   const start=performance.now();
   function loop(now){setTime(((now-start)/1000)%DURATION);requestAnimationFrame(loop);}
   requestAnimationFrame(loop);
 }
}catch(error){
 console.error(error);window.__loadError=String(error.stack||error);
 document.getElementById('notice').textContent='Load error: '+String(error.message||error);
}
