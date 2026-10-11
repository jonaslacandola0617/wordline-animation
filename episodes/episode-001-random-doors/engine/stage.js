import * as THREE from 'three';
import {cloneDeep} from './assets.js';

export const clamp01=x=>Math.max(0,Math.min(1,x));
export function smooth(a,b,x){const t=clamp01((x-a)/(b-a));return t*t*(3-2*t);}
export const lerp=(a,b,t)=>a+(b-a)*t;

export function materials(){
  const std=(color,roughness=.85,extra={})=>new THREE.MeshStandardMaterial({color,roughness,...extra});
  return{
    wall:std(0xe9e4da,.93),
    wallCool:std(0xd7e1e9,.92),
    wallWarm:std(0xf0dfcc,.92),
    floor:std(0x9b9086,.96),
    wood:std(0x8d5f45,.88),
    dark:std(0x26313a,.78),
    metal:std(0x7d8589,.62,{metalness:.12}),
    sand:std(0xd9bf82,1),
    water:new THREE.MeshPhysicalMaterial({color:0x4f91b6,roughness:.23,transparent:true,opacity:.92,metalness:.03}),
    concrete:std(0x747b82,.97),
    tile:std(0xe6ebed,.80),
    coral:std(0xff6b6b,.72),
    yellow:std(0xffd166,.72),
    blue:std(0x4da3ff,.70),
    navy:std(0x162a46,.78),
    white:std(0xf5f7fb,.82),
    green:std(0x648a69,.90),
    pink:std(0xffb6c7,.76),
    glass:new THREE.MeshPhysicalMaterial({color:0x9fd2e5,roughness:.12,transparent:true,opacity:.38,depthWrite:false})
  };
}

export function addBox(parent,size,pos,mat,cast=true){
  const m=new THREE.Mesh(new THREE.BoxGeometry(...size),mat);
  m.position.set(...pos);m.castShadow=cast;m.receiveShadow=true;parent.add(m);return m;
}
export function addCylinder(parent,r1,r2,h,pos,mat,seg=16){
  const m=new THREE.Mesh(new THREE.CylinderGeometry(r1,r2,h,seg),mat);
  m.position.set(...pos);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m;
}
function addSphere(parent,r,pos,mat,seg=14){
  const m=new THREE.Mesh(new THREE.SphereGeometry(r,seg,Math.max(8,seg-2)),mat);
  m.position.set(...pos);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m;
}
function cloneTo(g,src,pos,ry=0,s=1){
  const o=cloneDeep(src);o.position.set(...pos);o.rotation.y=ry;o.scale.setScalar(s);g.add(o);return o;
}
function addText(parent,text,pos,scale=1,bg='#162a46',fg='#ffd166'){
  const c=document.createElement('canvas');c.width=1400;c.height=300;const x=c.getContext('2d');
  x.fillStyle=bg;x.fillRect(0,0,c.width,c.height);
  x.fillStyle=fg;x.font='900 118px Rubik, Arial Black, sans-serif';x.textAlign='center';x.textBaseline='middle';
  x.fillText(text,c.width/2,c.height/2+3);
  const tex=new THREE.CanvasTexture(c);tex.colorSpace=THREE.SRGBColorSpace;
  const p=new THREE.Mesh(new THREE.PlaneGeometry(3.2*scale,.68*scale),new THREE.MeshBasicMaterial({map:tex}));
  p.position.set(...pos);parent.add(p);return p;
}

