// ES2016-ES2025 Feature Test for Hackmud
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
    
    // === ES2016 ===
    results.push("=== ES2016 ===");
    test("Exponentiation (**)", () => 2**3===8);
    test("Array.includes", () => [1,2,3].includes(2) && ![1,2,3].includes(5));
    
    // === ES2017 ===
    results.push("=== ES2017 ===");
    test("async function", () => { async function f(){return 1;} return typeof f==="function"; });
    test("await (in async)", () => { async function f(){return await Promise.resolve(42);} return f() instanceof Promise; });
    test("Object.values", () => Object.values({a:1,b:2}).join()==="1,2");
    test("Object.entries", () => Object.entries({a:1})[0].join()==="a,1");
    test("String.padStart", () => "5".padStart(3,"0")==="005");
    test("String.padEnd", () => "5".padEnd(3,"0")==="500");
    test("Object.getOwnPropertyDescriptors", () => {
        let d=Object.getOwnPropertyDescriptors({x:1});
        return d.x && d.x.value===1;
    });
    test("Trailing commas in params", () => { function f(a,b,){return a+b;} return f(1,2)===3; });
    
    // === ES2018 ===
    results.push("=== ES2018 ===");
    test("Object rest spread", () => { let {a,...r}={a:1,b:2,c:3}; return r.b===2 && r.c===3; });
    test("Promise.finally", () => typeof Promise.resolve().finally==="function");
    test("Async iteration", () => { try{eval("(async function*(){})");return true;}catch(e){return false;} });
    test("RegExp named groups", () => { let m=/(?<year>\d+)/.exec("2024"); return m && m.groups && m.groups.year==="2024"; });
    test("RegExp lookbehind", () => /(?<=@)\w+/.test("@user"));
    test("RegExp dotAll (s flag)", () => /a.b/s.test("a\nb"));
    test("RegExp unicode escapes", () => /\p{L}/u.test("a"));
    
    // === ES2019 ===
    results.push("=== ES2019 ===");
    test("Array.flat", () => [[1],[2,[3]]].flat(2).join()==="1,2,3");
    test("Array.flatMap", () => [1,2].flatMap(x=>[x,x*2]).join()==="1,2,2,4");
    test("Object.fromEntries", () => Object.fromEntries([["a",1],["b",2]]).b===2);
    test("String.trimStart", () => "  hi".trimStart()==="hi");
    test("String.trimEnd", () => "hi  ".trimEnd()==="hi");
    test("Optional catch binding", () => { try{throw 1;}catch{return true;} return false; });
    test("Symbol.description", () => Symbol("test").description==="test");
    test("Array.sort stable", () => { 
        let a=[{v:1,i:0},{v:1,i:1},{v:2,i:2}]; 
        a.sort((x,y)=>x.v-y.v); 
        return a[0].i===0 && a[1].i===1;
    });
    
    // === ES2020 ===
    results.push("=== ES2020 ===");
    test("Optional chaining (?.)", () => { let o={a:{b:1}}; return o?.a?.b===1 && o?.x?.y===undefined; });
    test("Nullish coalescing (??)", () => (null??5)===5 && (0??5)===0 && (""??5)==="");
    test("BigInt literal", () => typeof 123n==="bigint");
    test("BigInt()", () => BigInt(123)===123n);
    test("BigInt operations", () => (10n+5n)===15n && (10n*2n)===20n);
    test("Promise.allSettled", () => typeof Promise.allSettled==="function");
    test("globalThis", () => typeof globalThis==="object");
    test("String.matchAll", () => { let m=[..."ab".matchAll(/./g)]; return m.length===2; });
    test("import.meta", () => { try{eval("import.meta");return true;}catch(e){return "N/A (module context)";} });
    test("Dynamic import()", () => typeof import==="function" || "N/A");
    
    // === ES2021 ===
    results.push("=== ES2021 ===");
    test("Logical AND assignment (&&=)", () => { let x=1; x&&=2; return x===2; });
    test("Logical OR assignment (||=)", () => { let x=0; x||=5; return x===5; });
    test("Nullish assignment (??=)", () => { let x=null; x??=5; return x===5; });
    test("String.replaceAll", () => "aaa".replaceAll("a","b")==="bbb");
    test("Promise.any", () => typeof Promise.any==="function");
    test("WeakRef", () => { try{let w=new WeakRef({});return true;}catch(e){return false;} });
    test("FinalizationRegistry", () => typeof FinalizationRegistry==="function" || "N/A");
    test("Numeric separators", () => 1_000_000===1000000);
    
    // === ES2022 ===
    results.push("=== ES2022 ===");
    test("Class fields (public)", () => { class C{x=5;} return new C().x===5; });
    test("Class fields (private)", () => { try{class C{#x=5;getX(){return this.#x;}} return new C().getX()===5;}catch(e){return false;} });
    test("Class static block", () => { try{class C{static{C.x=5;}} return C.x===5;}catch(e){return false;} });
    test("Top-level await", () => "N/A (module context)");
    test("Array.at", () => [1,2,3].at(-1)===3);
    test("String.at", () => "abc".at(-1)==="c");
    test("Object.hasOwn", () => Object.hasOwn({a:1},"a") && !Object.hasOwn({a:1},"b"));
    test("Error.cause", () => { let e=new Error("msg",{cause:"reason"}); return e.cause==="reason"; });
    test("RegExp match indices (d)", () => { let m=/a/d.exec("ba"); return m && m.indices && m.indices[0][0]===1; });
    
    // === ES2023 ===
    results.push("=== ES2023 ===");
    test("Array.findLast", () => [1,2,3,2].findLast(x=>x===2)===2);
    test("Array.findLastIndex", () => [1,2,3,2].findLastIndex(x=>x===2)===3);
    test("Array.toReversed", () => { let a=[1,2,3]; let b=a.toReversed(); return b.join()==="3,2,1" && a[0]===1; });
    test("Array.toSorted", () => { let a=[3,1,2]; let b=a.toSorted(); return b.join()==="1,2,3" && a[0]===3; });
    test("Array.toSpliced", () => { let a=[1,2,3]; let b=a.toSpliced(1,1,5); return b.join()==="1,5,3" && a[1]===2; });
    test("Array.with", () => { let a=[1,2,3]; let b=a.with(1,5); return b.join()==="1,5,3" && a[1]===2; });
    test("Hashbang (#!)", () => "N/A (parse-time)");
    test("WeakMap symbol keys", () => { try{let w=new WeakMap();let s=Symbol();w.set(s,1);return w.get(s)===1;}catch(e){return false;} });
    
    // === ES2024 ===
    results.push("=== ES2024 ===");
    test("Object.groupBy", () => { try{let g=Object.groupBy([1,2,3],x=>x%2);return g[1].length===2;}catch(e){return "N/A";} });
    test("Map.groupBy", () => { try{let g=Map.groupBy([1,2,3],x=>x%2);return g.get(1).length===2;}catch(e){return "N/A";} });
    test("Promise.withResolvers", () => { try{let{promise,resolve}=Promise.withResolvers();return promise instanceof Promise;}catch(e){return "N/A";} });
    test("String.isWellFormed", () => { try{return "abc".isWellFormed()===true;}catch(e){return "N/A";} });
    test("String.toWellFormed", () => { try{return typeof "".toWellFormed()==="string";}catch(e){return "N/A";} });
    test("Atomics.waitAsync", () => { try{return typeof Atomics.waitAsync==="function";}catch(e){return "N/A";} });
    test("ArrayBuffer.resize", () => { try{let b=new ArrayBuffer(8,{maxByteLength:16});b.resize(16);return b.byteLength===16;}catch(e){return "N/A";} });
    
    // === ES2025 ===
    results.push("=== ES2025 ===");
    test("Set.union", () => { try{let a=new Set([1,2]);let b=new Set([2,3]);return a.union(b).size===3;}catch(e){return "N/A";} });
    test("Set.intersection", () => { try{let a=new Set([1,2]);let b=new Set([2,3]);return a.intersection(b).size===1;}catch(e){return "N/A";} });
    test("Set.difference", () => { try{let a=new Set([1,2]);let b=new Set([2,3]);return a.difference(b).size===1;}catch(e){return "N/A";} });
    test("Set.symmetricDifference", () => { try{let a=new Set([1,2]);let b=new Set([2,3]);return a.symmetricDifference(b).size===2;}catch(e){return "N/A";} });
    test("Set.isSubsetOf", () => { try{let a=new Set([1,2]);let b=new Set([1,2,3]);return a.isSubsetOf(b);}catch(e){return "N/A";} });
    test("Set.isSupersetOf", () => { try{let a=new Set([1,2,3]);let b=new Set([1,2]);return a.isSupersetOf(b);}catch(e){return "N/A";} });
    test("Set.isDisjointFrom", () => { try{let a=new Set([1,2]);let b=new Set([3,4]);return a.isDisjointFrom(b);}catch(e){return "N/A";} });
    test("Iterator.prototype methods", () => { try{return [1,2,3].values().map(x=>x*2).toArray().join()==="2,4,6";}catch(e){return "N/A";} });
    test("RegExp.escape", () => { try{return typeof RegExp.escape==="function";}catch(e){return "N/A";} });
    
    // Summary
    results.push(`\n=== SUMMARY: ${pass} passed, ${fail} failed ===`);
    
    return results.join("\n");
}
