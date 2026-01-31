// ES6/ES2015 Feature Test for Hackmud
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
    
    results.push("=== ES6/ES2015 ===");
    
    // let and const
    test("let declaration", () => { let x = 5; return x === 5; });
    test("let block scope", () => { let x = 1; { let x = 2; } return x === 1; });
    test("const declaration", () => { const x = 5; return x === 5; });
    test("const immutable", () => { const x = 5; try { x = 6; return false; } catch(e) { return true; } });
    test("const object mutable", () => { const o = {a:1}; o.a = 2; return o.a === 2; });
    
    // Arrow functions
    test("arrow function", () => { let f = x => x * 2; return f(3) === 6; });
    test("arrow no args", () => { let f = () => 42; return f() === 42; });
    test("arrow multi args", () => { let f = (a,b) => a + b; return f(2,3) === 5; });
    test("arrow block body", () => { let f = x => { return x * 2; }; return f(3) === 6; });
    test("arrow this binding", () => { let o = { x: 1, f: function() { return (() => this.x)(); } }; return o.f() === 1; });
    
    // Template literals
    test("template literal", () => `hello` === "hello");
    test("template interpolation", () => { let x = 5; return `value: ${x}` === "value: 5"; });
    test("template expression", () => `sum: ${2+3}` === "sum: 5");
    test("template multiline", () => `a\nb`.includes("\n"));
    
    // Destructuring
    test("array destructure", () => { let [a,b] = [1,2]; return a === 1 && b === 2; });
    test("array destructure skip", () => { let [a,,c] = [1,2,3]; return a === 1 && c === 3; });
    test("array destructure rest", () => { let [a,...rest] = [1,2,3]; return rest.length === 2; });
    test("array destructure default", () => { let [a,b=5] = [1]; return b === 5; });
    test("object destructure", () => { let {a,b} = {a:1,b:2}; return a === 1 && b === 2; });
    test("object destructure rename", () => { let {a:x} = {a:1}; return x === 1; });
    test("object destructure default", () => { let {a,b=5} = {a:1}; return b === 5; });
    test("nested destructure", () => { let {a:{b}} = {a:{b:1}}; return b === 1; });
    test("function param destructure", () => { let f = ({a,b}) => a+b; return f({a:1,b:2}) === 3; });
    
    // Default parameters
    test("default param", () => { let f = (x=5) => x; return f() === 5; });
    test("default param expr", () => { let f = (x=2+3) => x; return f() === 5; });
    test("default with value", () => { let f = (x=5) => x; return f(10) === 10; });
    
    // Rest parameters
    test("rest params", () => { let f = (...args) => args.length; return f(1,2,3) === 3; });
    test("rest params mixed", () => { let f = (a,...rest) => rest.length; return f(1,2,3) === 2; });
    
    // Spread operator
    test("spread array", () => { let a = [1,2]; let b = [...a,3]; return b.join(",") === "1,2,3"; });
    test("spread in call", () => Math.max(...[1,5,3]) === 5);
    test("spread object", () => { let o = {...{a:1}, b:2}; return o.a === 1 && o.b === 2; });
    
    // Enhanced object literals
    test("shorthand property", () => { let x = 5; let o = {x}; return o.x === 5; });
    test("shorthand method", () => { let o = { f() { return 42; } }; return o.f() === 42; });
    test("computed property", () => { let key = "x"; let o = {[key]: 5}; return o.x === 5; });
    test("computed method", () => { let key = "f"; let o = {[key]() { return 42; }}; return o.f() === 42; });
    
    // Classes
    test("class declaration", () => { class C { constructor(x) { this.x = x; } } return new C(5).x === 5; });
    test("class method", () => { class C { m() { return 42; } } return new C().m() === 42; });
    test("class getter", () => { class C { get x() { return 42; } } return new C().x === 42; });
    test("class setter", () => { class C { constructor() { this._x = 0; } set x(v) { this._x = v; } } let c = new C(); c.x = 5; return c._x === 5; });
    test("class static", () => { class C { static s() { return 42; } } return C.s() === 42; });
    test("class extends", () => { class A { f() { return 1; } } class B extends A {} return new B().f() === 1; });
    test("class super", () => { class A { f() { return 1; } } class B extends A { f() { return super.f() + 1; } } return new B().f() === 2; });
    
    // Symbol
    test("Symbol exists", () => typeof Symbol === "function");
    test("Symbol creation", () => typeof Symbol() === "symbol");
    test("Symbol unique", () => Symbol() !== Symbol());
    test("Symbol description", () => Symbol("desc").toString().includes("desc"));
    test("Symbol.for", () => Symbol.for("key") === Symbol.for("key"));
    test("Symbol.keyFor", () => Symbol.keyFor(Symbol.for("test")) === "test");
    
    // Iterators
    test("Symbol.iterator", () => typeof Symbol.iterator === "symbol");
    test("array iterator", () => { let a = [1,2,3]; let it = a[Symbol.iterator](); return it.next().value === 1; });
    test("string iterator", () => { let s = "ab"; let it = s[Symbol.iterator](); return it.next().value === "a"; });
    
    // for-of
    test("for-of array", () => { let sum = 0; for (let x of [1,2,3]) sum += x; return sum === 6; });
    test("for-of string", () => { let chars = []; for (let c of "abc") chars.push(c); return chars.join("") === "abc"; });
    
    // Map
    test("Map exists", () => typeof Map === "function");
    test("Map set/get", () => { let m = new Map(); m.set("a", 1); return m.get("a") === 1; });
    test("Map size", () => { let m = new Map(); m.set("a", 1); m.set("b", 2); return m.size === 2; });
    test("Map has", () => { let m = new Map(); m.set("a", 1); return m.has("a") && !m.has("b"); });
    test("Map delete", () => { let m = new Map(); m.set("a", 1); m.delete("a"); return !m.has("a"); });
    test("Map iteration", () => { let m = new Map([["a",1],["b",2]]); return [...m.keys()].join("") === "ab"; });
    test("Map object key", () => { let m = new Map(); let k = {}; m.set(k, 1); return m.get(k) === 1; });
    
    // Set
    test("Set exists", () => typeof Set === "function");
    test("Set add/has", () => { let s = new Set(); s.add(1); return s.has(1); });
    test("Set size", () => { let s = new Set([1,2,3]); return s.size === 3; });
    test("Set unique", () => { let s = new Set([1,1,2,2,3]); return s.size === 3; });
    test("Set delete", () => { let s = new Set([1]); s.delete(1); return !s.has(1); });
    test("Set iteration", () => [...new Set([1,2,3])].join(",") === "1,2,3");
    
    // WeakMap
    test("WeakMap exists", () => typeof WeakMap === "function");
    test("WeakMap set/get", () => { let wm = new WeakMap(); let k = {}; wm.set(k, 1); return wm.get(k) === 1; });
    
    // WeakSet
    test("WeakSet exists", () => typeof WeakSet === "function");
    test("WeakSet add/has", () => { let ws = new WeakSet(); let k = {}; ws.add(k); return ws.has(k); });
    
    // Promise
    test("Promise exists", () => typeof Promise === "function");
    test("Promise.resolve", () => Promise.resolve(42) instanceof Promise);
    test("Promise.reject", () => Promise.reject("err") instanceof Promise);
    
    // Array methods
    test("Array.from", () => Array.from("abc").join("") === "abc");
    test("Array.from mapFn", () => Array.from([1,2,3], x => x*2).join(",") === "2,4,6");
    test("Array.of", () => Array.of(1,2,3).join(",") === "1,2,3");
    test("Array.fill", () => [1,2,3].fill(0).join(",") === "0,0,0");
    test("Array.find", () => [1,2,3].find(x => x > 1) === 2);
    test("Array.findIndex", () => [1,2,3].findIndex(x => x > 1) === 1);
    test("Array.copyWithin", () => [1,2,3,4,5].copyWithin(0,3).join(",") === "4,5,3,4,5");
    test("Array.entries", () => { let e = [1,2].entries(); return e.next().value[0] === 0; });
    test("Array.keys", () => [...[1,2,3].keys()].join(",") === "0,1,2");
    test("Array.values", () => [...[1,2,3].values()].join(",") === "1,2,3");
    
    // String methods
    test("String.startsWith", () => "hello".startsWith("he"));
    test("String.endsWith", () => "hello".endsWith("lo"));
    test("String.includes", () => "hello".includes("ll"));
    test("String.repeat", () => "ab".repeat(3) === "ababab");
    test("String.raw", () => String.raw`a\nb` === "a\\nb");
    
    // Number methods
    test("Number.isFinite", () => Number.isFinite(42) && !Number.isFinite(Infinity));
    test("Number.isInteger", () => Number.isInteger(5) && !Number.isInteger(5.5));
    test("Number.isNaN", () => Number.isNaN(NaN) && !Number.isNaN("NaN"));
    test("Number.isSafeInteger", () => Number.isSafeInteger(5) && !Number.isSafeInteger(9007199254740992));
    test("Number.EPSILON", () => typeof Number.EPSILON === "number");
    test("Number.MAX_SAFE_INTEGER", () => Number.MAX_SAFE_INTEGER === 9007199254740991);
    
    // Math methods
    test("Math.sign", () => Math.sign(-5) === -1 && Math.sign(5) === 1);
    test("Math.trunc", () => Math.trunc(4.7) === 4);
    test("Math.cbrt", () => Math.cbrt(27) === 3);
    test("Math.log2", () => Math.log2(8) === 3);
    test("Math.log10", () => Math.log10(100) === 2);
    test("Math.hypot", () => Math.hypot(3,4) === 5);
    
    // Object.assign
    test("Object.assign", () => { let o = Object.assign({a:1}, {b:2}); return o.a === 1 && o.b === 2; });
    
    // Generators
    test("generator function", () => { function* g() { yield 1; yield 2; } let it = g(); return it.next().value === 1; });
    test("generator yield", () => { function* g() { yield 1; yield 2; } return [...g()].join(",") === "1,2"; });
    test("yield*", () => { function* g1() { yield 1; } function* g2() { yield* g1(); yield 2; } return [...g2()].join(",") === "1,2"; });
    
    // Proxy
    test("Proxy exists", () => typeof Proxy === "function");
    test("Proxy get trap", () => { let p = new Proxy({}, { get: () => 42 }); return p.anything === 42; });
    test("Proxy set trap", () => { let val; let p = new Proxy({}, { set: (t,k,v) => { val = v; return true; } }); p.x = 5; return val === 5; });
    
    // Reflect
    test("Reflect exists", () => typeof Reflect === "object");
    test("Reflect.get", () => Reflect.get({a:1}, "a") === 1);
    test("Reflect.set", () => { let o = {}; Reflect.set(o, "a", 1); return o.a === 1; });
    test("Reflect.has", () => Reflect.has({a:1}, "a") === true);
    
    results.push(`\n--- ES6 Summary: ${passed} passed, ${failed} failed ---`);
    
    return results.join("\n");
}
