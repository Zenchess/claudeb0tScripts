// ES6/ES2015 Feature Test for Hackmud
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
    
    results.push("=== ES6/ES2015 Features ===");
    
    // let and const
    test("let declaration", () => { let x=5; return x===5; });
    test("let block scope", () => { let x=1; {let x=2;} return x===1; });
    test("const declaration", () => { const x=5; return x===5; });
    test("const reassign throws", () => { try{const x=1;x=2;return false;}catch(e){return true;} });
    test("const object mutation", () => { const o={x:1}; o.x=2; return o.x===2; });
    
    // Arrow functions
    test("Arrow function basic", () => (()=>42)()===42);
    test("Arrow with params", () => ((x,y)=>x+y)(3,4)===7);
    test("Arrow implicit return", () => (x=>x*2)(5)===10);
    test("Arrow lexical this", () => { 
        var o={x:1,f:function(){return (()=>this.x)();}}; 
        return o.f()===1; 
    });
    
    // Template literals
    test("Template literal", () => `hello`==="hello");
    test("Template interpolation", () => { let x=5; return `val=${x}`==="val=5"; });
    test("Template multi-line", () => `a\nb`.includes("\n"));
    test("Template expression", () => `${2+2}`==="4");
    
    // Destructuring
    test("Array destructuring", () => { let [a,b]=[1,2]; return a===1&&b===2; });
    test("Array destruct skip", () => { let [,b]=[1,2]; return b===2; });
    test("Array destruct rest", () => { let [a,...r]=[1,2,3]; return r.length===2; });
    test("Object destructuring", () => { let {x,y}={x:1,y:2}; return x===1&&y===2; });
    test("Object destruct rename", () => { let {x:a}={x:5}; return a===5; });
    test("Object destruct default", () => { let {x=10}={}; return x===10; });
    test("Nested destructuring", () => { let {a:{b}}={a:{b:5}}; return b===5; });
    test("Param destructuring", () => (({x})=>x)({x:42})===42);
    
    // Spread operator
    test("Array spread", () => [...[1,2,3]].length===3);
    test("Spread in call", () => Math.max(...[1,5,3])===5);
    test("Object spread", () => ({...{a:1},...{b:2}}).b===2);
    test("Array spread concat", () => [...[1,2],...[3,4]].join()==="1,2,3,4");
    
    // Rest parameters
    test("Rest params", () => { function f(...a){return a.length;} return f(1,2,3)===3; });
    test("Rest after param", () => { function f(a,...r){return r.length;} return f(1,2,3)===2; });
    
    // Default parameters
    test("Default param", () => { function f(x=10){return x;} return f()===10; });
    test("Default param override", () => { function f(x=10){return x;} return f(5)===5; });
    test("Default param expr", () => { function f(x=2*3){return x;} return f()===6; });
    
    // Classes
    test("Class declaration", () => { class C{} return typeof C==="function"; });
    test("Class constructor", () => { class C{constructor(x){this.x=x;}} return new C(5).x===5; });
    test("Class method", () => { class C{f(){return 42;}} return new C().f()===42; });
    test("Class extends", () => { class A{f(){return 1;}} class B extends A{} return new B().f()===1; });
    test("Class super", () => { class A{f(){return 1;}} class B extends A{f(){return super.f()+1;}} return new B().f()===2; });
    test("Class static", () => { class C{static f(){return 42;}} return C.f()===42; });
    test("Class getter", () => { class C{get x(){return 5;}} return new C().x===5; });
    test("Class setter", () => { class C{set x(v){this._x=v;}} var c=new C();c.x=5;return c._x===5; });
    
    // Symbols
    test("Symbol creation", () => typeof Symbol()==="symbol");
    test("Symbol uniqueness", () => Symbol("a")!==Symbol("a"));
    test("Symbol.for", () => Symbol.for("test")===Symbol.for("test"));
    test("Symbol as key", () => { let s=Symbol(); let o={[s]:42}; return o[s]===42; });
    
    // Iterators
    test("Array iterator", () => { let a=[1,2]; let it=a[Symbol.iterator](); return it.next().value===1; });
    test("String iterator", () => { let s="ab"; let it=s[Symbol.iterator](); return it.next().value==="a"; });
    test("for...of array", () => { let s=0;for(let x of[1,2,3])s+=x;return s===6; });
    test("for...of string", () => { let a=[];for(let c of"ab")a.push(c);return a.join()==="a,b"; });
    
    // Map and Set
    test("Map creation", () => new Map() instanceof Map);
    test("Map set/get", () => { let m=new Map(); m.set("a",1); return m.get("a")===1; });
    test("Map size", () => { let m=new Map([["a",1],["b",2]]); return m.size===2; });
    test("Map has", () => { let m=new Map([["a",1]]); return m.has("a") && !m.has("b"); });
    test("Map delete", () => { let m=new Map([["a",1]]); m.delete("a"); return !m.has("a"); });
    test("Map keys/values", () => { let m=new Map([["a",1]]); return [...m.keys()][0]==="a"; });
    test("Set creation", () => new Set() instanceof Set);
    test("Set add/has", () => { let s=new Set(); s.add(1); return s.has(1); });
    test("Set size", () => new Set([1,2,2,3]).size===3);
    test("WeakMap", () => { let w=new WeakMap(); let o={}; w.set(o,1); return w.get(o)===1; });
    test("WeakSet", () => { let w=new WeakSet(); let o={}; w.add(o); return w.has(o); });
    
    // Promises
    test("Promise creation", () => new Promise(r=>r()) instanceof Promise);
    test("Promise.resolve", () => Promise.resolve(42) instanceof Promise);
    test("Promise.reject", () => Promise.reject("err") instanceof Promise);
    test("Promise.all", () => Promise.all([1,2]) instanceof Promise);
    
    // Generators
    test("Generator function", () => { function*g(){yield 1;} return typeof g()==="object"; });
    test("Generator yield", () => { function*g(){yield 1;yield 2;} let it=g();return it.next().value===1; });
    test("Generator iteration", () => { function*g(){yield 1;yield 2;} return [...g()].join()==="1,2"; });
    
    // Proxy
    test("Proxy creation", () => { let p=new Proxy({},{get:()=>42}); return p.anything===42; });
    test("Proxy handler", () => { let o={x:1}; let p=new Proxy(o,{get:(t,k)=>t[k]*2}); return p.x===2; });
    
    // Reflect
    test("Reflect.get", () => Reflect.get({x:5},"x")===5);
    test("Reflect.set", () => { let o={};Reflect.set(o,"x",5);return o.x===5; });
    test("Reflect.has", () => Reflect.has({x:1},"x")===true);
    
    // Number methods
    test("Number.isFinite", () => Number.isFinite(5) && !Number.isFinite(Infinity));
    test("Number.isNaN", () => Number.isNaN(NaN) && !Number.isNaN("NaN"));
    test("Number.isInteger", () => Number.isInteger(5) && !Number.isInteger(5.5));
    test("Number.parseFloat", () => Number.parseFloat("3.14")===3.14);
    test("Number.parseInt", () => Number.parseInt("42")===42);
    
    // String methods
    test("String.includes", () => "hello".includes("ell"));
    test("String.startsWith", () => "hello".startsWith("hel"));
    test("String.endsWith", () => "hello".endsWith("lo"));
    test("String.repeat", () => "ab".repeat(3)==="ababab");
    test("String.padStart", () => { try{return "5".padStart(3,"0")==="005";}catch(e){return "N/A";} });
    test("String.padEnd", () => { try{return "5".padEnd(3,"0")==="500";}catch(e){return "N/A";} });
    
    // Array methods
    test("Array.from", () => Array.from("abc").join()==="a,b,c");
    test("Array.of", () => Array.of(1,2,3).join()==="1,2,3");
    test("Array.find", () => [1,2,3].find(x=>x>1)===2);
    test("Array.findIndex", () => [1,2,3].findIndex(x=>x>1)===1);
    test("Array.fill", () => [1,2,3].fill(0).join()==="0,0,0");
    test("Array.copyWithin", () => [1,2,3,4].copyWithin(0,2).join()==="3,4,3,4");
    
    // Computed property names
    test("Computed property", () => { let k="x"; return {[k]:5}.x===5; });
    test("Computed method", () => { let k="f"; return {[k](){return 42;}}[k]()===42; });
    
    // Method shorthand
    test("Method shorthand", () => ({f(){return 1;}}).f()===1);
    test("Property shorthand", () => { let x=5; return {x}.x===5; });
    
    // Summary
    results.push(`\n=== SUMMARY: ${pass} passed, ${fail} failed ===`);
    
    return results.join("\n");
}
