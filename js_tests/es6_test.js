// ES6/ES2015 Feature Tests
function(c, a) {
    let results = [];
    
    // === LET/CONST ===
    try { let x = 1; results.push("✓ let"); } catch(e) { results.push("✗ let: " + e.message); }
    try { const y = 1; results.push("✓ const"); } catch(e) { results.push("✗ const: " + e.message); }
    
    // === ARROW FUNCTIONS ===
    try { const f = () => 1; f(); results.push("✓ arrow function () => expr"); } catch(e) { results.push("✗ arrow: " + e.message); }
    try { const f = x => x*2; f(2); results.push("✓ arrow function x => expr"); } catch(e) { results.push("✗ arrow single param: " + e.message); }
    try { const f = (a,b) => a+b; f(1,2); results.push("✓ arrow function (a,b) => expr"); } catch(e) { results.push("✗ arrow multi param: " + e.message); }
    try { const f = () => { return 1; }; f(); results.push("✓ arrow function with block"); } catch(e) { results.push("✗ arrow block: " + e.message); }
    
    // === TEMPLATE LITERALS ===
    try { const s = `hello`; results.push("✓ template literal"); } catch(e) { results.push("✗ template literal: " + e.message); }
    try { const x = 1; const s = `x is ${x}`; results.push("✓ template interpolation ${expr}"); } catch(e) { results.push("✗ template interp: " + e.message); }
    try { const s = `line1
line2`; results.push("✓ template multiline"); } catch(e) { results.push("✗ template multiline: " + e.message); }
    
    // === DESTRUCTURING ===
    try { const [a,b] = [1,2]; results.push("✓ array destructuring"); } catch(e) { results.push("✗ array destructure: " + e.message); }
    try { const {x,y} = {x:1,y:2}; results.push("✓ object destructuring"); } catch(e) { results.push("✗ object destructure: " + e.message); }
    try { const {a:x} = {a:1}; results.push("✓ destructuring rename"); } catch(e) { results.push("✗ destructure rename: " + e.message); }
    try { const {a=0} = {}; results.push("✓ destructuring default"); } catch(e) { results.push("✗ destructure default: " + e.message); }
    try { const [a,...rest] = [1,2,3]; results.push("✓ array rest destructuring"); } catch(e) { results.push("✗ array rest: " + e.message); }
    try { const {a,...rest} = {a:1,b:2,c:3}; results.push("✓ object rest destructuring"); } catch(e) { results.push("✗ object rest: " + e.message); }
    
    // === SPREAD OPERATOR ===
    try { const a = [1,2]; const b = [...a,3]; results.push("✓ array spread"); } catch(e) { results.push("✗ array spread: " + e.message); }
    try { const o = {a:1}; const p = {...o,b:2}; results.push("✓ object spread"); } catch(e) { results.push("✗ object spread: " + e.message); }
    try { function f(...args){return args;} f(1,2,3); results.push("✓ rest parameters"); } catch(e) { results.push("✗ rest params: " + e.message); }
    
    // === SHORTHAND SYNTAX ===
    try { const x=1; const o = {x}; results.push("✓ shorthand property"); } catch(e) { results.push("✗ shorthand prop: " + e.message); }
    try { const o = {fn(){return 1;}}; o.fn(); results.push("✓ shorthand method"); } catch(e) { results.push("✗ shorthand method: " + e.message); }
    try { const k='x'; const o = {[k]:1}; results.push("✓ computed property name"); } catch(e) { results.push("✗ computed prop: " + e.message); }
    
    // === DEFAULT PARAMETERS ===
    try { function f(x=1){return x;} f(); results.push("✓ default parameters"); } catch(e) { results.push("✗ default params: " + e.message); }
    
    // === FOR-OF ===
    try { for(const x of [1,2,3]){} results.push("✓ for-of loop"); } catch(e) { results.push("✗ for-of: " + e.message); }
    
    // === CLASSES ===
    try { class C {} new C(); results.push("✓ class declaration"); } catch(e) { results.push("✗ class: " + e.message); }
    try { class C {constructor(){this.x=1;}} new C(); results.push("✓ class constructor"); } catch(e) { results.push("✗ class constructor: " + e.message); }
    try { class C {fn(){return 1;}} new C().fn(); results.push("✓ class methods"); } catch(e) { results.push("✗ class methods: " + e.message); }
    try { class C {static fn(){return 1;}} C.fn(); results.push("✓ static methods"); } catch(e) { results.push("✗ static methods: " + e.message); }
    try { class A {} class B extends A {} new B(); results.push("✓ class extends"); } catch(e) { results.push("✗ extends: " + e.message); }
    try { class A {fn(){return 1;}} class B extends A {fn(){return super.fn()+1;}} results.push("✓ super keyword"); } catch(e) { results.push("✗ super: " + e.message); }
    
    // === SYMBOL ===
    try { const s = Symbol(); results.push("✓ Symbol()"); } catch(e) { results.push("✗ Symbol: " + e.message); }
    try { const s = Symbol("desc"); results.push("✓ Symbol(description)"); } catch(e) { results.push("✗ Symbol desc: " + e.message); }
    try { Symbol.iterator; results.push("✓ Symbol.iterator"); } catch(e) { results.push("✗ Symbol.iterator: " + e.message); }
    
    // === MAP/SET ===
    try { new Map(); results.push("✓ Map"); } catch(e) { results.push("✗ Map: " + e.message); }
    try { const m = new Map(); m.set('a',1); m.get('a'); results.push("✓ Map.set/get"); } catch(e) { results.push("✗ Map set/get: " + e.message); }
    try { new Set(); results.push("✓ Set"); } catch(e) { results.push("✗ Set: " + e.message); }
    try { const s = new Set(); s.add(1); s.has(1); results.push("✓ Set.add/has"); } catch(e) { results.push("✗ Set add/has: " + e.message); }
    try { new WeakMap(); results.push("✓ WeakMap"); } catch(e) { results.push("✗ WeakMap: " + e.message); }
    try { new WeakSet(); results.push("✓ WeakSet"); } catch(e) { results.push("✗ WeakSet: " + e.message); }
    
    // === PROMISE ===
    try { new Promise((res,rej)=>res(1)); results.push("✓ Promise"); } catch(e) { results.push("✗ Promise: " + e.message); }
    try { Promise.resolve(1); results.push("✓ Promise.resolve()"); } catch(e) { results.push("✗ Promise.resolve: " + e.message); }
    try { Promise.reject(1).catch(()=>{}); results.push("✓ Promise.reject()"); } catch(e) { results.push("✗ Promise.reject: " + e.message); }
    
    // === PROXY/REFLECT ===
    try { new Proxy({}, {}); results.push("✓ Proxy"); } catch(e) { results.push("✗ Proxy: " + e.message); }
    try { Reflect.get({a:1}, 'a'); results.push("✓ Reflect"); } catch(e) { results.push("✗ Reflect: " + e.message); }
    
    // === NUMBER/MATH ===
    try { Number.isFinite(1); results.push("✓ Number.isFinite()"); } catch(e) { results.push("✗ Number.isFinite: " + e.message); }
    try { Number.isNaN(NaN); results.push("✓ Number.isNaN()"); } catch(e) { results.push("✗ Number.isNaN: " + e.message); }
    try { Number.isInteger(1); results.push("✓ Number.isInteger()"); } catch(e) { results.push("✗ Number.isInteger: " + e.message); }
    try { Number.parseFloat("1.5"); results.push("✓ Number.parseFloat()"); } catch(e) { results.push("✗ Number.parseFloat: " + e.message); }
    try { Number.parseInt("5"); results.push("✓ Number.parseInt()"); } catch(e) { results.push("✗ Number.parseInt: " + e.message); }
    try { Math.trunc(1.5); results.push("✓ Math.trunc()"); } catch(e) { results.push("✗ Math.trunc: " + e.message); }
    try { Math.sign(-5); results.push("✓ Math.sign()"); } catch(e) { results.push("✗ Math.sign: " + e.message); }
    
    // === OBJECT/ARRAY ===
    try { Object.assign({}, {a:1}); results.push("✓ Object.assign()"); } catch(e) { results.push("✗ Object.assign: " + e.message); }
    try { Object.is(1, 1); results.push("✓ Object.is()"); } catch(e) { results.push("✗ Object.is: " + e.message); }
    try { Array.from("abc"); results.push("✓ Array.from()"); } catch(e) { results.push("✗ Array.from: " + e.message); }
    try { Array.of(1,2,3); results.push("✓ Array.of()"); } catch(e) { results.push("✗ Array.of: " + e.message); }
    try { [1,2,3].find(x=>x>1); results.push("✓ Array.find()"); } catch(e) { results.push("✗ Array.find: " + e.message); }
    try { [1,2,3].findIndex(x=>x>1); results.push("✓ Array.findIndex()"); } catch(e) { results.push("✗ Array.findIndex: " + e.message); }
    try { [1,2,3].fill(0); results.push("✓ Array.fill()"); } catch(e) { results.push("✗ Array.fill: " + e.message); }
    try { [1,2,3].copyWithin(0,1); results.push("✓ Array.copyWithin()"); } catch(e) { results.push("✗ Array.copyWithin: " + e.message); }
    try { [1,2,3].includes(2); results.push("✓ Array.includes()"); } catch(e) { results.push("✗ Array.includes: " + e.message); }
    try { [1,2,3].entries(); results.push("✓ Array.entries()"); } catch(e) { results.push("✗ Array.entries: " + e.message); }
    try { [1,2,3].keys(); results.push("✓ Array.keys()"); } catch(e) { results.push("✗ Array.keys: " + e.message); }
    try { [1,2,3].values(); results.push("✓ Array.values()"); } catch(e) { results.push("✗ Array.values: " + e.message); }
    
    // === STRING ===
    try { "abc".includes("b"); results.push("✓ String.includes()"); } catch(e) { results.push("✗ String.includes: " + e.message); }
    try { "abc".startsWith("a"); results.push("✓ String.startsWith()"); } catch(e) { results.push("✗ String.startsWith: " + e.message); }
    try { "abc".endsWith("c"); results.push("✓ String.endsWith()"); } catch(e) { results.push("✗ String.endsWith: " + e.message); }
    try { "ab".repeat(2); results.push("✓ String.repeat()"); } catch(e) { results.push("✗ String.repeat: " + e.message); }
    
    return "=== ES6/ES2015 TEST RESULTS ===\n" + results.join("\n");
}
