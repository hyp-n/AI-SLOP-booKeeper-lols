# booKeeper — one-line installer (Windows PowerShell)
# Usage: powershell -ExecutionPolicy Bypass -File install.ps1
#   or:  iwr -useb https://raw.githubusercontent.com/yourrepo/booKeeper/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RepoDir

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  booKeeper — Installation" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# --- 1. Check dependencies ---
Write-Host ""
Write-Host "[1/5] Checking dependencies..." -ForegroundColor Yellow

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
}
if (-not $python) {
    Write-Host "ERROR: python is required but not installed." -ForegroundColor Red
    Write-Host "Install it from https://www.python.org/downloads/"
    exit 1
}

$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) {
    Write-Host "ERROR: node is required but not installed." -ForegroundColor Red
    Write-Host "Install it from https://nodejs.org/"
    exit 1
}

$npm = Get-Command npm -ErrorAction SilentlyContinue
if (-not $npm) {
    Write-Host "ERROR: npm is required but not installed." -ForegroundColor Red
    exit 1
}

# Check MongoDB
$mongo = Get-Command mongod -ErrorAction SilentlyContinue
if (-not $mongo) {
    $mongo = Get-Command mongo -ErrorAction SilentlyContinue
}
if (-not $mongo) {
    Write-Host "  WARNING: MongoDB not found in PATH." -ForegroundColor Yellow
    Write-Host "  You'll need MongoDB running locally or a MongoDB Atlas URI." -ForegroundColor Yellow
    Write-Host "  Local install: https://www.mongodb.com/try/download/community" -ForegroundColor Yellow
    Write-Host "  Atlas (cloud): https://www.mongodb.com/atlas" -ForegroundColor Yellow
} else {
    Write-Host "  mongodb: $($mongo.Source)"
}

Write-Host "  python: $($python.Source)"
Write-Host "  node:   $($node.Source)"
Write-Host "  npm:    $($npm.Source)"

# --- 2. Install Python dependencies ---
Write-Host ""
Write-Host "[2/5] Installing Python dependencies..." -ForegroundColor Yellow
& $python.Source -m pip install -r backend/requirements.txt

# --- 3. Install & build frontend ---
Write-Host ""
Write-Host "[3/5] Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
& $npm.Source install

Write-Host ""
Write-Host "[4/5] Building frontend..." -ForegroundColor Yellow
& $npm.Source run build
Set-Location ..

# --- 5. Done ---
Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "  Installation complete!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  IMPORTANT: Start MongoDB before running the app!" -ForegroundColor Yellow
Write-Host "  Windows: net start MongoDB"
Write-Host "  Or set MONGODB_URI in backend/.env to a MongoDB Atlas URI"
Write-Host ""
Write-Host "  Start the app:"
Write-Host "    cd backend; python run.py"
Write-Host ""
Write-Host "  Then open: http://localhost:5000"
Write-Host ""
Write-Host "  For development (hot-reload):"
Write-Host "    Terminal 1: cd backend; python run.py"
Write-Host "    Terminal 2: cd frontend; npm run dev"
Write-Host "    Open: http://localhost:5173"
Write-Host ""
