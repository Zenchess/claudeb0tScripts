// ES1 Minimal Test
function(c,a){
var r=[];
try{var x=1;r.push("var:OK")}catch(e){r.push("var:FAIL")}
try{var n=42,s="hi",b=true;r.push("types:OK")}catch(e){r.push("types:FAIL")}
try{var o={a:1};r.push("obj:OK")}catch(e){r.push("obj:FAIL")}
try{var a=[1,2];r.push("arr:OK")}catch(e){r.push("arr:FAIL")}
try{if(1){}else{};r.push("if:OK")}catch(e){r.push("if:FAIL")}
try{for(var i=0;i<1;i++){};r.push("for:OK")}catch(e){r.push("for:FAIL")}
try{var i=0;while(i<1)i++;r.push("while:OK")}catch(e){r.push("while:FAIL")}
try{switch(1){case 1:break};r.push("switch:OK")}catch(e){r.push("switch:FAIL")}
try{function f(){return 1};f();r.push("func:OK")}catch(e){r.push("func:FAIL")}
try{(function(){})();r.push("IIFE:OK")}catch(e){r.push("IIFE:FAIL")}
try{Math.abs(-1);r.push("Math:OK")}catch(e){r.push("Math:FAIL")}
try{new Date();r.push("Date:OK")}catch(e){r.push("Date:FAIL")}
try{try{throw new Error("x")}catch(e){};r.push("try:OK")}catch(e){r.push("try:FAIL")}
return "ES1: "+r.join(" | ")
}
