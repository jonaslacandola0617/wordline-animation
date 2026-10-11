import * as THREE from 'three';
import {idlePose,walkPose,carryPose,gesturePose} from './assets.js';
import {smooth,lerp,setCakeState} from './stage.js';

export const DURATIONS={'01':25,'02':20,'03':35,'04':30,'05':25,'06':30,'07':15,'08':35,'09':23,'10':20,'11':10};

const place=(r,x,z,ry=0,y=0)=>{r.root.position.set(x,y,z);r.root.rotation.y=ry;};
const cam=(c,p,t=[0,1.35,-1])=>{c.camera.position.set(...p);c.camera.lookAt(new THREE.Vector3(...t));};
function face(r,x,z){r.root.rotation.y=Math.atan2(x-r.root.position.x,z-r.root.position.z);}
function vis(c,roles){for(const[k,r]of Object.entries(c.chars))r.root.visible=roles.includes(k);}
function base(c,s,d,roles=['A']){
  c.stage.showSource(s);c.stage.showDest(d);vis(c,roles);
  c.donut.visible=false;c.coffee.visible=false;c.cake.visible=false;c.wave.visible=false;
}
const door=(c,p)=>c.stage.door.setOpen(p);

function carry(c,state=0){
  c.cake.visible=true;
  setCakeState(c.cake,state);
  const a=c.chars.A;
  carryPose(a,c.t);
  c.cake.position.set(a.root.position.x,a.root.position.y+.79,a.root.position.z-.43);
  c.cake.rotation.y=a.root.rotation.y;
  c.cake.rotation.z=[0,.025,.055,.09,.125][state]||0;
}
function idle(r,t,p=0){idlePose(r,t,p);}
function coffeeAt(c,r){c.coffee.visible=true;c.coffee.position.set(r.root.position.x+.30,1.08,r.root.position.z-.12);}
function push(c,t,a,b,p0,p1,target=[0,1.35,-1]){
  const q=smooth(a,b,t);
  cam(c,[lerp(p0[0],p1[0],q),lerp(p0[1],p1[1],q),lerp(p0[2],p1[2],q)],target);
}

function scene01(c,t){
  base(c,'apartment','bus',['A','E1']);
  c.cake.visible=true;c.cake.position.set(-1.65,.83,-.65);setCakeState(c.cake,0);
  place(c.chars.A,-1.25,.42);face(c.chars.A,0,-2.9);idle(c.chars.A,t);
  place(c.chars.E1,.35,-5.0,0);idle(c.chars.E1,t);

  if(t<4){
    c.stage.showDest('bus');door(c,smooth(.55,1.10,t)*(1-smooth(3.20,3.75,t)));
    cam(c,[2.35,1.72,3.85],[0,1.35,-2.35]);
  }else if(t<8){
    c.stage.showDest('kitchen');door(c,smooth(4.18,4.62,t)*(1-smooth(7.15,7.68,t)));
    cam(c,[-2.25,1.68,3.55],[0,1.32,-2.38]);
  }else if(t<12){
    c.stage.showDest('rooftop');door(c,smooth(8.15,8.56,t)*(1-smooth(11.22,11.72,t)));
    cam(c,[2.20,1.64,3.48],[0,1.35,-2.4]);
  }else{
    door(c,0);vis(c,['A']);
    if(t<17){
      face(c.chars.A,-1.65,-.65);
      cam(c,[2.15,1.65,3.15],[-1.25,1.05,-.35]);
    }else{
      face(c.chars.A,0,-2.9);
      push(c,t,17,25,[1.9,1.60,3.0],[1.38,1.52,2.55],[-1.35,1.0,-.55]);
    }
  }
}

function scene02(c,t){
  base(c,'apartment','beach',['A','B']);
  place(c.chars.A,-1.45,.38);face(c.chars.A,0,-2.9);carry(c,0);
  const f=smooth(.45,1.25,t);
  place(c.chars.B,.28,lerp(-3.8,-.18,f),0);
  walkPose(c.chars.B,t,7.2);
  door(c,smooth(.12,.34,t)*(1-smooth(4.30,5.25,t)));

  if(t<5.4){
    cam(c,[2.45,1.72,3.75],[-.05,1.30,-1.65]);
  }else{
    place(c.chars.B,.30,-.12);
    face(c.chars.A,c.chars.B.root.position.x,c.chars.B.root.position.z);
    face(c.chars.B,c.chars.A.root.position.x,c.chars.A.root.position.z);
    idle(c.chars.B,t,.8);
    if(t>10.8)gesturePose(c.chars.B,'R',.85);
    cam(c,[.15,1.68,3.35],[-.52,1.25,.05]);
  }
}

