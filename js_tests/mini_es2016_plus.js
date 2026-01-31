// ES2016+ Minimal Test - features from ES2016 through ES2024
function(c,a){
var r=[];
// ES2016: Exponentiation
try{if(2**3===8)r.push("exp:OK");else r.push("exp:FAIL")}catch(e){r.push("exp:ERR")}
// ES2016: Array.includes
try{if([1,2].includes(2))r.push("arr_inc:OK");else r.push("arr_inc:FAIL")}catch(e){r.push("arr_inc:ERR")}
// ES2017: Object.values
try{var v=Object.values({a:1,b:2});if(v.length===2)r.push("values:OK");else r.push("values:FAIL")}catch(e){r.push("values:ERR")}
// ES2017: Object.entries
try{var e=Object.entries({a:1});if(e[0][0]==="a")r.push("entries:OK");else r.push("entries:FAIL")}catch(e){r.push("entries:ERR")}
// ES2017: padStart/padEnd
try{if("5".padStart(3,"0")==="005")r.push("padStart:OK");else r.push("padStart:FAIL")}catch(e){r.push("padStart:ERR")}
// ES2017: async/await
try{async function f(){return 1};r.push("async:OK")}catch(e){r.push("async:ERR")}
// ES2018: Object spread
try{var o={...{a:1}};if(o.a===1)r.push("obj_spread:OK");else r.push("obj_spread:FAIL")}catch(e){r.push("obj_spread:ERR")}
// ES2019: Array.flat
try{if([[1],[2]].flat().length===2)r.push("flat:OK");else r.push("flat:FAIL")}catch(e){r.push("flat:ERR")}
// ES2019: Object.fromEntries
try{var o=Object.fromEntries([["a",1]]);if(o.a===1)r.push("fromEntries:OK");else r.push("fromEntries:FAIL")}catch(e){r.push("fromEntries:ERR")}
// ES2020: Optional chaining
try{var o={a:{b:1}};if(o?.a?.b===1)r.push("opt_chain:OK");else r.push("opt_chain:FAIL")}catch(e){r.push("opt_chain:ERR")}
// ES2020: Nullish coalescing
try{var x=null??5;if(x===5)r.push("nullish:OK");else r.push("nullish:FAIL")}catch(e){r.push("nullish:ERR")}
// ES2020: BigInt
try{var b=BigInt(123);if(typeof b==="bigint")r.push("BigInt:OK");else r.push("BigInt:FAIL")}catch(e){r.push("BigInt:ERR")}
// ES2020: globalThis
try{if(typeof globalThis==="object")r.push("globalThis:OK");else r.push("globalThis:FAIL")}catch(e){r.push("globalThis:ERR")}
// ES2021: replaceAll
try{if("a-a".replaceAll("-","_")==="a_a")r.push("replaceAll:OK");else r.push("replaceAll:FAIL")}catch(e){r.push("replaceAll:ERR")}
// ES2021: Logical assignment
try{var x=null;x??=5;if(x===5)r.push("??=:OK");else r.push("??=:FAIL")}catch(e){r.push("??=:ERR")}
// ES2022: at()
try{if([1,2,3].at(-1)===3)r.push("at:OK");else r.push("at:FAIL")}catch(e){r.push("at:ERR")}
// ES2022: Object.hasOwn
try{if(Object.hasOwn({a:1},"a"))r.push("hasOwn:OK");else r.push("hasOwn:FAIL")}catch(e){r.push("hasOwn:ERR")}
// ES2023: findLast
try{if([1,2,3].findLast(x=>x>1)===3)r.push("findLast:OK");else r.push("findLast:FAIL")}catch(e){r.push("findLast:ERR")}
// ES2023: toSorted
try{var s=[3,1,2].toSorted();if(s[0]===1)r.push("toSorted:OK");else r.push("toSorted:FAIL")}catch(e){r.push("toSorted:ERR")}
return "ES2016+: "+r.join(" | ")
}
