// ═══════════════════════════════════════════════════════════════════════════
// Hackmud Kate Syntax Highlighting Showcase
// ═══════════════════════════════════════════════════════════════════════════
// Author: claudeb0t 🪆⬢
// This file demonstrates ALL syntax highlighting features.
// Open in Kate to see the full color scheme.

/* ═══════════════════════════════════════════════════════════════════════════
   SECTION 1: TRUST-LEVEL SCRIPTORS (Split Coloring)
   Each trust level has its own color:
   - #fs = FULLSEC (bright green #1EFF00) - safest
   - #hs = HIGHSEC (teal #4EC9B0) - trusted  
   - #ms = MIDSEC (yellow #DCDCAA) - medium trust
   - #ls = LOWSEC (orange #FF8000) - caution
   - #ns = NULLSEC (red #F44747) - danger
   - #s  = Generic (gray #808080) - unknown
   
   Scriptor parts are split:
   - Trust prefix → trust-level color (bold)
   - Username → orange #FF8000 (trust) or gray #9B9B9B (user)
   - Script name → green #1EFF00
   ═══════════════════════════════════════════════════════════════════════════ */

// Trust scripts - orange username, green script
#fs.accts.balance               // FULLSEC: balance check
#fs.sys.upgrades                // FULLSEC: list upgrades
#hs.chats.send                  // HIGHSEC: send chat message
#ms.market.browse               // MIDSEC: browse market
#ls.scripts.lowsec              // LOWSEC: check script access
#ns.sys.breach                  // NULLSEC: breach status

// User scripts - gray username, green script
#s.someuser.their_script        // Generic user script
#s.claudeb0t.t2crack            // My cracking script
#s.trust.me                     // Another user script

// All trust script prefixes
#fs.accts.transactions
#fs.autos.reset
#fs.chats.tell
#fs.corps.top
#fs.escrow.stats
#fs.gui.quiet
#fs.kernel.hardline
#fs.market.sell
#fs.marks.sync
#fs.scripts.fullsec
#fs.sys.specs
#fs.trust.me
#fs.users.inspect

/* ═══════════════════════════════════════════════════════════════════════════
   SECTION 2: DATABASE ACCESS (#db)
   Purple highlighting for database operations
   ═══════════════════════════════════════════════════════════════════════════ */

#db.f({ type: "upgrade" })                    // Find documents
#db.i({ name: "item", value: 100 })           // Insert document
#db.r({ _id: #db.ObjectId("abc123") })        // Remove document
#db.u({ name: "item" }, { $set: { value: 200 } })  // Update document
#db.u1({ name: "item" }, { $inc: { count: 1 } })   // Update one
#db.us({ name: "item" }, { value: 150 })      // Upsert

/* ═══════════════════════════════════════════════════════════════════════════
   SECTION 3: HACKMUD MACROS
   Purple bold highlighting
   ═══════════════════════════════════════════════════════════════════════════ */

let debug_output = #D("Debugging value:", some_var)  // Debug print
let formatted = #G                                    // GUI formatting
let fmcl = #FMCL                                      // Find my caller level
let s4 = #4S                                          // ???

/* ═══════════════════════════════════════════════════════════════════════════
   SECTION 4: COLOR CODES (Xstring backtick syntax)
   Gray highlighting (#9B9B9B) - used in `Xstrings`
   ═══════════════════════════════════════════════════════════════════════════ */

// Color codes #0-#9
let colors = `#0gray #1white #2green #3cyan #4red #5orange #6yellow #7white #8gray #9dark`

// Color codes #a-#z  
let more = `#awhite #bred #corange #ddark #eblue #fpurple #g... #z...`

/* ═══════════════════════════════════════════════════════════════════════════
   SECTION 5: HACKMUD GLOBALS
   Light blue highlighting (#9CDCFE)
   ═══════════════════════════════════════════════════════════════════════════ */

let start_time = _START               // Script start timestamp
let end_time = _END                   // Timeout deadline
let timeout = _TIMEOUT                // Timeout value
let run_id = _RUN_ID                  // Unique run identifier

DEEP_FREEZE(some_object)              // Freeze object deeply

/* ═══════════════════════════════════════════════════════════════════════════
   SECTION 5B: FUNCTION PARAMETER HIGHLIGHTING (NEW in v2.2!)
   Special italic highlighting for context/args parameter variations
   - Context variations → Light Blue italic (#9CDCFE)
   - Args variations → Yellow italic (#DCDCAA)
   ═══════════════════════════════════════════════════════════════════════════ */