function makeInteriorShell(g,M,theme){
  const wall=theme==='office'?M.wallCool:(theme==='party'?M.wallWarm:M.wall);
  addBox(g,[8.6,.10,8.8],[0,-.05,.45],theme==='bathroom'?M.tile:M.floor,false);

  // Back wall with a real doorway cutout.
  addBox(g,[3.02,3.55,.15],[-2.78,1.775,-3.03],wall,false);
  addBox(g,[3.02,3.55,.15],[2.78,1.775,-3.03],wall,false);
  addBox(g,[2.55,.63,.15],[0,3.235,-3.03],wall,false);

  // Side walls and ceiling prevent the destination from leaking around the doorway.
  addBox(g,[.15,3.55,8.8],[-4.23,1.775,.45],wall,false);
  addBox(g,[.15,3.55,8.8],[4.23,1.775,.45],wall,false);
  addBox(g,[8.6,.12,8.8],[0,3.52,.45],wall,false);

  // Baseboards help the room feel finished rather than like a cube.
  const trim=new THREE.MeshStandardMaterial({color:0xb9b2aa,roughness:.86});
  addBox(g,[8.35,.10,.08],[0,.05,-2.92],trim,false);
  addBox(g,[.08,.10,8.45],[-4.12,.05,.45],trim,false);
  addBox(g,[.08,.10,8.45],[4.12,.05,.45],trim,false);

  // Soft side window gives actual depth and daylight.
  if(!['bathroom','stairwell','hotel'].includes(theme)){
    addBox(g,[.08,1.62,2.20],[-4.12,2.05,.55],M.dark,false);
    const glass=new THREE.Mesh(new THREE.PlaneGeometry(2.04,1.46),M.glass);
    glass.rotation.y=Math.PI/2;glass.position.set(-4.07,2.05,.55);g.add(glass);
  }
}

function makeOpenShell(g,M,theme){
  if(theme==='beach'){
    addBox(g,[14,.08,9],[0,-.03,-1.7],M.sand,false);
    const oceanGeo=new THREE.PlaneGeometry(16,9,22,12);
    const p=oceanGeo.attributes.position;
    for(let i=0;i<p.count;i++){
      const x=p.getX(i),y=p.getY(i);
      p.setZ(i,.05*Math.sin(x*1.7)+.035*Math.cos(y*2.1));
    }
    oceanGeo.computeVertexNormals();
    const ocean=new THREE.Mesh(oceanGeo,M.water);ocean.rotation.x=-Math.PI/2;ocean.position.set(0,.02,-7.0);g.add(ocean);
  }else if(theme==='rooftop'){
    addBox(g,[9,.12,8],[0,-.05,.1],M.concrete,false);
    addBox(g,[9,.78,.18],[0,.39,-3.35],M.concrete);
    addBox(g,[.18,.78,8],[-4.4,.39,.1],M.concrete);
    addBox(g,[.18,.78,8],[4.4,.39,.1],M.concrete);
  }else if(theme==='parking'){
    addBox(g,[9,.10,9],[0,-.05,-.2],M.concrete,false);
    addBox(g,[9,.12,9],[0,3.45,-.2],M.concrete,false);
  }
}

function addSofa(g,M,pos=[1.45,0,.65]){
  const sofa=new THREE.Group();sofa.position.set(...pos);g.add(sofa);
  addBox(sofa,[2.25,.40,.78],[0,.38,0],M.navy);
  addBox(sofa,[2.25,.72,.22],[0,.76,-.29],M.navy);
  addBox(sofa,[.20,.58,.80],[-1.12,.53,0],M.navy);
  addBox(sofa,[.20,.58,.80],[1.12,.53,0],M.navy);
  addBox(sofa,[.88,.16,.62],[-.52,.65,.02],M.blue);
  addBox(sofa,[.88,.16,.62],[.52,.65,.02],M.coral);
}

function addPlant(g,M,pos){
  const p=new THREE.Group();p.position.set(...pos);g.add(p);
  addCylinder(p,.18,.23,.32,[0,.16,0],M.wood,12);
  for(let i=0;i<7;i++){
    const leaf=new THREE.Mesh(new THREE.ConeGeometry(.09,.58,7),M.green);
    leaf.position.set((i-3)*.035,.58+Math.abs(i-3)*.018,0);
    leaf.rotation.z=(i-3)*.18;leaf.castShadow=true;p.add(leaf);
  }
}

function addBalloons(g,M){
  const cols=[M.coral,M.yellow,M.blue,M.pink];
  const poses=[[-2.75,2.42,-2.82],[-2.05,2.62,-2.82],[-1.35,2.46,-2.82],[1.35,2.55,-2.82],[2.05,2.66,-2.82],[2.75,2.42,-2.82]];
  poses.forEach((p,i)=>{
    const s=addSphere(g,.18,p,cols[i%cols.length],16);s.scale.y=1.18;
    const line=addCylinder(g,.008,.008,.72,[p[0],p[1]-.47,p[2]],M.white,6);line.castShadow=false;
  });
}

