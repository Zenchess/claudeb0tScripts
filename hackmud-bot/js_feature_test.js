// Comprehensive JavaScript Feature Test for Hackmud
// Tests ES1 through ES2025 features

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
    
    // ========== ES1 (1997) ==========
    results.push("\n=== ES1 (1997) ===");
    
    // Variables
    test("var declaration", () => { var x = 1; return x === 1; });
    
    // Primitive types
    test("typeof number", () => typeof 42 === "number");
    test("typeof string", () => typeof "hello" === "string");
    test("typeof boolean", () => typeof true === "boolean");
    test("typeof undefined", () => typeof undefined === "undefined");
    test("typeof null", () => typeof null === "object"); // famous quirk
    test("typeof object", () => typeof {} === "object");
    test("typeof function", () => typeof function(){} === "function");
    
    // Operators
    test("arithmetic +", () => 2 + 3 === 5);
    test("arithmetic -", () => 5 - 3 === 2);
    test("arithmetic *", () => 4 * 3 === 12);
    test("arithmetic /", () => 10 / 2 === 5);
    test("arithmetic %", () => 7 % 3 === 1);
    test("comparison ==", () => "5" == 5);
    test("comparison !=", () => 5 != 6);
    test("comparison <", () => 3 < 5);
    test("comparison >", () => 5 > 3);
    test("comparison <=", () => 5 <= 5);
    test("comparison >=", () => 5 >= 5);
    test("logical &&", () => (true && true) === true);
    test("logical ||", () => (false || true) === true);
    test("logical !", () => !false === true);
    test("bitwise &", () => (5 & 3) === 1);
    test("bitwise |", () => (5 | 3) === 7);
    test("bitwise ^", () => (5 ^ 3) === 6);
    test("bitwise ~", () => (~5) === -6);
    test("bitwise <<", () => (1 << 3) === 8);
    test("bitwise >>", () => (8 >> 2) === 2);
    test("bitwise >>>", () => (-1 >>> 0) === 4294967295);
    test("ternary ?:", () => (true ? "a" : "b") === "a");
    
    // Control flow
    test("if statement", () => { if (true) return true; return false; });
    test("if-else", () => { if (false) return false; else return true; });
    test("for loop", () => { let sum = 0; for (var i = 0; i < 5; i++) sum += i; return sum === 10; });
    test("while loop", () => { let n = 0; while (n < 3) n++; return n === 3; });
    test("do-while", () => { let n = 0; do { n++; } while (n < 3); return n === 3; });
    test("break", () => { for (var i = 0; i < 10; i++) { if (i === 5) break; } return i === 5; });
    test("continue", () => { let sum = 0; for (var i = 0; i < 5; i++) { if (i === 2) continue; sum += i; } return sum === 8; });
    test("switch-case", () => { switch (2) { case 1: return false; case 2: return true; default: return false; } });
    
    // Functions
    test("function declaration", () => { function f() { return 42; } return f() === 42; });
    test("function expression", () => { var f = function() { return 42; }; return f() === 42; });
    test("function arguments", () => { function f(a, b) { return a + b; } return f(2, 3) === 5; });
    test("function return", () => { function f() { return 99; } return f() === 99; });
    test("recursive function", () => { function fact(n) { return n <= 1 ? 1 : n * fact(n-1); } return fact(5) === 120; });
    
    // Objects
    test("object literal", () => { var o = {a: 1}; return o.a === 1; });
    test("object dot access", () => { var o = {x: 5}; return o.x === 5; });
    test("object bracket access", () => { var o = {x: 5}; return o["x"] === 5; });
    test("object property assign", () => { var o = {}; o.a = 1; return o.a === 1; });
    test("delete property", () => { var o = {a: 1}; delete o.a; return o.a === undefined; });
    test("in operator", () => { var o = {a: 1}; return "a" in o; });
    
    // Arrays
    test("array literal", () => { var a = [1, 2, 3]; return a.length === 3; });
    test("array index access", () => { var a = [10, 20, 30]; return a[1] === 20; });
    test("array index assign", () => { var a = [1]; a[0] = 99; return a[0] === 99; });
    test("array length", () => { var a = [1, 2, 3, 4, 5]; return a.length === 5; });
    
    // Built-in objects
    test("Math.abs", () => Math.abs(-5) === 5);
    test("Math.floor", () => Math.floor(3.7) === 3);
    test("Math.ceil", () => Math.ceil(3.2) === 4);
    test("Math.round", () => Math.round(3.5) === 4);
    test("Math.max", () => Math.max(1, 5, 3) === 5);
    test("Math.min", () => Math.min(1, 5, 3) === 1);
    test("Math.pow", () => Math.pow(2, 3) === 8);
    test("Math.sqrt", () => Math.sqrt(16) === 4);
    test("Math.random", () => { var r = Math.random(); return r >= 0 && r < 1; });
    test("Math.PI", () => Math.PI > 3.14 && Math.PI < 3.15);
    
    test("String.length", () => "hello".length === 5);
    test("String.charAt", () => "hello".charAt(1) === "e");
    test("String.indexOf", () => "hello".indexOf("l") === 2);
    test("String.substring", () => "hello".substring(1, 3) === "el");
    test("String.toLowerCase", () => "HELLO".toLowerCase() === "hello");
    test("String.toUpperCase", () => "hello".toUpperCase() === "HELLO");
    
    test("Array.join", () => [1, 2, 3].join("-") === "1-2-3");
    test("Array.reverse", () => [1, 2, 3].reverse().join("") === "321");
    test("Array.sort", () => [3, 1, 2].sort().join("") === "123");
    test("Array.concat", () => [1, 2].concat([3, 4]).length === 4);
    test("Array.slice", () => [1, 2, 3, 4].slice(1, 3).join("") === "23");
    
    test("Date object", () => { var d = new Date(); return typeof d.getTime === "function"; });
    test("Date.getTime", () => { var d = new Date(); return typeof d.getTime() === "number"; });
    
    test("parseInt", () => parseInt("42") === 42);
    test("parseFloat", () => parseFloat("3.14") === 3.14);
    test("isNaN", () => isNaN(NaN) === true);
    test("isFinite", () => isFinite(42) === true);
    
    // Error handling
    test("try-catch", () => { try { throw new Error("test"); } catch (e) { return e.message === "test"; } });
    test("throw", () => { try { throw "custom error"; } catch (e) { return e === "custom error"; } });
    
    // ========== ES2 (1998) ==========
    results.push("\n=== ES2 (1998) ===");
    results.push("(Editorial changes only, no new features)");
    
    // ========== ES3 (1999) ==========
    results.push("\n=== ES3 (1999) ===");
    
    test("RegExp literal", () => /test/.test("testing"));
    test("RegExp constructor", () => new RegExp("test").test("testing"));
    test("RegExp.exec", () => { var m = /(\w+)/.exec("hello"); return m[0] === "hello"; });
    test("String.match", () => "hello".match(/l/g).length === 2);
    test("String.replace", () => "hello".replace("l", "x") === "hexlo");
    test("String.replace regex", () => "hello".replace(/l/g, "x") === "hexxo");
    test("String.search", () => "hello".search(/l/) === 2);
    test("String.split", () => "a,b,c".split(",").length === 3);
    
    test("Array.push", () => { var a = [1]; a.push(2); return a.length === 2; });
    test("Array.pop", () => { var a = [1, 2]; return a.pop() === 2; });
    test("Array.shift", () => { var a = [1, 2]; return a.shift() === 1; });
    test("Array.unshift", () => { var a = [2]; a.unshift(1); return a[0] === 1; });
    test("Array.splice", () => { var a = [1, 2, 3]; a.splice(1, 1); return a.join("") === "13"; });
    
    test("for-in loop", () => { var o = {a: 1, b: 2}; var keys = []; for (var k in o) keys.push(k); return keys.length === 2; });
    test("instanceof", () => [] instanceof Array);
    
    test("Function.apply", () => { function f(a, b) { return a + b; } return f.apply(null, [2, 3]) === 5; });
    test("Function.call", () => { function f(a, b) { return a + b; } return f.call(null, 2, 3) === 5; });
    
    test("try-catch-finally", () => { var x = 0; try { x = 1; } finally { x = 2; } return x === 2; });
    
    test("encodeURI", () => encodeURI("hello world").includes("%20"));
    test("decodeURI", () => decodeURI("hello%20world") === "hello world");
    test("encodeURIComponent", () => encodeURIComponent("a=b") === "a%3Db");
    test("decodeURIComponent", () => decodeURIComponent("a%3Db") === "a=b");
    
    // Summary for this batch
    results.push(`\n--- ES1-ES3 Summary: ${passed} passed, ${failed} failed ---`);
    
    return results.join("\n");
}