// Standard naming
function(context, args) {
    let caller = context.caller           // context = light blue italic
    let user_args = args                  // args = yellow italic
    return { ok: true }
}

// Short naming
function(c, a) {
    let caller = c.caller                 // c = light blue italic
    let user_args = a                     // a = yellow italic
}

// Context variations (all light blue italic)
function(ctx, args) { ctx.caller }        // ctx
function(CONTEXT, ARGS) { CONTEXT.caller }  // UPPERCASE
function(CTX, A) { CTX.caller }           // mixed
function(Context, Args) { Context.caller }  // PascalCase
function(_context, _args) { _context.caller }  // underscore prefix
function(context_, args_) { context_.caller }  // underscore suffix
function(cont, arg) { cont.caller }       // abbreviated
function(cntx, params) { cntx.caller }    // other variations
function(cx, p) { cx.caller }             // super short

// Args/input variations (all yellow italic)
function(c, params) { params.target }     // params
function(c, input) { input.value }        // input
function(c, opts) { opts.flag }           // opts
function(c, options) { options.setting }  // options
function(c, data) { data.payload }        // data
function(c, d) { d.key }                  // d (short for data)

// Complete example with all variations recognized
function(context, args) {
    // These will all be highlighted as parameters:
    let ctx = context           // context → light blue italic
    let c = context             // c → light blue italic
    let a = args                // args, a → yellow italic
    let params = args           // params → yellow italic
    let input = args            // input → yellow italic
    
    // Using context variations
    if (ctx.caller == c.caller && context.this_script) {
        // All recognized as the same semantic meaning
    }
    
    // Using args variations  
    if (a.target == args.target && params.value && input.data) {
        // All recognized as args-like parameters
    }
    
    return { ok: true }
}

/* ═══════════════════════════════════════════════════════════════════════════
   SECTION 6: PARAMETER KEYS (Object Keys)
   Cyan highlighting (#00FFFF)
   ═══════════════════════════════════════════════════════════════════════════ */

let obj = {
    to: "target_user",                    // key: cyan, value: string color
    msg: "Hello there!",
    amount: 1000000,
    include_array: [1, 2, 3],
    nested: {
        inner_key: true,
        another: false
    }
}

#fs.chats.tell({ to: "someone", msg: "Hi!" })
#fs.accts.xfer_gc_to({ to: "friend", amount: 500000 })
#fs.sys.xfer_upgrade_to({ i: 0, name: "recipient" })

/* ═══════════════════════════════════════════════════════════════════════════
   SECTION 7: KEYWORDS
   Blue highlighting (#569CD6)
   ═══════════════════════════════════════════════════════════════════════════ */

// Declarations
var old_style = "avoid this"
let modern = "use this"
const CONSTANT = "immutable"
function named_func() { }
class MyClass extends BaseClass {
    constructor() { super() }
    static helper() { }
    get value() { return this._value }
    set value(v) { this._value = v }
}

// Control flow
if (condition) {
    // do something
} else {
    // do something else
}

switch (value) {
    case 1: break
    case 2: continue
    default: return null
}

for (let i = 0; i < 10; i++) { }
for (let item of array) { }
for (let key in object) { }
while (running) { }
do { } while (condition)

try {
    throw new Error("oops")
} catch (e) {
    // handle
} finally {
    // cleanup
}

// Operators & Values
new Date()
delete obj.property
typeof variable
instanceof Object
"key" in object
void 0
this.method()

// Boolean literals
true
false
null
undefined
NaN
Infinity

/* ═══════════════════════════════════════════════════════════════════════════
   SECTION 8: BUILT-IN OBJECTS
   Teal highlighting (#4EC9B0)
   ═══════════════════════════════════════════════════════════════════════════ */

// Fully supported
Object.keys(obj)
Array.isArray(arr)
String.fromCharCode(65)
Number.parseInt("42")
Boolean(value)
Function.prototype
Symbol("unique")
BigInt(9007199254740991)
Math.random()
Date.now()
RegExp("pattern")
Error("message")
JSON.parse("{}")
Map
Set
WeakMap
WeakSet
ArrayBuffer
DataView
Int8Array
Uint8Array
Int16Array
Uint16Array
Int32Array
Uint32Array
Float32Array
Float64Array
WebAssembly

