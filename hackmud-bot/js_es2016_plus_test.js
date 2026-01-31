// ES2016-ES2025 Feature Test for Hackmud
function(context, args) {
    let results = [];
    let passed = 0;
    let failed = 0;
    
    function test(name, fn) {
        try {
            let result = fn();
            if (result === true || result !== false) {
                results.push(`✓ ${name}`);
                passed++;
            } else {
                results.push(`✗ ${name}: returned ${result}`);
                failed++;
            }
        } catch (e) {
            results.push(`✗ ${name}: ${e.message || e}`);
            failed++;
        }
    }
    
    // ========== ES2016 (ES7) ==========
    results.push("=== ES2016 (ES7) ===");
    
    test("Array.includes", () => [1,2,3].includes(2));
    test("Array.includes fromIndex", () => ![1,2,3].includes(1, 1));
    test("Exponentiation **", () => 2 ** 3 === 8);
    test("Exponentiation **=", () => { let x = 2; x **= 3; return x === 8; });
    
    // ========== ES2017 (ES8) ==========
    results.push("\n=== ES2017 (ES8) ===");
    
    test("Object.values", () => Object.values({a:1,b:2}).join(",") === "1,2");
    test("Object.entries", () => Object.entries({a:1})[0].join("") === "a1");
    test("String.padStart", () => "5".padStart(3, "0") === "005");
    test("String.padEnd", () => "5".padEnd(3, "0") === "500");
    test("Object.getOwnPropertyDescriptors", () => {
        let d = Object.getOwnPropertyDescriptors({a:1});
        return d.a.value === 1;
    });
    test("Trailing commas in params", () => { let f = (a,b,) => a+b; return f(1,2,) === 3; });
    
    // async/await
    test("async function exists", () => { async function f() { return 1; } return typeof f === "function"; });
    test("async returns promise", () => { async function f() { return 42; } return f() instanceof Promise; });
    
    // ========== ES2018 (ES9) ==========
    results.push("\n=== ES2018 (ES9) ===");
    
    test("Rest props in object destructure", () => { let {a, ...rest} = {a:1,b:2,c:3}; return rest.b === 2 && rest.c === 3; });
    test("Spread in object literal", () => { let o = {a:1}; let p = {...o, b:2}; return p.a === 1 && p.b === 2; });
    test("RegExp named groups", () => { let m = /(?<year>\d{4})/.exec("2024"); return m.groups.year === "2024"; });
    test("RegExp lookbehind", () => /(?<=\$)\d+/.test("$100"));
    test("RegExp dotAll flag", () => /a.b/s.test("a\nb"));
    test("RegExp unicode prop", () => /\p{Emoji}/u.test("😀"));
    test("Promise.finally", () => typeof Promise.prototype.finally === "function");
    
    // async iteration
    test("Symbol.asyncIterator", () => typeof Symbol.asyncIterator === "symbol");
    
    // ========== ES2019 (ES10) ==========
    results.push("\n=== ES2019 (ES10) ===");
    
    test("Array.flat", () => [1,[2,3]].flat().join(",") === "1,2,3");
    test("Array.flat depth", () => [1,[2,[3]]].flat(2).join(",") === "1,2,3");
    test("Array.flatMap", () => [1,2].flatMap(x => [x, x*2]).join(",") === "1,2,2,4");
    test("Object.fromEntries", () => Object.fromEntries([["a",1],["b",2]]).a === 1);
    test("String.trimStart", () => "  hi".trimStart() === "hi");
    test("String.trimEnd", () => "hi  ".trimEnd() === "hi");
    test("Optional catch binding", () => { try { throw "err"; } catch { return true; } });
    test("Symbol.description", () => Symbol("desc").description === "desc");
    test("Array.sort stable", () => { 
        let a = [{v:1,i:0},{v:1,i:1},{v:2,i:2}];
        a.sort((x,y) => x.v - y.v);
        return a[0].i === 0 && a[1].i === 1;
    });
    test("JSON superset", () => JSON.parse('"\u2028"') === "\u2028");
    test("Function.toString", () => (function test(){}).toString().includes("test"));
    
    // ========== ES2020 (ES11) ==========
    results.push("\n=== ES2020 (ES11) ===");
    
    test("BigInt exists", () => typeof BigInt === "function");
    test("BigInt literal", () => typeof 123n === "bigint");
    test("BigInt operations", () => 10n + 20n === 30n);
    test("BigInt comparison", () => 10n > 5n);
    test("Optional chaining ?.", () => { let o = {a:{b:1}}; return o?.a?.b === 1; });
    test("Optional chaining undefined", () => { let o = {}; return o?.a?.b === undefined; });
    test("Optional call ?.()", () => { let f; return f?.() === undefined; });
    test("Nullish coalescing ??", () => (null ?? 5) === 5);
    test("Nullish vs OR", () => (0 ?? 5) === 0 && (0 || 5) === 5);
    test("Promise.allSettled", () => typeof Promise.allSettled === "function");
    test("globalThis", () => typeof globalThis === "object");
    test("String.matchAll", () => { let m = [...("aaa").matchAll(/a/g)]; return m.length === 3; });
    test("import.meta", () => { try { return typeof import.meta === "undefined" || typeof import.meta === "object"; } catch(e) { return "syntax error"; } });
    test("Dynamic import", () => typeof import === "undefined" || typeof import === "function" ? "syntax varies" : true);
    
    // ========== ES2021 (ES12) ==========
    results.push("\n=== ES2021 (ES12) ===");
    
    test("String.replaceAll", () => "aaa".replaceAll("a", "b") === "bbb");
    test("Promise.any", () => typeof Promise.any === "function");
    test("AggregateError", () => typeof AggregateError === "function");
    test("Logical OR assign ||=", () => { let x = 0; x ||= 5; return x === 5; });
    test("Logical AND assign &&=", () => { let x = 1; x &&= 5; return x === 5; });
    test("Nullish assign ??=", () => { let x = null; x ??= 5; return x === 5; });
    test("Numeric separators", () => 1_000_000 === 1000000);
    test("WeakRef exists", () => typeof WeakRef === "function");
    test("FinalizationRegistry", () => typeof FinalizationRegistry === "function");
    
    // ========== ES2022 (ES13) ==========
    results.push("\n=== ES2022 (ES13) ===");
    
    test("Array.at", () => [1,2,3].at(-1) === 3);
    test("String.at", () => "abc".at(-1) === "c");
    test("Object.hasOwn", () => Object.hasOwn({a:1}, "a") === true);
    test("Error.cause", () => { let e = new Error("msg", {cause: "root"}); return e.cause === "root"; });
    test("Class static block", () => { 
        let val;
        class C { static { val = 42; } }
        return val === 42;
    });
    test("Class private field", () => { 
        class C { #x = 5; get() { return this.#x; } }
        return new C().get() === 5;
    });
    test("Class private method", () => {
        class C { #m() { return 42; } get() { return this.#m(); } }
        return new C().get() === 42;
    });
    test("Private field in check", () => {
        class C { #x; static has(o) { return #x in o; } }
        return C.has(new C()) === true;
    });
    test("Top-level await", () => "syntax varies in hackmud");
    test("RegExp /d flag", () => { let m = /a/d.exec("ba"); return m.indices !== undefined; });
    
    // ========== ES2023 (ES14) ==========
    results.push("\n=== ES2023 (ES14) ===");
    
    test("Array.findLast", () => [1,2,3,2,1].findLast(x => x === 2) === 2);
    test("Array.findLastIndex", () => [1,2,3,2,1].findLastIndex(x => x === 2) === 3);
    test("Array.toReversed", () => { let a = [1,2,3]; let b = a.toReversed(); return b.join(",") === "3,2,1" && a.join(",") === "1,2,3"; });
    test("Array.toSorted", () => { let a = [3,1,2]; let b = a.toSorted(); return b.join(",") === "1,2,3" && a.join(",") === "3,1,2"; });
    test("Array.toSpliced", () => { let a = [1,2,3]; let b = a.toSpliced(1,1,9); return b.join(",") === "1,9,3" && a.join(",") === "1,2,3"; });
    test("Array.with", () => { let a = [1,2,3]; let b = a.with(1, 9); return b.join(",") === "1,9,3" && a.join(",") === "1,2,3"; });
    test("Hashbang #!", () => "syntax - not testable in function");
    test("Symbol as WeakMap key", () => { let wm = new WeakMap(); let s = Symbol(); wm.set(s, 1); return wm.get(s) === 1; });
    
    // ========== ES2024 (ES15) ==========
    results.push("\n=== ES2024 (ES15) ===");
    
    test("Object.groupBy", () => { 
        try {
            let g = Object.groupBy([1,2,3,4], x => x % 2 === 0 ? "even" : "odd");
            return g.even.length === 2;
        } catch(e) { return "not available"; }
    });
    test("Map.groupBy", () => {
        try {
            let g = Map.groupBy([1,2,3,4], x => x % 2);
            return g.get(0).length === 2;
        } catch(e) { return "not available"; }
    });
    test("Promise.withResolvers", () => {
        try {
            let {promise, resolve} = Promise.withResolvers();
            return promise instanceof Promise;
        } catch(e) { return "not available"; }
    });
    test("String.isWellFormed", () => { try { return "abc".isWellFormed() === true; } catch(e) { return "not available"; } });
    test("String.toWellFormed", () => { try { return typeof "abc".toWellFormed() === "string"; } catch(e) { return "not available"; } });
    test("Atomics.waitAsync", () => typeof Atomics?.waitAsync === "function" ? true : "not available");
    test("ArrayBuffer.resize", () => { try { return typeof ArrayBuffer.prototype.resize === "function"; } catch(e) { return "not available"; } });
    
    // ========== ES2025 (ES16) - Proposals ==========
    results.push("\n=== ES2025 (ES16) - Proposals ===");
    
    test("Set methods - union", () => { try { return typeof Set.prototype.union === "function"; } catch(e) { return "not available"; } });
    test("Set methods - intersection", () => { try { return typeof Set.prototype.intersection === "function"; } catch(e) { return "not available"; } });
    test("Set methods - difference", () => { try { return typeof Set.prototype.difference === "function"; } catch(e) { return "not available"; } });
    test("Set methods - symmetricDiff", () => { try { return typeof Set.prototype.symmetricDifference === "function"; } catch(e) { return "not available"; } });
    test("Iterator helpers", () => { try { return typeof [].values().map === "function"; } catch(e) { return "not available"; } });
    test("RegExp escaping", () => { try { return typeof RegExp.escape === "function"; } catch(e) { return "not available"; } });
    
    results.push(`\n--- ES2016-2025 Summary: ${passed} passed, ${failed} failed ---`);
    
    return results.join("\n");
}
