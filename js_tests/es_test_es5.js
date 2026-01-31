// ES5 (2009) Feature Test for Hackmud
function(context, args) {
    let results = [];
    let pass = 0, fail = 0;
    
    function test(name, fn) {
        try {
            let r = fn();
            if (r === true) { pass++; results.push(`✓ ${name}`); }
            else { fail++; results.push(`✗ ${name}: ${r}`); }
        } catch(e) { fail++; results.push(`✗ ${name}: ${e.message || e}`); }
    }
    
    results.push("=== ES5 (2009) Features ===");
    
    // Strict mode
    test("strict mode", () => { "use strict"; return true; });
    
    // Array methods
    test("Array.forEach", () => { let sum=0; [1,2,3].forEach(x=>sum+=x); return sum===6; });
    test("Array.map", () => [1,2,3].map(x=>x*2).join()=="2,4,6");
    test("Array.filter", () => [1,2,3,4].filter(x=>x%2===0).join()=="2,4");
    test("Array.reduce", () => [1,2,3,4].reduce((a,b)=>a+b,0)===10);
    test("Array.reduceRight", () => [1,2,3].reduceRight((a,b)=>a+b,0)===6);
    test("Array.every", () => [2,4,6].every(x=>x%2===0));
    test("Array.some", () => [1,2,3].some(x=>x===2));
    test("Array.indexOf", () => [1,2,3,2].indexOf(2)===1);
    test("Array.lastIndexOf", () => [1,2,3,2].lastIndexOf(2)===3);
    test("Array.isArray", () => Array.isArray([]) && !Array.isArray({}));
    
    // JSON
    test("JSON.stringify", () => JSON.stringify({a:1})==='{"a":1}');
    test("JSON.parse", () => JSON.parse('{"a":1}').a===1);
    test("JSON.stringify array", () => JSON.stringify([1,2,3])==='[1,2,3]');
    test("JSON.parse array", () => JSON.parse('[1,2,3]')[1]===2);
    
    // Object methods
    test("Object.keys", () => Object.keys({a:1,b:2}).join()=="a,b");
    test("Object.values", () => { try{return Object.values({a:1,b:2}).join()=="1,2";}catch(e){return "N/A (ES2017)";} });
    test("Object.entries", () => { try{return Object.entries({a:1})[0].join()=="a,1";}catch(e){return "N/A (ES2017)";} });
    test("Object.create", () => { var p={x:1}; var o=Object.create(p); return o.x===1; });
    test("Object.defineProperty", () => { var o={}; Object.defineProperty(o,'x',{value:5}); return o.x===5; });
    test("Object.getOwnPropertyNames", () => Object.getOwnPropertyNames({a:1,b:2}).length===2);
    test("Object.getPrototypeOf", () => Object.getPrototypeOf([])===Array.prototype);
    test("Object.freeze", () => { var o={a:1}; Object.freeze(o); o.a=2; return o.a===1; });
    test("Object.seal", () => { var o={a:1}; Object.seal(o); o.b=2; return o.b===undefined; });
    test("Object.isFrozen", () => { var o={}; Object.freeze(o); return Object.isFrozen(o); });
    test("Object.isSealed", () => { var o={}; Object.seal(o); return Object.isSealed(o); });
    test("Object.isExtensible", () => { var o={}; return Object.isExtensible(o); });
    test("Object.preventExtensions", () => { var o={}; Object.preventExtensions(o); return !Object.isExtensible(o); });
    
    // Property descriptors
    test("Object.getOwnPropertyDescriptor", () => {
        var o={x:5};
        var d=Object.getOwnPropertyDescriptor(o,'x');
        return d.value===5 && d.writable===true;
    });
    
    // Getters and setters
    test("Getter (get)", () => { var o={get x(){return 42;}}; return o.x===42; });
    test("Setter (set)", () => { var o={_x:0,set x(v){this._x=v;}}; o.x=5; return o._x===5; });
    test("Getter/Setter combined", () => { 
        var o={_v:0,get v(){return this._v;},set v(x){this._v=x*2;}}; 
        o.v=5; return o.v===10; 
    });
    
    // String methods
    test("String.trim", () => "  hello  ".trim()==="hello");
    test("String.trimStart", () => { try{return "  hi".trimStart()==="hi";}catch(e){return "N/A (ES2019)";} });
    test("String.trimEnd", () => { try{return "hi  ".trimEnd()==="hi";}catch(e){return "N/A (ES2019)";} });
    
    // Date methods
    test("Date.now()", () => typeof Date.now()==="number" && Date.now()>0);
    test("Date.toISOString", () => new Date(0).toISOString()==="1970-01-01T00:00:00.000Z");
    test("Date.toJSON", () => typeof new Date().toJSON()==="string");
    
    // Function.bind
    test("Function.bind", () => { 
        function f(){return this.x;} 
        var bound=f.bind({x:42}); 
        return bound()===42; 
    });
    test("Function.bind with args", () => {
        function f(a,b){return a+b;}
        var bound=f.bind(null,10);
        return bound(5)===15;
    });
    
    // Reserved words as property names (ES5)
    test("Reserved word as property", () => { var o={class:1,if:2}; return o.class===1 && o.if===2; });
    
    // Trailing commas in arrays/objects
    test("Trailing comma in array", () => [1,2,3,].length===3);
    test("Trailing comma in object", () => ({a:1,b:2,}).a===1);
    
    // Summary
    results.push(`\n=== SUMMARY: ${pass} passed, ${fail} failed ===`);
    
    return results.join("\n");
}