/* ═══════════════════════════════════════════════════════════════════════════
   SECTION 9: METHODS (Array, Object, String, Math, scripts.lib)
   Yellow highlighting (#DCDCAA)
   ═══════════════════════════════════════════════════════════════════════════ */

// Array methods
arr.push(item)
arr.pop()
arr.shift()
arr.unshift(item)
arr.slice(0, 5)
arr.splice(1, 2)
arr.concat(other)
arr.reverse()
arr.sort((a, b) => a - b)
arr.indexOf(item)
arr.lastIndexOf(item)
arr.forEach(fn)
arr.map(x => x * 2)
arr.filter(x => x > 0)
arr.reduce((acc, x) => acc + x, 0)
arr.reduceRight(fn)
arr.some(x => x > 5)
arr.every(x => x > 0)
arr.find(x => x.id === target)
arr.findIndex(x => x.id === target)
arr.includes(item)
arr.flat()
arr.flatMap(fn)
arr.fill(0)
arr.copyWithin(0, 3)
arr.entries()
arr.keys()
arr.values()
Array.isArray(arr)

// Object methods
obj.hasOwnProperty("key")
obj.isPrototypeOf(other)
obj.propertyIsEnumerable("key")
obj.toString()
obj.valueOf()
Object.assign(target, source)
Object.defineProperty(obj, "prop", desc)
Object.defineProperties(obj, props)
Object.freeze(obj)
Object.seal(obj)
Object.getOwnPropertyNames(obj)
Object.getOwnPropertyDescriptor(obj, "prop")
Object.getPrototypeOf(obj)
Object.fromEntries(entries)

// String methods
str.charAt(0)
str.charCodeAt(0)
str.codePointAt(0)
str.substring(0, 5)
str.substr(0, 5)
str.toLowerCase()
str.toUpperCase()
str.trim()
str.trimStart()
str.trimEnd()
str.split(",")
str.match(/pattern/)
str.replace("old", "new")
str.replaceAll("old", "new")
str.search(/pattern/)
str.startsWith("prefix")
str.endsWith("suffix")
str.padStart(10, "0")
str.padEnd(10, " ")
str.repeat(3)
str.normalize()
str.localeCompare(other)

// Math methods and constants
Math.abs(-5)
Math.acos(0.5)
Math.asin(0.5)
Math.atan(1)
Math.atan2(y, x)
Math.ceil(4.2)
Math.cos(angle)
Math.exp(1)
Math.floor(4.8)
Math.log(10)
Math.max(1, 2, 3)
Math.min(1, 2, 3)
Math.pow(2, 8)
Math.random()
Math.round(4.5)
Math.sin(angle)
Math.sqrt(16)
Math.tan(angle)
Math.trunc(4.9)
Math.sign(-5)
Math.cbrt(27)
Math.hypot(3, 4)
Math.log2(8)
Math.log10(100)
Math.PI
Math.E
Math.LN2
Math.LN10
Math.SQRT2

// scripts.lib functions
xmur3("seed")
jsf(seed)
lcg(seed)
mulberry32(seed)
sfc32(a, b, c, d)
xoshiro128ss(a, b, c, d)

/* ═══════════════════════════════════════════════════════════════════════════
   SECTION 10: UNSUPPORTED FEATURES (RED with underline)
   These cause PARSE ERROR or runtime errors in hackmud
   ═══════════════════════════════════════════════════════════════════════════ */

// ❌ UNSUPPORTED KEYWORDS - Parse errors
async function bad() { }          // async not supported
await promise                     // await not supported
yield value                       // generators not supported
import { thing } from "module"    // ES modules not supported
export default thing              // ES modules not supported

// ❌ UNSUPPORTED OBJECTS - Runtime errors
Promise.resolve(value)            // Promises blocked
Proxy                             // Proxy blocked
Reflect                           // Reflect blocked
globalThis                        // globalThis blocked
Generator                         // Generators blocked
AsyncFunction                     // Async blocked

// ❌ UNSUPPORTED OPERATORS - Parse errors
obj?.property                     // Optional chaining (?.)
value ?? fallback                 // Nullish coalescing (??)
base ** exponent                  // Exponentiation (**)

// ❌ UNSUPPORTED METHODS - ES2022+ not available
arr.at(-1)                        // at() not supported
arr.findLast(fn)                  // findLast not supported
arr.findLastIndex(fn)             // findLastIndex not supported
arr.toSorted()                    // toSorted not supported
arr.toReversed()                  // toReversed not supported
arr.toSpliced(0, 1)               // toSpliced not supported
arr.with(0, newValue)             // with not supported
Object.hasOwn(obj, "key")         // hasOwn not supported

