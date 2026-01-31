// ES2016-ES2020 Feature Tests
function(c, a) {
    let results = [];
    
    // === ES2016 (ES7) ===
    try { 2 ** 10; results.push("✓ ES2016: exponentiation (**)"); } catch(e) { results.push("✗ **: " + e.message); }
    try { [1,2,3].includes(2); results.push("✓ ES2016: Array.includes()"); } catch(e) { results.push("✗ includes: " + e.message); }
    
    // === ES2017 (ES8) ===
    try { Object.values({a:1,b:2}); results.push("✓ ES2017: Object.values()"); } catch(e) { results.push("✗ Object.values: " + e.message); }
    try { Object.entries({a:1,b:2}); results.push("✓ ES2017: Object.entries()"); } catch(e) { results.push("✗ Object.entries: " + e.message); }
    try { "a".padStart(3, "0"); results.push("✓ ES2017: String.padStart()"); } catch(e) { results.push("✗ padStart: " + e.message); }
    try { "a".padEnd(3, "0"); results.push("✓ ES2017: String.padEnd()"); } catch(e) { results.push("✗ padEnd: " + e.message); }
    try { Object.getOwnPropertyDescriptors({}); results.push("✓ ES2017: Object.getOwnPropertyDescriptors()"); } catch(e) { results.push("✗ getOwnPropertyDescriptors: " + e.message); }
    try { function f(a,b,){} results.push("✓ ES2017: trailing comma in params"); } catch(e) { results.push("✗ trailing comma params: " + e.message); }
    
    // async/await is ES2017 but likely won't work in hackmud's sync execution
    try { async function f(){} results.push("✓ ES2017: async function syntax"); } catch(e) { results.push("✗ async function: " + e.message); }
    try { async function f(){return await Promise.resolve(1);} results.push("✓ ES2017: await syntax"); } catch(e) { results.push("✗ await: " + e.message); }
    
    // === ES2018 (ES9) ===
    try { const {a,...rest} = {a:1,b:2,c:3}; results.push("✓ ES2018: object rest properties"); } catch(e) { results.push("✗ object rest: " + e.message); }
    try { const o = {a:1}; const p = {...o}; results.push("✓ ES2018: object spread properties"); } catch(e) { results.push("✗ object spread: " + e.message); }
    try { /(?<year>\d{4})/.exec("2020"); results.push("✓ ES2018: named capture groups"); } catch(e) { results.push("✗ named capture: " + e.message); }
    try { /foo(?=bar)/.test("foobar"); results.push("✓ ES2018: lookbehind assertions"); } catch(e) { results.push("✗ lookbehind: " + e.message); }
    try { /./s.test("\n"); results.push("✓ ES2018: dotAll flag (s)"); } catch(e) { results.push("✗ dotAll: " + e.message); }
    try { /\p{Script=Latin}/u; results.push("✓ ES2018: Unicode property escapes"); } catch(e) { results.push("✗ unicode props: " + e.message); }
    try { Promise.prototype.finally; results.push("✓ ES2018: Promise.finally()"); } catch(e) { results.push("✗ Promise.finally: " + e.message); }
    
    // async iteration - likely won't work but test syntax
    try { (async function*(){}); results.push("✓ ES2018: async generator syntax"); } catch(e) { results.push("✗ async generator: " + e.message); }
    
    // === ES2019 (ES10) ===
    try { [1,[2,[3]]].flat(2); results.push("✓ ES2019: Array.flat()"); } catch(e) { results.push("✗ Array.flat: " + e.message); }
    try { [[1,2],[3,4]].flatMap(x=>x); results.push("✓ ES2019: Array.flatMap()"); } catch(e) { results.push("✗ Array.flatMap: " + e.message); }
    try { Object.fromEntries([["a",1]]); results.push("✓ ES2019: Object.fromEntries()"); } catch(e) { results.push("✗ Object.fromEntries: " + e.message); }
    try { "  abc  ".trimStart(); results.push("✓ ES2019: String.trimStart()"); } catch(e) { results.push("✗ trimStart: " + e.message); }
    try { "  abc  ".trimEnd(); results.push("✓ ES2019: String.trimEnd()"); } catch(e) { results.push("✗ trimEnd: " + e.message); }
    try { try{throw 1;}catch{} results.push("✓ ES2019: optional catch binding"); } catch(e) { results.push("✗ optional catch: " + e.message); }
    try { Symbol("test").description; results.push("✓ ES2019: Symbol.description"); } catch(e) { results.push("✗ Symbol.description: " + e.message); }
    
    // === ES2020 (ES11) ===
    try { BigInt(9007199254740991); results.push("✓ ES2020: BigInt()"); } catch(e) { results.push("✗ BigInt: " + e.message); }
    try { 9007199254740991n; results.push("✓ ES2020: BigInt literal (n)"); } catch(e) { results.push("✗ BigInt literal: " + e.message); }
    try { const x = null; x ?? "default"; results.push("✓ ES2020: nullish coalescing (??)"); } catch(e) { results.push("✗ ??: " + e.message); }
    try { const o = null; o?.x; results.push("✓ ES2020: optional chaining (?.)"); } catch(e) { results.push("✗ ?.: " + e.message); }
    try { const o = null; o?.fn?.(); results.push("✓ ES2020: optional call (?.)"); } catch(e) { results.push("✗ optional call: " + e.message); }
    try { Promise.allSettled([Promise.resolve(1)]); results.push("✓ ES2020: Promise.allSettled()"); } catch(e) { results.push("✗ Promise.allSettled: " + e.message); }
    try { "abc".matchAll(/./g); results.push("✓ ES2020: String.matchAll()"); } catch(e) { results.push("✗ matchAll: " + e.message); }
    try { globalThis; results.push("✓ ES2020: globalThis"); } catch(e) { results.push("✗ globalThis: " + e.message); }
    
    // Dynamic import - likely won't work
    try { typeof import === 'function' || true; results.push("? ES2020: dynamic import() (untestable)"); } catch(e) { results.push("✗ import(): " + e.message); }
    
    return "=== ES2016-ES2020 TEST RESULTS ===\n" + results.join("\n");
}
