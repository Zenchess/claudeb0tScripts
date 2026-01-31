// ES5 (ECMAScript 2009) Feature Tests
function(c, a) {
    let results = [];
    
    // === STRICT MODE ===
    try { "use strict"; var x = 1; results.push("✓ 'use strict' directive"); } catch(e) { results.push("✗ use strict: " + e.message); }
    
    // === JSON ===
    try { JSON.stringify({a:1}); results.push("✓ JSON.stringify()"); } catch(e) { results.push("✗ JSON.stringify: " + e.message); }
    try { JSON.parse('{"a":1}'); results.push("✓ JSON.parse()"); } catch(e) { results.push("✗ JSON.parse: " + e.message); }
    
    // === ARRAY METHODS (ES5) ===
    try { [1,2,3].forEach(function(x){}); results.push("✓ Array.forEach()"); } catch(e) { results.push("✗ forEach: " + e.message); }
    try { [1,2,3].map(function(x){return x*2;}); results.push("✓ Array.map()"); } catch(e) { results.push("✗ map: " + e.message); }
    try { [1,2,3].filter(function(x){return x>1;}); results.push("✓ Array.filter()"); } catch(e) { results.push("✗ filter: " + e.message); }
    try { [1,2,3].reduce(function(a,b){return a+b;},0); results.push("✓ Array.reduce()"); } catch(e) { results.push("✗ reduce: " + e.message); }
    try { [1,2,3].reduceRight(function(a,b){return a+b;},0); results.push("✓ Array.reduceRight()"); } catch(e) { results.push("✗ reduceRight: " + e.message); }
    try { [1,2,3].some(function(x){return x>2;}); results.push("✓ Array.some()"); } catch(e) { results.push("✗ some: " + e.message); }
    try { [1,2,3].every(function(x){return x>0;}); results.push("✓ Array.every()"); } catch(e) { results.push("✗ every: " + e.message); }
    try { [1,2,3].indexOf(2); results.push("✓ Array.indexOf()"); } catch(e) { results.push("✗ indexOf: " + e.message); }
    try { [1,2,3].lastIndexOf(2); results.push("✓ Array.lastIndexOf()"); } catch(e) { results.push("✗ lastIndexOf: " + e.message); }
    try { Array.isArray([1,2]); results.push("✓ Array.isArray()"); } catch(e) { results.push("✗ isArray: " + e.message); }
    
    // === OBJECT METHODS (ES5) ===
    try { Object.keys({a:1,b:2}); results.push("✓ Object.keys()"); } catch(e) { results.push("✗ Object.keys: " + e.message); }
    try { Object.create(null); results.push("✓ Object.create()"); } catch(e) { results.push("✗ Object.create: " + e.message); }
    try { Object.defineProperty({}, 'x', {value:1}); results.push("✓ Object.defineProperty()"); } catch(e) { results.push("✗ Object.defineProperty: " + e.message); }
    try { Object.defineProperties({}, {x:{value:1}}); results.push("✓ Object.defineProperties()"); } catch(e) { results.push("✗ Object.defineProperties: " + e.message); }
    try { Object.getOwnPropertyDescriptor({a:1}, 'a'); results.push("✓ Object.getOwnPropertyDescriptor()"); } catch(e) { results.push("✗ getOwnPropertyDescriptor: " + e.message); }
    try { Object.getOwnPropertyNames({a:1}); results.push("✓ Object.getOwnPropertyNames()"); } catch(e) { results.push("✗ getOwnPropertyNames: " + e.message); }
    try { Object.getPrototypeOf({}); results.push("✓ Object.getPrototypeOf()"); } catch(e) { results.push("✗ getPrototypeOf: " + e.message); }
    try { Object.preventExtensions({}); results.push("✓ Object.preventExtensions()"); } catch(e) { results.push("✗ preventExtensions: " + e.message); }
    try { Object.isExtensible({}); results.push("✓ Object.isExtensible()"); } catch(e) { results.push("✗ isExtensible: " + e.message); }
    try { Object.seal({}); results.push("✓ Object.seal()"); } catch(e) { results.push("✗ Object.seal: " + e.message); }
    try { Object.isSealed({}); results.push("✓ Object.isSealed()"); } catch(e) { results.push("✗ isSealed: " + e.message); }
    try { Object.freeze({}); results.push("✓ Object.freeze()"); } catch(e) { results.push("✗ Object.freeze: " + e.message); }
    try { Object.isFrozen({}); results.push("✓ Object.isFrozen()"); } catch(e) { results.push("✗ isFrozen: " + e.message); }
    
    // === FUNCTION METHODS ===
    try { (function(){}).bind({}); results.push("✓ Function.bind()"); } catch(e) { results.push("✗ Function.bind: " + e.message); }
    
    // === GETTER/SETTER ===
    try { var o = {get x(){return 1;}}; o.x; results.push("✓ getter"); } catch(e) { results.push("✗ getter: " + e.message); }
    try { var o = {_x:0, set x(v){this._x=v;}}; o.x=1; results.push("✓ setter"); } catch(e) { results.push("✗ setter: " + e.message); }
    
    // === DATE METHODS ===
    try { Date.now(); results.push("✓ Date.now()"); } catch(e) { results.push("✗ Date.now: " + e.message); }
    try { new Date().toISOString(); results.push("✓ Date.toISOString()"); } catch(e) { results.push("✗ toISOString: " + e.message); }
    try { new Date().toJSON(); results.push("✓ Date.toJSON()"); } catch(e) { results.push("✗ toJSON: " + e.message); }
    
    // === STRING METHODS ===
    try { "  abc  ".trim(); results.push("✓ String.trim() (ES5)"); } catch(e) { results.push("✗ String.trim: " + e.message); }
    
    // === PROPERTY ACCESS ===
    try { var o = {}; o["prop"] = 1; results.push("✓ bracket notation"); } catch(e) { results.push("✗ bracket notation: " + e.message); }
    try { var o = {"reserved-word": 1}; results.push("✓ reserved words as keys"); } catch(e) { results.push("✗ reserved keys: " + e.message); }
    try { var o = {if:1, for:2}; results.push("✓ reserved words as unquoted keys"); } catch(e) { results.push("✗ reserved unquoted: " + e.message); }
    
    // === TRAILING COMMAS ===
    try { var a = [1,2,3,]; results.push("✓ trailing comma in arrays"); } catch(e) { results.push("✗ trailing comma array: " + e.message); }
    try { var o = {a:1,b:2,}; results.push("✓ trailing comma in objects"); } catch(e) { results.push("✗ trailing comma object: " + e.message); }
    
    return "=== ES5 (2009) TEST RESULTS ===\n" + results.join("\n");
}
