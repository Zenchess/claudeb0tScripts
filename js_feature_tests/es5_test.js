// ES5 (2009) Feature Tests for Hackmud
// Tests: strict mode, JSON, Array methods, Object methods, getters/setters

function(context, args) {
    let results = {};
    
    // ===== ES5 (2009) FEATURES =====
    
    // 1. "use strict" (can't really test in hackmud context, but check if it doesn't error)
    try {
        (function() {
            "use strict";
            var x = 1;
        })();
        results.use_strict = "✅ (no error)";
    } catch(e) { results.use_strict = "❌ " + e.message; }
    
    // 2. JSON.parse
    try {
        var parsed = JSON.parse('{"a":1,"b":"test"}');
        results.json_parse = (parsed.a === 1 && parsed.b === "test") ? "✅" : "❌";
    } catch(e) { results.json_parse = "❌ " + e.message; }
    
    // 3. JSON.stringify
    try {
        var str = JSON.stringify({x: 1, y: [1,2,3]});
        results.json_stringify = str.includes('"x":1') ? "✅" : "❌";
    } catch(e) { results.json_stringify = "❌ " + e.message; }
    
    // 4. Array.isArray
    try {
        results.array_isArray = (Array.isArray([1,2]) && !Array.isArray({a:1})) ? "✅" : "❌";
    } catch(e) { results.array_isArray = "❌ " + e.message; }
    
    // 5. Array.prototype.forEach
    try {
        var sum = 0;
        [1,2,3].forEach(function(n) { sum += n; });
        results.array_forEach = sum === 6 ? "✅" : "❌";
    } catch(e) { results.array_forEach = "❌ " + e.message; }
    
    // 6. Array.prototype.map
    try {
        var mapped = [1,2,3].map(function(n) { return n * 2; });
        results.array_map = (mapped[0] === 2 && mapped[2] === 6) ? "✅" : "❌";
    } catch(e) { results.array_map = "❌ " + e.message; }
    
    // 7. Array.prototype.filter
    try {
        var filtered = [1,2,3,4,5].filter(function(n) { return n > 2; });
        results.array_filter = (filtered.length === 3 && filtered[0] === 3) ? "✅" : "❌";
    } catch(e) { results.array_filter = "❌ " + e.message; }
    
    // 8. Array.prototype.reduce
    try {
        var reduced = [1,2,3,4].reduce(function(acc, n) { return acc + n; }, 0);
        results.array_reduce = reduced === 10 ? "✅" : "❌";
    } catch(e) { results.array_reduce = "❌ " + e.message; }
    
    // 9. Array.prototype.reduceRight
    try {
        var reducedR = [[1,2],[3,4]].reduceRight(function(acc, arr) { return acc.concat(arr); }, []);
        results.array_reduceRight = reducedR[0] === 3 ? "✅" : "❌";
    } catch(e) { results.array_reduceRight = "❌ " + e.message; }
    
    // 10. Array.prototype.some
    try {
        results.array_some = [1,2,3].some(function(n) { return n > 2; }) ? "✅" : "❌";
    } catch(e) { results.array_some = "❌ " + e.message; }
    
    // 11. Array.prototype.every
    try {
        results.array_every = [1,2,3].every(function(n) { return n < 10; }) ? "✅" : "❌";
    } catch(e) { results.array_every = "❌ " + e.message; }
    
    // 12. Array.prototype.indexOf
    try {
        results.array_indexOf = [1,2,3,2].indexOf(2) === 1 ? "✅" : "❌";
    } catch(e) { results.array_indexOf = "❌ " + e.message; }
    
    // 13. Array.prototype.lastIndexOf
    try {
        results.array_lastIndexOf = [1,2,3,2].lastIndexOf(2) === 3 ? "✅" : "❌";
    } catch(e) { results.array_lastIndexOf = "❌ " + e.message; }
    
    // 14. Object.keys
    try {
        var keys = Object.keys({a:1, b:2, c:3});
        results.object_keys = keys.length === 3 ? "✅" : "❌";
    } catch(e) { results.object_keys = "❌ " + e.message; }
    
    // 15. Object.create
    try {
        var proto = { greet: function() { return "hi"; } };
        var child = Object.create(proto);
        results.object_create = child.greet() === "hi" ? "✅" : "❌";
    } catch(e) { results.object_create = "❌ " + e.message; }
    
    // 16. Object.defineProperty
    try {
        var defObj = {};
        Object.defineProperty(defObj, 'x', { value: 42, writable: false });
        results.object_defineProperty = defObj.x === 42 ? "✅" : "❌";
    } catch(e) { results.object_defineProperty = "❌ " + e.message; }
    
    // 17. Object.defineProperties
    try {
        var defObj2 = {};
        Object.defineProperties(defObj2, {
            a: { value: 1 },
            b: { value: 2 }
        });
        results.object_defineProperties = (defObj2.a === 1 && defObj2.b === 2) ? "✅" : "❌";
    } catch(e) { results.object_defineProperties = "❌ " + e.message; }
    
    // 18. Object.getOwnPropertyDescriptor
    try {
        var desc = Object.getOwnPropertyDescriptor({x: 1}, 'x');
        results.object_getOwnPropertyDescriptor = desc.value === 1 ? "✅" : "❌";
    } catch(e) { results.object_getOwnPropertyDescriptor = "❌ " + e.message; }
    
    // 19. Object.getOwnPropertyNames
    try {
        var names = Object.getOwnPropertyNames({a:1, b:2});
        results.object_getOwnPropertyNames = names.length === 2 ? "✅" : "❌";
    } catch(e) { results.object_getOwnPropertyNames = "❌ " + e.message; }
    
    // 20. Object.getPrototypeOf
    try {
        function Parent() {}
        var pInst = new Parent();
        results.object_getPrototypeOf = Object.getPrototypeOf(pInst) === Parent.prototype ? "✅" : "❌";
    } catch(e) { results.object_getPrototypeOf = "❌ " + e.message; }
    
    // 21. Object.freeze
    try {
        var frozen = Object.freeze({x: 1});
        results.object_freeze = Object.isFrozen(frozen) ? "✅" : "❌";
    } catch(e) { results.object_freeze = "❌ " + e.message; }
    
    // 22. Object.seal
    try {
        var sealed = Object.seal({x: 1});
        results.object_seal = Object.isSealed(sealed) ? "✅" : "❌";
    } catch(e) { results.object_seal = "❌ " + e.message; }
    
    // 23. Object.preventExtensions
    try {
        var noExt = Object.preventExtensions({x: 1});
        results.object_preventExtensions = !Object.isExtensible(noExt) ? "✅" : "❌";
    } catch(e) { results.object_preventExtensions = "❌ " + e.message; }
    
    // 24. Getter/Setter with defineProperty
    try {
        var gsObj = {};
        var _val = 10;
        Object.defineProperty(gsObj, 'val', {
            get: function() { return _val; },
            set: function(v) { _val = v; }
        });
        gsObj.val = 20;
        results.getter_setter_defineProperty = gsObj.val === 20 ? "✅" : "❌";
    } catch(e) { results.getter_setter_defineProperty = "❌ " + e.message; }
    
    // 25. Getter/Setter literal syntax
    try {
        var gsLiteral = {
            _v: 5,
            get v() { return this._v; },
            set v(x) { this._v = x; }
        };
        gsLiteral.v = 15;
        results.getter_setter_literal = gsLiteral.v === 15 ? "✅" : "❌";
    } catch(e) { results.getter_setter_literal = "❌ " + e.message; }
    
    // 26. Function.prototype.bind
    try {
        function bindTest() { return this.x; }
        var bound = bindTest.bind({x: 99});
        results.function_bind = bound() === 99 ? "✅" : "❌";
    } catch(e) { results.function_bind = "❌ " + e.message; }
    
    // 27. String.prototype.trim
    try {
        results.string_trim = "  hello  ".trim() === "hello" ? "✅" : "❌";
    } catch(e) { results.string_trim = "❌ " + e.message; }
    
    // 28. Date.now
    try {
        var now = Date.now();
        results.date_now = typeof now === "number" && now > 0 ? "✅" : "❌";
    } catch(e) { results.date_now = "❌ " + e.message; }
    
    // 29. Date.prototype.toISOString
    try {
        var isoStr = new Date().toISOString();
        results.date_toISOString = isoStr.includes("T") ? "✅" : "❌";
    } catch(e) { results.date_toISOString = "❌ " + e.message; }
    
    // 30. Reserved words as property names
    try {
        var resObj = { class: 1, if: 2, return: 3 };
        results.reserved_as_props = resObj.class === 1 ? "✅" : "❌";
    } catch(e) { results.reserved_as_props = "❌ " + e.message; }
    
    return { es_version: "ES5", results: results };
}
