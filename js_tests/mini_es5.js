// ES5 Minimal Test - features added in ES5 (2009)
function(c,a){
var r=[];
// JSON
try{var j=JSON.stringify({a:1});if(j==='{"a":1}')r.push("JSON.stringify:OK");else r.push("JSON.stringify:"+j)}catch(e){r.push("JSON.stringify:ERR")}
try{var o=JSON.parse('{"a":1}');if(o.a===1)r.push("JSON.parse:OK");else r.push("JSON.parse:FAIL")}catch(e){r.push("JSON.parse:ERR")}
// Array.isArray
try{if(Array.isArray([]))r.push("isArray:OK");else r.push("isArray:FAIL")}catch(e){r.push("isArray:ERR")}
// Array forEach
try{var s=0;[1,2].forEach(function(x){s+=x});if(s===3)r.push("forEach:OK");else r.push("forEach:FAIL")}catch(e){r.push("forEach:ERR")}
// Array map
try{var m=[1,2].map(function(x){return x*2});if(m[1]===4)r.push("map:OK");else r.push("map:FAIL")}catch(e){r.push("map:ERR")}
// Array filter
try{var f=[1,2,3].filter(function(x){return x>1});if(f.length===2)r.push("filter:OK");else r.push("filter:FAIL")}catch(e){r.push("filter:ERR")}
// Array reduce
try{var s=[1,2,3].reduce(function(a,b){return a+b},0);if(s===6)r.push("reduce:OK");else r.push("reduce:FAIL")}catch(e){r.push("reduce:ERR")}
// Array indexOf
try{if([1,2,3].indexOf(2)===1)r.push("indexOf:OK");else r.push("indexOf:FAIL")}catch(e){r.push("indexOf:ERR")}
// Array some/every
try{if([1,2].some(function(x){return x>1}))r.push("some:OK");else r.push("some:FAIL")}catch(e){r.push("some:ERR")}
try{if([2,3].every(function(x){return x>1}))r.push("every:OK");else r.push("every:FAIL")}catch(e){r.push("every:ERR")}
// Object.keys
try{var k=Object.keys({a:1,b:2});if(k.length===2)r.push("keys:OK");else r.push("keys:FAIL")}catch(e){r.push("keys:ERR")}
// Function.bind
try{var f=function(){return this.x}.bind({x:42});if(f()===42)r.push("bind:OK");else r.push("bind:FAIL")}catch(e){r.push("bind:ERR")}
// String.trim
try{if("  hi  ".trim()==="hi")r.push("trim:OK");else r.push("trim:FAIL")}catch(e){r.push("trim:ERR")}
// Date.now
try{if(typeof Date.now()==="number")r.push("Date.now:OK");else r.push("Date.now:FAIL")}catch(e){r.push("Date.now:ERR")}
return "ES5: "+r.join(" | ")
}
