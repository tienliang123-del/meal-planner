# 每日菜單推薦 — 啟動腳本
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "🍳 每日菜單推薦平台" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# ── 確認 Python ──
$pyExe = $null
foreach ($candidate in @("python", "python3", "py")) {
    try {
        $ver = & $candidate --version 2>&1
        if ($ver -match "Python 3\.") { $pyExe = $candidate; break }
    } catch {}
}

if (-not $pyExe) {
    Write-Host ""
    Write-Host "⚠️  找不到 Python，嘗試用 winget 自動安裝..." -ForegroundColor Yellow
    winget install --id Python.Python.3.12 --source winget --accept-source-agreements --accept-package-agreements
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path", "User")
    $pyExe = "python"
}

Write-Host "✅ 使用 $($pyExe): $(& $pyExe --version)" -ForegroundColor Green

# ── 建立虛擬環境 ──
if (-not (Test-Path ".venv")) {
    Write-Host "📦 建立虛擬環境..." -ForegroundColor Yellow
    & $pyExe -m venv .venv
}

$pip = ".venv\Scripts\pip.exe"
$uvi = ".venv\Scripts\uvicorn.exe"

# ── 安裝套件 ──
Write-Host "📦 安裝相依套件..." -ForegroundColor Yellow
& $pip install -r requirements.txt -q

Write-Host ""
Write-Host "🚀 伺服器啟動中..." -ForegroundColor Cyan
Write-Host "   開啟瀏覽器前往 → http://localhost:8000" -ForegroundColor Green
Write-Host "   按 Ctrl+C 停止" -ForegroundColor Gray
Write-Host ""

& $uvi main:app --reload --host 0.0.0.0 --port 8000
