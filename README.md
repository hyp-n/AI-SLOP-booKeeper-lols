# Hey everybody, i made this project for fun lol it is fully ai, by opencode, so not reccomend using this

# booKeeper

A self-hosted personal book manager. Scan ISBNs, organize collections, track reading progress, and find ebook downloads.

## Features

- **ISBN Scanning** — Look up books by ISBN via OpenLibrary (manual entry + camera support)
- **Library Management** — Grid/list views, search, sort, and filter
- **Collections** — Organize books with drag-and-drop collections
- **Reading Tracker** — Track pages, status (Want to Read / Reading / Finished), and progress percentage
- **Ebook Downloads** — Search Anna's Archive and Project Gutenberg for EPUB/PDF downloads
- **Statistics** — Dashboard with reading stats and library breakdown
- **Social** — Friend requests, user profiles, real-time messaging
- **Self-Hosted** — PostgreSQL database, single Flask process

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- **PostgreSQL** (local or Supabase)

### Setup

```bash
# 1. Clone and enter the project
cd booKeeper

# 2. Set up Python backend
cd backend
pip install -r requirements.txt

# 3. Set up frontend (first time only)
cd ../frontend
npm install
npm run build

# 4. Run the app
cd ../backend
python run.py
```

The app will be available at **http://localhost:5000**

### Development Mode

For development with hot-reload:

```bash
# Terminal 1: Backend
cd backend
python run.py

# Terminal 2: Frontend (hot-reload on :5173, proxies API to :5000)
cd frontend
npm run dev
```

### Configuration

Create a `.env` file in `backend/` to customize:

```bash
# PostgreSQL connection (Supabase or local)
DATABASE_URL=postgresql://postgres:password@db.xxxx.supabase.co:5432/postgres

# Local PostgreSQL:
# DATABASE_URL=postgresql://localhost:5432/bookeeper

# Optional: Secret key (auto-generated if not set)
# SECRET_KEY=your-secret-key

# Optional: Google OAuth (leave blank to disable)
# GOOGLE_CLIENT_ID=
# GOOGLE_CLIENT_SECRET=

# Optional: Allowed CORS origins (comma-separated)
# ALLOWED_ORIGINS=http://localhost:5000,http://localhost:5173
```

## How to Use

### Adding Books

1. Click **+ Add Book** on the Library page
2. Enter an ISBN manually or use camera scanning
3. Or search by title/author and pick from results

### Organizing Collections

1. Use the sidebar to create new collections
2. Go to a collection page
3. Drag and drop books to reorder them
4. Use **+ Add Books** to add books from your library

### Tracking Reading

1. Click any book to view details
2. Set status (Want to Read / Reading / Finished)
3. Enter your current page — progress updates automatically

### Finding Ebooks

1. On a book's detail page, use the **Download Ebook** section
2. Search by title or ISBN
3. Click **Download** to visit the source

### Social Features

1. Register multiple accounts
2. Search for friends by email on the Friends page
3. Send/receive friend requests
4. Start private or group chats on the Messages page

## Project Structure

```
booKeeper/
├── backend/
│   ├── run.py              # Entry point
│   ├── config.py           # Configuration
│   ├── models.py           # SQLAlchemy models
│   ├── routes/             # API endpoints
│   └── services/           # External API integrations
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page-level components
│   │   └── api/            # API client
│   └── ...
└── README.md
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS, DaisyUI |
| Drag & Drop | @dnd-kit |
| Backend | Flask, Flask-SQLAlchemy, Flask-SocketIO |
| Database | **PostgreSQL** (Supabase) |
| Real-time | Socket.IO (eventlet) |
| APIs | OpenLibrary, Anna's Archive, Project Gutenberg |

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /api/books/` | List all books |
| `POST /api/books/` | Add a book |
| `GET /api/books/lookup/<isbn>` | Look up ISBN |
| `GET /api/books/search?q=` | Search books |
| `GET /api/collections/` | List collections |
| `POST /api/collections/` | Create collection |
| `PUT /api/collections/<id>/reorder` | Reorder books |
| `GET /api/ebooks/search?q=` | Search ebook sources |
| `PUT /api/reading/<book_id>` | Update reading progress |
| `GET /api/reading/stats` | Reading statistics |
| `POST /api/auth/register` | Register user |
| `POST /api/auth/login` | Login user |
| `GET /api/social/friends` | List friends |
| `POST /api/social/friends/request` | Send friend request |
| `POST /api/messages/conversations` | Create conversation |
| `POST /api/messages/conversations/<id>/messages` | Send message |

## License

MIT

---

## 🌐 Deploy: Frontend on GitHub Pages + Backend on PythonAnywhere (Free)

### Frontend → GitHub Pages (Free, Static)

1. **Push to GitHub**
   ```bash
   git init && git add . && git commit -m "init"
   # Create repo at github.com, then:
   git remote add origin https://github.com/YOUR_USERNAME/bookeeper.git
   git push -u origin main
   ```

2. **Enable GitHub Pages**
   - Repo → Settings → Pages → Source: **GitHub Actions**

3. **Add Backend URL as Secret**
   - Settings → Secrets → Actions → New secret
   - Name: `VITE_API_BASE_URL`
   - Value: `https://yourusername.pythonanywhere.com/api` (get this after backend deploy)

4. **Deploy Happens Automatically**
   - Push to `main` → GitHub Actions builds → Deploys to Pages
   - Your app: `https://YOUR_USERNAME.github.io/bookkeeper/`

### Backend → PythonAnywhere (Free, Always-On)

1. **Supabase** (free): [supabase.com](https://supabase.com) → Create project → Get connection string
2. **PythonAnywhere Dashboard** → Web → Add a new web app → Flask → Python 3.10
3. **WSGI Configuration**:
   ```python
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
4. **Reload** → Your API is live at `https://yourusername.pythonanywhere.com/api`

### See `DEPLOY.md` for detailed steps and `BACKEND_DEPLOY.md` for more backend options.