// ES1-ES3 (1997-1999) Feature Test for Hackmud
function(context, args) {
    let results = [];
    let pass = 0, fail = 0;
    
    function test(name, fn) {
        try {
            let r = fn();
            if (r === true) { pass++; results.push(`✓ ${name}`); }
            else { fail++; results.push(`✗ ${name}: ${r}`); }
        } catch(e) { fail++; results.push(`✗ ${name}: ${e.message || e}`); }
    }
    
    // === ES1 (1997) Core ===
    results.push("=== ES1 (1997) ===");
    
    // Variables
    test("var declaration", () => { var x = 5; return x === 5; });
    
    // Primitive types
    test("Number type", () => typeof 42 === "number");
    test("String type", () => typeof "hello" === "string");
    test("Boolean type", () => typeof true === "boolean");
    test("undefined type", () => typeof undefined === "undefined");
    test("null (typeof object)", () => typeof null === "object");
    
    // Operators
    test("Arithmetic (+,-,*,/,%)", () => (5+3===8) && (5-3===2) && (5*3===15) && (6/3===2) && (7%3===1));
    test("Comparison (==,!=,<,>,<=,>=)", () => (5==5) && (5!=3) && (5>3) && (3<5) && (5>=5) && (3<=5));
    test("Logical (&&,||,!)", () => (true && true) && (true || false) && (!false));
    test("String concat (+)", () => "hello " + "world" === "hello world");
    test("typeof operator", () => typeof typeof 5 === "string");
    
    // Control flow
    test("if/else", () => { if (true) return true; else return false; });
    test("for loop", () => { let sum=0; for(var i=0;i<5;i++)sum+=i; return sum===10; });
    test("while loop", () => { let x=0; while(x<3)x++; return x===3; });
    test("do-while loop", () => { let x=0; do{x++}while(x<3); return x===3; });
    test("switch/case", () => { switch(2){case 1:return false;case 2:return true;default:return false;} });
    test("break statement", () => { for(var i=0;i<10;i++){if(i===3)break;} return i===3; });
    test("continue statement", () => { let s=0;for(var i=0;i<5;i++){if(i===2)continue;s+=i;} return s===8; });
    
    // Functions
    test("function declaration", () => { function f(){return 42;} return f()===42; });
    test("function expression", () => { var f = function(){return 42;}; return f()===42; });
    test("arguments object", () => { function f(){return arguments.length;} return f(1,2,3)===3; });
    test("return statement", () => { function f(){return 5;} return f()===5; });
    test("recursion", () => { function fact(n){return n<=1?1:n*fact(n-1);} return fact(5)===120; });
    
    // Objects
    test("Object literal", () => { var o = {a:1,b:2}; return o.a===1 && o.b===2; });
    test("Object property access (.)", () => { var o={x:5}; return o.x===5; });
    test("Object property access ([])", () => { var o={x:5}; return o["x"]===5; });
    test("Object dynamic key", () => { var o={}; var k="foo"; o[k]=42; return o.foo===42; });
    test("delete property", () => { var o={a:1}; delete o.a; return o.a===undefined; });
    test("in operator", () => { var o={a:1}; return "a" in o && !("b" in o); });
    
    // Arrays
    test("Array literal", () => { var a=[1,2,3]; return a.length===3; });
    test("Array index access", () => { var a=[1,2,3]; return a[0]===1 && a[2]===3; });
    test("Array.length", () => { var a=[1,2,3]; return a.length===3; });
    test("Array.push", () => { var a=[1]; a.push(2); return a.length===2 && a[1]===2; });
    test("Array.pop", () => { var a=[1,2]; return a.pop()===2 && a.length===1; });
    test("Array.shift", () => { var a=[1,2]; return a.shift()===1 && a.length===1; });
    test("Array.unshift", () => { var a=[1]; a.unshift(0); return a[0]===0 && a.length===2; });
    test("Array.join", () => [1,2,3].join("-") === "1-2-3");
    test("Array.reverse", () => { var a=[1,2,3]; a.reverse(); return a[0]===3; });
    test("Array.sort", () => { var a=[3,1,2]; a.sort(); return a[0]===1; });
    test("Array.slice", () => [1,2,3,4].slice(1,3).join()=="2,3");
    test("Array.splice", () => { var a=[1,2,3]; a.splice(1,1); return a.join()==="1,3"; });
    test("Array.concat", () => [1,2].concat([3,4]).join()==="1,2,3,4");
    
    // Strings
    test("String.length", () => "hello".length === 5);
    test("String.charAt", () => "hello".charAt(1) === "e");
    test("String.indexOf", () => "hello".indexOf("l") === 2);
    test("String.lastIndexOf", () => "hello".lastIndexOf("l") === 3);
    test("String.substring", () => "hello".substring(1,4) === "ell");
    test("String.toLowerCase", () => "HELLO".toLowerCase() === "hello");
    test("String.toUpperCase", () => "hello".toUpperCase() === "HELLO");
    test("String.split", () => "a,b,c".split(",").join("|") === "a|b|c");
    
    // Math
    test("Math.abs", () => Math.abs(-5) === 5);
    test("Math.floor", () => Math.floor(3.7) === 3);
    test("Math.ceil", () => Math.ceil(3.2) === 4);
    test("Math.round", () => Math.round(3.5) === 4);
    test("Math.max", () => Math.max(1,5,3) === 5);
    test("Math.min", () => Math.min(1,5,3) === 1);
    test("Math.pow", () => Math.pow(2,3) === 8);
    test("Math.sqrt", () => Math.sqrt(16) === 4);
    test("Math.random", () => { var r=Math.random(); return r>=0 && r<1; });
    test("Math.PI", () => Math.PI > 3.14 && Math.PI < 3.15);
    
    // Date (basic)
    test("new Date()", () => new Date() instanceof Date);
    test("Date.now exists", () => typeof Date.now === "function");
    
    // Error handling
    test("try/catch", () => { try{throw new Error("test");return false;}catch(e){return e.message==="test";} });
    test("throw statement", () => { try{throw "oops";return false;}catch(e){return e==="oops";} });
    
    // this keyword
    test("this in method", () => { var o={x:5,f:function(){return this.x;}}; return o.f()===5; });
    
    // === ES3 (1999) Additions ===
    results.push("=== ES3 (1999) ===");
    
    test("RegExp literal", () => /test/.test("testing"));
    test("RegExp.test()", () => /\d+/.test("abc123def"));
    test("RegExp.exec()", () => { var m=/(\d+)/.exec("abc123"); return m && m[1]==="123"; });
    test("String.match()", () => { var m="abc123".match(/\d+/); return m && m[0]==="123"; });
    test("String.replace()", () => "hello".replace(/l/g,"x") === "hexxo");
    test("String.search()", () => "abc123".search(/\d/) === 3);
    test("instanceof operator", () => [] instanceof Array && {} instanceof Object);
    test("Array.isArray (ES5)", () => Array.isArray ? Array.isArray([]) : "N/A");
    
    // Summary
    results.push(`\n=== SUMMARY: ${pass} passed, ${fail} failed ===`);
    
    return results.join("\n");
}
