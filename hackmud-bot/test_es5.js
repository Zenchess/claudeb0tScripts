// ES5 (2009) Feature Test for Hackmud
// Tests: strict mode, array methods, object methods, JSON, bind

function(context, args) {
    "use strict";
    var results = [];
    results.push("=== ES5 FEATURES ===");
    
    // Strict mode (implicit test - script wouldn't run if broken)
    results.push("use strict: ✓ (script running)");
    
    // === ARRAY METHODS ===
    results.push("\n--- Array Methods ---");
    
    var arr = [1, 2, 3, 4, 5];
    
    // forEach
    var sum = 0;
    arr.forEach(function(x) { sum += x; });
    results.push("forEach: " + (sum === 15 ? "✓" : "✗"));
    
    // map
    var doubled = arr.map(function(x) { return x * 2; });
    results.push("map: " + (doubled.join(",") === "2,4,6,8,10" ? "✓" : "✗"));
    
    // filter
    var evens = arr.filter(function(x) { return x % 2 === 0; });
    results.push("filter: " + (evens.join(",") === "2,4" ? "✓" : "✗"));
    
    // reduce
    var product = arr.reduce(function(a, b) { return a * b; }, 1);
    results.push("reduce: " + (product === 120 ? "✓" : "✗"));
    
    // every
    var allPositive = arr.every(function(x) { return x > 0; });
    results.push("every: " + (allPositive ? "✓" : "✗"));
    
    // some
    var hasEven = arr.some(function(x) { return x % 2 === 0; });
    results.push("some: " + (hasEven ? "✓" : "✗"));
    
    // indexOf / lastIndexOf
    var idx = [1,2,3,2,1];
    results.push("indexOf: " + (idx.indexOf(2) === 1 ? "✓" : "✗"));
    results.push("lastIndexOf: " + (idx.lastIndexOf(2) === 3 ? "✓" : "✗"));
    
    // isArray
    results.push("Array.isArray: " + (Array.isArray(arr) ? "✓" : "✗"));
    
    // === OBJECT METHODS ===
    results.push("\n--- Object Methods ---");
    
    var obj = {a: 1, b: 2, c: 3};
    
    // Object.keys
    results.push("Object.keys: " + (Object.keys(obj).length === 3 ? "✓" : "✗"));
    
    // Object.create
    var proto = {greet: function() { return "hi"; }};
    var child = Object.create(proto);
    results.push("Object.create: " + (child.greet() === "hi" ? "✓" : "✗"));
    
    // Object.defineProperty
    var defObj = {};
    Object.defineProperty(defObj, "x", {value: 42, writable: false});
    results.push("defineProperty: " + (defObj.x === 42 ? "✓" : "✗"));
    
    // Object.freeze
    var frozen = Object.freeze({a: 1});
    results.push("Object.freeze: " + (Object.isFrozen(frozen) ? "✓" : "✗"));
    
    // Getters/Setters
    var gsObj = {
        _val: 0,
        get val() { return this._val; },
        set val(v) { this._val = v; }
    };
    gsObj.val = 10;
    results.push("getter/setter: " + (gsObj.val === 10 ? "✓" : "✗"));
    
    // === JSON ===
    results.push("\n--- JSON ---");
    
    var jsonStr = JSON.stringify({a: 1, b: [2, 3]});
    results.push("JSON.stringify: " + (jsonStr === '{"a":1,"b":[2,3]}' ? "✓" : "✗"));
    
    var parsed = JSON.parse('{"x": 42}');
    results.push("JSON.parse: " + (parsed.x === 42 ? "✓" : "✗"));
    
    // === STRING ===
    results.push("\n--- String ---");
    results.push("trim: " + ("  hi  ".trim() === "hi" ? "✓" : "✗"));
    results.push("charAt: " + ("abc".charAt(1) === "b" ? "✓" : "✗"));
    results.push("indexOf: " + ("hello".indexOf("ll") === 2 ? "✓" : "✗"));
    
    // === FUNCTION ===
    results.push("\n--- Function ---");
    
    function greet(greeting) { return greeting + " " + this.name; }
    var person = {name: "Claude"};
    var boundGreet = greet.bind(person);
    results.push("Function.bind: " + (boundGreet("Hello") === "Hello Claude" ? "✓" : "✗"));
    
    // Date.now
    results.push("Date.now: " + (typeof Date.now() === "number" ? "✓" : "✗"));
    
    return results.join("\n");
}
