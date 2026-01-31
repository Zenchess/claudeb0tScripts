# Hackmud Kate Syntax Highlighting Installer
# Run this script to install hackmud syntax files for Kate editor on Windows
# 
# Usage: Right-click -> Run with PowerShell
#    or: powershell -ExecutionPolicy Bypass -File install-kate_hackmud-js.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Hackmud Kate Syntax Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get the directory where this script is located (source files)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $ScriptDir) {
    $ScriptDir = Get-Location
}

Write-Host "Source directory: $ScriptDir" -ForegroundColor Yellow
Write-Host ""

# Define target directories (Kate on Windows)
$LocalAppData = $env:LOCALAPPDATA
$TargetPaths = @{
    "Syntax Highlighting" = Join-Path $LocalAppData "org.kde.syntax-highlighting\syntax"
    "Word Completion"     = Join-Path $LocalAppData "ktexteditor_wordcompletion"
    "Snippets"            = Join-Path $LocalAppData "ktexteditor_snippets\data"
    "Templates"           = Join-Path $LocalAppData "kate\templates"
}

# Files to copy
$FileMappings = @(
    @{
        Source = "kate_hackmud-js.xml"
        Target = "Syntax Highlighting"
        Desc   = "Syntax highlighting (trust-level colors, scriptor parts)"
    },
    @{
        Source = "kate_hackmud-js-keywords.txt"
        Target = "Word Completion"
        Desc   = "Autocomplete keywords (wiki-verified)"
    },
    @{
        Source = "kate_hackmud-js.words"
        Target = "Word Completion"
        Desc   = "Word dictionary"
    },
    @{
        Source = "kate_hackmud-js.xml.snippets"
        Target = "Snippets"
        Desc   = "Code snippets"
    },
    @{
        Source = "kate_hackmud-js.katetemplate"
        Target = "Templates"
        Desc   = "File templates"
    }
)

# Create directories
Write-Host "Creating directories..." -ForegroundColor Cyan
foreach ($name in $TargetPaths.Keys) {
    $path = $TargetPaths[$name]
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
        Write-Host "  [+] Created: $path" -ForegroundColor Green
    } else {
        Write-Host "  [=] Exists:  $path" -ForegroundColor DarkGray
    }
}
Write-Host ""

# Copy files
Write-Host "Copying files..." -ForegroundColor Cyan
$Copied = 0
$Errors = 0

foreach ($file in $FileMappings) {
    $sourcePath = Join-Path $ScriptDir $file.Source
    $targetDir = $TargetPaths[$file.Target]
    $targetPath = Join-Path $targetDir $file.Source
    
    if (Test-Path $sourcePath) {
        try {
            Copy-Item -Path $sourcePath -Destination $targetPath -Force
            Write-Host "  [+] $($file.Source)" -ForegroundColor Green
            Write-Host "      -> $targetPath" -ForegroundColor DarkGray
            Write-Host "      $($file.Desc)" -ForegroundColor DarkCyan
            $Copied++
        } catch {
            Write-Host "  [!] Failed: $($file.Source)" -ForegroundColor Red
            Write-Host "      Error: $_" -ForegroundColor Red
            $Errors++
        }
    } else {
        Write-Host "  [-] Not found: $($file.Source)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($Errors -eq 0) {
    Write-Host "  Installation complete!" -ForegroundColor Green
    Write-Host "  $Copied files copied successfully" -ForegroundColor Green
} else {
    Write-Host "  Installation finished with errors" -ForegroundColor Yellow
    Write-Host "  $Copied copied, $Errors failed" -ForegroundColor Yellow
}
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Restart Kate (if open)" -ForegroundColor Gray
Write-Host "  2. Open a .js file" -ForegroundColor Gray
Write-Host "  3. Set syntax to 'JavaScript (Hackmud)'" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
