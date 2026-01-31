// ES1 (ECMAScript 1997) Feature Tests
function(c, a) {
    let results = [];
    
    // === VARIABLES ===
    try { var x = 1; results.push("✓ var declaration"); } catch(e) { results.push("✗ var: " + e.message); }
    
    // === DATA TYPES ===
    try { var n = 42; var s = "str"; var b = true; var nu = null; var u = undefined; results.push("✓ primitives (number/string/bool/null/undefined)"); } catch(e) { results.push("✗ primitives: " + e.message); }
    try { var arr = [1,2,3]; results.push("✓ array literal"); } catch(e) { results.push("✗ array: " + e.message); }
    try { var obj = {a:1, b:2}; results.push("✓ object literal"); } catch(e) { results.push("✗ object: " + e.message); }
    
    // === OPERATORS ===
    try { var r = 1+2-3*4/2%3; results.push("✓ arithmetic (+,-,*,/,%)"); } catch(e) { results.push("✗ arithmetic: " + e.message); }
    try { var r = 1==1 && 1!=2 && 1<2 && 2>1 && 1<=1 && 2>=2; results.push("✓ comparison (==,!=,<,>,<=,>=)"); } catch(e) { results.push("✗ comparison: " + e.message); }
    try { var r = true && false || !true; results.push("✓ logical (&&,||,!)"); } catch(e) { results.push("✗ logical: " + e.message); }
    try { var r = 5 & 3 | 2 ^ 1 << 2 >> 1 >>> 1 & ~0; results.push("✓ bitwise (&,|,^,<<,>>,>>>,~)"); } catch(e) { results.push("✗ bitwise: " + e.message); }
    try { var x = 1; x += 1; x -= 1; x *= 2; x /= 2; results.push("✓ assignment (+=,-=,*=,/=)"); } catch(e) { results.push("✗ assignment: " + e.message); }
    try { var x = 1; x++; ++x; x--; --x; results.push("✓ increment/decrement (++,--)"); } catch(e) { results.push("✗ inc/dec: " + e.message); }
    try { var r = true ? "a" : "b"; results.push("✓ ternary (?:)"); } catch(e) { results.push("✗ ternary: " + e.message); }
    try { var r = typeof 1; results.push("✓ typeof"); } catch(e) { results.push("✗ typeof: " + e.message); }
    
    // === CONTROL FLOW ===
    try { if(true){} else {} results.push("✓ if/else"); } catch(e) { results.push("✗ if/else: " + e.message); }
    try { for(var i=0;i<1;i++){} results.push("✓ for loop"); } catch(e) { results.push("✗ for: " + e.message); }
    try { var i=0; while(i<1){i++;} results.push("✓ while loop"); } catch(e) { results.push("✗ while: " + e.message); }
    try { var i=0; do{i++;}while(i<1); results.push("✓ do-while loop"); } catch(e) { results.push("✗ do-while: " + e.message); }
    try { switch(1){case 1:break;default:} results.push("✓ switch/case"); } catch(e) { results.push("✗ switch: " + e.message); }
    try { for(var i=0;i<2;i++){if(i==0)continue;break;} results.push("✓ break/continue"); } catch(e) { results.push("✗ break/continue: " + e.message); }
    
    // === FUNCTIONS ===
    try { function f(){return 1;} f(); results.push("✓ function declaration"); } catch(e) { results.push("✗ function decl: " + e.message); }
    try { var f = function(){return 1;}; f(); results.push("✓ function expression"); } catch(e) { results.push("✗ function expr: " + e.message); }
    try { function f(a,b){return a+b;} f(1,2); results.push("✓ function params"); } catch(e) { results.push("✗ function params: " + e.message); }
    try { (function(){return 1;})(); results.push("✓ IIFE"); } catch(e) { results.push("✗ IIFE: " + e.message); }
    
    // === BUILT-IN OBJECTS ===
    try { Math.abs(-1); results.push("✓ Math"); } catch(e) { results.push("✗ Math: " + e.message); }
    try { new Date(); results.push("✓ Date"); } catch(e) { results.push("✗ Date: " + e.message); }
    try { "abc".length; results.push("✓ String"); } catch(e) { results.push("✗ String: " + e.message); }
    try { [1,2].length; results.push("✓ Array"); } catch(e) { results.push("✗ Array: " + e.message); }
    try { new Object(); results.push("✓ Object"); } catch(e) { results.push("✗ Object: " + e.message); }
    try { new Boolean(true); results.push("✓ Boolean"); } catch(e) { results.push("✗ Boolean: " + e.message); }
    try { new Number(1); results.push("✓ Number"); } catch(e) { results.push("✗ Number: " + e.message); }
    try { new Function("return 1"); results.push("✓ Function constructor"); } catch(e) { results.push("✗ Function: " + e.message); }
    
    // === ERROR HANDLING ===
    try { try{throw new Error("test");}catch(e){} results.push("✓ try/catch/throw"); } catch(e) { results.push("✗ try/catch: " + e.message); }
    try { try{}finally{} results.push("✓ finally"); } catch(e) { results.push("✗ finally: " + e.message); }
    
    return "=== ES1 (1997) TEST RESULTS ===\n" + results.join("\n");
}
