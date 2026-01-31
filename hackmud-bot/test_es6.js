// ES6/ES2015 Feature Test for Hackmud
// Tests: let/const, arrow, classes, destructuring, template literals, etc

function(context, args) {
    let results = [];
    results.push("=== ES6/ES2015 FEATURES ===");
    
    // === LET/CONST ===
    results.push("\n--- Variables ---");
    
    let x = 1;
    x = 2;
    results.push("let: " + (x === 2 ? "✓" : "✗"));
    
    const y = 42;
    results.push("const: " + (y === 42 ? "✓" : "✗"));
    
    // Block scoping
    let outer = "outer";
    {
        let inner = "inner";
        outer = "modified";
    }
    results.push("block scope: " + (outer === "modified" ? "✓" : "✗"));
    
    // === ARROW FUNCTIONS ===
    results.push("\n--- Arrow Functions ---");
    
    const add = (a, b) => a + b;
    results.push("arrow basic: " + (add(2, 3) === 5 ? "✓" : "✗"));
    
    const square = x => x * x;
    results.push("arrow single param: " + (square(4) === 16 ? "✓" : "✗"));
    
    const getObj = () => ({a: 1});
    results.push("arrow return obj: " + (getObj().a === 1 ? "✓" : "✗"));
    
    // === DEFAULT/REST/SPREAD ===
    results.push("\n--- Params & Spread ---");
    
    const greet = (name = "World") => "Hello " + name;
    results.push("default params: " + (greet() === "Hello World" ? "✓" : "✗"));
    
    const sum = (...nums) => nums.reduce((a,b) => a+b, 0);
    results.push("rest params: " + (sum(1,2,3,4) === 10 ? "✓" : "✗"));
    
    const arr1 = [1, 2];
    const arr2 = [...arr1, 3, 4];
    results.push("spread array: " + (arr2.length === 4 ? "✓" : "✗"));
    
    // === CLASSES ===
    results.push("\n--- Classes ---");
    
    class Animal {
        constructor(name) { this.name = name; }
        speak() { return this.name + " speaks"; }
        static type() { return "Animal"; }
    }
    
    const dog = new Animal("Dog");
    results.push("class + constructor: " + (dog.name === "Dog" ? "✓" : "✗"));
    results.push("class method: " + (dog.speak() === "Dog speaks" ? "✓" : "✗"));
    results.push("static method: " + (Animal.type() === "Animal" ? "✓" : "✗"));
    
    class Cat extends Animal {
        speak() { return this.name + " meows"; }
    }
    const cat = new Cat("Whiskers");
    results.push("extends: " + (cat.speak() === "Whiskers meows" ? "✓" : "✗"));
    
    // === DESTRUCTURING ===
    results.push("\n--- Destructuring ---");
    
    const [a, b, c] = [1, 2, 3];
    results.push("array destructure: " + (a === 1 && b === 2 ? "✓" : "✗"));
    
    const {name, age} = {name: "Bob", age: 30};
    results.push("object destructure: " + (name === "Bob" ? "✓" : "✗"));
    
    const {x: px, y: py} = {x: 10, y: 20};
    results.push("rename destructure: " + (px === 10 ? "✓" : "✗"));
    
    // === TEMPLATE LITERALS ===
    results.push("\n--- Template Literals ---");
    
    const val = 42;
    const tpl = `Value is ${val}`;
    results.push("interpolation: " + (tpl === "Value is 42" ? "✓" : "✗"));
    
    const multi = `line1
line2`;
    results.push("multiline: " + (multi.includes("\n") ? "✓" : "✗"));
    
    // === FOR...OF ===
    results.push("\n--- Iterators ---");
    
    let forOfSum = 0;
    for (const n of [1, 2, 3]) { forOfSum += n; }
    results.push("for...of: " + (forOfSum === 6 ? "✓" : "✗"));
    
    // === MAP/SET ===
    results.push("\n--- Collections ---");
    
    const map = new Map();
    map.set("key", "value");
    results.push("Map: " + (map.get("key") === "value" ? "✓" : "✗"));
    
    const set = new Set([1, 2, 2, 3]);
    results.push("Set: " + (set.size === 3 ? "✓" : "✗"));
    
    // === SYMBOL ===
    results.push("\n--- Symbol ---");
    const sym = Symbol("test");
    results.push("Symbol: " + (typeof sym === "symbol" ? "✓" : "✗"));
    
    // === PROMISE ===
    results.push("\n--- Promise ---");
    results.push("Promise exists: " + (typeof Promise === "function" ? "✓" : "✗"));
    
    // === OTHER ES6 ===
    results.push("\n--- Other ES6 ---");
    results.push("Array.from: " + (Array.from("abc").join(",") === "a,b,c" ? "✓" : "✗"));
    results.push("Array.of: " + (Array.of(1,2,3).length === 3 ? "✓" : "✗"));
    results.push("Object.assign: " + (Object.assign({}, {a:1}).a === 1 ? "✓" : "✗"));
    results.push("includes: " + ("hello".includes("ell") ? "✓" : "✗"));
    results.push("startsWith: " + ("hello".startsWith("he") ? "✓" : "✗"));
    results.push("endsWith: " + ("hello".endsWith("lo") ? "✓" : "✗"));
    results.push("repeat: " + ("ab".repeat(3) === "ababab" ? "✓" : "✗"));
    
    return results.join("\n");
}
