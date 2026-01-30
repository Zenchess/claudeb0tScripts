# JavaScript (Hackmud) - Kate Editor Syntax Highlighting & Autocomplete

Custom syntax highlighting and word completion for writing hackmud scripts in [Kate Editor](https://kate-editor.org/).

## Features

### Syntax Highlighting (VS Code Dark+ Theme)

- **Keywords** - Blue (`#569CD6`) - `let`, `const`, `function`, `class`, etc.
- **Built-in Objects** - Teal (`#4EC9B0`) - `Array`, `Object`, `Map`, `Set`, etc.
- **Methods** - Yellow (`#DCDCAA`) - `map`, `filter`, `reduce`, `forEach`, etc.
- **Strings** - Orange (`#CE9178`) - Regular and template literals
- **Numbers** - Green (`#B5CEA8`) - Including BigInt
- **Comments** - Green italic (`#6A9955`)
- **Hackmud Scriptor** - Magenta bold (`#C586C0`) - `#fs.user.script`, `#db.f`, etc.
- **Hackmud Globals** - Light blue (`#9CDCFE`) - `context`, `args`, `_G`, `_DB`
- **⚠️ Unsupported Features** - Red underline (`#F44747`) - `async`, `await`, `?.`, `??`, `**`

### Autocomplete Keywords

500+ keywords including:
- All supported ES6 keywords
- Hackmud-specific globals and scriptor syntax
- Array, Object, String, Math, Date methods
- WebAssembly API
- Map/Set methods

## Installation

### Syntax Highlighting

1. Copy `javascript_hackmud.xml` to Kate's syntax definitions folder:

```bash
# Linux
mkdir -p ~/.local/share/org.kde.syntax-highlighting/syntax/
cp javascript_hackmud.xml ~/.local/share/org.kde.syntax-highlighting/syntax/

# macOS (if using KDE/Kate)
mkdir -p ~/Library/Application\ Support/org.kde.syntax-highlighting/syntax/
cp javascript_hackmud.xml ~/Library/Application\ Support/org.kde.syntax-highlighting/syntax/
```

2. Restart Kate
3. Open a `.js` file and select **JavaScript (Hackmud)** from the syntax dropdown (bottom-right)

### Word Completion / Autocomplete

1. Enable the Word Completion plugin in Kate:
   - **Settings** → **Configure Kate** → **Plugins** → Enable **Word Completion**

2. Copy the keywords file:

```bash
mkdir -p ~/.local/share/ktexteditor_wordcompletion/
cp hackmud-keywords.txt ~/.local/share/ktexteditor_wordcompletion/
```

3. Restart Kate

## File Structure

```
javascript_hackmud_features/
├── javascript_hackmud.xml    # Syntax highlighting definition
├── hackmud-keywords.txt      # Autocomplete keywords
├── javascript_features.html  # Comprehensive JS feature reference
└── README.md                 # This file
```

## Hackmud JavaScript Support Summary

| Feature | Status |
|---------|--------|
| ES1-ES3 | ✅ Full |
| ES5 | ✅ Full |
| ES6 (let, const, arrow, class, etc.) | ✅ Full |
| ES2016-2019 (includes, flat, etc.) | ⚠️ Partial |
| ES2020+ syntax (`?.`, `??`, `**`) | ❌ Parse Error |
| async/await | ❌ Parse Error |
| Promise | ❌ Not Available |
| WebAssembly | ✅ Works |

## Unsupported Features (Highlighted in Red)

The syntax highlighter will mark these as errors (red underline):

- `async` / `await` - Parse error
- `?.` - Optional chaining - Parse error
- `??` - Nullish coalescing - Parse error  
- `**` - Exponentiation - Parse error (use `Math.pow()`)
- `Promise` - Runtime error
- `globalThis` - Undefined

## Workarounds

```javascript
// Instead of: obj?.prop?.value
// Use:
obj && obj.prop && obj.prop.value

// Instead of: value ?? defaultValue
// Use:
(value !== null && value !== undefined) ? value : defaultValue

// Instead of: {...obj, newProp: value}
// Use:
Object.assign({}, obj, { newProp: value })

// Instead of: 2 ** 3
// Use:
Math.pow(2, 3)
```

## License

MIT

## Author

claudeb0t (2026-01-30)

Based on comprehensive testing of hackmud's JavaScript runtime.
