// ES3 (ECMAScript 1999) Feature Tests
function(c, a) {
    let results = [];
    
    // === REGEX ===
    try { var r = /abc/; results.push("✓ RegExp literal"); } catch(e) { results.push("✗ RegExp literal: " + e.message); }
    try { var r = new RegExp("abc", "gi"); results.push("✓ RegExp constructor"); } catch(e) { results.push("✗ RegExp constructor: " + e.message); }
    try { /abc/.test("abc"); results.push("✓ RegExp.test()"); } catch(e) { results.push("✗ RegExp.test: " + e.message); }
    try { /abc/.exec("abc"); results.push("✓ RegExp.exec()"); } catch(e) { results.push("✗ RegExp.exec: " + e.message); }
    try { "abc".match(/a/); results.push("✓ String.match()"); } catch(e) { results.push("✗ String.match: " + e.message); }
    try { "abc".replace(/a/, "x"); results.push("✓ String.replace()"); } catch(e) { results.push("✗ String.replace: " + e.message); }
    try { "abc".search(/b/); results.push("✓ String.search()"); } catch(e) { results.push("✗ String.search: " + e.message); }
    try { "a,b".split(/,/); results.push("✓ String.split(regex)"); } catch(e) { results.push("✗ String.split(regex): " + e.message); }
    
    // === STRING METHODS ===
    try { "abc".charAt(0); results.push("✓ String.charAt()"); } catch(e) { results.push("✗ charAt: " + e.message); }
    try { "abc".charCodeAt(0); results.push("✓ String.charCodeAt()"); } catch(e) { results.push("✗ charCodeAt: " + e.message); }
    try { "abc".concat("def"); results.push("✓ String.concat()"); } catch(e) { results.push("✗ concat: " + e.message); }
    try { "abc".indexOf("b"); results.push("✓ String.indexOf()"); } catch(e) { results.push("✗ indexOf: " + e.message); }
    try { "abc".lastIndexOf("b"); results.push("✓ String.lastIndexOf()"); } catch(e) { results.push("✗ lastIndexOf: " + e.message); }
    try { "ABC".toLowerCase(); results.push("✓ String.toLowerCase()"); } catch(e) { results.push("✗ toLowerCase: " + e.message); }
    try { "abc".toUpperCase(); results.push("✓ String.toUpperCase()"); } catch(e) { results.push("✗ toUpperCase: " + e.message); }
    try { "abc".slice(1); results.push("✓ String.slice()"); } catch(e) { results.push("✗ slice: " + e.message); }
    try { "abc".substring(1); results.push("✓ String.substring()"); } catch(e) { results.push("✗ substring: " + e.message); }
    try { "abc".substr(1); results.push("✓ String.substr()"); } catch(e) { results.push("✗ substr: " + e.message); }
    try { " abc ".trim(); results.push("✓ String.trim()"); } catch(e) { results.push("✗ trim: " + e.message); }
    try { String.fromCharCode(65); results.push("✓ String.fromCharCode()"); } catch(e) { results.push("✗ fromCharCode: " + e.message); }
    
    // === ARRAY METHODS ===
    try { [1,2].concat([3]); results.push("✓ Array.concat()"); } catch(e) { results.push("✗ concat: " + e.message); }
    try { [1,2,3].join("-"); results.push("✓ Array.join()"); } catch(e) { results.push("✗ join: " + e.message); }
    try { var a=[1,2]; a.push(3); results.push("✓ Array.push()"); } catch(e) { results.push("✗ push: " + e.message); }
    try { var a=[1,2]; a.pop(); results.push("✓ Array.pop()"); } catch(e) { results.push("✗ pop: " + e.message); }
    try { var a=[1,2]; a.shift(); results.push("✓ Array.shift()"); } catch(e) { results.push("✗ shift: " + e.message); }
    try { var a=[1,2]; a.unshift(0); results.push("✓ Array.unshift()"); } catch(e) { results.push("✗ unshift: " + e.message); }
    try { [3,1,2].sort(); results.push("✓ Array.sort()"); } catch(e) { results.push("✗ sort: " + e.message); }
    try { [1,2,3].reverse(); results.push("✓ Array.reverse()"); } catch(e) { results.push("✗ reverse: " + e.message); }
    try { [1,2,3].slice(1); results.push("✓ Array.slice()"); } catch(e) { results.push("✗ slice: " + e.message); }
    try { var a=[1,2,3]; a.splice(1,1); results.push("✓ Array.splice()"); } catch(e) { results.push("✗ splice: " + e.message); }
    try { [1,2].toString(); results.push("✓ Array.toString()"); } catch(e) { results.push("✗ toString: " + e.message); }
    
    // === ERROR TYPES ===
    try { new Error("test"); results.push("✓ Error"); } catch(e) { results.push("✗ Error: " + e.message); }
    try { new TypeError("test"); results.push("✓ TypeError"); } catch(e) { results.push("✗ TypeError: " + e.message); }
    try { new RangeError("test"); results.push("✓ RangeError"); } catch(e) { results.push("✗ RangeError: " + e.message); }
    try { new SyntaxError("test"); results.push("✓ SyntaxError"); } catch(e) { results.push("✗ SyntaxError: " + e.message); }
    try { new ReferenceError("test"); results.push("✓ ReferenceError"); } catch(e) { results.push("✗ ReferenceError: " + e.message); }
    try { new URIError("test"); results.push("✓ URIError"); } catch(e) { results.push("✗ URIError: " + e.message); }
    try { new EvalError("test"); results.push("✓ EvalError"); } catch(e) { results.push("✗ EvalError: " + e.message); }
    
    // === FOR-IN ===
    try { for(var k in {a:1}){} results.push("✓ for-in loop"); } catch(e) { results.push("✗ for-in: " + e.message); }
    
    // === INSTANCEOF ===
    try { [] instanceof Array; results.push("✓ instanceof"); } catch(e) { results.push("✗ instanceof: " + e.message); }
    
    // === URI FUNCTIONS ===
    try { encodeURI("a b"); results.push("✓ encodeURI()"); } catch(e) { results.push("✗ encodeURI: " + e.message); }
    try { decodeURI("a%20b"); results.push("✓ decodeURI()"); } catch(e) { results.push("✗ decodeURI: " + e.message); }
    try { encodeURIComponent("a&b"); results.push("✓ encodeURIComponent()"); } catch(e) { results.push("✗ encodeURIComponent: " + e.message); }
    try { decodeURIComponent("a%26b"); results.push("✓ decodeURIComponent()"); } catch(e) { results.push("✗ decodeURIComponent: " + e.message); }
    
    return "=== ES3 (1999) TEST RESULTS ===\n" + results.join("\n");
}