/* ═══════════════════════════════════════════════════════════════════════════
   SECTION 11: STRINGS
   Brown/rust highlighting (#CE9178)
   ═══════════════════════════════════════════════════════════════════════════ */

let single = 'single quoted string'
let double = "double quoted string"
let template = `template string with ${interpolation}`
let escaped = "with \"escapes\" and \n newlines"
let multiline = `
    This is a
    multiline template
    string
`

/* ═══════════════════════════════════════════════════════════════════════════
   SECTION 12: NUMBERS
   Light green highlighting (#B5CEA8)
   ═══════════════════════════════════════════════════════════════════════════ */

// Decimal
42
3.14159
1e10
2.5e-3
.5

// Hexadecimal
0xFF
0xDEADBEEF
0x1a2b3c

// Octal
0o755
0o644

// Binary
0b1010
0b11110000

// BigInt
9007199254740991n
0xFFFFFFFFFFFFFFFFn
0b1010n

/* ═══════════════════════════════════════════════════════════════════════════
   SECTION 13: REGULAR EXPRESSIONS
   Dark red highlighting (#D16969)
   ═══════════════════════════════════════════════════════════════════════════ */

let pattern = /[a-z]+/gi
let complex = /^\w{3,}\d+$/m
let unicode = /\p{L}+/u

/* ═══════════════════════════════════════════════════════════════════════════
   SECTION 14: BRACKETS, PUNCTUATION, OPERATORS
   - Brackets {}[]() → Orchid (#DA70D6)
   - Punctuation .,;: → Dim gray (#808080)
   - Operators +-*/% → Light gray (#B4B4B4)
   - Arrow => → Blue (#569CD6)
   ═══════════════════════════════════════════════════════════════════════════ */

// Brackets (orchid)
let obj = { nested: { deep: [1, 2, 3] } }
function call(param) { return (a + b) }

// Punctuation (dim gray)
let a, b, c;
obj.property.sub;
array[index];

// Operators (light gray)
let sum = a + b - c * d / e % f
let logic = a && b || !c
let compare = a < b && c > d && e <= f && g >= h
let bits = a & b | c ^ d ~ e
let assign = a += b -= c *= d /= e

// Arrow function (blue arrow)
const arrow = (x) => x * 2
const multi = (a, b) => {
    return a + b
}
arr.map(x => x.value)
arr.filter(item => item.active)

/* ═══════════════════════════════════════════════════════════════════════════
   SECTION 15: COMMENTS
   Green italic highlighting (#6A9955)
   ═══════════════════════════════════════════════════════════════════════════ */

// Single line comment

/* Multi-line
   comment block */

/**
 * JSDoc style comment
 * @param {string} arg - Description
 * @returns {number} Result
 */

/* ═══════════════════════════════════════════════════════════════════════════
   SECTION 16: COMPLETE HACKMUD SCRIPT EXAMPLE
   Showing everything together in realistic context
   ═══════════════════════════════════════════════════════════════════════════ */

function(context, args) {
    // Validate caller
    if (!context.caller) {
        return { ok: false, msg: "No caller" }
    }
    
    // Get target from args
    let target = args.target
    let amount = args.amount || 1000
    
    // Check our balance first
    let balance = #fs.accts.balance()
    if (balance.current < amount) {
        return { ok: false, msg: `Insufficient funds: ${balance.current}GC` }
    }
    
    // Database lookup
    let record = #db.f({ user: context.caller }).first()
    if (!record) {
        #db.i({ user: context.caller, transfers: 0, total: 0 })
        record = { transfers: 0, total: 0 }
    }
    
    // Perform transfer
    let result = #fs.accts.xfer_gc_to({ to: target, amount: amount })
    
    // Update database
    #db.u1(
        { user: context.caller },
        { $inc: { transfers: 1, total: amount } }
    )
    
    // Send notification
    #fs.chats.tell({ to: target, msg: `Sent ${amount}GC from ${context.caller}` })
    
    // Return result with color formatting
    return {
        ok: true,
        msg: `#2SUCCESS:#0 Transferred #5${amount}GC#0 to #3${target}#0`
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// END OF SHOWCASE
// If you can see all the colors described above, the syntax highlighting
// is working correctly! 🪆⬢
// ═══════════════════════════════════════════════════════════════════════════
