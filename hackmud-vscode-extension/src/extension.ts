import * as vscode from 'vscode';
import * as path from 'path';

// Patterns to detect hackmud files
const HACKMUD_COMMENT_PATTERN = /^\s*\/\/\s*@hackmud/m;
const HACKMUD_FUNCTION_PATTERN = /^\s*function\s*\(\s*(context|c)\s*,\s*(args|a)\s*\)\s*\{/m;

export function activate(context: vscode.ExtensionContext) {
    console.log('Hackmud Language Support activated');

    // Auto-detect hackmud files on open
    const detectDisposable = vscode.workspace.onDidOpenTextDocument((document) => {
        detectAndSetLanguage(document);
    });

    // Also check already open documents
    vscode.workspace.textDocuments.forEach(detectAndSetLanguage);

    // Register the manual detect command
    const detectCommand = vscode.commands.registerCommand('hackmud.detectAndSetLanguage', () => {
        const editor = vscode.window.activeTextEditor;
        if (editor) {
            detectAndSetLanguage(editor.document, true);
        }
    });

    // Register format command with prettier
    const formatCommand = vscode.commands.registerCommand('hackmud.formatDocument', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor');
            return;
        }
        await formatHackmudDocument(editor);
    });

    // Register document formatter
    const formatterProvider = vscode.languages.registerDocumentFormattingEditProvider('hackmud', {
        async provideDocumentFormattingEdits(document: vscode.TextDocument): Promise<vscode.TextEdit[]> {
            return formatDocument(document);
        }
    });

    context.subscriptions.push(
        detectDisposable,
        detectCommand,
        formatCommand,
        formatterProvider
    );
}

function detectAndSetLanguage(document: vscode.TextDocument, showMessage = false): void {
    // Only check .js files
    if (document.languageId !== 'javascript' && document.languageId !== 'hackmud') {
        return;
    }

    // Check if it's in a hackmud scripts folder
    const config = vscode.workspace.getConfiguration('hackmud');
    const scriptsPath = config.get<string>('scriptsPath');
    const autoDetect = config.get<boolean>('autoDetect', true);

    if (!autoDetect && document.languageId !== 'hackmud') {
        return;
    }

    const text = document.getText();
    const isHackmudFile = 
        HACKMUD_COMMENT_PATTERN.test(text) || 
        HACKMUD_FUNCTION_PATTERN.test(text) ||
        (scriptsPath && document.uri.fsPath.includes(scriptsPath));

    if (isHackmudFile && document.languageId !== 'hackmud') {
        vscode.languages.setTextDocumentLanguage(document, 'hackmud');
        if (showMessage) {
            vscode.window.showInformationMessage('Detected as Hackmud script');
        }
    } else if (!isHackmudFile && showMessage) {
        vscode.window.showInformationMessage('Not detected as Hackmud script');
    }
}

async function formatHackmudDocument(editor: vscode.TextEditor): Promise<void> {
    const document = editor.document;
    const edits = await formatDocument(document);
    
    if (edits.length > 0) {
        const edit = new vscode.WorkspaceEdit();
        edit.set(document.uri, edits);
        await vscode.workspace.applyEdit(edit);
        vscode.window.showInformationMessage('Formatted Hackmud script');
    }
}

async function formatDocument(document: vscode.TextDocument): Promise<vscode.TextEdit[]> {
    try {
        // Try to use prettier if available
        let prettier;
        try {
            prettier = require('prettier');
        } catch {
            // Prettier not available, try workspace node_modules
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (workspaceFolders) {
                for (const folder of workspaceFolders) {
                    try {
                        const prettierPath = path.join(folder.uri.fsPath, 'node_modules', 'prettier');
                        prettier = require(prettierPath);
                        break;
                    } catch {
                        continue;
                    }
                }
            }
        }

        if (!prettier) {
            vscode.window.showWarningMessage('Prettier not found. Install prettier for formatting.');
            return [];
        }

        const text = document.getText();
        
        // Hackmud-specific prettier config
        const options = {
            parser: 'babel',
            semi: false,          // Hackmud style often omits semis for golfing
            singleQuote: true,
            tabWidth: 2,
            useTabs: false,
            trailingComma: 'none' as const,
            printWidth: 100,
            // Preserve the top-level function structure
            arrowParens: 'always' as const,
        };

        // Try to find and use a prettier config in the workspace
        try {
            const configPath = await prettier.resolveConfigFile(document.uri.fsPath);
            if (configPath) {
                const userConfig = await prettier.resolveConfig(document.uri.fsPath);
                Object.assign(options, userConfig);
            }
        } catch {
            // Use defaults
        }

        // Format the code
        const formatted = await prettier.format(text, options);
        
        // Replace entire document
        const fullRange = new vscode.Range(
            document.positionAt(0),
            document.positionAt(text.length)
        );
        
        return [vscode.TextEdit.replace(fullRange, formatted)];

    } catch (error: any) {
        vscode.window.showErrorMessage(`Format error: ${error.message}`);
        return [];
    }
}

export function deactivate() {}
