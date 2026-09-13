import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const element = () => ({style:{},classList:{toggle(){},add(){},remove(){}},addEventListener(){},replaceChildren(){}});
const nodes = new Map();
const context = vm.createContext({document:{getElementById(id){if(!nodes.has(id)) nodes.set(id,element()); return nodes.get(id);},createElement:element,querySelectorAll:()=>[]},localStorage:{getItem(){return null;}},setInterval(){},setTimeout(){},clearTimeout(){},URL,AbortController});
vm.runInContext(fs.readFileSync(new URL('../tools/document-converter.js', import.meta.url),'utf8'), context);
function view(task, now=1000) {context.task=task; return vm.runInContext(`progressView(task, ${now})`,context);}
const base={status:'processing',progress:34,message:'识别',telemetry:{pages:1114,page:6,completed_pages:5,stage:'recognizing',started_at:500,stage_started_at:900,heartbeat_at:999,last_completed_at:950}};
assert.equal(view(base).label,'5 / 1114 页');
assert.ok(view(base).percent < 1);
assert.equal(view({status:'processing',progress:34}).percent,null);
assert.equal(view({...base,telemetry:{...base.telemetry,stage:'packaging',completed_pages:1114}}).percent,null);
assert.match(view({...base,telemetry:{...base.telemetry,heartbeat_at:900}}).activity,/运行状态待确认/);
assert.match(view({...base,telemetry:{...base.telemetry,stage_started_at:500}}).activity,/不能仅凭心跳/);
assert.equal(view({...base,status:'completed'}).percent,100);
assert.equal(view({...base,status:'failed'}).label,'已停止');
assert.equal(view({...base,status:'cancelled'}).label,'已停止');
console.log('PASS: 8 real-progress, legacy fallback, packaging, stale-heartbeat and terminal-state assertions');
