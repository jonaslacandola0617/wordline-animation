import * as THREE from 'three';
import {OBJLoader} from '/node_modules/three/examples/jsm/loaders/OBJLoader.js';
import {MTLLoader} from '/node_modules/three/examples/jsm/loaders/MTLLoader.js';

export const BASE46='/assets/claude%20generated%20assets/WORLDLINE_LAB_ASSET_PACK_46/models/humans/';
export const BASE03A='/assets/claude%20generated%20assets/WORLDLINE_ASSET_PACK_03A_80/';
export const BASE03B='/assets/claude%20generated%20assets/WORLDLINE_ASSET_PACK_03B_81/';

export async function loadObjMtl(base,objFile,mtlFile){
  const ml=new MTLLoader();ml.setPath(base);const mats=await ml.loadAsync(mtlFile);mats.preload();
  const ol=new OBJLoader();ol.setPath(base);ol.setMaterials(mats);const obj=await ol.loadAsync(objFile);
  obj.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;const arr=Array.isArray(o.material)?o.material:[o.material];for(const m of arr){if(m?.opacity<1){m.transparent=true;m.depthWrite=false;}}}});
  return obj;
}
export function cloneDeep(obj){
  const c=obj.clone(true);c.traverse(o=>{if(o.isMesh){o.geometry=o.geometry.clone();if(Array.isArray(o.material))o.material=o.material.map(m=>m.clone());else if(o.material)o.material=o.material.clone();}});return c;
}
function findNamed(root,name){let out=null;root.traverse(o=>{if(!out&&o.name===name)out=o;});return out;}
function makeJoint(root,name,nodes,pivot){const found=nodes.map(n=>findNamed(root,n)).filter(Boolean);if(!found.length)return null;root.updateMatrixWorld(true);const g=new THREE.Group();g.name=name;g.position.set(...pivot);root.add(g);g.updateMatrixWorld(true);for(const n of found)g.attach(n);return g;}
const P={
HUMAN_01:{hipL:[.096,.905,0],hipR:[-.096,.905,0],shoulderL:[.21,1.42,0],shoulderR:[-.21,1.42,0],neck:[0,1.55,.02]},
HUMAN_02:{hipL:[.097,.873,0],hipR:[-.097,.873,0],shoulderL:[.190,1.351,0],shoulderR:[-.190,1.351,0],neck:[0,1.48,.02]},
HUMAN_03:{hipL:[.097,.972,0],hipR:[-.097,.972,0],shoulderL:[.255,1.505,0],shoulderR:[-.255,1.505,0],neck:[0,1.66,.02]},
HUMAN_04:{hipL:[.099,.899,0],hipR:[-.099,.899,0],shoulderL:[.195,1.391,0],shoulderR:[-.195,1.391,0],neck:[0,1.52,.02]},
HUMAN_05:{hipL:[.096,.915,0],hipR:[-.096,.915,0],shoulderL:[.22,1.43,0],shoulderR:[-.22,1.43,0],neck:[0,1.56,.02]},
HUMAN_08:{hipL:[.091,.914,0],hipR:[-.091,.914,0],shoulderL:[.214,1.416,0],shoulderR:[-.214,1.416,0],neck:[0,1.55,.02]}
};
export function rigHuman(root,id){const p=P[id]||P.HUMAN_03;return{root,id,
 hipL:makeJoint(root,id+'_hipL',['leg_L','legwear_L','shoe_L'],p.hipL),
 hipR:makeJoint(root,id+'_hipR',['leg_R','legwear_R','shoe_R'],p.hipR),
 shoulderL:makeJoint(root,id+'_shoulderL',['arm_L','sleeve_L','hand_L'],p.shoulderL),
 shoulderR:makeJoint(root,id+'_shoulderR',['arm_R','sleeve_R','hand_R'],p.shoulderR),
 head:makeJoint(root,id+'_head',['head','face','hair','glasses','headwear'],p.neck)
};}
export function resetRig(r){for(const j of [r.hipL,r.hipR,r.shoulderL,r.shoulderR,r.head])if(j)j.rotation.set(0,0,0);}
export function idlePose(r,t,p=0){resetRig(r);if(r.head){r.head.rotation.y=Math.sin(t*.65+p)*.045;r.head.rotation.z=Math.sin(t*.85+p)*.012;}r.root.position.y+=Math.sin(t*1.7+p)*.004;}
export function carryPose(r,t){resetRig(r);if(r.shoulderL){r.shoulderL.rotation.x=-.78;r.shoulderL.rotation.z=.20;}if(r.shoulderR){r.shoulderR.rotation.x=-.78;r.shoulderR.rotation.z=-.20;}if(r.head)r.head.rotation.x=.05+Math.sin(t*.8)*.01;}
export function walkPose(r,t,s=5.4){resetRig(r);const a=Math.sin(t*s);if(r.hipL)r.hipL.rotation.x=.38*a;if(r.hipR)r.hipR.rotation.x=-.38*a;if(r.shoulderL)r.shoulderL.rotation.x=-.28*a;if(r.shoulderR)r.shoulderR.rotation.x=.28*a;}
export function gesturePose(r,side='R',a=.65){const j=side==='R'?r.shoulderR:r.shoulderL;if(j){j.rotation.x=-a;j.rotation.z=side==='R'?-0.35:0.35;}}
export async function loadLibrary(){
 const jobs=[
  loadObjMtl(BASE46,'HUMAN_01.obj','HUMAN_01.mtl'),
  loadObjMtl(BASE46,'HUMAN_02.obj','HUMAN_02.mtl'),
  loadObjMtl(BASE46,'HUMAN_03.obj','HUMAN_03.mtl'),
  loadObjMtl(BASE46,'HUMAN_04.obj','HUMAN_04.mtl'),
  loadObjMtl(BASE46,'HUMAN_05.obj','HUMAN_05.mtl'),
  loadObjMtl(BASE46,'HUMAN_08.obj','HUMAN_08.mtl'),
  loadObjMtl(BASE03A+'land_vehicles/','LAND_01.obj','LAND_01.mtl'),
  loadObjMtl(BASE03B+'interiors/','INTERIOR_04_OfficeDesk.obj','INTERIOR_04_OfficeDesk.mtl'),
  loadObjMtl(BASE03B+'interiors/','INTERIOR_05_OfficeChair.obj','INTERIOR_05_OfficeChair.mtl'),
  loadObjMtl(BASE03B+'interiors/','INTERIOR_06_Shelf.obj','INTERIOR_06_Shelf.mtl'),
  loadObjMtl(BASE03B+'interiors/','INTERIOR_08_Refrigerator.obj','INTERIOR_08_Refrigerator.mtl'),
  loadObjMtl(BASE03B+'interiors/','INTERIOR_02_Table.obj','INTERIOR_02_Table.mtl'),
  loadObjMtl(BASE03B+'interiors/','INTERIOR_11_RestaurantTable.obj','INTERIOR_11_RestaurantTable.mtl'),
  loadObjMtl(BASE03B+'interiors/','INTERIOR_12_OutdoorUmbrella.obj','INTERIOR_12_OutdoorUmbrella.mtl')
 ];
 const v=await Promise.all(jobs);const k=['h01','h02','h03','h04','h05','h08','bus','desk','officeChair','shelf','fridge','table','restaurantTable','umbrella'];return Object.fromEntries(k.map((x,i)=>[x,v[i]]));
}
export function createCharacter(scene,lib,key,id){const root=cloneDeep(lib[key]);scene.add(root);root.visible=false;return rigHuman(root,id);}
