// ES1 (1997) Feature Test for Hackmud
// Tests: var, types, operators, control flow, functions

function(context, args) {
    var results = [];
    
    // === VARIABLES & TYPES ===
    var num = 42;
    var str = "hello";
    var bool = true;
    var nul = null;
    var undef = undefined;
    var obj = {a: 1, b: 2};
    var arr = [1, 2, 3];
    
    results.push("=== ES1 TYPES ===");
    results.push("var num: " + (typeof num === "number" ? "✓" : "✗"));
    results.push("var str: " + (typeof str === "string" ? "✓" : "✗"));
    results.push("var bool: " + (typeof bool === "boolean" ? "✓" : "✗"));
    results.push("null: " + (nul === null ? "✓" : "✗"));
    results.push("undefined: " + (undef === undefined ? "✓" : "✗"));
    results.push("object: " + (typeof obj === "object" ? "✓" : "✗"));
    results.push("array: " + (arr instanceof Array ? "✓" : "✗"));
    
    // === OPERATORS ===
    results.push("\n=== ES1 OPERATORS ===");
    results.push("+ : " + (2 + 3 === 5 ? "✓" : "✗"));
    results.push("- : " + (5 - 2 === 3 ? "✓" : "✗"));
    results.push("* : " + (3 * 4 === 12 ? "✓" : "✗"));
    results.push("/ : " + (10 / 2 === 5 ? "✓" : "✗"));
    results.push("% : " + (7 % 3 === 1 ? "✓" : "✗"));
    results.push("== : " + (5 == "5" ? "✓" : "✗"));
    results.push("!= : " + (5 != 6 ? "✓" : "✗"));
    results.push("< > <= >= : " + (1 < 2 && 2 > 1 && 2 <= 2 && 2 >= 2 ? "✓" : "✗"));
    results.push("&& : " + (true && true ? "✓" : "✗"));
    results.push("|| : " + (false || true ? "✓" : "✗"));
    results.push("! : " + (!false === true ? "✓" : "✗"));
    results.push("typeof : " + (typeof 42 === "number" ? "✓" : "✗"));
    
    // === CONTROL FLOW ===
    results.push("\n=== ES1 CONTROL FLOW ===");
    
    // if/else
    var ifTest = "✗";
    if (true) { ifTest = "✓"; }
    results.push("if/else: " + ifTest);
    
    // for loop
    var forSum = 0;
    for (var i = 0; i < 3; i++) { forSum += i; }
    results.push("for loop: " + (forSum === 3 ? "✓" : "✗"));
    
    // while loop
    var whileCount = 0;
    while (whileCount < 3) { whileCount++; }
    results.push("while: " + (whileCount === 3 ? "✓" : "✗"));
    
    // do-while
    var doCount = 0;
    do { doCount++; } while (doCount < 3);
    results.push("do-while: " + (doCount === 3 ? "✓" : "✗"));
    
    // switch
    var switchResult = "✗";
    switch (2) {
        case 1: switchResult = "wrong"; break;
        case 2: switchResult = "✓"; break;
        default: switchResult = "wrong";
    }
    results.push("switch/case: " + switchResult);
    
    // break/continue
    var breakTest = 0;
    for (var j = 0; j < 10; j++) {
        if (j === 3) break;
        breakTest++;
    }
    results.push("break: " + (breakTest === 3 ? "✓" : "✗"));
    
    // === FUNCTIONS ===
    results.push("\n=== ES1 FUNCTIONS ===");
    
    function add(a, b) { return a + b; }
    results.push("function decl: " + (add(2, 3) === 5 ? "✓" : "✗"));
    
    function outer() {
        function inner() { return 42; }
        return inner();
    }
    results.push("nested funcs: " + (outer() === 42 ? "✓" : "✗"));
    
    return results.join("\n");
}
