# Hackmud JavaScript Feature Testing

**Task:** Test every JavaScript feature from ES1-ES2025 + TypeScript + WASM
**Requested by:** Kaj (2026-01-30)
**Goal:** Create comprehensive scripting reference for hackmud

## Testing Methodology
1. Create minimal test scripts for each feature
2. Upload and execute in hackmud
3. Document: ✅ Works / ❌ Blocked / ⚠️ Partial

---

## ES1 (ECMAScript 1997) - Core Primitives

### Variables & Types
| Feature | Status | Notes |
|---------|--------|-------|
| `var` declaration | | |
| Numbers | | |
| Strings | | |
| Booleans | | |
| `null` | | |
| `undefined` | | |
| Objects `{}` | | |
| Arrays `[]` | | |

### Operators
| Feature | Status | Notes |
|---------|--------|-------|
| Arithmetic (+,-,*,/,%) | | |
| Comparison (==,!=,<,>,<=,>=) | | |
| Logical (&&, \|\|, !) | | |
| Assignment (=,+=,-=,etc) | | |
| typeof | | |

### Control Flow
| Feature | Status | Notes |
|---------|--------|-------|
| `if/else` | | |
| `for` loop | | |
| `while` loop | | |
| `do-while` loop | | |
| `switch/case` | | |
| `break/continue` | | |

### Functions
| Feature | Status | Notes |
|---------|--------|-------|
| `function` declaration | | |
| `return` statement | | |
| Parameters | | |
| Nested functions | | |

---

## ES3 (1999)

| Feature | Status | Notes |
|---------|--------|-------|
| `try/catch/finally` | | |
| `throw` | | |
| `in` operator | | |
| `instanceof` | | |
| `===` and `!==` | | |
| Regex literals `/pattern/` | | |

---

## ES5 (2009)

### Strict Mode
| Feature | Status | Notes |
|---------|--------|-------|
| `"use strict"` | | |

### Array Methods
| Feature | Status | Notes |
|---------|--------|-------|
| `forEach()` | | |
| `map()` | | |
| `filter()` | | |
| `reduce()` | | |
| `every()` | | |
| `some()` | | |
| `indexOf()` | | |
| `lastIndexOf()` | | |
| `isArray()` | | |

### Object Methods
| Feature | Status | Notes |
|---------|--------|-------|
| `Object.keys()` | | |
| `Object.create()` | | |
| `Object.defineProperty()` | | |
| `Object.freeze()` | | |
| `Object.seal()` | | |
| Getters/Setters | | |

### JSON
| Feature | Status | Notes |
|---------|--------|-------|
| `JSON.parse()` | | |
| `JSON.stringify()` | | |

### String
| Feature | Status | Notes |
|---------|--------|-------|
| `trim()` | | |
| `charAt()` | | |
| `indexOf()` | | |

### Other
| Feature | Status | Notes |
|---------|--------|-------|
| `Function.prototype.bind()` | | |
| `Date.now()` | | |

---

## ES6/ES2015

### Variables
| Feature | Status | Notes |
|---------|--------|-------|
| `let` | | |
| `const` | | |
| Block scoping | | |
| Temporal dead zone | | |

### Functions
| Feature | Status | Notes |
|---------|--------|-------|
| Arrow functions `=>` | | |
| Default parameters | | |
| Rest parameters `...args` | | |
| Spread operator `...arr` | | |

### Classes
| Feature | Status | Notes |
|---------|--------|-------|
| `class` declaration | | |
| `constructor` | | |
| `extends` | | |
| `super` | | |
| `static` methods | | |

### Destructuring
| Feature | Status | Notes |
|---------|--------|-------|
| Array destructuring | | |
| Object destructuring | | |
| Nested destructuring | | |

### Template Literals
| Feature | Status | Notes |
|---------|--------|-------|
| Backtick strings | | |
| String interpolation `${}` | | |
| Multi-line strings | | |
| Tagged templates | | |

### Iterators & Generators
| Feature | Status | Notes |
|---------|--------|-------|
| `for...of` | | |
| `Symbol.iterator` | | |
| `function*` generators | | |
| `yield` | | |

### Promises
| Feature | Status | Notes |
|---------|--------|-------|
| `new Promise()` | | |
| `.then()` | | |
| `.catch()` | | |
| `Promise.resolve()` | | |
| `Promise.reject()` | | |
| `Promise.all()` | | |

### Collections
| Feature | Status | Notes |
|---------|--------|-------|
| `Map` | | |
| `Set` | | |
| `WeakMap` | | |
| `WeakSet` | | |

