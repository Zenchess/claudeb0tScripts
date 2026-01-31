// WebAssembly Feature Test for Hackmud
// Based on Kaj's working example

function(context, args) {
    let results = [];
    results.push("=== WEBASSEMBLY TESTS ===");
    
    // Test 1: Basic availability
    results.push("\n--- Availability ---");
    results.push("WebAssembly object: " + (typeof WebAssembly !== "undefined" ? "✓" : "✗"));
    results.push("WebAssembly.Module: " + (typeof WebAssembly.Module === "function" ? "✓" : "✗"));
    results.push("WebAssembly.Instance: " + (typeof WebAssembly.Instance === "function" ? "✓" : "✗"));
    results.push("WebAssembly.Memory: " + (typeof WebAssembly.Memory === "function" ? "✓" : "✗"));
    results.push("WebAssembly.Table: " + (typeof WebAssembly.Table === "function" ? "✓" : "✗"));
    
    // Test 2: Kaj's add function (CONFIRMED WORKING)
    results.push("\n--- Basic Function (add) ---");
    try {
        // (module
        //   (func (export "add") (param i32 i32) (result i32)
        //     local.get 0
        //     local.get 1
        //     i32.add
        //   )
        // )
        let buffer = new Uint8Array([
            0,  97, 115, 109,   1,   0,   0,   0,   1,   7,   1,  96,   2, 127, 127,   1, 
          127,   3,   2,   1,   0,   7,   7,   1,   3,  97, 100, 100,   0,   0,  10,   9, 
            1,   7,   0,  32,   0,  32,   1, 106,  11, 
        ]);
        
        let module = new WebAssembly.Module(buffer);
        let inst = new WebAssembly.Instance(module, {});
        let result = inst.exports.add(3, 5);
        
        results.push("add(3, 5) = " + result + " " + (result === 8 ? "✓" : "✗"));
        results.push("add(100, 200) = " + inst.exports.add(100, 200) + " " + (inst.exports.add(100, 200) === 300 ? "✓" : "✗"));
        results.push("add(-5, 10) = " + inst.exports.add(-5, 10) + " " + (inst.exports.add(-5, 10) === 5 ? "✓" : "✗"));
    } catch (e) {
        results.push("add function: ✗ (" + e.message + ")");
    }
    
    // Test 3: Multiply function
    results.push("\n--- Multiply Function ---");
    try {
        // (module
        //   (func (export "mul") (param i32 i32) (result i32)
        //     local.get 0
        //     local.get 1
        //     i32.mul
        //   )
        // )
        let mulBuffer = new Uint8Array([
            0,  97, 115, 109,   1,   0,   0,   0,   1,   7,   1,  96,   2, 127, 127,   1,
          127,   3,   2,   1,   0,   7,   7,   1,   3, 109, 117, 108,   0,   0,  10,   9,
            1,   7,   0,  32,   0,  32,   1, 108,  11,
        ]);
        
        let mulModule = new WebAssembly.Module(mulBuffer);
        let mulInst = new WebAssembly.Instance(mulModule, {});
        let mulResult = mulInst.exports.mul(6, 7);
        
        results.push("mul(6, 7) = " + mulResult + " " + (mulResult === 42 ? "✓" : "✗"));
    } catch (e) {
        results.push("mul function: ✗ (" + e.message + ")");
    }
    
    // Test 4: Memory operations
    results.push("\n--- Memory ---");
    try {
        let memory = new WebAssembly.Memory({initial: 1}); // 1 page = 64KB
        results.push("Memory create: " + (memory.buffer.byteLength === 65536 ? "✓" : "✗"));
        
        // Write and read from memory
        let view = new Uint8Array(memory.buffer);
        view[0] = 42;
        results.push("Memory write/read: " + (view[0] === 42 ? "✓" : "✗"));
    } catch (e) {
        results.push("Memory: ✗ (" + e.message + ")");
    }
    
    // Test 5: Table
    results.push("\n--- Table ---");
    try {
        let table = new WebAssembly.Table({initial: 2, element: "anyfunc"});
        results.push("Table create: " + (table.length === 2 ? "✓" : "✗"));
    } catch (e) {
        results.push("Table: ✗ (" + e.message + ")");
    }
    
    // Test 6: Validate
    results.push("\n--- Validation ---");
    try {
        let validBuffer = new Uint8Array([0, 97, 115, 109, 1, 0, 0, 0]); // minimal valid module
        let isValid = WebAssembly.validate(validBuffer);
        results.push("WebAssembly.validate: " + (isValid ? "✓" : "✗"));
    } catch (e) {
        results.push("WebAssembly.validate: ✗ (" + e.message + ")");
    }
    
    // Test 7: Compile (async)
    results.push("\n--- Async APIs ---");
    results.push("WebAssembly.compile: " + (typeof WebAssembly.compile === "function" ? "✓ (exists)" : "✗"));
    results.push("WebAssembly.instantiate: " + (typeof WebAssembly.instantiate === "function" ? "✓ (exists)" : "✗"));
    
    return results.join("\n");
}
