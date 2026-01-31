// WebAssembly and TypeScript Feature Tests for Hackmud
// Tests: WASM instantiation, TypeScript compile-time features

function(context, args) {
    let results = {};
    
    // ===== WEBASSEMBLY =====
    results["_header_WASM"] = "=== WebAssembly ===";
    
    // 1. WebAssembly global object
    try {
        results.wasm_global = typeof WebAssembly !== "undefined" ? "✅" : "❌";
    } catch(e) { results.wasm_global = "❌ " + e.message; }
    
    // 2. WebAssembly.Module
    try {
        results.wasm_module = typeof WebAssembly.Module === "function" ? "✅" : "❌";
    } catch(e) { results.wasm_module = "❌ " + e.message; }
    
    // 3. WebAssembly.Instance
    try {
        results.wasm_instance = typeof WebAssembly.Instance === "function" ? "✅" : "❌";
    } catch(e) { results.wasm_instance = "❌ " + e.message; }
    
    // 4. WebAssembly.Memory
    try {
        const memory = new WebAssembly.Memory({ initial: 1 });
        results.wasm_memory = memory.buffer.byteLength === 65536 ? "✅" : "❌";
    } catch(e) { results.wasm_memory = "❌ " + e.message; }
    
    // 5. WebAssembly.Table
    try {
        const table = new WebAssembly.Table({ initial: 1, element: "anyfunc" });
        results.wasm_table = table.length === 1 ? "✅" : "❌";
    } catch(e) { results.wasm_table = "❌ " + e.message; }
    
    // 6. WebAssembly.compile
    try {
        results.wasm_compile = typeof WebAssembly.compile === "function" ? "✅" : "❌";
    } catch(e) { results.wasm_compile = "❌ " + e.message; }
    
    // 7. WebAssembly.instantiate
    try {
        results.wasm_instantiate = typeof WebAssembly.instantiate === "function" ? "✅" : "❌";
    } catch(e) { results.wasm_instantiate = "❌ " + e.message; }
    
    // 8. WebAssembly.validate
    try {
        results.wasm_validate = typeof WebAssembly.validate === "function" ? "✅" : "❌";
    } catch(e) { results.wasm_validate = "❌ " + e.message; }
    
    // 9. WASM add function (kaj's example)
    try {
        let buffer = new Uint8Array([
            0,  97, 115, 109,   1,   0,   0,   0,   1,   7,   1,  96,   2, 127, 127,   1, 
          127,   3,   2,   1,   0,   7,   7,   1,   3,  97, 100, 100,   0,   0,  10,   9, 
            1,   7,   0,  32,   0,  32,   1, 106,  11, 
        ]);
        let module = new WebAssembly.Module(buffer);
        let inst = new WebAssembly.Instance(module, {});
        const result = inst.exports.add(3, 5);
        results.wasm_add_function = result === 8 ? "✅ (3+5=8)" : "❌ got " + result;
    } catch(e) { results.wasm_add_function = "❌ " + e.message; }
    
    // 10. WASM multiply function
    try {
        // (module
        //   (func (export "mul") (param i32 i32) (result i32)
        //     local.get 0
        //     local.get 1
        //     i32.mul
        //   )
        // )
        let buffer = new Uint8Array([
            0,  97, 115, 109,   1,   0,   0,   0,   1,   7,   1,  96,   2, 127, 127,   1,
          127,   3,   2,   1,   0,   7,   7,   1,   3, 109, 117, 108,   0,   0,  10,   9,
            1,   7,   0,  32,   0,  32,   1, 108,  11,
        ]);
        let module = new WebAssembly.Module(buffer);
        let inst = new WebAssembly.Instance(module, {});
        const result = inst.exports.mul(6, 7);
        results.wasm_mul_function = result === 42 ? "✅ (6*7=42)" : "❌ got " + result;
    } catch(e) { results.wasm_mul_function = "❌ " + e.message; }
    
    // 11. WASM with imported function
    try {
        // Module that imports a function
        let buffer = new Uint8Array([
            0, 97, 115, 109, 1, 0, 0, 0, 1, 8, 2, 96, 1, 127, 0, 96,
            0, 0, 2, 11, 1, 3, 101, 110, 118, 3, 108, 111, 103, 0, 0,
            3, 2, 1, 1, 7, 8, 1, 4, 116, 101, 115, 116, 0, 1, 10,
            8, 1, 6, 0, 65, 42, 16, 0, 11
        ]);
        let loggedValue = null;
        let module = new WebAssembly.Module(buffer);
        let inst = new WebAssembly.Instance(module, {
            env: { log: (val) => { loggedValue = val; } }
        });
        inst.exports.test();
        results.wasm_imports = loggedValue === 42 ? "✅" : "❌ got " + loggedValue;
    } catch(e) { results.wasm_imports = "❌ " + e.message; }
    
    // ===== TYPESCRIPT =====
    results["_header_TypeScript"] = "=== TypeScript ===";
    results["_note_ts"] = "⚠️ TypeScript is compile-time only";
    
    // TypeScript features that compile to JS (checking JS equivalents):
    
    // 12. Type annotations compile away (runtime JS)
    try {
        // In TS: const x: number = 5;
        // Compiles to: const x = 5;
        const x = 5;
        results.ts_type_annotations = "✅ (compiles to plain JS)";
    } catch(e) { results.ts_type_annotations = "❌ " + e.message; }
    
    // 13. Interface (compile-time only)
    results.ts_interfaces = "✅ (compile-time, no runtime equivalent)";
    
    // 14. Enums (compile to objects)
    try {
        // TS enum compiles to object
        const Color = { Red: 0, Green: 1, Blue: 2 };
        results.ts_enums_as_objects = Color.Red === 0 ? "✅ (use object literal)" : "❌";
    } catch(e) { results.ts_enums_as_objects = "❌ " + e.message; }
    
    // 15. Type guards (instanceof, typeof work in JS)
    try {
        const isString = (val) => typeof val === "string";
        results.ts_type_guards = isString("hello") ? "✅ (typeof works)" : "❌";
    } catch(e) { results.ts_type_guards = "❌ " + e.message; }
    
    // 16. Optional properties (using ?.)
    try {
        const obj = { a: { b: 1 } };
        results.ts_optional_properties = obj?.a?.b === 1 ? "✅ (use ?.)" : "❌";
    } catch(e) { results.ts_optional_properties = "❌ " + e.message; }
    
    // 17. Readonly (enforcement is compile-time only)
    results.ts_readonly = "✅ (compile-time, use Object.freeze at runtime)";
    
    // 18. Generics (compile-time only)
    results.ts_generics = "✅ (compile-time, no runtime equivalent)";
    
    // 19. Decorators (may require transpilation)
    results.ts_decorators = "⚠️ (requires transpilation, not native JS)";
    
    // 20. Namespace (compiles to IIFE)
    try {
        const MyNamespace = (function() {
            return { helper: () => 42 };
        })();
        results.ts_namespace = MyNamespace.helper() === 42 ? "✅ (use IIFE/object)" : "❌";
    } catch(e) { results.ts_namespace = "❌ " + e.message; }
    
    // ===== TYPED ARRAYS =====
    results["_header_TypedArrays"] = "=== Typed Arrays ===";
    
    // 21. Int8Array
    try {
        const arr = new Int8Array([1, 2, 3]);
        results.int8array = arr[0] === 1 ? "✅" : "❌";
    } catch(e) { results.int8array = "❌ " + e.message; }
    
    // 22. Uint8Array
    try {
        const arr = new Uint8Array([255, 0, 128]);
        results.uint8array = arr[0] === 255 ? "✅" : "❌";
    } catch(e) { results.uint8array = "❌ " + e.message; }
    
    // 23. Int16Array
    try {
        const arr = new Int16Array([1000, -1000]);
        results.int16array = arr[1] === -1000 ? "✅" : "❌";
    } catch(e) { results.int16array = "❌ " + e.message; }
    
    // 24. Uint16Array
    try {
        const arr = new Uint16Array([65535]);
        results.uint16array = arr[0] === 65535 ? "✅" : "❌";
    } catch(e) { results.uint16array = "❌ " + e.message; }
    
    // 25. Int32Array
    try {
        const arr = new Int32Array([2147483647]);
        results.int32array = arr[0] === 2147483647 ? "✅" : "❌";
    } catch(e) { results.int32array = "❌ " + e.message; }
    
    // 26. Uint32Array
    try {
        const arr = new Uint32Array([4294967295]);
        results.uint32array = arr[0] === 4294967295 ? "✅" : "❌";
    } catch(e) { results.uint32array = "❌ " + e.message; }
    
    // 27. Float32Array
    try {
        const arr = new Float32Array([3.14]);
        results.float32array = Math.abs(arr[0] - 3.14) < 0.001 ? "✅" : "❌";
    } catch(e) { results.float32array = "❌ " + e.message; }
    
    // 28. Float64Array
    try {
        const arr = new Float64Array([Math.PI]);
        results.float64array = arr[0] === Math.PI ? "✅" : "❌";
    } catch(e) { results.float64array = "❌ " + e.message; }
    
    // 29. BigInt64Array
    try {
        const arr = new BigInt64Array([9007199254740991n]);
        results.bigint64array = arr[0] === 9007199254740991n ? "✅" : "❌";
    } catch(e) { results.bigint64array = "❌ " + e.message; }
    
    // 30. BigUint64Array
    try {
        const arr = new BigUint64Array([18446744073709551615n]);
        results.biguint64array = arr[0] === 18446744073709551615n ? "✅" : "❌";
    } catch(e) { results.biguint64array = "❌ " + e.message; }
    
    // 31. DataView
    try {
        const buffer = new ArrayBuffer(8);
        const view = new DataView(buffer);
        view.setInt32(0, 42);
        results.dataview = view.getInt32(0) === 42 ? "✅" : "❌";
    } catch(e) { results.dataview = "❌ " + e.message; }
    
    // 32. ArrayBuffer
    try {
        const buffer = new ArrayBuffer(16);
        results.arraybuffer = buffer.byteLength === 16 ? "✅" : "❌";
    } catch(e) { results.arraybuffer = "❌ " + e.message; }
    
    return { es_version: "WASM + TypeScript + Typed Arrays", results: results };
}