function scene03(c,t){
  base(c,'apartment','bathroom',['A','B','E1']);
  place(c.chars.A,-1.35,.42);place(c.chars.B,.58,.50);face(c.chars.A,0,-2.9);face(c.chars.B,0,-2.9);
  carry(c,0);idle(c.chars.B,t,.6);

  if(t<9){
    c.stage.showDest('bathroom');
    door(c,smooth(.45,.95,t)*(1-smooth(7.55,8.28,t)));
    place(c.chars.E1,.58,-5.0,0);idle(c.chars.E1,t);
    cam(c,[2.28,1.67,3.60],[0,1.28,-2.25]);
  }else if(t<20){
    c.stage.showDest('office');
    door(c,smooth(9.25,9.80,t)*(1-smooth(18.55,19.28,t)));
    c.donut.visible=true;c.donut.position.set(.55,.84,-4.50);
    cam(c,[-2.20,1.68,3.50],[0,1.28,-2.25]);
    if(t>13&&c.chars.B.head)c.chars.B.head.rotation.y=-.35;
  }else if(t<29){
    c.stage.showDest('parking');
    door(c,smooth(20.20,20.75,t)*(1-smooth(27.75,28.55,t)));
    const p=smooth(23.0,27.6,t);
    place(c.chars.A,lerp(-1.35,-.35,p),lerp(.42,-2.05,p));face(c.chars.A,0,-3.5);carry(c,1);
    place(c.chars.B,lerp(.58,.40,p),lerp(.50,-1.65,p));face(c.chars.B,0,-3.5);walkPose(c.chars.B,t,6.2);
    cam(c,[2.0,1.65,3.25],[0,1.25,-1.85]);
  }else{
    c.stage.showSource('parking');c.stage.showDest('laundromat');
    place(c.chars.A,-.95,.10);place(c.chars.B,.65,.18);face(c.chars.A,0,-2.9);face(c.chars.B,0,-2.9);carry(c,1);idle(c.chars.B,t);
    door(c,smooth(29.35,29.95,t));
    cam(c,[2.05,1.68,3.35],[0,1.25,-2.15]);
  }
}

function scene04(c,t){
  const beats=[
    [0,6,'parking','kitchen',1],
    [6,12,'kitchen','office',1],
    [12,18,'office','bus',2],
    [18,24,'bus','rooftop',2],
    [24,30,'rooftop','beach',2]
  ];
  const idx=Math.min(beats.length-1,Math.floor(t/6));
  const b=beats[idx],l=t-b[0];
  base(c,b[2],b[3],['A','B','E1']);
  door(c,smooth(.15,.52,l)*(1-smooth(5.22,5.76,l)));
  place(c.chars.A,-1.15,.32);place(c.chars.B,.65,.38);face(c.chars.A,0,-2.9);face(c.chars.B,0,-2.9);
  carry(c,b[4]);idle(c.chars.B,t,idx*.7);
  place(c.chars.E1,.12,-4.95,0);idle(c.chars.E1,t);
  if(b[3]==='rooftop')c.cake.rotation.z=.10*Math.sin(l*3.2);
  if(b[3]==='beach'&&c.chars.B.head)c.chars.B.head.rotation.z=.12;
  const side=idx%2===0?1:-1;
  cam(c,[side*2.18,1.68,3.48],[0,1.28,-2.15]);
}

function scene05(c,t){
  base(c,'office','convenience',['A','B','C']);
  door(c,1);
  place(c.chars.A,-1.45,.42);place(c.chars.B,.40,.45);place(c.chars.C,1.55,.12);
  face(c.chars.A,c.chars.C.root.position.x,c.chars.C.root.position.z);
  face(c.chars.B,c.chars.C.root.position.x,c.chars.C.root.position.z);
  face(c.chars.C,-.45,.42);
  carry(c,2);idle(c.chars.B,t,.7);idle(c.chars.C,t,1.3);coffeeAt(c,c.chars.C);

  if(t<9){
    if(t>6.5)gesturePose(c.chars.C,'L',.38);
    cam(c,[2.35,1.70,3.45],[.25,1.28,.05]);
  }else if(t<16){
    cam(c,[-2.20,1.68,3.25],[-.45,1.28,.15]);
  }else{
    c.donut.visible=true;c.donut.position.set(c.chars.B.root.position.x+.16,1.00,c.chars.B.root.position.z-.12);
    gesturePose(c.chars.B,'R',.12);
    cam(c,[1.40,1.62,2.55],[.35,1.20,.25]);
  }
}