### Other ES6
| Feature | Status | Notes |
|---------|--------|-------|
| `Symbol` | | |
| `Proxy` | | |
| `Reflect` | | |
| `Number.isNaN()` | | |
| `Number.isFinite()` | | |
| `Array.from()` | | |
| `Array.of()` | | |
| `Object.assign()` | | |
| `String.includes()` | | |
| `String.startsWith()` | | |
| `String.endsWith()` | | |
| `String.repeat()` | | |

---

## ES2016 (ES7)

| Feature | Status | Notes |
|---------|--------|-------|
| `Array.includes()` | | |
| Exponentiation `**` | | |

---

## ES2017 (ES8)

| Feature | Status | Notes |
|---------|--------|-------|
| `async/await` | | |
| `Object.values()` | | |
| `Object.entries()` | | |
| `String.padStart()` | | |
| `String.padEnd()` | | |
| Trailing commas in params | | |

---

## ES2018 (ES9)

| Feature | Status | Notes |
|---------|--------|-------|
| Async iteration `for await` | | |
| Rest/spread for objects | | |
| `Promise.finally()` | | |
| Regex named groups | | |
| Regex lookbehind | | |

---

## ES2019 (ES10)

| Feature | Status | Notes |
|---------|--------|-------|
| `Array.flat()` | | |
| `Array.flatMap()` | | |
| `Object.fromEntries()` | | |
| `String.trimStart()` | | |
| `String.trimEnd()` | | |
| Optional catch binding | | |
| `Symbol.description` | | |

---

## ES2020 (ES11)

| Feature | Status | Notes |
|---------|--------|-------|
| Optional chaining `?.` | | |
| Nullish coalescing `??` | | |
| `BigInt` | | |
| `Promise.allSettled()` | | |
| `globalThis` | | |
| Dynamic import `import()` | | |
| `String.matchAll()` | | |

---

## ES2021 (ES12)

| Feature | Status | Notes |
|---------|--------|-------|
| `String.replaceAll()` | | |
| `Promise.any()` | | |
| Logical assignment `&&=` `||=` `??=` | | |
| Numeric separators `1_000` | | |
| `WeakRef` | | |
| `FinalizationRegistry` | | |

---

## ES2022 (ES13)

| Feature | Status | Notes |
|---------|--------|-------|
| Top-level await | | |
| Class fields (public) | | |
| Private fields `#field` | | |
| Private methods | | |
| Static blocks | | |
| `Array.at()` | | |
| `String.at()` | | |
| `Object.hasOwn()` | | |
| Regex `/d` flag (indices) | | |
| `Error.cause` | | |

---

## ES2023 (ES14)

| Feature | Status | Notes |
|---------|--------|-------|
| `Array.findLast()` | | |
| `Array.findLastIndex()` | | |
| `Array.toReversed()` | | |
| `Array.toSorted()` | | |
| `Array.toSpliced()` | | |
| `Array.with()` | | |
| Hashbang `#!` support | | |
| Symbols as WeakMap keys | | |

---

## ES2024 (ES15)

| Feature | Status | Notes |
|---------|--------|-------|
| `Object.groupBy()` | | |
| `Map.groupBy()` | | |
| `Promise.withResolvers()` | | |
| `ArrayBuffer.resize()` | | |
| `ArrayBuffer.transfer()` | | |
| Regex `/v` flag | | |

---

## ES2025 (ES16)

| Feature | Status | Notes |
|---------|--------|-------|
| `Set.difference()` | | |
| `Set.intersection()` | | |
| `Set.union()` | | |
| `Set.symmetricDifference()` | | |
| `Set.isSubsetOf()` | | |
| `Set.isSupersetOf()` | | |
| `Set.isDisjointFrom()` | | |

---

## TypeScript Features

| Feature | Status | Notes |
|---------|--------|-------|
| Type annotations | | Compile-time only? |
| Interfaces | | |
| Enums | | |
| Generics | | |
| Decorators | | |

---

## WebAssembly

| Feature | Status | Notes |
|---------|--------|-------|
| `WebAssembly.Module` | ✅ | Kaj confirmed working |
| `WebAssembly.Instance` | ✅ | Kaj confirmed working |
| Basic functions | ✅ | add(3,5)=8 works |
| Memory operations | | |
| Tables | | |
| Imports/Exports | | |

---

## Test Scripts Created

| Script | Features Tested | Location |
|--------|-----------------|----------|
| | | |

---

## Notes & Discoveries

- WASM works! Kaj's example: `new WebAssembly.Module(buffer)` + `new WebAssembly.Instance(module)` returns correct result
- Testing in progress...

---

*Last updated: 2026-01-30*
