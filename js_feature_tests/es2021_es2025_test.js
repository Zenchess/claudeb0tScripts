// ES2021-ES2025 Feature Tests for Hackmud
// Tests: logical assignment, replaceAll, at(), Object.hasOwn, etc.

function(context, args) {
    let results = {};
    
    // ===== ES2021 FEATURES =====
    results["_header_ES2021"] = "=== ES2021 ===";
    
    // 1. Logical assignment operators (&&=, ||=, ??=)
    try {
        let a = 1; a &&= 2;
        let b = 0; b ||= 5;
        let c = null; c ??= 10;
        results.logical_and_assign = a === 2 ? "✅" : "❌";
        results.logical_or_assign = b === 5 ? "✅" : "❌";
        results.nullish_assign = c === 10 ? "✅" : "❌";
    } catch(e) { 
        results.logical_and_assign = "❌ " + e.message;
        results.logical_or_assign = "❌";
        results.nullish_assign = "❌";
    }
    
    // 2. String.prototype.replaceAll
    try {
        results.string_replaceAll = "aabbcc".replaceAll("b", "x") === "aaxxcc" ? "✅" : "❌";
    } catch(e) { results.string_replaceAll = "❌ " + e.message; }
    
    // 3. Promise.any
    try {
        results.promise_any = typeof Promise.any === "function" ? "✅" : "❌";
    } catch(e) { results.promise_any = "❌ " + e.message; }
    
    // 4. WeakRef
    try {
        const obj = { data: 1 };
        const ref = new WeakRef(obj);
        results.weakref = ref.deref()?.data === 1 ? "✅" : "❌";
    } catch(e) { results.weakref = "❌ " + e.message; }
    
    // 5. FinalizationRegistry
    try {
        const registry = new FinalizationRegistry(() => {});
        results.finalization_registry = registry instanceof FinalizationRegistry ? "✅" : "❌";
    } catch(e) { results.finalization_registry = "❌ " + e.message; }
    
    // 6. Numeric separators
    try {
        const num = 1_000_000;
        results.numeric_separators = num === 1000000 ? "✅" : "❌";
    } catch(e) { results.numeric_separators = "❌ " + e.message; }
    
    // ===== ES2022 FEATURES =====
    results["_header_ES2022"] = "=== ES2022 ===";
    
    // 7. Class fields (public)
    try {
        class TestClass {
            publicField = 42;
        }
        const inst = new TestClass();
        results.class_public_fields = inst.publicField === 42 ? "✅" : "❌";
    } catch(e) { results.class_public_fields = "❌ " + e.message; }
    
    // 8. Class private fields (#)
    try {
        class TestClass {
            #privateField = 99;
            getPrivate() { return this.#privateField; }
        }
        const inst = new TestClass();
        results.class_private_fields = inst.getPrivate() === 99 ? "✅" : "❌";
    } catch(e) { results.class_private_fields = "❌ " + e.message; }
    
    // 9. Private methods
    try {
        class TestClass {
            #privateMethod() { return "secret"; }
            callPrivate() { return this.#privateMethod(); }
        }
        const inst = new TestClass();
        results.class_private_methods = inst.callPrivate() === "secret" ? "✅" : "❌";
    } catch(e) { results.class_private_methods = "❌ " + e.message; }
    
    // 10. Static class fields
    try {
        class TestClass {
            static staticField = 123;
        }
        results.class_static_fields = TestClass.staticField === 123 ? "✅" : "❌";
    } catch(e) { results.class_static_fields = "❌ " + e.message; }
    
    // 11. Static initialization blocks
    try {
        class TestClass {
            static value;
            static {
                TestClass.value = 456;
            }
        }
        results.class_static_blocks = TestClass.value === 456 ? "✅" : "❌";
    } catch(e) { results.class_static_blocks = "❌ " + e.message; }
    
    // 12. Top-level await (can't test - no module context)
    results.top_level_await = "⚠️ N/A (no ES modules)";
    
    // 13. Array.prototype.at()
    try {
        const arr = [1, 2, 3, 4, 5];
        results.array_at = (arr.at(0) === 1 && arr.at(-1) === 5) ? "✅" : "❌";
    } catch(e) { results.array_at = "❌ " + e.message; }
    
    // 14. String.prototype.at()
    try {
        results.string_at = ("hello".at(0) === "h" && "hello".at(-1) === "o") ? "✅" : "❌";
    } catch(e) { results.string_at = "❌ " + e.message; }
    
    // 15. Object.hasOwn
    try {
        const obj = { a: 1 };
        results.object_hasOwn = (Object.hasOwn(obj, "a") && !Object.hasOwn(obj, "b")) ? "✅" : "❌";
    } catch(e) { results.object_hasOwn = "❌ " + e.message; }
    
    // 16. Error.cause
    try {
        const error = new Error("outer", { cause: new Error("inner") });
        results.error_cause = error.cause?.message === "inner" ? "✅" : "❌";
    } catch(e) { results.error_cause = "❌ " + e.message; }
    
    // 17. RegExp match indices (d flag)
    try {
        const re = /a+/d;
        const match = re.exec("aaa");
        results.regexp_indices = match.indices[0][0] === 0 ? "✅" : "❌";
    } catch(e) { results.regexp_indices = "❌ " + e.message; }
    
    // ===== ES2023 FEATURES =====
    results["_header_ES2023"] = "=== ES2023 ===";
    
    // 18. Array.prototype.findLast/findLastIndex
    try {
        const arr = [1, 2, 3, 4, 3];
        results.array_findLast = arr.findLast(x => x === 3) === 3 ? "✅" : "❌";
        results.array_findLastIndex = arr.findLastIndex(x => x === 3) === 4 ? "✅" : "❌";
    } catch(e) { 
        results.array_findLast = "❌ " + e.message;
        results.array_findLastIndex = "❌";
    }
    
    // 19. Array.prototype.toSorted (non-mutating)
    try {
        const arr = [3, 1, 2];
        const sorted = arr.toSorted();
        results.array_toSorted = (sorted[0] === 1 && arr[0] === 3) ? "✅" : "❌";
    } catch(e) { results.array_toSorted = "❌ " + e.message; }
    
    // 20. Array.prototype.toReversed (non-mutating)
    try {
        const arr = [1, 2, 3];
        const reversed = arr.toReversed();
        results.array_toReversed = (reversed[0] === 3 && arr[0] === 1) ? "✅" : "❌";
    } catch(e) { results.array_toReversed = "❌ " + e.message; }
    
    // 21. Array.prototype.toSpliced (non-mutating)
    try {
        const arr = [1, 2, 3];
        const spliced = arr.toSpliced(1, 1, 99);
        results.array_toSpliced = (spliced[1] === 99 && arr[1] === 2) ? "✅" : "❌";
    } catch(e) { results.array_toSpliced = "❌ " + e.message; }
    
    // 22. Array.prototype.with (non-mutating)
    try {
        const arr = [1, 2, 3];
        const changed = arr.with(1, 99);
        results.array_with = (changed[1] === 99 && arr[1] === 2) ? "✅" : "❌";
    } catch(e) { results.array_with = "❌ " + e.message; }
    
    // 23. Hashbang grammar (#!/usr/bin/env node)
    results.hashbang = "⚠️ N/A (script context)";
    
    // 24. WeakMap keys with Symbols
    try {
        const sym = Symbol("key");
        const wm = new WeakMap();
        wm.set(sym, "value");
        results.weakmap_symbol_keys = wm.get(sym) === "value" ? "✅" : "❌";
    } catch(e) { results.weakmap_symbol_keys = "❌ " + e.message; }
    
    // ===== ES2024 FEATURES =====
    results["_header_ES2024"] = "=== ES2024 ===";
    
    // 25. Object.groupBy
    try {
        const arr = [{type: "a"}, {type: "b"}, {type: "a"}];
        const grouped = Object.groupBy(arr, item => item.type);
        results.object_groupBy = (grouped.a?.length === 2 && grouped.b?.length === 1) ? "✅" : "❌";
    } catch(e) { results.object_groupBy = "❌ " + e.message; }
    
    // 26. Map.groupBy
    try {
        const arr = [{type: "a", val: 1}, {type: "b", val: 2}];
        const grouped = Map.groupBy(arr, item => item.type);
        results.map_groupBy = grouped.get("a")?.length === 1 ? "✅" : "❌";
    } catch(e) { results.map_groupBy = "❌ " + e.message; }
    
    // 27. Promise.withResolvers
    try {
        const {promise, resolve, reject} = Promise.withResolvers();
        results.promise_withResolvers = (promise instanceof Promise) ? "✅" : "❌";
    } catch(e) { results.promise_withResolvers = "❌ " + e.message; }
    
    // 28. ArrayBuffer.prototype.resize / transfer
    try {
        const ab = new ArrayBuffer(8, { maxByteLength: 16 });
        results.arraybuffer_resizable = ab.resizable === true ? "✅" : "❌";
    } catch(e) { results.arraybuffer_resizable = "❌ " + e.message; }
    
    // 29. Atomics.waitAsync
    try {
        results.atomics_waitAsync = typeof Atomics?.waitAsync === "function" ? "✅" : "❌";
    } catch(e) { results.atomics_waitAsync = "❌ " + e.message; }
    
    // 30. String.prototype.isWellFormed / toWellFormed
    try {
        const wellFormed = "hello".isWellFormed();
        results.string_isWellFormed = wellFormed === true ? "✅" : "❌";
    } catch(e) { results.string_isWellFormed = "❌ " + e.message; }
    
    // ===== ES2025 FEATURES =====
    results["_header_ES2025"] = "=== ES2025 ===";
    
    // 31. Set methods (union, intersection, difference, etc.)
    try {
        const a = new Set([1, 2, 3]);
        const b = new Set([2, 3, 4]);
        const union = a.union(b);
        results.set_union = union.size === 4 ? "✅" : "❌";
    } catch(e) { results.set_union = "❌ " + e.message; }
    
    try {
        const a = new Set([1, 2, 3]);
        const b = new Set([2, 3, 4]);
        const inter = a.intersection(b);
        results.set_intersection = inter.size === 2 ? "✅" : "❌";
    } catch(e) { results.set_intersection = "❌ " + e.message; }
    
    try {
        const a = new Set([1, 2, 3]);
        const b = new Set([2, 3, 4]);
        const diff = a.difference(b);
        results.set_difference = diff.size === 1 && diff.has(1) ? "✅" : "❌";
    } catch(e) { results.set_difference = "❌ " + e.message; }
    
    // 32. RegExp modifiers ((?i:...))
    try {
        const re = /(?i:abc)/;
        results.regexp_modifiers = re.test("ABC") ? "✅" : "❌";
    } catch(e) { results.regexp_modifiers = "❌ " + e.message; }
    
    // 33. Iterator helpers (map, filter, take, drop, etc.)
    try {
        const iter = [1, 2, 3, 4, 5].values();
        const taken = iter.take(3);
        const arr = [...taken];
        results.iterator_take = arr.length === 3 ? "✅" : "❌";
    } catch(e) { results.iterator_take = "❌ " + e.message; }
    
    try {
        const iter = [1, 2, 3].values();
        const mapped = iter.map(x => x * 2);
        const arr = [...mapped];
        results.iterator_map = arr[0] === 2 ? "✅" : "❌";
    } catch(e) { results.iterator_map = "❌ " + e.message; }
    
    // 34. Duplicate named capture groups in alternation
    try {
        const re = /(?<val>a)|(?<val>b)/;
        const m1 = re.exec("a");
        const m2 = re.exec("b");
        results.duplicate_named_groups = (m1.groups.val === "a" && m2.groups.val === "b") ? "✅" : "❌";
    } catch(e) { results.duplicate_named_groups = "❌ " + e.message; }
    
    return { es_version: "ES2021-ES2025", results: results };
}
