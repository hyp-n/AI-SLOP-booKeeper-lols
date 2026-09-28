# Backend Hosting Options (Pick One)

Your frontend goes to **GitHub Pages** (free, static). Your Flask backend needs a **server** — here are the easiest free options:

---

## Option 1: PythonAnywhere (Recommended, Free, Always-On)
- Native Python, no Docker
- Always-on (no spin-down)
- No credit card required
- **Setup**: 5 min

```bash
# In PythonAnywhere dashboard:
# Web → Add a new web app → Flask → Python 3.10
# WSGI file:
import sys, os
path = '/home/yourusername/bookeeper/backend'
if path not in sys.path:
    sys.path.append(path)
os.environ['DATABASE_URL'] = 'postgresql://postgres:password@db.xxxx.supabase.co:5432/postgres'
os.environ['SECRET_KEY'] = 'your-secret-key'
os.environ['ALLOWED_ORIGINS'] = 'https://YOUR_USERNAME.github.io'
from run import create_app
application = create_app()
```

---

## Option 2: Render.com (Free, Spins Down)
- Native Python, no Docker
- Spins down after 15 min inactivity
- **Setup**: 3 min

```bash
# In Render dashboard:
# New → Web Service → Connect repo
# Build: pip install -r backend/requirements.txt
# Start: cd backend && gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT run:create_app()
# Env vars: DATABASE_URL, SECRET_KEY, ALLOWED_ORIGINS=https://<your-github-username>.github.io
```

---

## Option 3: Railway.app (Free tier)
- Simple, fast deploys
- $5/month credit (covers hobby usage)
- **Setup**: 2 min

```bash
# railway login → railway init → railway up
# Add DATABASE_URL in Railway dashboard
```

---

## Option 4: Fly.io (Free allowance)
- Runs Docker
- 3 shared-cpu-1x VMs free
- **Setup**: 5 min

```bash
# fly launch → fly deploy
# fly secrets set DATABASE_URL=...
```

---

## Option 5: Your Own VPS ($4-6/mo)
- Full control, always on
- DigitalOcean, Linode, Hetzner
- Run with `gunicorn` + `systemd` + nginx

---

## Required Environment Variables (All Platforms)

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | Your Supabase PostgreSQL connection string |
| `SECRET_KEY` | Auto-generate or set a 32-char hex string |
| `ALLOWED_ORIGINS` | `https://<your-github-username>.github.io,http://localhost:5173` |
| `FLASK_DEBUG` | `false` |
| `JWT_EXPIRY_DAYS` | `30` |

---

## Supabase (Free, Required for All)

1. [supabase.com](https://supabase.com) → Free tier (no credit card)
2. Create project → Settings → Database → Connection string
3. Copy URI: `postgresql://postgres:password@db.xxxx.supabase.co:5432/postgres`

---

## After Backend Deploy

1. Copy your backend URL (e.g., `https://yourusername.pythonanywhere.com`)
2. Go to GitHub repo → Settings → Secrets → Actions
3. Add secret: `VITE_API_BASE_URL` = `https://yourusername.pythonanywhere.com/api`
4. Push to main → GitHub Actions builds + deploys frontend
5. Your app: `https://<your-username>.github.io/bookkeeper/`