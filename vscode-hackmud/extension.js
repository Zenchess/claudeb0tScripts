// Hackmud Language Extension for VS Code
// Provides hover docs, diagnostics for unsupported features, and completions

const vscode = require('vscode');

// Hackmud globals with documentation
const HACKMUD_GLOBALS = {
  'context': 'Object containing script execution context: caller, this_script, calling_script, cols, rows',
  'args': 'Arguments passed to the script (may be null/undefined)',
  'caller': 'context.caller - Username of who called this script',
  'this_script': 'context.this_script - Full name of this script (user.script)',
  'calling_script': 'context.calling_script - Full name of the calling script (or null)',
  '_START': 'Timestamp (ms) when script execution started',
  '_END': 'Timestamp (ms) when script will timeout (5000ms from _START)',
  '_TIMEOUT': 'Same as _END - script timeout timestamp',
  '_G': 'Global storage object (persists across script calls)',
  '_ST': 'Script token for this execution',
  '_DB': 'Database access object'
};

// Scriptor syntax docs
const SCRIPTOR_DOCS = {
  '#fs': 'Full-sec scriptor call - #fs.user.script({ args })',
  '#hs': 'High-sec scriptor call - #hs.user.script({ args })',
  '#ms': 'Mid-sec scriptor call - #ms.user.script({ args })',
  '#ls': 'Low-sec scriptor call - #ls.user.script({ args })',
  '#ns': 'Null-sec scriptor call - #ns.user.script({ args })',
  '#s': 'Generic scriptor call - #s.user.script({ args })',
  '#db.f': 'Database find - #db.f({ query }) returns cursor',
  '#db.i': 'Database insert - #db.i({ document })',
  '#db.r': 'Database remove - #db.r({ query })',
  '#db.u': 'Database update - #db.u({ query }, { $set: {...} })',
  '#db.u1': 'Database update one - #db.u1({ query }, { $set: {...} })',
  '#db.us': 'Database upsert - #db.us({ query }, { $set: {...} })',
  '#D': 'Debug macro - logs value and returns it',
  '#G': 'Global storage access - #G.key',
  '#FMCL': 'Full-sec/Mid-sec/Call/Low-sec conditional call',
  '#4S': 'Four-tier security call'
};

// Unsupported features to warn about
const UNSUPPORTED_PATTERNS = [
  { pattern: /\?\./g, message: 'Optional chaining (?.) is not supported in hackmud' },
  { pattern: /\?\?/g, message: 'Nullish coalescing (??) is not supported in hackmud' },
  { pattern: /\*\*/g, message: 'Exponentiation operator (**) is not supported - use Math.pow()' },
  { pattern: /\basync\b/g, message: 'async/await is not supported in hackmud' },
  { pattern: /\bawait\b/g, message: 'async/await is not supported in hackmud' },
  { pattern: /\bPromise\b/g, message: 'Promise is blocked in hackmud' },
  { pattern: /\bProxy\b/g, message: 'Proxy is blocked in hackmud' },
  { pattern: /\bReflect\b/g, message: 'Reflect is blocked in hackmud' }
];

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
  console.log('Hackmud Language extension activated');

  // Hover provider for hackmud-specific items
  const hoverProvider = vscode.languages.registerHoverProvider(
    ['hackmud', 'javascript'],
    {
      provideHover(document, position, token) {
        const range = document.getWordRangeAtPosition(position, /#?[a-zA-Z_$][a-zA-Z0-9_$.]*/);
        if (!range) return;

        const word = document.getText(range);

        // Check hackmud globals
        if (HACKMUD_GLOBALS[word]) {
          return new vscode.Hover(
            new vscode.MarkdownString(`**Hackmud Global**\n\n${HACKMUD_GLOBALS[word]}`)
          );
        }

        // Check scriptor syntax
        for (const [prefix, doc] of Object.entries(SCRIPTOR_DOCS)) {
          if (word.startsWith(prefix)) {
            return new vscode.Hover(
              new vscode.MarkdownString(`**Hackmud Scriptor**\n\n${doc}`)
            );
          }
        }

        return null;
      }
    }
  );

  // Diagnostics for unsupported features
  const diagnosticCollection = vscode.languages.createDiagnosticCollection('hackmud');

  function updateDiagnostics(document) {
    if (!['hackmud', 'javascript'].includes(document.languageId)) {
      return;
    }

    const diagnostics = [];
    const text = document.getText();

    for (const { pattern, message } of UNSUPPORTED_PATTERNS) {
      let match;
      const regex = new RegExp(pattern.source, pattern.flags);
      while ((match = regex.exec(text)) !== null) {
        const startPos = document.positionAt(match.index);
        const endPos = document.positionAt(match.index + match[0].length);
        const range = new vscode.Range(startPos, endPos);

        diagnostics.push(new vscode.Diagnostic(
          range,
          message,
          vscode.DiagnosticSeverity.Error
        ));
      }
    }

    diagnosticCollection.set(document.uri, diagnostics);
  }

  // Update diagnostics on document open and change
  context.subscriptions.push(
    vscode.workspace.onDidOpenTextDocument(updateDiagnostics),
    vscode.workspace.onDidChangeTextDocument(e => updateDiagnostics(e.document)),
    vscode.workspace.onDidCloseTextDocument(doc => diagnosticCollection.delete(doc.uri))
  );

  // Update for all open documents
  vscode.workspace.textDocuments.forEach(updateDiagnostics);

  // Completion provider for hackmud-specific items
  const completionProvider = vscode.languages.registerCompletionItemProvider(
    ['hackmud', 'javascript'],
    {
      provideCompletionItems(document, position, token, context) {
        const completions = [];

        // Hackmud globals
        for (const [name, doc] of Object.entries(HACKMUD_GLOBALS)) {
          const item = new vscode.CompletionItem(name, vscode.CompletionItemKind.Variable);
          item.documentation = new vscode.MarkdownString(doc);
          item.detail = 'Hackmud Global';
          completions.push(item);
        }

        // Scriptor prefixes
        const scriptorItems = [
          { label: '#fs.', detail: 'Full-sec scriptor', insertText: '#fs.' },
          { label: '#hs.', detail: 'High-sec scriptor', insertText: '#hs.' },
          { label: '#ms.', detail: 'Mid-sec scriptor', insertText: '#ms.' },
          { label: '#ls.', detail: 'Low-sec scriptor', insertText: '#ls.' },
          { label: '#ns.', detail: 'Null-sec scriptor', insertText: '#ns.' },
          { label: '#db.f', detail: 'Database find', insertText: '#db.f({ $1 })' },
          { label: '#db.i', detail: 'Database insert', insertText: '#db.i({ $1 })' },
          { label: '#db.r', detail: 'Database remove', insertText: '#db.r({ $1 })' },
          { label: '#db.u', detail: 'Database update', insertText: '#db.u({ $1 }, { \\$set: { $2 } })' },
          { label: '#D', detail: 'Debug macro', insertText: '#D($1)' },
          { label: '#G', detail: 'Global storage', insertText: '#G.' }
        ];

        for (const s of scriptorItems) {
          const item = new vscode.CompletionItem(s.label, vscode.CompletionItemKind.Function);
          item.detail = s.detail;
          item.insertText = new vscode.SnippetString(s.insertText);
          completions.push(item);
        }

        return completions;
      }
    },
    '.', '#'
  );

  context.subscriptions.push(
    hoverProvider,
    completionProvider,
    diagnosticCollection
  );
}

function deactivate() {}

module.exports = {
  activate,
  deactivate
};
