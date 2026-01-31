// ES6/ES2015 Feature Tests for Hackmud
// Tests: let, const, arrow functions, classes, template literals, destructuring, etc.

function(context, args) {
    let results = {};
    
    // ===== ES6/ES2015 FEATURES =====
    
    // 1. let declaration
    try {
        let x = 42;
        results.let_declaration = x === 42 ? "✅" : "❌";
    } catch(e) { results.let_declaration = "❌ " + e.message; }
    
    // 2. const declaration
    try {
        const PI = 3.14159;
        results.const_declaration = PI === 3.14159 ? "✅" : "❌";
    } catch(e) { results.const_declaration = "❌ " + e.message; }
    
    // 3. Block scoping
    try {
        let outer = "outer";
        { let inner = "inner"; }
        // inner should not be accessible here
        results.block_scoping = outer === "outer" ? "✅" : "❌";
    } catch(e) { results.block_scoping = "❌ " + e.message; }
    
    // 4. Arrow functions (basic)
    try {
        const add = (a, b) => a + b;
        results.arrow_function_basic = add(2, 3) === 5 ? "✅" : "❌";
    } catch(e) { results.arrow_function_basic = "❌ " + e.message; }
    
    // 5. Arrow functions (single param no parens)
    try {
        const double = x => x * 2;
        results.arrow_function_single_param = double(5) === 10 ? "✅" : "❌";
    } catch(e) { results.arrow_function_single_param = "❌ " + e.message; }
    
    // 6. Arrow functions with block body
    try {
        const compute = (x) => {
            const y = x * 2;
            return y + 1;
        };
        results.arrow_function_block = compute(3) === 7 ? "✅" : "❌";
    } catch(e) { results.arrow_function_block = "❌ " + e.message; }
    
    // 7. Template literals
    try {
        const name = "World";
        const greeting = `Hello, ${name}!`;
        results.template_literals = greeting === "Hello, World!" ? "✅" : "❌";
    } catch(e) { results.template_literals = "❌ " + e.message; }
    
    // 8. Multi-line template strings
    try {
        const multi = `line1
line2`;
        results.template_multiline = multi.includes("\n") ? "✅" : "❌";
    } catch(e) { results.template_multiline = "❌ " + e.message; }
    
    // 9. Object destructuring
    try {
        const obj = { a: 1, b: 2 };
        const { a, b } = obj;
        results.object_destructuring = (a === 1 && b === 2) ? "✅" : "❌";
    } catch(e) { results.object_destructuring = "❌ " + e.message; }
    
    // 10. Array destructuring
    try {
        const arr = [1, 2, 3];
        const [first, second] = arr;
        results.array_destructuring = (first === 1 && second === 2) ? "✅" : "❌";
    } catch(e) { results.array_destructuring = "❌ " + e.message; }
    
    // 11. Destructuring with defaults
    try {
        const { x = 10, y = 20 } = { x: 5 };
        results.destructuring_defaults = (x === 5 && y === 20) ? "✅" : "❌";
    } catch(e) { results.destructuring_defaults = "❌ " + e.message; }
    
    // 12. Rest parameters
    try {
        const sum = (...nums) => nums.reduce((a, b) => a + b, 0);
        results.rest_parameters = sum(1, 2, 3, 4) === 10 ? "✅" : "❌";
    } catch(e) { results.rest_parameters = "❌ " + e.message; }
    
    // 13. Spread operator (arrays)
    try {
        const a = [1, 2];
        const b = [...a, 3, 4];
        results.spread_array = (b.length === 4 && b[2] === 3) ? "✅" : "❌";
    } catch(e) { results.spread_array = "❌ " + e.message; }
    
    // 14. Spread operator (objects)
    try {
        const obj1 = { a: 1 };
        const obj2 = { ...obj1, b: 2 };
        results.spread_object = (obj2.a === 1 && obj2.b === 2) ? "✅" : "❌";
    } catch(e) { results.spread_object = "❌ " + e.message; }
    
    // 15. Default parameters
    try {
        const greet = (name = "Guest") => `Hi, ${name}`;
        results.default_params = greet() === "Hi, Guest" ? "✅" : "❌";
    } catch(e) { results.default_params = "❌ " + e.message; }
    
    // 16. Classes
    try {
        class Animal {
            constructor(name) { this.name = name; }
            speak() { return `${this.name} speaks`; }
        }
        const dog = new Animal("Dog");
        results.classes = dog.speak() === "Dog speaks" ? "✅" : "❌";
    } catch(e) { results.classes = "❌ " + e.message; }
    
    // 17. Class inheritance (extends)
    try {
        class Base { greet() { return "base"; } }
        class Derived extends Base { greet() { return super.greet() + "-derived"; } }
        const d = new Derived();
        results.class_extends = d.greet() === "base-derived" ? "✅" : "❌";
    } catch(e) { results.class_extends = "❌ " + e.message; }
    
    // 18. Static class methods
    try {
        class Utils { static add(a, b) { return a + b; } }
        results.class_static = Utils.add(2, 3) === 5 ? "✅" : "❌";
    } catch(e) { results.class_static = "❌ " + e.message; }
    
    // 19. Shorthand object properties
    try {
        const x = 1, y = 2;
        const obj = { x, y };
        results.shorthand_props = (obj.x === 1 && obj.y === 2) ? "✅" : "❌";
    } catch(e) { results.shorthand_props = "❌ " + e.message; }
    
    // 20. Shorthand method definitions
    try {
        const obj = { greet() { return "hi"; } };
        results.shorthand_methods = obj.greet() === "hi" ? "✅" : "❌";
    } catch(e) { results.shorthand_methods = "❌ " + e.message; }
    
    // 21. Computed property names
    try {
        const key = "dynamic";
        const obj = { [key]: 42 };
        results.computed_props = obj.dynamic === 42 ? "✅" : "❌";
    } catch(e) { results.computed_props = "❌ " + e.message; }
    
    // 22. for-of loop
    try {
        let sum = 0;
        for (const n of [1, 2, 3]) { sum += n; }
        results.for_of = sum === 6 ? "✅" : "❌";
    } catch(e) { results.for_of = "❌ " + e.message; }
    
    // 23. Symbol
    try {
        const sym = Symbol("test");
        results.symbol = typeof sym === "symbol" ? "✅" : "❌";
    } catch(e) { results.symbol = "❌ " + e.message; }
    
    // 24. Map
    try {
        const map = new Map();
        map.set("key", "value");
        results.map = map.get("key") === "value" ? "✅" : "❌";
    } catch(e) { results.map = "❌ " + e.message; }
    
    // 25. Set
    try {
        const set = new Set([1, 2, 2, 3]);
        results.set = set.size === 3 ? "✅" : "❌";
    } catch(e) { results.set = "❌ " + e.message; }
    
    // 26. WeakMap
    try {
        const wm = new WeakMap();
        const key = {};
        wm.set(key, "val");
        results.weakmap = wm.get(key) === "val" ? "✅" : "❌";
    } catch(e) { results.weakmap = "❌ " + e.message; }
    
    // 27. WeakSet
    try {
        const ws = new WeakSet();
        const obj = {};
        ws.add(obj);
        results.weakset = ws.has(obj) ? "✅" : "❌";
    } catch(e) { results.weakset = "❌ " + e.message; }
    
    // 28. Promise
    try {
        const p = new Promise((resolve) => resolve(42));
        results.promise = p instanceof Promise ? "✅" : "❌";
    } catch(e) { results.promise = "❌ " + e.message; }
    
    // 29. Promise.resolve/reject
    try {
        const resolved = Promise.resolve(1);
        results.promise_resolve = resolved instanceof Promise ? "✅" : "❌";
    } catch(e) { results.promise_resolve = "❌ " + e.message; }
    
    // 30. Number methods (isNaN, isFinite, isInteger)
    try {
        results.number_methods = (Number.isNaN(NaN) && Number.isFinite(42) && Number.isInteger(5)) ? "✅" : "❌";
    } catch(e) { results.number_methods = "❌ " + e.message; }
    
    // 31. Object.assign
    try {
        const target = { a: 1 };
        const result = Object.assign(target, { b: 2 });
        results.object_assign = (result.a === 1 && result.b === 2) ? "✅" : "❌";
    } catch(e) { results.object_assign = "❌ " + e.message; }
    
    // 32. Object.is
    try {
        results.object_is = (Object.is(NaN, NaN) && !Object.is(0, -0)) ? "✅" : "❌";
    } catch(e) { results.object_is = "❌ " + e.message; }
    
    // 33. Array.from
    try {
        const arr = Array.from("abc");
        results.array_from = (arr.length === 3 && arr[0] === "a") ? "✅" : "❌";
    } catch(e) { results.array_from = "❌ " + e.message; }
    
    // 34. Array.of
    try {
        const arr = Array.of(1, 2, 3);
        results.array_of = (arr.length === 3 && arr[1] === 2) ? "✅" : "❌";
    } catch(e) { results.array_of = "❌ " + e.message; }
    
    // 35. Array.prototype.find
    try {
        const found = [1, 2, 3, 4].find(x => x > 2);
        results.array_find = found === 3 ? "✅" : "❌";
    } catch(e) { results.array_find = "❌ " + e.message; }
    
    // 36. Array.prototype.findIndex
    try {
        const idx = [1, 2, 3, 4].findIndex(x => x > 2);
        results.array_findIndex = idx === 2 ? "✅" : "❌";
    } catch(e) { results.array_findIndex = "❌ " + e.message; }
    
    // 37. Array.prototype.fill
    try {
        const arr = [1, 2, 3].fill(0);
        results.array_fill = (arr[0] === 0 && arr[2] === 0) ? "✅" : "❌";
    } catch(e) { results.array_fill = "❌ " + e.message; }
    
    // 38. Array.prototype.copyWithin
    try {
        const arr = [1, 2, 3, 4, 5].copyWithin(0, 3);
        results.array_copyWithin = arr[0] === 4 ? "✅" : "❌";
    } catch(e) { results.array_copyWithin = "❌ " + e.message; }
    
    // 39. String.prototype.includes
    try {
        results.string_includes = "hello world".includes("world") ? "✅" : "❌";
    } catch(e) { results.string_includes = "❌ " + e.message; }
    
    // 40. String.prototype.startsWith/endsWith
    try {
        results.string_startsEndsWith = ("hello".startsWith("he") && "hello".endsWith("lo")) ? "✅" : "❌";
    } catch(e) { results.string_startsEndsWith = "❌ " + e.message; }
    
    // 41. String.prototype.repeat
    try {
        results.string_repeat = "ab".repeat(3) === "ababab" ? "✅" : "❌";
    } catch(e) { results.string_repeat = "❌ " + e.message; }
    
    return { es_version: "ES6/ES2015", results: results };
}
