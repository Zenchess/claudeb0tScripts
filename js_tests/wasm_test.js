// WASM Support Test for Hackmud
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
    
    results.push("=== WebAssembly Support ===");
    
    // Core WASM availability
    test("WebAssembly object exists", () => typeof WebAssembly === "object");
    test("WebAssembly.Module exists", () => typeof WebAssembly.Module === "function");
    test("WebAssembly.Instance exists", () => typeof WebAssembly.Instance === "function");
    test("WebAssembly.compile exists", () => typeof WebAssembly.compile === "function");
    test("WebAssembly.instantiate exists", () => typeof WebAssembly.instantiate === "function");
    test("WebAssembly.validate exists", () => typeof WebAssembly.validate === "function");
    
    // Add function (Kaj's example)
    test("WASM add(3,5)=8", () => {
        let buffer = new Uint8Array([
            0,  97, 115, 109,   1,   0,   0,   0,   1,   7,   1,  96,   2, 127, 127,   1, 
          127,   3,   2,   1,   0,   7,   7,   1,   3,  97, 100, 100,   0,   0,  10,   9, 
            1,   7,   0,  32,   0,  32,   1, 106,  11, 
        ]);
        let module = new WebAssembly.Module(buffer);
        let inst = new WebAssembly.Instance(module, {});
        return inst.exports.add(3, 5) === 8;
    });
    
    // Multiplication test
    test("WASM multiply(6,7)=42", () => {
        // (module (func (export "mul") (param i32 i32) (result i32) local.get 0 local.get 1 i32.mul))
        let buffer = new Uint8Array([
            0, 97, 115, 109, 1, 0, 0, 0, 1, 7, 1, 96, 2, 127, 127, 1,
            127, 3, 2, 1, 0, 7, 7, 1, 3, 109, 117, 108, 0, 0, 10, 9,
            1, 7, 0, 32, 0, 32, 1, 108, 11
        ]);
        let module = new WebAssembly.Module(buffer);
        let inst = new WebAssembly.Instance(module, {});
        return inst.exports.mul(6, 7) === 42;
    });
    
    // WebAssembly.validate
    test("WASM validate (valid)", () => {
        let buffer = new Uint8Array([0, 97, 115, 109, 1, 0, 0, 0]);
        return WebAssembly.validate(buffer) === true;
    });
    
    test("WASM validate (invalid)", () => {
        let buffer = new Uint8Array([1, 2, 3, 4]);
        return WebAssembly.validate(buffer) === false;
    });
    
    // Memory
    test("WebAssembly.Memory", () => {
        try {
            let mem = new WebAssembly.Memory({initial: 1});
            return mem.buffer.byteLength === 65536; // 1 page = 64KB
        } catch(e) { return e.message; }
    });
    
    // Table
    test("WebAssembly.Table", () => {
        try {
            let table = new WebAssembly.Table({initial: 1, element: "anyfunc"});
            return table.length === 1;
        } catch(e) { return e.message; }
    });
    
    // Global
    test("WebAssembly.Global", () => {
        try {
            let g = new WebAssembly.Global({value: "i32", mutable: true}, 42);
            return g.value === 42;
        } catch(e) { return e.message; }
    });
    
    // More complex: factorial
    test("WASM factorial(5)=120", () => {
        // Iterative factorial in WASM
        // (module
        //   (func (export "fact") (param i32) (result i32)
        //     (local i32)
        //     i32.const 1
        //     local.set 1
        //     block
        //       loop
        //         local.get 0
        //         i32.eqz
        //         br_if 1
        //         local.get 1
        //         local.get 0
        //         i32.mul
        //         local.set 1
        //         local.get 0
        //         i32.const 1
        //         i32.sub
        //         local.set 0
        //         br 0
        //       end
        //     end
        //     local.get 1
        //   )
        // )
        let buffer = new Uint8Array([
            0, 97, 115, 109, 1, 0, 0, 0, 1, 6, 1, 96, 1, 127, 1, 127,
            3, 2, 1, 0, 7, 8, 1, 4, 102, 97, 99, 116, 0, 0, 10, 31,
            1, 29, 1, 1, 127, 65, 1, 33, 1, 2, 64, 3, 64, 32, 0, 69,
            13, 1, 32, 1, 32, 0, 108, 33, 1, 32, 0, 65, 1, 107, 33, 0,
            12, 0, 11, 11, 32, 1, 11
        ]);
        let module = new WebAssembly.Module(buffer);
        let inst = new WebAssembly.Instance(module, {});
        return inst.exports.fact(5) === 120;
    });
    
    // i64 support
    test("WASM i64 (BigInt)", () => {
        // (module (func (export "i64test") (result i64) i64.const 9007199254740993))
        let buffer = new Uint8Array([
            0, 97, 115, 109, 1, 0, 0, 0, 1, 5, 1, 96, 0, 1, 126,
            3, 2, 1, 0, 7, 11, 1, 7, 105, 54, 52, 116, 101, 115, 116, 0, 0,
            10, 13, 1, 11, 0, 66, 129, 128, 128, 128, 128, 128, 128, 16, 11
        ]);
        try {
            let module = new WebAssembly.Module(buffer);
            let inst = new WebAssembly.Instance(module, {});
            let result = inst.exports.i64test();
            return typeof result === "bigint" && result === 9007199254740993n;
        } catch(e) { return e.message; }
    });
    
    // f32 support
    test("WASM f32", () => {
        // (module (func (export "f32test") (result f32) f32.const 3.14))
        let buffer = new Uint8Array([
            0, 97, 115, 109, 1, 0, 0, 0, 1, 5, 1, 96, 0, 1, 125,
            3, 2, 1, 0, 7, 11, 1, 7, 102, 51, 50, 116, 101, 115, 116, 0, 0,
            10, 9, 1, 7, 0, 67, 195, 245, 72, 64, 11
        ]);
        try {
            let module = new WebAssembly.Module(buffer);
            let inst = new WebAssembly.Instance(module, {});
            let result = inst.exports.f32test();
            return Math.abs(result - 3.14) < 0.01;
        } catch(e) { return e.message; }
    });
    
    // Summary
    results.push(`\n=== SUMMARY: ${pass} passed, ${fail} failed ===`);
    
    return results.join("\n");
}
