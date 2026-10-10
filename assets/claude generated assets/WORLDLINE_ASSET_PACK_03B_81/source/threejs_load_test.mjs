import fs from 'fs';
import path from 'path';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';
import { MTLLoader } from 'three/examples/jsm/loaders/MTLLoader.js';
import * as THREE from 'three';
const root = process.argv[2];
const cat = JSON.parse(fs.readFileSync(path.join(root, 'ASSET_CATALOG.json')));
const out = {};
for (const a of cat.assets) {
  const r = { ok: false };
  try {
    const mtlText = fs.readFileSync(path.join(root, a.mtl), 'utf8');
    const mats = new MTLLoader().parse(mtlText, '');
    mats.preload();
    const loader = new OBJLoader();
    loader.setMaterials(mats);
    const obj = loader.parse(fs.readFileSync(path.join(root, a.file), 'utf8'));
    let meshes = 0, tris = 0, unmatched = 0; const names = [];
    obj.traverse(o => {
      if (o.isMesh) {
        meshes++; names.push(o.name);
        tris += o.geometry.attributes.position.count / 3;
        const ms = Array.isArray(o.material) ? o.material : [o.material];
        for (const m of ms) if (!m || !m.name || !(m.name in mats.materials)) unmatched++;
      }
    });
    const box = new THREE.Box3().setFromObject(obj); const sz = box.getSize(new THREE.Vector3());
    Object.assign(r, { ok: meshes > 0 && unmatched === 0, meshes, tris, unmatched, size: [sz.x, sz.y, sz.z].map(v => +v.toFixed(3)), minY: +box.min.y.toFixed(3) });
  } catch (e) { r.error = String(e); }
  out[a.id] = r;
}
fs.writeFileSync(path.join(root, 'metadata', '_threejs_load_results.json'), JSON.stringify(out, null, 1));
const bad = Object.entries(out).filter(([k, v]) => !v.ok);
console.log('loaded', Object.keys(out).length, 'failures', bad.length, JSON.stringify(bad.slice(0, 5)));
