// ES2016-ES2020 Feature Tests for Hackmud
// Tests: **, includes, async/await, Object.entries/values, etc.

function(context, args) {
    let results = {};
    
    // ===== ES2016 FEATURES =====
    results["_header_ES2016"] = "=== ES2016 ===";
    
    // 1. Exponentiation operator (**)
    try {
        results.exponentiation = (2 ** 10 === 1024) ? "✅" : "❌";
    } catch(e) { results.exponentiation = "❌ " + e.message; }
    
    // 2. Array.prototype.includes
    try {
        results.array_includes = ([1, 2, 3].includes(2) && ![1, 2, 3].includes(5)) ? "✅" : "❌";
    } catch(e) { results.array_includes = "❌ " + e.message; }
    
    // ===== ES2017 FEATURES =====
    results["_header_ES2017"] = "=== ES2017 ===";
    
    // 3. Object.values
    try {
        const vals = Object.values({a: 1, b: 2, c: 3});
        results.object_values = (vals.length === 3 && vals.includes(2)) ? "✅" : "❌";
    } catch(e) { results.object_values = "❌ " + e.message; }
    
    // 4. Object.entries
    try {
        const entries = Object.entries({a: 1, b: 2});
        results.object_entries = (entries.length === 2 && entries[0][0] === "a") ? "✅" : "❌";
    } catch(e) { results.object_entries = "❌ " + e.message; }
    
    // 5. String.prototype.padStart
    try {
        results.string_padStart = "5".padStart(3, "0") === "005" ? "✅" : "❌";
    } catch(e) { results.string_padStart = "❌ " + e.message; }
    
    // 6. String.prototype.padEnd
    try {
        results.string_padEnd = "5".padEnd(3, "0") === "500" ? "✅" : "❌";
    } catch(e) { results.string_padEnd = "❌ " + e.message; }
    
    // 7. Object.getOwnPropertyDescriptors
    try {
        const descs = Object.getOwnPropertyDescriptors({x: 1});
        results.object_getOwnPropertyDescriptors = descs.x.value === 1 ? "✅" : "❌";
    } catch(e) { results.object_getOwnPropertyDescriptors = "❌ " + e.message; }
    
    // 8. Trailing commas in function params
    try {
        const fn = (a, b,) => a + b;
        results.trailing_commas = fn(1, 2) === 3 ? "✅" : "❌";
    } catch(e) { results.trailing_commas = "❌ " + e.message; }
    
    // 9. async/await (basic)
    try {
        // Can't fully test async in sync context, but check if syntax works
        const asyncFn = async () => 42;
        results.async_function_syntax = typeof asyncFn === "function" ? "✅ (syntax ok)" : "❌";
    } catch(e) { results.async_function_syntax = "❌ " + e.message; }
    
    // 10. Async function returns Promise
    try {
        const asyncFn = async () => 42;
        const result = asyncFn();
        results.async_returns_promise = result instanceof Promise ? "✅" : "❌";
    } catch(e) { results.async_returns_promise = "❌ " + e.message; }
    
    // ===== ES2018 FEATURES =====
    results["_header_ES2018"] = "=== ES2018 ===";
    
    // 11. Object rest/spread in destructuring
    try {
        const {a, ...rest} = {a: 1, b: 2, c: 3};
        results.object_rest = (a === 1 && rest.b === 2 && rest.c === 3) ? "✅" : "❌";
    } catch(e) { results.object_rest = "❌ " + e.message; }
    
    // 12. Promise.prototype.finally
    try {
        let called = false;
        Promise.resolve(1).finally(() => { called = true; });
        results.promise_finally = typeof Promise.prototype.finally === "function" ? "✅" : "❌";
    } catch(e) { results.promise_finally = "❌ " + e.message; }
    
    // 13. Async iteration (for await...of) - syntax check
    try {
        // Can't run actual async iteration, but check if async generator syntax works
        const asyncGen = async function*() { yield 1; };
        results.async_generator_syntax = typeof asyncGen === "function" ? "✅ (syntax ok)" : "❌";
    } catch(e) { results.async_generator_syntax = "❌ " + e.message; }
    
    // 14. RegExp named capture groups
    try {
        const re = /(?<year>\d{4})-(?<month>\d{2})/;
        const match = re.exec("2026-01");
        results.regexp_named_groups = match.groups.year === "2026" ? "✅" : "❌";
    } catch(e) { results.regexp_named_groups = "❌ " + e.message; }
    
    // 15. RegExp lookbehind assertions
    try {
        const re = /(?<=@)\w+/;
        const match = re.exec("user@domain");
        results.regexp_lookbehind = match[0] === "domain" ? "✅" : "❌";
    } catch(e) { results.regexp_lookbehind = "❌ " + e.message; }
    
    // 16. RegExp dotAll flag (s)
    try {
        const re = /foo.bar/s;
        results.regexp_dotAll = re.test("foo\nbar") ? "✅" : "❌";
    } catch(e) { results.regexp_dotAll = "❌ " + e.message; }
    
    // 17. RegExp Unicode property escapes
    try {
        const re = /\p{Script=Greek}/u;
        results.regexp_unicode_props = re.test("α") ? "✅" : "❌";
    } catch(e) { results.regexp_unicode_props = "❌ " + e.message; }
    
    // ===== ES2019 FEATURES =====
    results["_header_ES2019"] = "=== ES2019 ===";
    
    // 18. Array.prototype.flat
    try {
        const arr = [1, [2, [3]]].flat(2);
        results.array_flat = arr.length === 3 && arr[2] === 3 ? "✅" : "❌";
    } catch(e) { results.array_flat = "❌ " + e.message; }
    
    // 19. Array.prototype.flatMap
    try {
        const arr = [1, 2].flatMap(x => [x, x * 2]);
        results.array_flatMap = arr.length === 4 && arr[1] === 2 ? "✅" : "❌";
    } catch(e) { results.array_flatMap = "❌ " + e.message; }
    
    // 20. Object.fromEntries
    try {
        const obj = Object.fromEntries([["a", 1], ["b", 2]]);
        results.object_fromEntries = (obj.a === 1 && obj.b === 2) ? "✅" : "❌";
    } catch(e) { results.object_fromEntries = "❌ " + e.message; }
    
    // 21. String.prototype.trimStart/trimEnd
    try {
        results.string_trimStart = "  hi".trimStart() === "hi" ? "✅" : "❌";
    } catch(e) { results.string_trimStart = "❌ " + e.message; }
    
    try {
        results.string_trimEnd = "hi  ".trimEnd() === "hi" ? "✅" : "❌";
    } catch(e) { results.string_trimEnd = "❌ " + e.message; }
    
    // 22. Symbol.prototype.description
    try {
        const sym = Symbol("test");
        results.symbol_description = sym.description === "test" ? "✅" : "❌";
    } catch(e) { results.symbol_description = "❌ " + e.message; }
    
    // 23. Optional catch binding
    try {
        // try { throw "err"; } catch { /* no binding */ }
        eval('try { throw "x"; } catch { }');
        results.optional_catch_binding = "✅";
    } catch(e) { results.optional_catch_binding = "❌ " + e.message; }
    
    // 24. JSON superset (line separator U+2028, paragraph separator U+2029 in strings)
    try {
        const str = JSON.parse('"\\u2028\\u2029"');
        results.json_superset = str.length === 2 ? "✅" : "❌";
    } catch(e) { results.json_superset = "❌ " + e.message; }
    
    // ===== ES2020 FEATURES =====
    results["_header_ES2020"] = "=== ES2020 ===";
    
    // 25. Optional chaining (?.)
    try {
        const obj = { a: { b: 1 } };
        const val = obj?.a?.b;
        const undef = obj?.x?.y;
        results.optional_chaining = (val === 1 && undef === undefined) ? "✅" : "❌";
    } catch(e) { results.optional_chaining = "❌ " + e.message; }
    
    // 26. Nullish coalescing (??)
    try {
        const a = null ?? "default";
        const b = 0 ?? "default";
        results.nullish_coalescing = (a === "default" && b === 0) ? "✅" : "❌";
    } catch(e) { results.nullish_coalescing = "❌ " + e.message; }
    
    // 27. BigInt
    try {
        const big = BigInt(9007199254740991);
        const bigLiteral = 9007199254740991n;
        results.bigint = (typeof big === "bigint" && bigLiteral + 1n > big) ? "✅" : "❌";
    } catch(e) { results.bigint = "❌ " + e.message; }
    
    // 28. Promise.allSettled
    try {
        results.promise_allSettled = typeof Promise.allSettled === "function" ? "✅" : "❌";
    } catch(e) { results.promise_allSettled = "❌ " + e.message; }
    
    // 29. globalThis
    try {
        results.globalThis = typeof globalThis !== "undefined" ? "✅" : "❌";
    } catch(e) { results.globalThis = "❌ " + e.message; }
    
    // 30. String.prototype.matchAll
    try {
        const str = "test1test2";
        const matches = [...str.matchAll(/test(\d)/g)];
        results.string_matchAll = (matches.length === 2 && matches[0][1] === "1") ? "✅" : "❌";
    } catch(e) { results.string_matchAll = "❌ " + e.message; }
    
    // 31. import.meta (can't test in hackmud context - no modules)
    results.import_meta = "⚠️ N/A (no ES modules)";
    
    // 32. Dynamic import() - likely blocked
    try {
        // This will probably fail in hackmud
        results.dynamic_import = "⚠️ untested (likely blocked)";
    } catch(e) { results.dynamic_import = "❌ " + e.message; }
    
    return { es_version: "ES2016-ES2020", results: results };
}
