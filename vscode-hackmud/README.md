# Hackmud JavaScript Extension for VS Code

Syntax highlighting, snippets, autocomplete, and diagnostics for [Hackmud](https://hackmud.com/) scripts.

![Hackmud Syntax](https://zenchess.github.io/claudeb0tScripts/javascript_hackmud_features/javascript_features.html)

## Features

### ✅ Syntax Highlighting
- Full ES6 JavaScript syntax support
- **Hackmud scriptor syntax** (`#fs.user.script`, `#db.f`, etc.) highlighted in purple
- **Hackmud globals** (`context`, `args`, `_START`, `_END`, `_G`, etc.) highlighted in blue
- **Unsupported features marked in red** with underline:
  - `async`/`await` (parse error)
  - `?.` optional chaining (parse error)
  - `??` nullish coalescing (parse error)
  - `**` exponentiation (parse error)
  - `Promise`, `Proxy`, `Reflect` (runtime blocked)

### ✅ IntelliSense & Autocomplete
- All hackmud globals with documentation
- Scriptor syntax completions (`#fs.`, `#db.`, etc.)
- 500+ JavaScript keywords and methods

### ✅ Code Snippets
Type these prefixes and press Tab:

| Prefix | Description |
|--------|-------------|
| `script` | Basic hackmud script template |
| `scriptargs` | Script with argument handling |
| `#fs`, `#hs`, `#ms`, `#ls`, `#ns` | Scriptor calls |
| `#db.f`, `dbfind` | Database find |
| `#db.i`, `dbinsert` | Database insert |
| `#db.u`, `dbupdate` | Database update |
| `#D` | Debug macro |
| `trycatch` | Try-catch with hackmud error return |
| `timeout` | Timeout check pattern |
| `mini` | Mini script template |
| `color` | Hackmud color code string |

### ✅ Error Diagnostics
Real-time warnings when you use unsupported hackmud features:
- Red squiggly underlines on problem code
- Hover for explanation
- Problems panel integration

### ✅ Hover Documentation
Hover over hackmud globals and scriptor syntax for instant documentation.

## Installation

### From VSIX (Local Install)
```bash
# In the extension directory
npx vsce package
code --install-extension hackmud-language-1.0.0.vsix
```

### Manual (Development)
1. Copy the `vscode-hackmud` folder to your VS Code extensions directory:
   - **Windows:** `%USERPROFILE%\.vscode\extensions\hackmud-language`
   - **macOS/Linux:** `~/.vscode/extensions/hackmud-language`
2. Restart VS Code
3. Open a `.js` file and set language to "Hackmud JavaScript"

### File Association
The extension activates for files matching:
- `*.hm.js`
- `*.hackmud.js`

Or manually set the language mode to "Hackmud JavaScript" for any file.

## Hackmud JavaScript Support

Based on comprehensive testing, hackmud uses:
- **Parser:** ES6 (arrow functions, template literals, destructuring, etc.)
- **Runtime:** ~ES2019 (most modern methods work)

### ✅ Supported (Green Light)
- `let`, `const`, arrow functions, classes
- Template literals with interpolation
- Destructuring, spread operator
- `Map`, `Set`, `WeakMap`, `WeakSet`
- `BigInt`, `Symbol`
- Most Array/Object/String methods through ES2019
- `WebAssembly` (Module, Instance, Memory)

### ❌ Unsupported (Red = Parse Error)
- `async`/`await`
- `?.` (optional chaining)
- `??` (nullish coalescing)  
- `**` (exponentiation)
- `import`/`export`

### ⚠️ Blocked (Runtime Error)
- `Promise` (blocked)
- `Proxy`, `Reflect` (blocked)
- `globalThis`

## Theme

Includes "Hackmud Dark" theme matching VS Code's Dark+ colors with hackmud-specific highlighting.

## Contributing

Found a bug or want to add a feature? PRs welcome!

GitHub: https://github.com/Zenchess/claudeb0tScripts

## Credits

Created by claudeb0t 🦞

Based on comprehensive JavaScript runtime testing in hackmud.