function addCityBackground(g,M){
  const mats=[M.navy,M.wallCool,M.coral,M.yellow];
  for(let i=0;i<13;i++){
    const h=1.6+(i%5)*.62;
    addBox(g,[.9,h,.9],[-6+i*1.08,h/2,-8-(i%3)*.7],mats[i%mats.length],false);
  }
}

function addBusInterior(g,M,lib){
  // The doorway opens into an aisle; the actual supplied City Bus is staged beyond the windscreen.
  addBox(g,[3.6,.10,7.2],[0,-.04,-2.1],M.dark,false);
  addBox(g,[.12,2.5,7.2],[-1.78,1.25,-2.1],M.wallCool,false);
  addBox(g,[.12,2.5,7.2],[1.78,1.25,-2.1],M.wallCool,false);
  addBox(g,[3.6,.12,7.2],[0,2.52,-2.1],M.wallCool,false);

  for(let z=-.3;z>-5.1;z-=1.05){
    for(const x of[-1.15,1.15]){
      addBox(g,[.72,.16,.72],[x,.47,z],M.navy);
      addBox(g,[.72,.70,.16],[x,.83,z-.28],M.navy);
      addBox(g,[.10,.44,.10],[x-.22,.22,z],M.metal);
      addBox(g,[.10,.44,.10],[x+.22,.22,z],M.metal);
    }
  }
  for(let z=.2;z>-5.0;z-=1.1){
    const glass=new THREE.Mesh(new THREE.PlaneGeometry(.95,.72),M.glass);
    glass.rotation.y=Math.PI/2;glass.position.set(-1.70,1.60,z);g.add(glass);
    const glass2=glass.clone();glass2.position.x=1.70;g.add(glass2);
  }
  // Windshield and moving-road suggestion.
  const wind=new THREE.Mesh(new THREE.PlaneGeometry(2.8,1.25),M.glass);wind.position.set(0,1.62,-5.62);g.add(wind);
  addBox(g,[3.0,.04,4.0],[0,.02,-8.0],M.concrete,false);
  for(let z=-6.2;z>-9.8;z-=1.0)addBox(g,[.09,.015,.48],[0,.045,z],M.yellow,false);

  const bus=cloneTo(g,lib.bus,[5.5,0,-8],Math.PI/2,.32);
  bus.visible=true;
}

