# Deploy booKeeper: Frontend on GitHub Pages + Backend on PythonAnywhere

## Architecture

| Layer | Technology | Hosting |
|-------|------------|---------|
| Frontend | React + Vite | GitHub Pages (free) |
| Backend | Flask + SQLAlchemy | PythonAnywhere (free) |
| Database | PostgreSQL | Supabase (free) |

---

## Step 1: Create Supabase Database (3 min)

1. Go to [supabase.com](https://supabase.com) → Sign up free (no credit card)
2. Create a new project (free tier)
3. Go to **Settings** → **Database** → **Connection string**
4. Copy the URI: `postgresql://postgres:password@db.xxxx.supabase.co:5432/postgres`
5. Keep this URI handy

---

## Step 2: Push to GitHub

```bash
cd "C:\Users\Admin\booKeeper - ai"
git init
git add .
git commit -m "Initial commit"
# Create repo at github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/bookeeper.git
git push -u origin main
```

---

## Step 3: Deploy Backend on PythonAnywhere (5 min)

1. Go to [pythonanywhere.com](https://www.pythonanywhere.com) → Sign up free
2. **Dashboard** → **Web** → **Add a new web app**
3. Select **Flask** and **Python 3.10**
4. Choose a username for your URL: `yourusername.pythonanywhere.com`
5. **Files** tab → Upload your `backend/` folder (or Git clone)
6. **Web** tab → **WSGI configuration file** → Replace with:

```python
import sys
import os

path = '/home/yourusername/bookeeper/backend'
if path not in sys.path:
    sys.path.append(path)

os.environ['DATABASE_URL'] = 'postgresql://postgres:password@db.xxxx.supabase.co:5432/postgres'
os.environ['SECRET_KEY'] = 'your-secret-key-here'
os.environ['ALLOWED_ORIGINS'] = 'https://YOUR_USERNAME.github.io,http://localhost:5173'

from run import create_app
application = create_app()
```

7. Click **Reload** on the Web tab
8. Your API is live at `https://yourusername.pythonanywhere.com/api`

---

## Step 4: Deploy Frontend on GitHub Pages (3 min)

1. Go to your repo → **Settings** → **Pages**
2. Source: **GitHub Actions**
3. Go to **Settings** → **Secrets and variables** → **Actions**
4. Add secret: `VITE_API_BASE_URL` = `https://yourusername.pythonanywhere.com/api`
5. Push to `main` → GitHub Actions builds → Deploys to Pages
6. Your app: `https://YOUR_USERNAME.github.io/bookkeeper/`

---

## Your Final URLs

| Service | URL |
|---------|-----|
| **Your app (share this)** | `https://YOUR_USERNAME.github.io/bookkeeper/` |
| **Backend API** | `https://yourusername.pythonanywhere.com/api` |

---

## Notes

- **PythonAnywhere free tier**: Always-on, no spin-down, no credit card
- **Supabase free tier**: 500 MB storage, shared CPU
- **GitHub Pages**: Free static hosting, auto-deploys on push
- **No Docker, no local database, no server management**

---

## Local Development (Unchanged)

```bash
# Terminal 1: Backend (needs local PostgreSQL or Supabase URI)
cd backend && python run.py

# Terminal 2: Frontend (hot reload)
cd frontend && npm run dev
# → http://localhost:5173
```