// ES2021-ES2025 Feature Tests
function(c, a) {
    let results = [];
    
    // === ES2021 (ES12) ===
    try { "a_b_c".replaceAll("_", "-"); results.push("✓ ES2021: String.replaceAll()"); } catch(e) { results.push("✗ replaceAll: " + e.message); }
    try { Promise.any([Promise.resolve(1)]); results.push("✓ ES2021: Promise.any()"); } catch(e) { results.push("✗ Promise.any: " + e.message); }
    try { const r = new WeakRef({}); results.push("✓ ES2021: WeakRef"); } catch(e) { results.push("✗ WeakRef: " + e.message); }
    try { const fr = new FinalizationRegistry(()=>{}); results.push("✓ ES2021: FinalizationRegistry"); } catch(e) { results.push("✗ FinalizationRegistry: " + e.message); }
    try { let x = 1; x ||= 2; results.push("✓ ES2021: logical OR assignment (||=)"); } catch(e) { results.push("✗ ||=: " + e.message); }
    try { let x = null; x &&= 2; results.push("✓ ES2021: logical AND assignment (&&=)"); } catch(e) { results.push("✗ &&=: " + e.message); }
    try { let x = null; x ??= 2; results.push("✓ ES2021: nullish assignment (??=)"); } catch(e) { results.push("✗ ??=: " + e.message); }
    try { 1_000_000; results.push("✓ ES2021: numeric separators (1_000)"); } catch(e) { results.push("✗ numeric separators: " + e.message); }
    
    // === ES2022 (ES13) ===
    try { class C { #x = 1; fn(){return this.#x;} } new C().fn(); results.push("✓ ES2022: private fields (#)"); } catch(e) { results.push("✗ private fields: " + e.message); }
    try { class C { static x = 1; } results.push("✓ ES2022: static class fields"); } catch(e) { results.push("✗ static fields: " + e.message); }
    try { class C { static #x = 1; static fn(){return C.#x;} } results.push("✓ ES2022: static private fields"); } catch(e) { results.push("✗ static private: " + e.message); }
    try { class C { static { this.x = 1; } } results.push("✓ ES2022: static blocks"); } catch(e) { results.push("✗ static blocks: " + e.message); }
    try { [1,2,3].at(-1); results.push("✓ ES2022: Array.at()"); } catch(e) { results.push("✗ Array.at: " + e.message); }
    try { "abc".at(-1); results.push("✓ ES2022: String.at()"); } catch(e) { results.push("✗ String.at: " + e.message); }
    try { Object.hasOwn({a:1}, "a"); results.push("✓ ES2022: Object.hasOwn()"); } catch(e) { results.push("✗ Object.hasOwn: " + e.message); }
    try { new Error("test", {cause: new Error("cause")}); results.push("✓ ES2022: Error.cause"); } catch(e) { results.push("✗ Error.cause: " + e.message); }
    try { /d/.exec("d").indices; results.push("✓ ES2022: RegExp match indices (d flag)"); } catch(e) { results.push("✗ RegExp indices: " + e.message); }
    
    // Top-level await - can't test in function
    results.push("? ES2022: top-level await (untestable in function)");
    
    // #x in obj syntax
    try { class C { #x = 1; has(o){return #x in this;} } results.push("✓ ES2022: ergonomic brand checks (#x in obj)"); } catch(e) { results.push("✗ brand checks: " + e.message); }
    
    // === ES2023 (ES14) ===
    try { [1,2,3].findLast(x=>x<3); results.push("✓ ES2023: Array.findLast()"); } catch(e) { results.push("✗ findLast: " + e.message); }
    try { [1,2,3].findLastIndex(x=>x<3); results.push("✓ ES2023: Array.findLastIndex()"); } catch(e) { results.push("✗ findLastIndex: " + e.message); }
    try { [3,1,2].toSorted(); results.push("✓ ES2023: Array.toSorted()"); } catch(e) { results.push("✗ toSorted: " + e.message); }
    try { [1,2,3].toReversed(); results.push("✓ ES2023: Array.toReversed()"); } catch(e) { results.push("✗ toReversed: " + e.message); }
    try { [1,2,3].toSpliced(1,1); results.push("✓ ES2023: Array.toSpliced()"); } catch(e) { results.push("✗ toSpliced: " + e.message); }
    try { [1,2,3].with(1,99); results.push("✓ ES2023: Array.with()"); } catch(e) { results.push("✗ Array.with: " + e.message); }
    try { const w = [1]; w[Symbol.isConcatSpreadable] = true; results.push("✓ ES2023: Symbol.isConcatSpreadable"); } catch(e) { results.push("✗ isConcatSpreadable: " + e.message); }
    
    // Hashbang syntax - can't test
    results.push("? ES2023: hashbang (#!) (untestable in function)");
    
    // === ES2024 (ES15) ===
    try { Object.groupBy([1,2,3], x => x%2); results.push("✓ ES2024: Object.groupBy()"); } catch(e) { results.push("✗ Object.groupBy: " + e.message); }
    try { Map.groupBy([1,2,3], x => x%2); results.push("✓ ES2024: Map.groupBy()"); } catch(e) { results.push("✗ Map.groupBy: " + e.message); }
    try { Promise.withResolvers; results.push("✓ ES2024: Promise.withResolvers()"); } catch(e) { results.push("✗ Promise.withResolvers: " + e.message); }
    try { "hello".isWellFormed(); results.push("✓ ES2024: String.isWellFormed()"); } catch(e) { results.push("✗ isWellFormed: " + e.message); }
    try { "hello".toWellFormed(); results.push("✓ ES2024: String.toWellFormed()"); } catch(e) { results.push("✗ toWellFormed: " + e.message); }
    try { Atomics.waitAsync; results.push("✓ ES2024: Atomics.waitAsync()"); } catch(e) { results.push("✗ Atomics.waitAsync: " + e.message); }
    try { ArrayBuffer.prototype.resize; results.push("✓ ES2024: Resizable ArrayBuffer"); } catch(e) { results.push("✗ Resizable ArrayBuffer: " + e.message); }
    
    // /v flag for regex
    try { /[\q{abc}]/v; results.push("✓ ES2024: RegExp v flag"); } catch(e) { results.push("✗ RegExp v flag: " + e.message); }
    
    // === ES2025 (ES16) Proposals ===
    try { Set.prototype.intersection; results.push("✓ ES2025: Set.intersection()"); } catch(e) { results.push("✗ Set.intersection: " + e.message); }
    try { Set.prototype.union; results.push("✓ ES2025: Set.union()"); } catch(e) { results.push("✗ Set.union: " + e.message); }
    try { Set.prototype.difference; results.push("✓ ES2025: Set.difference()"); } catch(e) { results.push("✗ Set.difference: " + e.message); }
    try { Set.prototype.symmetricDifference; results.push("✓ ES2025: Set.symmetricDifference()"); } catch(e) { results.push("✗ Set.symmetricDifference: " + e.message); }
    try { Set.prototype.isSubsetOf; results.push("✓ ES2025: Set.isSubsetOf()"); } catch(e) { results.push("✗ Set.isSubsetOf: " + e.message); }
    try { Iterator.prototype; results.push("✓ ES2025: Iterator helpers"); } catch(e) { results.push("✗ Iterator helpers: " + e.message); }
    
    // Decorators - syntax test
    try { eval("class C { @dec fn(){} }"); results.push("✓ ES2025: decorators syntax"); } catch(e) { results.push("✗ decorators: " + e.message); }
    
    return "=== ES2021-ES2025 TEST RESULTS ===\n" + results.join("\n");
}