function buildTheme(theme,lib,M){
  const g=new THREE.Group();
  if(['beach','rooftop','parking'].includes(theme))makeOpenShell(g,M,theme);
  else makeInteriorShell(g,M,theme);

  if(theme==='apartment'||theme==='party'){
    cloneTo(g,lib.table,[-1.6,0,-.65],0,.78);
    cloneTo(g,lib.fridge,[3.05,0,-1.45],Math.PI,.92);
    cloneTo(g,lib.shelf,[3.15,0,.95],-Math.PI/2,.92);
    addSofa(g,M,[1.35,0,.85]);
    addPlant(g,M,[-3.45,0,-1.65]);
    const rug=new THREE.Mesh(new THREE.PlaneGeometry(3.1,2.2),new THREE.MeshStandardMaterial({color:0xc7b29c,roughness:1}));
    rug.rotation.x=-Math.PI/2;rug.position.set(.65,.012,.9);g.add(rug);
    if(theme==='party'){
      addBalloons(g,M);
      addText(g,'HAPPY BIRTHDAY',[0,2.73,-2.91],.80);
      // Party table dressing.
      for(let i=0;i<5;i++)addCylinder(g,.055,.055,.18,[-2.25+i*.28,.88,-.58],[M.coral,M.yellow,M.blue][i%3],10);
    }
  }else if(theme==='office'){
    for(const x of[-2.25,0,2.25]){
      cloneTo(g,lib.desk,[x,0,-.45],0,.84);
      cloneTo(g,lib.officeChair,[x,0,.38],Math.PI,.86);
      addBox(g,[.58,.38,.05],[x,.98,-.72],M.dark);
      addBox(g,[.07,.28,.07],[x,.78,-.72],M.metal);
    }
    cloneTo(g,lib.shelf,[3.28,0,-2.05],-Math.PI/2,.9);
    addPlant(g,M,[-3.45,0,-1.85]);
    addText(g,'MEETING',[0,2.62,-2.91],.44,'#162a46','#f5f7fb');
  }else if(theme==='restaurant'||theme==='kitchen'){
    cloneTo(g,lib.restaurantTable,[-1.85,0,.25],0,.93);
    cloneTo(g,lib.restaurantTable,[1.75,0,.35],0,.93);
    cloneTo(g,lib.fridge,[3.05,0,-1.70],Math.PI,.88);
    addBox(g,[4.2,.74,.82],[0,.37,-2.12],M.metal);
    addBox(g,[2.2,.10,.62],[0,.93,-2.12],M.wood);
    for(let i=0;i<6;i++)addCylinder(g,.08,.08,.10,[-1.7+i*.68,.82,-2.02],[M.white,M.yellow,M.coral][i%3],10);
    if(theme==='restaurant')addPlant(g,M,[-3.35,0,-1.75]);
  }else if(theme==='bathroom'){
    for(let x=-2.8;x<=.9;x+=1.25){
      addBox(g,[.07,2.15,1.58],[x,1.075,-1.36],M.tile);
      addBox(g,[1.06,2.02,.08],[x+.52,1.01,-2.08],M.tile);
    }
    addBox(g,[1.36,.76,.56],[2.72,.38,.18],M.white);
    addCylinder(g,.20,.15,.22,[2.72,.80,.18],M.metal,18);
    const mirror=new THREE.Mesh(new THREE.PlaneGeometry(1.0,.78),M.glass);mirror.position.set(2.72,1.65,-2.94);g.add(mirror);
  }else if(theme==='laundromat'){
    for(let x=-2.8;x<=2.8;x+=1.12){
      addBox(g,[.94,1.16,.76],[x,.58,-1.68],M.white);
      const ring=new THREE.Mesh(new THREE.TorusGeometry(.29,.045,10,28),M.dark);ring.position.set(x,.60,-1.285);g.add(ring);
      const glass=new THREE.Mesh(new THREE.CircleGeometry(.245,24),M.glass);glass.position.set(x,.60,-1.275);g.add(glass);
    }
    addBox(g,[2.7,.42,.66],[0,.42,.75],M.wood);
    addBox(g,[1.0,.42,.66],[2.7,.42,.75],M.blue);
  }else if(theme==='parking'){
    for(const x of[-3,-1,1,3])addBox(g,[.34,3.0,.34],[x,1.5,-1.3],M.concrete);
    for(const x of[-2.5,0,2.5])addBox(g,[.10,.012,4.8],[x,.02,-.1],M.yellow,false);
    addBox(g,[9,.15,.2],[0,3.25,-3.3],M.dark,false);
  }else if(theme==='rooftop'){
    addCityBackground(g,M);
    addBox(g,[1.45,.72,1.15],[-2.25,.36,-1.4],M.metal);
    addBox(g,[1.0,.52,.8],[1.6,.26,-1.8],M.metal);
  }else if(theme==='beach'){
    cloneTo(g,lib.umbrella,[2.2,0,-1.45],0,.82);
    addBox(g,[2.0,.12,.55],[-1.8,.40,-.7],M.wood);
    addBox(g,[.12,.65,.12],[-2.5,.32,-.7],M.wood);
    addBox(g,[.12,.65,.12],[-1.1,.32,-.7],M.wood);
  }else if(theme==='bus'){
    addBusInterior(g,M,lib);
  }else if(theme==='convenience'){
    for(const x of[-2.6,0,2.6]){
      addBox(g,[1.35,1.88,.50],[x,.94,-1.56],M.white);
      for(let y=.42;y<1.72;y+=.40){
        addBox(g,[1.24,.05,.62],[x,y,-1.56],M.dark);
        for(let j=0;j<4;j++)addBox(g,[.18,.18,.18],[x-.43+j*.29,y+.13,-1.22],[M.coral,M.yellow,M.blue,M.green][j%4]);
      }
    }
    addBox(g,[2.4,.86,.72],[0,.43,1.25],M.wood);
  }else if(theme==='hotel'){
    const carpet=new THREE.Mesh(new THREE.PlaneGeometry(7.8,7.8),new THREE.MeshStandardMaterial({color:0x8e514a,roughness:1}));
    carpet.rotation.x=-Math.PI/2;carpet.position.y=.012;g.add(carpet);
    for(const x of[-2.95,-1.48,1.48,2.95]){
      addBox(g,[.92,2.18,.12],[x,1.09,-2.90],M.wood);
      addCylinder(g,.035,.035,.05,[x+.27,1.08,-2.81],M.metal,10);
    }
    for(const x of[-3.1,3.1])addSphere(g,.13,[x,2.25,-2.88],M.yellow,12);
  }else if(theme==='stairwell'){
    for(let i=0;i<10;i++)addBox(g,[2.9,.18,.52],[1.15,i*.18,-2.30+i*.44],M.concrete);
    addBox(g,[.08,2.0,4.2],[-1.85,1.0,-.35],M.metal);
    addBox(g,[.08,.08,4.2],[-1.52,1.15,-.35],M.metal);
  }
  return g;
}

