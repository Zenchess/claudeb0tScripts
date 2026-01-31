# Hackmud JavaScript Feature Reference

**Project:** Comprehensive JavaScript feature testing for hackmud scripting  
**Started:** 2026-01-30  
**Author:** claudeb0t (for kaj)

## Testing Methodology

Each feature is tested by creating a hackmud script that exercises the feature and returns a result object indicating:
- ✅ Supported (works as expected)
- ⚠️ Partial (works with caveats)  
- ❌ Unsupported (throws error or doesn't work)

## Test Files

| File | Coverage |
|------|----------|
| `es1_es3_test.js` | ES1 (1997) - ES3 (1999): Core primitives, types, operators, loops, functions, objects, arrays, regex |
| `es5_test.js` | ES5 (2009): strict mode, JSON, Array methods, Object methods, getters/setters |
| `es6_test.js` | ES6/2015: let/const, arrow functions, classes, template literals, destructuring, Promises, Map/Set |
| `es2016_es2020_test.js` | ES2016-ES2020: **, includes, async/await, Object.entries/values, optional chaining, BigInt |
| `es2021_es2025_test.js` | ES2021-ES2025: logical assignment, replaceAll, at(), Object.hasOwn, Set methods |
| `wasm_typescript_test.js` | WebAssembly, TypeScript patterns, Typed Arrays |

## How to Run Tests

Upload each test file as a hackmud script and run it:

```
#up es1_es3_test
claudeb0t.es1_es3_test{}
```

## Coverage Summary

### ES1-ES3 (Foundation)
- Variable declarations: `var`
- Types: number, string, boolean, undefined, null, object, function
- Operators: arithmetic, comparison, logical, bitwise, ternary
- Control flow: if/else, for, while, do-while, switch, break, continue
- Functions: declaration, expression, arguments, recursion
- Objects: literals, property access, deletion, `in` operator
- Arrays: literals, indexing, length
- Built-ins: Math, String, Array, Date, RegExp
- Error handling: try/catch/finally, throw

### ES5 (2009)
- `"use strict"` mode
- JSON.parse/stringify
- Array methods: forEach, map, filter, reduce, some, every, indexOf
- Object methods: keys, create, defineProperty, freeze, seal
- Getters/setters
- Function.bind
- String.trim
- Date.now

### ES6/2015
- `let` and `const`
- Arrow functions
- Template literals
- Destructuring (object/array)
- Rest/spread operators
- Default parameters
- Classes and inheritance
- Symbols
- Map, Set, WeakMap, WeakSet
- Promises
- for-of loops
- New String/Array methods

### ES2016-ES2020
- Exponentiation operator `**`
- Array.includes
- async/await
- Object.values/entries
- String padding
- Object rest/spread
- Optional chaining `?.`
- Nullish coalescing `??`
- BigInt
- Promise.allSettled
- globalThis

### ES2021-ES2025
- Logical assignment operators `&&=` `||=` `??=`
- String.replaceAll
- Numeric separators `1_000_000`
- Class fields (public/private)
- Array.at()
- Object.hasOwn
- Error.cause
- Array.findLast/findLastIndex
- Non-mutating array methods: toSorted, toReversed, toSpliced, with
- Set methods: union, intersection, difference

### WebAssembly
- Module creation
- Instance instantiation  
- Memory and Table
- Imports/exports
- Custom functions (add, multiply)

### TypeScript
- Type annotations (compile-time only)
- Interfaces (compile-time only)
- Enums as objects
- Type guards
- Optional properties

### Typed Arrays
- Int8/16/32Array
- Uint8/16/32Array
- Float32/64Array
- BigInt64/BigUint64Array
- DataView
- ArrayBuffer

## Export Formats (TODO)

- [ ] Codepilot/IDE syntax highlighting reference
- [ ] JSON/YAML lookup table
- [ ] Markdown documentation

---

*Tests need to be run in hackmud to get actual results.*
