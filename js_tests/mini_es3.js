// ES3 Minimal Test - features added in ES3 (1999)
function(c,a){
var r=[];
// Regex literal
try{var re=/test/i;if(re.test("TEST"))r.push("regex:OK");else r.push("regex:FAIL")}catch(e){r.push("regex:ERR")}
// Regex exec
try{var m=/(\w+)/.exec("hello");if(m[1]==="hello")r.push("regex_exec:OK");else r.push("regex_exec:FAIL")}catch(e){r.push("regex_exec:ERR")}
// instanceof
try{if([]instanceof Array)r.push("instanceof:OK");else r.push("instanceof:FAIL")}catch(e){r.push("instanceof:ERR")}
// Strict equality
try{if(1==="1")r.push("strict_eq:FAIL");else r.push("strict_eq:OK")}catch(e){r.push("strict_eq:ERR")}
// do-while
try{var i=0;do{i++}while(i<1);r.push("do_while:OK")}catch(e){r.push("do_while:ERR")}
// in operator
try{var o={a:1};if("a"in o)r.push("in_op:OK");else r.push("in_op:FAIL")}catch(e){r.push("in_op:ERR")}
// hasOwnProperty
try{var o={x:1};if(o.hasOwnProperty("x"))r.push("hasOwn:OK");else r.push("hasOwn:FAIL")}catch(e){r.push("hasOwn:ERR")}
// Array push/pop
try{var a=[1];a.push(2);if(a.pop()===2)r.push("push_pop:OK");else r.push("push_pop:FAIL")}catch(e){r.push("push_pop:ERR")}
// Array shift/unshift
try{var a=[1];a.unshift(0);if(a.shift()===0)r.push("shift_unshift:OK");else r.push("shift_unshift:FAIL")}catch(e){r.push("shift_unshift:ERR")}
// Array splice
try{var a=[1,2,3];a.splice(1,1);if(a.length===2)r.push("splice:OK");else r.push("splice:FAIL")}catch(e){r.push("splice:ERR")}
// String methods
try{if("hello".charAt(0)==="h")r.push("charAt:OK");else r.push("charAt:FAIL")}catch(e){r.push("charAt:ERR")}
try{if("hello".substring(1,3)==="el")r.push("substring:OK");else r.push("substring:FAIL")}catch(e){r.push("substring:ERR")}
try{if("a,b".split(",").length===2)r.push("split:OK");else r.push("split:FAIL")}catch(e){r.push("split:ERR")}
return "ES3: "+r.join(" | ")
}