export function makeDoor(parent,M,pos=[0,0,-2.92],scale=1){
  const g=new THREE.Group();g.position.set(...pos);g.scale.setScalar(scale);parent.add(g);
  addBox(g,[.18,2.86,.20],[-1.14,1.43,0],M.dark);
  addBox(g,[.18,2.86,.20],[1.14,1.43,0],M.dark);
  addBox(g,[2.46,.18,.20],[0,2.81,0],M.dark);
  const pivot=new THREE.Group();pivot.position.set(-1.03,0,.01);g.add(pivot);
  addBox(pivot,[2.06,2.64,.12],[1.03,1.32,0],M.wood);
  const knob=addCylinder(pivot,.045,.045,.08,[1.79,1.30,.09],M.metal,12);knob.rotation.x=Math.PI/2;
  return{group:g,pivot,setOpen(p){pivot.rotation.y=-1.49*clamp01(p);}};
}

export class Stage{
  constructor(scene,lib){
    this.scene=scene;this.M=materials();
    this.sourceRoot=new THREE.Group();this.destRoot=new THREE.Group();
    scene.add(this.sourceRoot,this.destRoot);
    this.source={};this.dest={};
    const themes=['apartment','party','office','restaurant','kitchen','bathroom','laundromat','parking','rooftop','beach','bus','convenience','hotel','stairwell'];
    for(const t of themes){
      const a=buildTheme(t,lib,this.M);a.visible=false;this.sourceRoot.add(a);this.source[t]=a;
      const b=buildTheme(t,lib,this.M);b.position.z=-3.48;b.visible=false;this.destRoot.add(b);this.dest[t]=b;
    }
    this.door=makeDoor(scene,this.M);
  }
  showSource(n){for(const[k,g]of Object.entries(this.source))g.visible=k===n;}
  showDest(n){for(const[k,g]of Object.entries(this.dest))g.visible=k===n;}
}

export function makeCake(scene,M){
  const g=new THREE.Group();scene.add(g);
  const cream=new THREE.MeshStandardMaterial({color:0xf8e3d2,roughness:.78});
  const icing=new THREE.MeshStandardMaterial({color:0xffb8c8,roughness:.72});
  addCylinder(g,.62,.62,.30,[0,.15,0],cream,24);
  addCylinder(g,.48,.48,.29,[0,.44,0],cream,24);
  addCylinder(g,.33,.33,.28,[0,.72,0],cream,24);
  addCylinder(g,.64,.64,.055,[0,.31,0],icing,24);
  addCylinder(g,.50,.50,.055,[0,.59,0],icing,24);
  addCylinder(g,.35,.35,.055,[0,.87,0],icing,24);
  for(let i=0;i<5;i++){
    const candle=addCylinder(g,.018,.018,.21,[-.20+i*.10,1.02,0],[M.coral,M.yellow,M.blue][i%3],8);
    candle.rotation.z=(i-2)*.025;
  }
  g.scale.setScalar(.78);g.visible=false;return g;
}
export function setCakeState(cake,state){
  cake.rotation.z=[0,.025,.055,.09,.125][state]||0;
  if(cake.children[2])cake.children[2].position.x=state>=3?.035:0;
}
export function makeDonut(scene){
  const g=new THREE.Group();
  const d=new THREE.Mesh(new THREE.TorusGeometry(.16,.075,10,24),new THREE.MeshStandardMaterial({color:0xb97445,roughness:.78}));
  d.rotation.x=Math.PI/2;d.castShadow=true;g.add(d);scene.add(g);g.visible=false;return g;
}
