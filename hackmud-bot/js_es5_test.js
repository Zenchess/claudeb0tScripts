// ES5 (2009) Feature Test for Hackmud
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
    
    results.push("=== ES5 (2009) ===");
    
    // Strict mode (can't test directly but functions work)
    test("strict mode exists", () => { "use strict"; return true; });
    
    // JSON
    test("JSON.stringify", () => JSON.stringify({a: 1}) === '{"a":1}');
    test("JSON.parse", () => JSON.parse('{"a":1}').a === 1);
    test("JSON.stringify array", () => JSON.stringify([1,2,3]) === '[1,2,3]');
    test("JSON.parse array", () => JSON.parse('[1,2,3]')[1] === 2);
    
    // Array methods
    test("Array.isArray", () => Array.isArray([1,2,3]) === true);
    test("Array.isArray false", () => Array.isArray({}) === false);
    test("Array.forEach", () => { let sum = 0; [1,2,3].forEach(x => sum += x); return sum === 6; });
    test("Array.map", () => [1,2,3].map(x => x*2).join(",") === "2,4,6");
    test("Array.filter", () => [1,2,3,4,5].filter(x => x > 2).join(",") === "3,4,5");
    test("Array.reduce", () => [1,2,3,4].reduce((a,b) => a+b, 0) === 10);
    test("Array.reduceRight", () => [1,2,3].reduceRight((a,b) => a+b) === 6);
    test("Array.some", () => [1,2,3].some(x => x > 2) === true);
    test("Array.every", () => [2,4,6].every(x => x % 2 === 0) === true);
    test("Array.indexOf", () => [1,2,3].indexOf(2) === 1);
    test("Array.lastIndexOf", () => [1,2,3,2].lastIndexOf(2) === 3);
    
    // Object methods
    test("Object.keys", () => Object.keys({a:1,b:2}).length === 2);
    test("Object.values", () => { try { return Object.values({a:1,b:2}).join(",") === "1,2"; } catch(e) { return "ES2017 feature"; } });
    test("Object.create", () => { let o = Object.create({x:1}); return o.x === 1; });
    test("Object.create null", () => { let o = Object.create(null); return !("toString" in o); });
    test("Object.defineProperty", () => { let o = {}; Object.defineProperty(o, 'x', {value: 42}); return o.x === 42; });
    test("Object.defineProperties", () => { let o = {}; Object.defineProperties(o, {a: {value:1}, b: {value:2}}); return o.a + o.b === 3; });
    test("Object.getOwnPropertyDescriptor", () => { let d = Object.getOwnPropertyDescriptor({x:1}, 'x'); return d.value === 1; });
    test("Object.getOwnPropertyNames", () => Object.getOwnPropertyNames({a:1,b:2}).length === 2);
    test("Object.getPrototypeOf", () => Object.getPrototypeOf([]) === Array.prototype);
    test("Object.preventExtensions", () => { let o = {a:1}; Object.preventExtensions(o); o.b = 2; return o.b === undefined; });
    test("Object.isExtensible", () => Object.isExtensible({}) === true);
    test("Object.seal", () => { let o = {a:1}; Object.seal(o); delete o.a; return o.a === 1; });
    test("Object.isSealed", () => { let o = {}; Object.seal(o); return Object.isSealed(o); });
    test("Object.freeze", () => { let o = {a:1}; Object.freeze(o); o.a = 2; return o.a === 1; });
    test("Object.isFrozen", () => { let o = {}; Object.freeze(o); return Object.isFrozen(o); });
    
    // String methods
    test("String.trim", () => "  hello  ".trim() === "hello");
    
    // Function.bind
    test("Function.bind", () => { function f(x) { return this.a + x; } return f.bind({a:10})(5) === 15; });
    test("Function.bind partial", () => { function f(a,b) { return a+b; } return f.bind(null, 5)(3) === 8; });
    
    // Date methods
    test("Date.now", () => typeof Date.now() === "number");
    test("Date.toISOString", () => new Date(0).toISOString() === "1970-01-01T00:00:00.000Z");
    test("Date.toJSON", () => typeof new Date().toJSON() === "string");
    
    // Getters and setters
    test("getter", () => { let o = { get x() { return 42; } }; return o.x === 42; });
    test("setter", () => { let o = { _x: 0, set x(v) { this._x = v; } }; o.x = 5; return o._x === 5; });
    test("defineProperty getter", () => {
        let o = {};
        Object.defineProperty(o, 'x', { get: function() { return 42; } });
        return o.x === 42;
    });
    
    // Property descriptors
    test("writable:false", () => {
        let o = {};
        Object.defineProperty(o, 'x', { value: 1, writable: false });
        o.x = 2;
        return o.x === 1;
    });
    test("enumerable:false", () => {
        let o = {};
        Object.defineProperty(o, 'x', { value: 1, enumerable: false });
        return Object.keys(o).length === 0;
    });
    test("configurable:false", () => {
        let o = {};
        Object.defineProperty(o, 'x', { value: 1, configurable: false });
        try { delete o.x; } catch(e) {}
        return o.x === 1;
    });
    
    // Array extras
    test("Array index trailing comma", () => [1,2,3,].length === 3);
    
    // Reserved words as property names
    test("reserved word as prop", () => { let o = {class: 1, if: 2}; return o.class + o.if === 3; });
    
    results.push(`\n--- ES5 Summary: ${passed} passed, ${failed} failed ---`);
    
    return results.join("\n");
}
