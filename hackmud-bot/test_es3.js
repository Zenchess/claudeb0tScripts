// ES3 (1999) Feature Test for Hackmud
// Tests: try/catch, throw, in, instanceof, ===, regex

function(context, args) {
    var results = [];
    results.push("=== ES3 FEATURES ===");
    
    // try/catch/finally
    var tryTest = "✗";
    try {
        throw new Error("test");
    } catch (e) {
        tryTest = e.message === "test" ? "✓" : "✗";
    }
    results.push("try/catch: " + tryTest);
    
    // finally
    var finallyRan = false;
    try { 
        // nothing 
    } finally { 
        finallyRan = true; 
    }
    results.push("finally: " + (finallyRan ? "✓" : "✗"));
    
    // throw
    var throwTest = "✗";
    try {
        throw {custom: "error"};
    } catch (e) {
        throwTest = e.custom === "error" ? "✓" : "✗";
    }
    results.push("throw: " + throwTest);
    
    // in operator
    var obj = {a: 1, b: 2};
    results.push("in operator: " + ("a" in obj && !("c" in obj) ? "✓" : "✗"));
    
    // instanceof
    var arr = [1, 2, 3];
    results.push("instanceof: " + (arr instanceof Array ? "✓" : "✗"));
    
    // === and !==
    results.push("=== : " + (5 === 5 && !(5 === "5") ? "✓" : "✗"));
    results.push("!== : " + (5 !== "5" && !(5 !== 5) ? "✓" : "✗"));
    
    // Regex literals
    var regex = /hello/i;
    results.push("regex literal: " + (regex.test("HELLO") ? "✓" : "✗"));
    
    var match = "test123".match(/\d+/);
    results.push("regex match: " + (match && match[0] === "123" ? "✓" : "✗"));
    
    var replaced = "foo bar".replace(/bar/, "baz");
    results.push("regex replace: " + (replaced === "foo baz" ? "✓" : "✗"));
    
    return results.join("\n");
}
