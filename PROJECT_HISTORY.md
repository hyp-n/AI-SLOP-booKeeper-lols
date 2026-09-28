# booKeeper - Project History & Current State

## Overview
A full-stack social reading platform: React + Vite (PWA) frontend, Flask + Socket.IO backend, MongoDB Atlas database. Built for cross-platform use (iOS, Android, Windows, macOS, Linux) via Progressive Web App - no native APK required.

---

## ✅ Completed Features

### Backend (Flask 3.1 + Flask-PyMongo)
- **API Routes** (33 endpoints under `/api/`):
  - Auth: register, login, me, update-me (JWT)
  - Books: CRUD, ISBN lookup (OpenLibrary), search, add-by-ISBN
  - Collections: CRUD, add/remove books, reorder
  - Reading: progress tracking, stats
  - Social: friends, requests, user search, profiles
  - Messages: conversations (1:1 + groups), real-time via Socket.IO
  - Ebooks: search (Anna's Archive, Gutenberg), save sources
- **Socket.IO** for real-time chat
- **Persistent SECRET_KEY** stored at `backend/data/.secret_key`
- **MongoDB Atlas** connection via `MONGO_URI` env var
- **CORS** configured for frontend origin

### Frontend (React 18 + Vite + Tailwind CSS v4 + DaisyUI 5)
- **Pages**: Login/Register, Library, Book Detail, Collections, Profile, Friends, Chat, Stats
- **Components**: Camera ISBN Scanner, Book Cards, Collection Sidebar, Ebook Search, Navbar, Reading Tracker
- **PWA**: Service Worker (`sw.js`), Manifest (`manifest.json`), Offline page
- **Theme**: DaisyUI themes, persisted in localStorage
- **Protected Routes** + Error Boundary
- **API Client** (axios) with auth interceptor

### Camera ISBN Scanner
- Modal on Login page: "Scan ISBN with Camera"
- Uses `navigator.mediaDevices.getUserMedia()` (environment camera)
- Simulates scan → calls `addBookByIsbn()` → redirects to library

### Deployment Setup
- **Frontend**: GitHub Pages at `https://hyp-n.github.io/AI-SLOP-booKeeper-lols/`
  - Workflow: `.github/workflows/deploy-frontend.yml`
  - Base path: `/AI-SLOP-booKeeper-lols/`
- **Backend**: Cloudflare Tunnel (quick tunnel) from local PC
  - Command: `cloudflared tunnel --url http://localhost:5000`
  - Current URL: `https://forums-crossword-times-giants.trycloudflare.com`
  - Frontend API base points to this tunnel URL
- **Repository**: `https://github.com/hyp-n/AI-SLOP-booKeeper-lols`

---

## 📁 Key File Structure

```
booKeeper - ai/
├── backend/
│   ├── run.py                 # Flask app factory, Socket.IO init
│   ├── config.py              # MongoDB URI, secret key persistence
│   ├── models.py              # MongoDB helpers, serialization
│   ├── requirements.txt
│   ├── routes/                # All API blueprints
│   │   ├── auth.py
│   │   ├── books.py
│   │   ├── collections.py
│   │   ├── reading.py
│   │   ├── social.py
│   │   ├── messages.py
│   │   ├── ebooks.py
│   │   └── socket_events.py   # Socket.IO handlers
│   ├── services/              # External API clients
│   └── smoke_test.py
├── frontend/
│   ├── src/
│   │   ├── api/client.js      # Axios instance + all API calls
│   │   ├── components/        # CameraScanner, BookCard, etc.
│   │   ├── pages/             # All page components
│   │   ├── App.jsx            # Router, theme, protected routes
│   │   ├── main.jsx
│   │   └── index.css          # Tailwind v4 imports
│   ├── public/
│   │   ├── sw.js              # Service Worker
│   │   ├── manifest.json      # PWA manifest
│   │   └── offline.html
│   ├── vite.config.js         # Base path for GitHub Pages
│   ├── postcss.config.js      # @tailwindcss/postcss
│   ├── tailwind.config.js
│   └── package.json
├── .github/workflows/
│   └── deploy-frontend.yml    # GitHub Pages deploy
├── install.ps1 / install.sh / install.py  # One-line installers
├── install-capacitor.ps1      # Capacitor setup (for future APK)
├── build-apk.ps1              # Android APK build script
└── PROJECT_HISTORY.md         # This file
```

---

## 🚀 How to Run (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 20+
- MongoDB Atlas account (connection string in `backend/.env`)

### One-Line Install (Windows)
```powershell
cd "C:\Users\Admin\booKeeper - ai"
.\install.ps1
```

### One-Line Install (Linux/macOS/WSL)
```bash
cd "C:\Users\Admin\booKeeper - ai"
chmod +x install.sh && ./install.sh
```

### Manual Steps
```bash
# Backend
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
cp .env.template .env   # Add MONGO_URI
python run.py           # Runs on http://localhost:5000

# Frontend (dev mode, separate terminal)
cd frontend
npm install
npm run dev             # Runs on http://localhost:5173 (proxies /api to :5000)
```

### Production Build (Flask serves built frontend)
```bash
cd frontend && npm run build
cd ../backend && python run.py   # Serves on http://localhost:5000
```

---

## 🌐 Current Live URLs

| Component | URL | Notes |
|-----------|-----|-------|
| **Frontend (PWA)** | `https://hyp-n.github.io/AI-SLOP-booKeeper-lols/` | GitHub Pages, auto-deploys on push to `main` touching `frontend/**` |
| **Backend API** | `https://forums-crossword-times-giants.trycloudflare.com` | Cloudflare quick tunnel from local PC. **Changes on restart**. |
| **GitHub Repo** | `https://github.com/hyp-n/AI-SLOP-booKeeper-lols` | Source of truth |

---

## ⚠️ Known Issues / Limitations

1. **Tunnel URL changes** on each `cloudflared` restart → must update `frontend/src/api/client.js` `TUNNEL_URL` constant and rebuild/push frontend.
2. **Backend only runs while PC is on** – tunnel + Flask must stay running.
3. **GitHub Pages base path** requires `GITHUB_PAGES=true` env var during build (handled in workflow).
4. **Tailwind v4** uses `@import "tailwindcss"` in CSS, not `@tailwind` directives.
5. **Anna's Archive scraping** is fragile (CSS selectors may break).
6. **No automated tests** configured.

---

## 🔮 Future Improvements (When Resources Allow)

1. **Permanent backend hosting**: Railway ($5/mo), Fly.io (free tier), or VPS
2. **Named Cloudflare Tunnel** (stable URL, no account-less limitations)
3. **Native APK** via Capacitor:
   ```powershell
   .\install-capacitor.ps1
   .\build-apk.ps1
   ```
   Requires Android SDK, JDK, ~10GB disk space.
4. **iOS build** via Capacitor + Xcode (macOS only)
5. **Real OCR** for ISBN scanning (replace simulation in `CameraScanner.jsx`)
6. **Automated tests** (pytest, Vitest)
7. **CI/CD** for backend (auto-deploy on push)

---

## 📝 Environment Variables

### Backend (`backend/.env`)
```env
MONGO_URI=mongodb+srv://<user>:<pass>@cluster.mongodb.net/booKeeper?retryWrites=true&w=majority
SECRET_KEY=auto-generated-and-persisted-to-data/.secret_key
FLASK_DEBUG=false
CORS_ORIGINS=https://hyp-n.github.io  # or tunnel URL for local dev
```

### Frontend (build-time)
```bash
GITHUB_PAGES=true npm run build   # Sets correct base path
```

---

## 🔑 Key Commands Reference

```bash
# Rebuild frontend for GitHub Pages (after tunnel URL change)
cd frontend
GITHUB_PAGES=true npm run build
git add -A && git commit -m "Update tunnel URL" && git push origin master:main

# Start tunnel (run in dedicated terminal)
cloudflared tunnel --url http://localhost:5000

# Start Flask backend (run in dedicated terminal)
cd backend && python run.py

# Check GitHub Actions status
# https://github.com/hyp-n/AI-SLOP-booKeeper-lols/actions

# View tunnel logs
# Output shows: "Your quick Tunnel has been created! Visit it at: https://xxx.trycloudflare.com"
```

---

## 📱 User (Dad) Instructions

1. Open `https://hyp-n.github.io/AI-SLOP-booKeeper-lols/` on phone
2. **iOS Safari**: Share → Add to Home Screen
   **Android Chrome**: ⋮ → Install app / Add to Home Screen
3. Register account → start scanning ISBNs, adding books, chatting with friends
4. Works offline for UI; data syncs when online

---

## 📅 Session Context

- **Date**: 2026-09-27
- **Git branch**: `master` (pushed to `origin/main`)
- **Last commit**: "Fix GitHub Pages base path for subdirectory deployment"
- **Tunnel URL**: `https://forums-crossword-times-giants.trycloudflare.com` (ephemeral)
- **Flask**: Running in background on `localhost:5000`
- **cloudflared**: Running in background

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| GitHub Pages blank | Check Actions tab; wait for green deploy; hard refresh phone |
| API calls fail | Verify tunnel URL in `client.js` matches current cloudflared output |
| CORS errors | Update `CORS_ORIGINS` in backend `.env` to match frontend origin |
| Tailwind build fails | Ensure `@tailwindcss/postcss` in `postcss.config.js` and `@import "tailwindcss"` in `index.css` |
| Camera scanner permission denied | HTTPS required (GitHub Pages + tunnel both provide) |
| MongoDB connection fails | Check `MONGO_URI` in `.env`, Atlas IP whitelist (0.0.0.0/0 for dev) |

---

**End of Project History** — Use this file to onboard new sessions quickly.