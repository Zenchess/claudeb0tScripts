// ES6 Minimal Test - features added in ES6/ES2015
function(c,a){
var r=[];
// let/const
try{let x=1;r.push("let:OK")}catch(e){r.push("let:ERR")}
try{const y=1;r.push("const:OK")}catch(e){r.push("const:ERR")}
// Arrow functions
try{var f=(x)=>x*2;if(f(3)===6)r.push("arrow:OK");else r.push("arrow:FAIL")}catch(e){r.push("arrow:ERR")}
// Template literals
try{var s=`hi`;if(s==="hi")r.push("template:OK");else r.push("template:FAIL")}catch(e){r.push("template:ERR")}
try{var n=5;var t=`n=${n}`;if(t==="n=5")r.push("template_expr:OK");else r.push("template_expr:FAIL")}catch(e){r.push("template_expr:ERR")}
// Destructuring
try{var{a}={a:1};if(a===1)r.push("destruct_obj:OK");else r.push("destruct_obj:FAIL")}catch(e){r.push("destruct_obj:ERR")}
try{var[x]=["hi"];if(x==="hi")r.push("destruct_arr:OK");else r.push("destruct_arr:FAIL")}catch(e){r.push("destruct_arr:ERR")}
// Spread
try{var arr=[...[1,2]];if(arr.length===2)r.push("spread:OK");else r.push("spread:FAIL")}catch(e){r.push("spread:ERR")}
// Rest
try{var f=(...args)=>args.length;if(f(1,2,3)===3)r.push("rest:OK");else r.push("rest:FAIL")}catch(e){r.push("rest:ERR")}
// Default params
try{var f=(x=5)=>x;if(f()===5)r.push("default:OK");else r.push("default:FAIL")}catch(e){r.push("default:ERR")}
// Classes
try{class C{constructor(x){this.x=x}};var c=new C(1);if(c.x===1)r.push("class:OK");else r.push("class:FAIL")}catch(e){r.push("class:ERR")}
// Symbol
try{var s=Symbol("x");if(typeof s==="symbol")r.push("symbol:OK");else r.push("symbol:FAIL")}catch(e){r.push("symbol:ERR")}
// Map
try{var m=new Map();m.set("a",1);if(m.get("a")===1)r.push("Map:OK");else r.push("Map:FAIL")}catch(e){r.push("Map:ERR")}
// Set
try{var s=new Set([1,1,2]);if(s.size===2)r.push("Set:OK");else r.push("Set:FAIL")}catch(e){r.push("Set:ERR")}
// Promise
try{var p=new Promise((r)=>r(1));r.push("Promise:OK")}catch(e){r.push("Promise:ERR")}
// for-of
try{var s="";for(var x of[1,2])s+=x;if(s==="12")r.push("for_of:OK");else r.push("for_of:FAIL")}catch(e){r.push("for_of:ERR")}
// Array.from
try{if(Array.from("ab").length===2)r.push("Array.from:OK");else r.push("Array.from:FAIL")}catch(e){r.push("Array.from:ERR")}
// String includes
try{if("hello".includes("ll"))r.push("str_includes:OK");else r.push("str_includes:FAIL")}catch(e){r.push("str_includes:ERR")}
return "ES6: "+r.join(" | ")
}
