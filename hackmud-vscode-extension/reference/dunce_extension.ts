import * as vscode from 'vscode';
import prettier from 'prettier';

const ASCII_CALL_PATTERN = /#[0-4nlmhf]s\.[a-z_][a-z0-9_]+\.[a-z_][a-z0-9_]+\(/gi;
const UNICODE_CALL_PATTERN = /ꖛ[0-4nlmhf]sꔷ[a-z_][a-z0-9_]+ꔷ[a-z_][a-z0-9_]+\(/gi;
const HACKMUD_DUMMY_NAME = '__hackmud_entry__';
const HACKMUD_PRETTIER_DEFAULTS: prettier.Options = {
  arrowParens: 'avoid',
  bracketSpacing: false,
  trailingComma: 'es5',
  semi: true,
  experimentalOperatorPosition: 'start',
  experimentalTernaries: false,
  tabWidth: 2
};

export function activate(context: vscode.ExtensionContext): void {
  const outputChannel = vscode.window.createOutputChannel('Hackmud JS Formatter');
  const diagnostics = vscode.languages.createDiagnosticCollection('hackmud-js');
  const formatter = vscode.languages.registerDocumentFormattingEditProvider('hackmud-js', {
    provideDocumentFormattingEdits(document, options, token) {
      return formatHackmudDocument(document, options, token, outputChannel, diagnostics);
    }
  });

  context.subscriptions.push(formatter, outputChannel, diagnostics);
}

async function formatHackmudDocument(
  document: vscode.TextDocument,
  options: vscode.FormattingOptions,
  token: vscode.CancellationToken,
  outputChannel: vscode.OutputChannel,
  diagnostics: vscode.DiagnosticCollection
): Promise<vscode.TextEdit[]> {
  log(outputChannel, '--- format start ---');
  log(outputChannel, `uri=${document.uri.toString(true)} lang=${document.languageId}`);
  diagnostics.delete(document.uri);
  const originalText = document.getText();
  if (!originalText) {
    log(outputChannel, 'document empty; skipping');
    return [];
  }

  log(
    outputChannel,
    `original length=${originalText.length} asciiMatches=${countMatches(ASCII_CALL_PATTERN, originalText)}`
  );
  const unicodeText = translateAsciiToUnicode(originalText);
  if (token.isCancellationRequested) {
    log(outputChannel, 'cancelled after ascii→unicode translation');
    return [];
  }

  const formattedUnicode = await formatWithPrettier(
    unicodeText,
    document,
    options,
    outputChannel,
    diagnostics
  );
  if (formattedUnicode === null) {
    log(outputChannel, 'prettier failed; diagnostics published');
    return [];
  }
  if (token.isCancellationRequested) {
    log(outputChannel, 'cancelled after prettier run');
    return [];
  }
  log(outputChannel, `formatted length=${formattedUnicode.length}`);

  const finalText = translateUnicodeToAscii(formattedUnicode);
  if (finalText === originalText) {
    log(outputChannel, 'formatter produced identical output; no edits applied');
    return [];
  }

  log(outputChannel, `final length=${finalText.length} changes applied`);
  return [vscode.TextEdit.replace(fullDocumentRange(document), finalText)];
}

async function formatWithPrettier(
  content: string,
  document: vscode.TextDocument,
  options: vscode.FormattingOptions,
  outputChannel: vscode.OutputChannel,
  diagnostics: vscode.DiagnosticCollection
): Promise<string | null> {
  const wrapResult = wrapHackmudEntry(content);
  if (wrapResult.didWrap) {
    log(outputChannel, 'inserted dummy function name to satisfy Prettier');
  }

  const prettierOptions = await buildPrettierOptions(document, options, outputChannel);

  try {
    log(outputChannel, `running prettier parser=${prettierOptions.parser}`);
    const formatted = await prettier.format(wrapResult.content, prettierOptions);
    return wrapResult.unwrap(formatted);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error('Hackmud JS formatter failed to run Prettier.', error);
    log(outputChannel, `prettier failed: ${message}`);
    publishDiagnostic(document, diagnostics, message);
    return null;
  }
}

async function buildPrettierOptions(
  document: vscode.TextDocument,
  options: vscode.FormattingOptions,
  outputChannel: vscode.OutputChannel
): Promise<prettier.Options & { filepath?: string }> {
  const base: prettier.Options & { filepath?: string } = {
    parser: 'babel',
    tabWidth: options.tabSize ?? (HACKMUD_PRETTIER_DEFAULTS.tabWidth ?? 2),
    useTabs: options.insertSpaces === false,
    filepath: inferVirtualFilePath(document)
  };

  let resolved: prettier.Options | null = null;
  if (document.uri.scheme === 'file') {
    try {
      resolved = await prettier.resolveConfig(document.uri.fsPath, { editorconfig: true });
    } catch (error) {
      console.debug('Hackmud JS formatter could not resolve Prettier config.', error);
    }
  }

  const merged: prettier.Options & { filepath?: string } = {
    ...(resolved ?? {}),
    ...base,
    ...HACKMUD_PRETTIER_DEFAULTS
  };

  merged.parser = 'babel';
  if (document.uri.scheme === 'file') {
    merged.filepath = document.uri.fsPath;
  }

  log(
    outputChannel,
    `prettier opts: semi=${merged.semi} tabWidth=${merged.tabWidth} useTabs=${merged.useTabs}`
  );

  return merged;
}

function translateAsciiToUnicode(text: string): string {
  return translateDelimitedCalls(text, ASCII_CALL_PATTERN, '#', 'ꖛ', '.', 'ꔷ');
}

function translateUnicodeToAscii(text: string): string {
  return translateDelimitedCalls(text, UNICODE_CALL_PATTERN, 'ꖛ', '#', 'ꔷ', '.');
}

function translateDelimitedCalls(
  text: string,
  pattern: RegExp,
  fromPrefix: string,
  toPrefix: string,
  fromSeparator: string,
  toSeparator: string
): string {
  pattern.lastIndex = 0;
  return text.replace(pattern, match => swapDelimiters(match, fromPrefix, toPrefix, fromSeparator, toSeparator));
}

function swapDelimiters(
  match: string,
  fromPrefix: string,
  toPrefix: string,
  fromSeparator: string,
  toSeparator: string
): string {
  const withPrefixSwapped = match.replace(fromPrefix, toPrefix);
  return replaceAll(withPrefixSwapped, fromSeparator, toSeparator);
}

function replaceAll(value: string, search: string, replacement: string): string {
  return value.split(search).join(replacement);
}

function countMatches(pattern: RegExp, text: string): number {
  const matcher = new RegExp(pattern.source, pattern.flags);
  let count = 0;
  while (matcher.exec(text)) {
    count += 1;
  }
  return count;
}

function inferVirtualFilePath(document: vscode.TextDocument): string {
  if (document.uri.scheme === 'file') {
    return document.uri.fsPath;
  }

  const segments = document.uri.path.split('/');
  const base = segments[segments.length - 1] || 'hackmud-temp.js';
  return base.endsWith('.js') ? `/virtual/${base}` : `/virtual/${base}.js`;
}

function fullDocumentRange(document: vscode.TextDocument): vscode.Range {
  const lastLine = document.lineAt(document.lineCount - 1);
  return new vscode.Range(new vscode.Position(0, 0), lastLine.range.end);
}

export function deactivate(): void {
  // Nothing to clean up explicitly.
}

function log(channel: vscode.OutputChannel, message: string): void {
  const timestamp = new Date().toISOString();
  channel.appendLine(`[${timestamp}] ${message}`);
}

function publishDiagnostic(
  document: vscode.TextDocument,
  diagnostics: vscode.DiagnosticCollection,
  message: string
): void {
  if (document.lineCount === 0) {
    return;
  }

  const range = fullDocumentRange(document);
  const diagnostic = new vscode.Diagnostic(
    range,
    `Hackmud JS formatter: ${message}`,
    vscode.DiagnosticSeverity.Error
  );
  diagnostic.source = 'Hackmud JS Formatter';
  diagnostics.set(document.uri, [diagnostic]);
}

interface HackmudWrapResult {
  content: string;
  unwrap: (text: string) => string;
  didWrap: boolean;
}

function wrapHackmudEntry(text: string): HackmudWrapResult {
  const matcher = /^(\s*function\s*)(\()/;
  if (!matcher.test(text)) {
    return {
      content: text,
      unwrap: value => value,
      didWrap: false
    };
  }

  const content = text.replace(matcher, `$1${HACKMUD_DUMMY_NAME}$2`);
  return {
    content,
    unwrap: value =>
      value.replace(new RegExp(`(function\\s+)${HACKMUD_DUMMY_NAME}(\\s*\\()`, 'g'), '$1$2'),
    didWrap: true
  };
}
