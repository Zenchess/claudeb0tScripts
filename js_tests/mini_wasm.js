// WASM Minimal Test
function(c,a){
var r=[];
// WebAssembly object exists
try{if(typeof WebAssembly==="object")r.push("WA_obj:OK");else r.push("WA_obj:FAIL")}catch(e){r.push("WA_obj:ERR")}
// WebAssembly.Module
try{if(typeof WebAssembly.Module==="function")r.push("WA_Module:OK");else r.push("WA_Module:FAIL")}catch(e){r.push("WA_Module:ERR")}
// WebAssembly.Instance
try{if(typeof WebAssembly.Instance==="function")r.push("WA_Instance:OK");else r.push("WA_Instance:FAIL")}catch(e){r.push("WA_Instance:ERR")}
// WebAssembly.Memory
try{var m=new WebAssembly.Memory({initial:1});if(m.buffer.byteLength===65536)r.push("WA_Memory:OK");else r.push("WA_Memory:FAIL")}catch(e){r.push("WA_Memory:ERR")}
// WebAssembly.Table
try{var t=new WebAssembly.Table({initial:1,element:"funcref"});r.push("WA_Table:OK")}catch(e){r.push("WA_Table:ERR")}
// WebAssembly minimal module (empty)
try{
var bytes=new Uint8Array([0,97,115,109,1,0,0,0]);
var m=new WebAssembly.Module(bytes);
r.push("WA_compile:OK")
}catch(e){r.push("WA_compile:ERR-"+e.message.slice(0,30))}
// WebAssembly add function (Kaj's example)
try{
// (module (func (export "add") (param i32 i32) (result i32) local.get 0 local.get 1 i32.add))
var bytes=new Uint8Array([0,97,115,109,1,0,0,0,1,7,1,96,2,127,127,1,127,3,2,1,0,7,7,1,3,97,100,100,0,0,10,9,1,7,0,32,0,32,1,106,11]);
var m=new WebAssembly.Module(bytes);
var i=new WebAssembly.Instance(m);
if(i.exports.add(3,5)===8)r.push("WA_add:OK");else r.push("WA_add:FAIL")
}catch(e){r.push("WA_add:ERR-"+e.message.slice(0,30))}
// Typed Arrays (used with WASM)
try{var a=new Int32Array(4);a[0]=42;if(a[0]===42)r.push("Int32Array:OK");else r.push("Int32Array:FAIL")}catch(e){r.push("Int32Array:ERR")}
try{var a=new Float64Array(2);a[0]=3.14;if(a[0]===3.14)r.push("Float64Array:OK");else r.push("Float64Array:FAIL")}catch(e){r.push("Float64Array:ERR")}
try{var b=new ArrayBuffer(16);var v=new DataView(b);v.setInt32(0,42);if(v.getInt32(0)===42)r.push("DataView:OK");else r.push("DataView:FAIL")}catch(e){r.push("DataView:ERR")}
return "WASM: "+r.join(" | ")
}
