// ES2022-ES2025 Feature Test for Hackmud

function(context, args) {
    let results = [];
    
    // === ES2022 (ES13) ===
    results.push("=== ES2022 (ES13) ===");
    
    // Class fields
    class TestClass {
        publicField = 42;
        #privateField = "secret";
        
        getPrivate() { return this.#privateField; }
        
        static staticField = "static";
        static #privateStatic = "private static";
        static getPrivateStatic() { return TestClass.#privateStatic; }
    }
    
    const tc = new TestClass();
    results.push("public class field: " + (tc.publicField === 42 ? "✓" : "✗"));
    results.push("private #field: " + (tc.getPrivate() === "secret" ? "✓" : "✗"));
    results.push("static field: " + (TestClass.staticField === "static" ? "✓" : "✗"));
    results.push("private static: " + (TestClass.getPrivateStatic() === "private static" ? "✓" : "✗"));
    
    // at() method
    results.push("Array.at(-1): " + ([1,2,3].at(-1) === 3 ? "✓" : "✗"));
    results.push("String.at(-1): " + ("abc".at(-1) === "c" ? "✓" : "✗"));
    
    // Object.hasOwn
    const hasOwnObj = {a: 1};
    results.push("Object.hasOwn: " + (Object.hasOwn(hasOwnObj, "a") ? "✓" : "✗"));
    
    // Error cause
    try {
        const err = new Error("outer", {cause: new Error("inner")});
        results.push("Error.cause: " + (err.cause?.message === "inner" ? "✓" : "✗"));
    } catch (e) {
        results.push("Error.cause: ✗ (" + e.message + ")");
    }
    
    // === ES2023 (ES14) ===
    results.push("\n=== ES2023 (ES14) ===");
    
    const arr = [1, 2, 3, 4, 5];
    
    // findLast / findLastIndex
    results.push("findLast: " + (arr.findLast(x => x > 2) === 5 ? "✓" : "✗"));
    results.push("findLastIndex: " + (arr.findLastIndex(x => x > 2) === 4 ? "✓" : "✗"));
    
    // Non-mutating array methods
    const original = [3, 1, 2];
    
    try {
        const reversed = original.toReversed();
        results.push("toReversed: " + (reversed.join(",") === "2,1,3" && original[0] === 3 ? "✓" : "✗"));
    } catch (e) {
        results.push("toReversed: ✗ (" + e.message + ")");
    }
    
    try {
        const sorted = original.toSorted();
        results.push("toSorted: " + (sorted.join(",") === "1,2,3" && original[0] === 3 ? "✓" : "✗"));
    } catch (e) {
        results.push("toSorted: ✗ (" + e.message + ")");
    }
    
    try {
        const spliced = [1,2,3,4].toSpliced(1, 2, "a", "b");
        results.push("toSpliced: " + (spliced.join(",") === "1,a,b,4" ? "✓" : "✗"));
    } catch (e) {
        results.push("toSpliced: ✗ (" + e.message + ")");
    }
    
    try {
        const withArr = [1,2,3].with(1, 99);
        results.push("Array.with: " + (withArr.join(",") === "1,99,3" ? "✓" : "✗"));
    } catch (e) {
        results.push("Array.with: ✗ (" + e.message + ")");
    }
    
    // === ES2024 (ES15) ===
    results.push("\n=== ES2024 (ES15) ===");
    
    // Object.groupBy
    try {
        const grouped = Object.groupBy([1,2,3,4,5], x => x % 2 === 0 ? "even" : "odd");
        results.push("Object.groupBy: " + (grouped.odd.length === 3 ? "✓" : "✗"));
    } catch (e) {
        results.push("Object.groupBy: ✗ (" + e.message + ")");
    }
    
    // Map.groupBy
    try {
        const mapGrouped = Map.groupBy([1,2,3], x => x % 2);
        results.push("Map.groupBy: " + (mapGrouped instanceof Map ? "✓" : "✗"));
    } catch (e) {
        results.push("Map.groupBy: ✗ (" + e.message + ")");
    }
    
    // Promise.withResolvers
    try {
        const {promise, resolve, reject} = Promise.withResolvers();
        results.push("Promise.withResolvers: " + (typeof resolve === "function" ? "✓" : "✗"));
    } catch (e) {
        results.push("Promise.withResolvers: ✗ (" + e.message + ")");
    }
    
    // === ES2025 (ES16) ===
    results.push("\n=== ES2025 (ES16) ===");
    
    const setA = new Set([1, 2, 3]);
    const setB = new Set([2, 3, 4]);
    
    // Set methods
    try {
        results.push("Set.union: " + (setA.union(setB).size === 4 ? "✓" : "✗"));
    } catch (e) {
        results.push("Set.union: ✗ (" + e.message + ")");
    }
    
    try {
        results.push("Set.intersection: " + (setA.intersection(setB).size === 2 ? "✓" : "✗"));
    } catch (e) {
        results.push("Set.intersection: ✗ (" + e.message + ")");
    }
    
    try {
        results.push("Set.difference: " + (setA.difference(setB).size === 1 ? "✓" : "✗"));
    } catch (e) {
        results.push("Set.difference: ✗ (" + e.message + ")");
    }
    
    try {
        results.push("Set.symmetricDiff: " + (setA.symmetricDifference(setB).size === 2 ? "✓" : "✗"));
    } catch (e) {
        results.push("Set.symmetricDiff: ✗ (" + e.message + ")");
    }
    
    try {
        results.push("Set.isSubsetOf: " + (new Set([1,2]).isSubsetOf(setA) ? "✓" : "✗"));
    } catch (e) {
        results.push("Set.isSubsetOf: ✗ (" + e.message + ")");
    }
    
    return results.join("\n");
}
