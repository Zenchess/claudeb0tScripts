// ES1-ES3 Feature Tests for Hackmud
// Tests: var, function, loops, basic types, objects, arrays, try/catch

function(context, args) {
    let results = {};
    
    // ===== ES1 (1997) CORE FEATURES =====
    
    // 1. var declaration
    try {
        var testVar = 42;
        results.var_declaration = testVar === 42 ? "✅" : "❌";
    } catch(e) { results.var_declaration = "❌ " + e.message; }
    
    // 2. function declaration (inside function - not hoisted the same way)
    try {
        function innerFunc() { return "works"; }
        results.function_declaration = innerFunc() === "works" ? "✅" : "❌";
    } catch(e) { results.function_declaration = "❌ " + e.message; }
    
    // 3. function expression
    try {
        var funcExpr = function() { return "expr"; };
        results.function_expression = funcExpr() === "expr" ? "✅" : "❌";
    } catch(e) { results.function_expression = "❌ " + e.message; }
    
    // 4. if/else
    try {
        var ifResult = "";
        if (true) { ifResult = "if"; } else { ifResult = "else"; }
        results.if_else = ifResult === "if" ? "✅" : "❌";
    } catch(e) { results.if_else = "❌ " + e.message; }
    
    // 5. for loop
    try {
        var forSum = 0;
        for (var i = 0; i < 5; i++) { forSum += i; }
        results.for_loop = forSum === 10 ? "✅" : "❌";
    } catch(e) { results.for_loop = "❌ " + e.message; }
    
    // 6. while loop
    try {
        var whileSum = 0;
        var w = 0;
        while (w < 5) { whileSum += w; w++; }
        results.while_loop = whileSum === 10 ? "✅" : "❌";
    } catch(e) { results.while_loop = "❌ " + e.message; }
    
    // 7. do-while loop
    try {
        var doWhileSum = 0;
        var d = 0;
        do { doWhileSum += d; d++; } while (d < 5);
        results.do_while_loop = doWhileSum === 10 ? "✅" : "❌";
    } catch(e) { results.do_while_loop = "❌ " + e.message; }
    
    // 8. switch statement
    try {
        var switchResult;
        switch(2) {
            case 1: switchResult = "one"; break;
            case 2: switchResult = "two"; break;
            default: switchResult = "default";
        }
        results.switch_statement = switchResult === "two" ? "✅" : "❌";
    } catch(e) { results.switch_statement = "❌ " + e.message; }
    
    // 9. break/continue
    try {
        var breakSum = 0;
        for (var b = 0; b < 10; b++) {
            if (b === 5) break;
            breakSum += b;
        }
        results.break_continue = breakSum === 10 ? "✅" : "❌";
    } catch(e) { results.break_continue = "❌ " + e.message; }
    
    // 10. Object literal
    try {
        var obj = { a: 1, b: 2 };
        results.object_literal = (obj.a === 1 && obj.b === 2) ? "✅" : "❌";
    } catch(e) { results.object_literal = "❌ " + e.message; }
    
    // 11. Array literal
    try {
        var arr = [1, 2, 3];
        results.array_literal = (arr[0] === 1 && arr.length === 3) ? "✅" : "❌";
    } catch(e) { results.array_literal = "❌ " + e.message; }
    
    // 12. typeof operator
    try {
        results.typeof_operator = (typeof 42 === "number" && typeof "s" === "string") ? "✅" : "❌";
    } catch(e) { results.typeof_operator = "❌ " + e.message; }
    
    // 13. this keyword
    try {
        var thisObj = {
            val: 99,
            getVal: function() { return this.val; }
        };
        results.this_keyword = thisObj.getVal() === 99 ? "✅" : "❌";
    } catch(e) { results.this_keyword = "❌ " + e.message; }
    
    // 14. new operator
    try {
        function MyClass(x) { this.x = x; }
        var instance = new MyClass(5);
        results.new_operator = instance.x === 5 ? "✅" : "❌";
    } catch(e) { results.new_operator = "❌ " + e.message; }
    
    // ===== ES3 (1999) ADDITIONS =====
    
    // 15. try/catch/finally
    try {
        var tryCatchResult = "";
        try {
            throw new Error("test");
        } catch(e) {
            tryCatchResult = "caught";
        } finally {
            tryCatchResult += "-finally";
        }
        results.try_catch_finally = tryCatchResult === "caught-finally" ? "✅" : "❌";
    } catch(e) { results.try_catch_finally = "❌ " + e.message; }
    
    // 16. instanceof operator
    try {
        function Foo() {}
        var fooInst = new Foo();
        results.instanceof_operator = fooInst instanceof Foo ? "✅" : "❌";
    } catch(e) { results.instanceof_operator = "❌ " + e.message; }
    
    // 17. in operator
    try {
        var inObj = { prop: 1 };
        results.in_operator = ("prop" in inObj && !("nope" in inObj)) ? "✅" : "❌";
    } catch(e) { results.in_operator = "❌ " + e.message; }
    
    // 18. for-in loop
    try {
        var forInObj = { a: 1, b: 2 };
        var forInKeys = [];
        for (var key in forInObj) { forInKeys.push(key); }
        results.for_in_loop = forInKeys.length === 2 ? "✅" : "❌";
    } catch(e) { results.for_in_loop = "❌ " + e.message; }
    
    // 19. Regular expressions
    try {
        var regex = /hello/i;
        results.regex_literal = regex.test("Hello World") ? "✅" : "❌";
    } catch(e) { results.regex_literal = "❌ " + e.message; }
    
    // 20. String methods (ES3)
    try {
        var str = "hello";
        results.string_methods = (str.charAt(0) === "h" && str.indexOf("l") === 2) ? "✅" : "❌";
    } catch(e) { results.string_methods = "❌ " + e.message; }
    
    // 21. Array methods (ES3)
    try {
        var arr3 = [1, 2, 3];
        arr3.push(4);
        var popped = arr3.pop();
        results.array_methods_es3 = (popped === 4 && arr3.join("-") === "1-2-3") ? "✅" : "❌";
    } catch(e) { results.array_methods_es3 = "❌ " + e.message; }
    
    // 22. delete operator
    try {
        var delObj = { x: 1, y: 2 };
        delete delObj.x;
        results.delete_operator = (!("x" in delObj) && delObj.y === 2) ? "✅" : "❌";
    } catch(e) { results.delete_operator = "❌ " + e.message; }
    
    // 23. Primitive types
    try {
        var num = 42;
        var str = "hello";
        var bool = true;
        var nul = null;
        var undef = undefined;
        results.primitive_types = (typeof num === "number" && typeof str === "string" && 
            typeof bool === "boolean" && nul === null && undef === undefined) ? "✅" : "❌";
    } catch(e) { results.primitive_types = "❌ " + e.message; }
    
    // 24. Comparison operators
    try {
        results.comparison_operators = (1 == "1" && 1 !== "1" && 1 === 1 && 2 > 1 && 1 < 2) ? "✅" : "❌";
    } catch(e) { results.comparison_operators = "❌ " + e.message; }
    
    // 25. Logical operators
    try {
        results.logical_operators = (true && true && !false && (true || false)) ? "✅" : "❌";
    } catch(e) { results.logical_operators = "❌ " + e.message; }
    
    // 26. Ternary operator
    try {
        var ternary = true ? "yes" : "no";
        results.ternary_operator = ternary === "yes" ? "✅" : "❌";
    } catch(e) { results.ternary_operator = "❌ " + e.message; }
    
    // 27. Comma operator
    try {
        var comma = (1, 2, 3);
        results.comma_operator = comma === 3 ? "✅" : "❌";
    } catch(e) { results.comma_operator = "❌ " + e.message; }
    
    // 28. Math object
    try {
        results.math_object = (Math.max(1,2,3) === 3 && Math.floor(1.9) === 1) ? "✅" : "❌";
    } catch(e) { results.math_object = "❌ " + e.message; }
    
    // 29. Date object
    try {
        var date = new Date();
        results.date_object = typeof date.getTime === "function" ? "✅" : "❌";
    } catch(e) { results.date_object = "❌ " + e.message; }
    
    // 30. Arguments object
    try {
        function argsTest() { return arguments.length; }
        results.arguments_object = argsTest(1, 2, 3) === 3 ? "✅" : "❌";
    } catch(e) { results.arguments_object = "❌ " + e.message; }
    
    return { es_version: "ES1-ES3", results: results };
}
