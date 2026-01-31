// ES2016-ES2021 Feature Test for Hackmud

function(context, args) {
    let results = [];
    
    // === ES2016 (ES7) ===
    results.push("=== ES2016 (ES7) ===");
    results.push("Array.includes: " + ([1,2,3].includes(2) ? "✓" : "✗"));
    results.push("Exponent **: " + (2 ** 10 === 1024 ? "✓" : "✗"));
    
    // === ES2017 (ES8) ===
    results.push("\n=== ES2017 (ES8) ===");
    results.push("Object.values: " + (Object.values({a:1,b:2}).join(",") === "1,2" ? "✓" : "✗"));
    results.push("Object.entries: " + (Object.entries({a:1}).length === 1 ? "✓" : "✗"));
    results.push("padStart: " + ("5".padStart(3, "0") === "005" ? "✓" : "✗"));
    results.push("padEnd: " + ("5".padEnd(3, "0") === "500" ? "✓" : "✗"));
    
    // async/await - can't fully test without actual async operations
    results.push("async function exists: " + (typeof (async () => {}) === "function" ? "✓" : "✗"));
    
    // === ES2018 (ES9) ===
    results.push("\n=== ES2018 (ES9) ===");
    
    // Object spread/rest
    const obj1 = {a: 1, b: 2};
    const obj2 = {...obj1, c: 3};
    results.push("object spread: " + (obj2.c === 3 && obj2.a === 1 ? "✓" : "✗"));
    
    const {a, ...rest} = {a: 1, b: 2, c: 3};
    results.push("object rest: " + (rest.b === 2 && rest.c === 3 ? "✓" : "✗"));
    
    // Regex named groups
    const namedMatch = "2026-01-30".match(/(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})/);
    results.push("regex named groups: " + (namedMatch && namedMatch.groups && namedMatch.groups.year === "2026" ? "✓" : "✗"));
    
    // === ES2019 (ES10) ===
    results.push("\n=== ES2019 (ES10) ===");
    
    results.push("Array.flat: " + ([[1,2],[3,4]].flat().join(",") === "1,2,3,4" ? "✓" : "✗"));
    results.push("Array.flatMap: " + ([1,2].flatMap(x => [x, x*2]).join(",") === "1,2,2,4" ? "✓" : "✗"));
    results.push("Object.fromEntries: " + (Object.fromEntries([["a",1],["b",2]]).a === 1 ? "✓" : "✗"));
    results.push("trimStart: " + ("  hi".trimStart() === "hi" ? "✓" : "✗"));
    results.push("trimEnd: " + ("hi  ".trimEnd() === "hi" ? "✓" : "✗"));
    
    // Optional catch binding
    let catchBindingWorks = false;
    try {
        eval("try { throw 1 } catch { catchBindingWorks = true }");
        eval("catchBindingWorks = true");
    } catch (e) {
        // If eval fails, try direct
        try { throw 1; } catch { catchBindingWorks = true; }
    }
    results.push("optional catch binding: " + (catchBindingWorks ? "✓" : "⚠️ (eval needed)"));
    
    // === ES2020 (ES11) ===
    results.push("\n=== ES2020 (ES11) ===");
    
    // Optional chaining
    const obj3 = {a: {b: {c: 42}}};
    results.push("optional ?. : " + (obj3?.a?.b?.c === 42 ? "✓" : "✗"));
    results.push("optional ?. null: " + (obj3?.x?.y?.z === undefined ? "✓" : "✗"));
    
    // Nullish coalescing
    const nullVal = null;
    const zeroVal = 0;
    results.push("nullish ?? : " + ((nullVal ?? "default") === "default" ? "✓" : "✗"));
    results.push("?? with 0: " + ((zeroVal ?? "default") === 0 ? "✓" : "✗"));
    
    // BigInt
    try {
        const big = BigInt(9007199254740993);
        results.push("BigInt: " + (typeof big === "bigint" ? "✓" : "✗"));
    } catch (e) {
        results.push("BigInt: ✗ (" + e.message + ")");
    }
    
    // globalThis
    results.push("globalThis: " + (typeof globalThis !== "undefined" ? "✓" : "✗"));
    
    // matchAll
    const matches = [...("test1test2".matchAll(/test(\d)/g))];
    results.push("String.matchAll: " + (matches.length === 2 ? "✓" : "✗"));
    
    // === ES2021 (ES12) ===
    results.push("\n=== ES2021 (ES12) ===");
    
    results.push("replaceAll: " + ("aaa".replaceAll("a", "b") === "bbb" ? "✓" : "✗"));
    
    // Logical assignment
    let logOr = null;
    logOr ||= "default";
    results.push("||= : " + (logOr === "default" ? "✓" : "✗"));
    
    let logAnd = "value";
    logAnd &&= "updated";
    results.push("&&= : " + (logAnd === "updated" ? "✓" : "✗"));
    
    let logNull = null;
    logNull ??= "fallback";
    results.push("??= : " + (logNull === "fallback" ? "✓" : "✗"));
    
    // Numeric separators
    const bigNum = 1_000_000;
    results.push("numeric separators: " + (bigNum === 1000000 ? "✓" : "✗"));
    
    // WeakRef (may not be available)
    try {
        const ref = new WeakRef({});
        results.push("WeakRef: " + (ref.deref() !== undefined ? "✓" : "✗"));
    } catch (e) {
        results.push("WeakRef: ✗ (not available)");
    }
    
    return results.join("\n");
}