function scene06(c,t){
  // Show the chain as four readable stable links rather than three freestanding portal props.
  const beats=[
    [0,7.5,'office','convenience'],
    [7.5,15,'convenience','hotel'],
    [15,22.5,'hotel','parking'],
    [22.5,30,'parking','stairwell']
  ];
  const b=beats.find(x=>t>=x[0]&&t<x[1])||beats.at(-1);
  const l=t-b[0];
  base(c,b[2],b[3],['A','B','C']);
  door(c,1);
  place(c.chars.A,-1.25,.34);place(c.chars.B,.50,.40);place(c.chars.C,1.55,.20);
  face(c.chars.A,0,-2.9);face(c.chars.B,0,-2.9);face(c.chars.C,0,-2.9);
  carry(c,2);idle(c.chars.B,t);idle(c.chars.C,t,.9);

  const p=smooth(1.1,5.8,l);
  c.chars.A.root.position.z=lerp(.34,-1.65,p);
  carry(c,2);
  if(t>20.0&&t<23.0)gesturePose(c.chars.A,'R',.60);

  const side=(Math.floor(t/7.5)%2===0)?2.15:-2.15;
  cam(c,[side,1.70,3.38],[0,1.28,-2.05]);
}

function scene07(c,t){
  base(c,'hotel','parking',['A','B','C']);
  door(c,1);
  place(c.chars.A,-1.65,.30);place(c.chars.B,.02,.25);place(c.chars.C,1.50,.22);
  face(c.chars.A,0,-2.9);face(c.chars.B,0,-2.9);face(c.chars.C,0,-2.9);
  carry(c,2);idle(c.chars.B,t);idle(c.chars.C,t,.8);

  c.donut.visible=true;
  const p=smooth(1,5,t);
  c.donut.position.set(lerp(.42,1.18,p),.13,lerp(.18,1.25,p));
  c.donut.rotation.z=t*2.2;

  if(t>4){
    c.chars.B.root.position.x=lerp(.02,.82,smooth(4,6,t));
    c.chars.B.root.position.z=lerp(.25,.92,smooth(4,6,t));
    gesturePose(c.chars.B,'R',.85);
  }
  door(c,1-smooth(5.25,7.05,t));

  if(t<7.4){
    cam(c,[1.48,1.34,2.65],[.55,.55,.20]);
  }else{
    face(c.chars.A,c.chars.B.root.position.x,c.chars.B.root.position.z);
    face(c.chars.B,c.chars.A.root.position.x,c.chars.A.root.position.z);
    cam(c,[-1.95,1.62,2.80],[-.25,1.18,.28]);
  }
}

function scene08(c,t){
  const beats=[
    [0,6,'hotel','bathroom'],
    [6,12,'bathroom','bus'],
    [12,18,'bus','beach'],
    [18,24,'beach','office'],
    [24,29,'office','rooftop'],
    [29,35,'rooftop','stairwell']
  ];
  const idx=beats.findIndex(x=>t>=x[0]&&t<x[1]);
  const b=idx>=0?beats[idx]:beats.at(-1),l=t-b[0];
  base(c,b[2],b[3],['A','B','E1']);
  door(c,smooth(.12,.42,l)*(1-smooth((b[1]-b[0])-1,(b[1]-b[0])-.3,l)));
  place(c.chars.A,-1.18,.22);place(c.chars.B,.62,.28);face(c.chars.A,0,-2.9);face(c.chars.B,0,-2.9);
  carry(c,3);idle(c.chars.B,t,idx*.5);
  place(c.chars.E1,0,-4.85,0);idle(c.chars.E1,t);

  if(b[3]==='beach'&&c.chars.B.head)c.chars.B.head.rotation.z=.14;
  if(b[3]==='office'&&l>2){
    c.donut.visible=true;c.donut.position.set(.60,.83,-4.30);
    if(c.chars.B.head)c.chars.B.head.rotation.y=-.45;
  }
  if(b[3]==='stairwell'&&l>2)gesturePose(c.chars.A,'R',.82);

  const side=idx%2===0?2.15:-2.15;
  cam(c,[side,1.68,3.42],[0,1.25,-2.08]);
}

