const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const elems={};function element(){return {value:'',valueAsNumber:0,textContent:'',disabled:false,children:[],handlers:{},addEventListener(n,f){this.handlers[n]=f},replaceChildren(){this.children=[]},append(x){this.children.push(x)},click(){this.clicked=true}}}
const ctx={document:{getElementById(id){return elems[id]??=element()},createElement(){return element()}},window:{print(){}},URL,Blob,setTimeout};
vm.createContext(ctx);vm.runInContext(fs.readFileSync('herramientas.js','utf8'),ctx);
const check=(s,v)=>assert.equal(vm.runInContext(s,ctx),v);
check('bmi(81,180)',25);check('resting(80,180,30,5)',1780);check('resting(60,165,40,-161)',1270.25);
const get=id=>ctx.document.getElementById(id); const submit=id=>get(id).handlers.submit({preventDefault(){}});
get('bmi-weight').valueAsNumber=81;get('bmi-height').valueAsNumber=180;submit('bmi-form');assert.match(get('bmi-result').textContent,/25/);
get('bp-time').value='2026-11-24T10:00';for(const [id,n] of Object.entries({'bp-s1':120,'bp-d1':80,'bp-s2':130,'bp-d2':90}))get(id).valueAsNumber=n;
submit('bp-form');assert.match(get('bp-average').textContent,/125\/85/);assert.equal(get('bp-rows').children.length,1);
get('bp-s1').valueAsNumber=181;submit('bp-form');assert.match(get('bp-alert').textContent,/muy alta/);
get('bp-clear').handlers.click();assert.equal(get('bp-rows').children.length,0);assert.equal(get('bp-export').disabled,true);
console.log('OK: IMC, energy formulas, BP average, high reading and clear');
