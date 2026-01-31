# Hackmud Language Support for VS Code

Syntax highlighting, snippets, and formatting for [Hackmud](https://hackmud.com) scripts.

## Features

### 🎨 Syntax Highlighting
- Full JavaScript/ES2019 syntax support
- **Hackmud-specific highlighting:**
  - Scriptor syntax (`#s.user.script`, `#fs`, `#ns`, etc.)
  - Database operations (`$db.f`, `$db.i`, etc.)
  - FMCL color codes (`` `N ``, `` `0 ``, etc.)
  - Context globals (`context`, `args`, `_ST`, `_ET`, `_TO`)
- **Unsupported features marked in red:**
  - `async`/`await`
  - Optional chaining (`?.`)
  - Nullish coalescing (`??`)
  - Exponentiation operator (`**`)
  - BigInt literals (`123n`)

### 📝 Snippets
- `hm-script` - Basic script template
- `hm-scriptor` - Scriptor call
- `hm-fs`/`hm-hs`/`hm-ms`/`hm-ls`/`hm-ns` - Security-level scriptor calls
- `hm-db-find`/`hm-db-insert`/`hm-db-update` - Database operations
- `hm-color` - FMCL color codes
- And more!

### 🔧 Formatting (Prettier Integration)
- Automatic formatting with Prettier
- Hackmud-optimized defaults
- Respects workspace `.prettierrc` if present

## File Detection

The extension automatically detects hackmud files by:

1. **Magic comment** at the top of the file:
   ```javascript
   // @hackmud
   function(context, args) {
     // ...
   }
   ```

2. **Anonymous function pattern** (hackmud's signature style):
   ```javascript
   function(context, args) {
     // Detected automatically!
   }
   ```

3. **Configured scripts path** - Set `hackmud.scriptsPath` to your scripts folder

## Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `hackmud.autoDetect` | `true` | Auto-detect hackmud files by content |
| `hackmud.scriptsPath` | `""` | Path to hackmud scripts folder |

## Installation

### From Source

1. Clone or download this extension
2. `npm install`
3. `npm run compile`
4. Copy to `~/.vscode/extensions/hackmud-language-support/`

### Development

1. Open this folder in VS Code
2. Press F5 to launch Extension Development Host
3. Edit `.js` files with hackmud scripts to test

## Usage with Prettier

For autoformatting:

1. Install prettier in your workspace: `npm install -D prettier`
2. Format with `Shift+Alt+F` or the command palette: "Format Document"

Optional: Create a `.prettierrc` in your scripts folder:
```json
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "none",
  "printWidth": 100
}
```

## Commands

- **Detect Hackmud Script** - Manually detect and set language mode
- **Format Hackmud Script** - Format with Prettier

## License

MIT