function scene09(c,t){
  base(c,'hotel','laundromat',['A','B']);
  place(c.chars.A,-1.28,.28);place(c.chars.B,.58,.32);face(c.chars.A,0,-2.9);face(c.chars.B,0,-2.9);
  carry(c,4);idle(c.chars.B,t);

  if(t<5){
    c.stage.showDest('laundromat');door(c,smooth(.30,.72,t)*(1-smooth(4.10,4.70,t)));
  }else if(t<9){
    c.stage.showDest('restaurant');door(c,smooth(5.20,5.62,t)*(1-smooth(8.18,8.72,t)));
  }else if(t<13){
    c.stage.showDest('parking');door(c,smooth(9.20,9.62,t)*(1-smooth(12.28,12.82,t)));
  }else{
    door(c,0);
  }

  if(t<13){
    cam(c,[2.15,1.68,3.40],[0,1.26,-2.12]);
  }else if(t<15.0){
    cam(c,[-1.75,1.58,2.65],[-.45,1.22,.15]);
  }else{
    vis(c,t>18.6?['A','B','C','D']:['A','B','D']);
    c.stage.showDest('party');
    door(c,smooth(15.0,15.45,t));
    place(c.chars.D,.18,-4.60,0);face(c.chars.D,-.4,.3);idle(c.chars.D,t,.4);
    if(t>18.6){
      place(c.chars.C,1.50,-4.85,0);walkPose(c.chars.C,t,4.2);coffeeAt(c,c.chars.C);
    }
    cam(c,[1.65,1.62,2.65],[0,1.30,-3.20]);
  }
}

function scene10(c,t){
  base(c,'party','apartment',['A','B','C','D']);
  door(c,0);
  place(c.chars.A,-1.42,.30);place(c.chars.B,.62,.32);place(c.chars.C,1.68,.08);place(c.chars.D,-.15,-.30);
  face(c.chars.A,-1.65,-.65);face(c.chars.B,-1.65,-.65);face(c.chars.C,-1.65,-.65);face(c.chars.D,-1.65,-.65);
  idle(c.chars.B,t,.4);idle(c.chars.C,t,.8);idle(c.chars.D,t,1.1);coffeeAt(c,c.chars.C);

  if(t<4.2){
    carry(c,4);
  }else{
    c.cake.visible=true;setCakeState(c.cake,4);c.cake.position.set(-1.65,.84,-.65);c.cake.rotation.y=0;
    idle(c.chars.A,t,1.4);
  }

  if(t<6.5){
    cam(c,[2.10,1.62,3.10],[-1.05,1.0,-.30]);
  }else if(t<12.2){
    cam(c,[-2.10,1.58,2.65],[-.75,1.12,-.40]);
  }else{
    // B eyes the cupboard; A catches it without turning the scene into a huge reaction.
    face(c.chars.B,3.0,-1.45);
    if(t>13.0)gesturePose(c.chars.B,'R',.20);
    face(c.chars.A,c.chars.B.root.position.x,c.chars.B.root.position.z);
    cam(c,[1.35,1.55,2.60],[.05,1.15,.18]);
  }
}

function scene11(c,t){
  base(c,'party','beach',['A','D']);

  if(t<6.7){
    place(c.chars.A,-1.35,.35);place(c.chars.D,.18,.22);
    face(c.chars.A,0,-2.9);face(c.chars.D,0,-2.9);
  }else{
    place(c.chars.A,-1.20,.38,Math.PI/2);
    place(c.chars.D,.22,.25,-Math.PI/2);
  }
  idle(c.chars.A,t,.3);idle(c.chars.D,t,.9);

  door(c,smooth(.80,1.38,t)*(1-smooth(6.0,6.68,t)));

  if(t>2.0&&t<6.35){
    c.wave.visible=true;
    const p=smooth(2.0,6.20,t);
    c.wave.position.z=lerp(-5.2,-4.25,p);
    c.wave.scale.y=lerp(1,1.08,p);
  }

  if(t<1.8){
    cam(c,[2.20,1.62,3.55],[-.15,1.25,-1.85]);
  }else if(t<6.75){
    // Over-the-shoulder reveal: the room itself masks the wave outside the doorway.
    cam(c,[.72,1.58,2.00],[0,1.52,-7.0]);
  }else{
    cam(c,[.10,1.55,3.10],[-.48,1.20,.25]);
  }
}

export function buildStory(id,c){
  const fn={'01':scene01,'02':scene02,'03':scene03,'04':scene04,'05':scene05,'06':scene06,'07':scene07,'08':scene08,'09':scene09,'10':scene10,'11':scene11}[id];
  if(!fn)throw new Error('Unknown scene '+id);
  return t=>{
    c.t=t;
    c.stage.door.group.visible=true;
    for(const d of c.chainDoors)d.group.visible=false;
    fn(c,t);
  };
}
