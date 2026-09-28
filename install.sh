#!/usr/bin/env bash
# booKeeper — one-line installer (macOS / Linux / Windows WSL)
# Usage: curl -fsSL https://raw.githubusercontent.com/yourrepo/booKeeper/main/install.sh | bash
#   or:  bash install.sh

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

echo "==============================================="
echo "  booKeeper — Installation"
echo "==============================================="

# --- 1. Check dependencies ---
echo ""
echo "[1/5] Checking dependencies..."

if ! command -v python3 &>/dev/null; then
  echo "ERROR: python3 is required but not installed."
  echo "Install it from https://www.python.org/downloads/"
  exit 1
fi

if ! command -v pip3 &>/dev/null; then
  echo "ERROR: pip3 is required but not installed."
  exit 1
fi

if ! command -v node &>/dev/null; then
  echo "ERROR: node is required but not installed."
  echo "Install it from https://nodejs.org/"
  exit 1
fi

if ! command -v npm &>/dev/null; then
  echo "ERROR: npm is required but not installed."
  exit 1
fi

# Check MongoDB
if ! command -v mongod &>/dev/null && ! command -v mongo &>/dev/null; then
  echo "  WARNING: MongoDB not found in PATH."
  echo "  You'll need MongoDB running locally or a MongoDB Atlas URI."
  echo "  Local install: https://www.mongodb.com/try/download/community"
  echo "  Atlas (cloud): https://www.mongodb.com/atlas"
else
  echo "  ✓ mongodb: $(command -v mongod || command -v mongo)"
fi

echo "  ✓ python3: $(python3 --version)"
echo "  ✓ node:    $(node --version)"
echo "  ✓ npm:     $(npm --version)"

# --- 2. Install Python dependencies ---
echo ""
echo "[2/5] Installing Python dependencies..."
pip3 install -r backend/requirements.txt

# --- 3. Install & build frontend ---
echo ""
echo "[3/5] Installing frontend dependencies..."
cd frontend
npm install

echo ""
echo "[4/5] Building frontend..."
npm run build
cd ..

# --- 5. Done ---
echo ""
echo "==============================================="
echo "  Installation complete!"
echo "==============================================="
echo ""
echo "  IMPORTANT: Start MongoDB before running the app!"
echo "  macOS:  brew services start mongodb-community"
echo "  Linux:  sudo systemctl start mongod"
echo "  Or set MONGODB_URI in backend/.env to a MongoDB Atlas URI"
echo ""
echo "  Start the app:"
echo "    cd backend && python3 run.py"
echo ""
echo "  Then open: http://localhost:5000"
echo ""
echo "  For development (hot-reload):"
echo "    Terminal 1: cd backend && python3 run.py"
echo "    Terminal 2: cd frontend && npm run dev"
echo "    Open: http://localhost:5173"
echo ""
