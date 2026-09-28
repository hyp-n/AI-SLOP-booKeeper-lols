# AGENTS.md

## Build & Run Order

The frontend MUST be built before Flask can serve it. Flask serves `frontend/dist` — if it doesn't exist, pages won't load.

```bash
# One-time setup
cd frontend && npm install && npm run build && cd ..
pip install -r backend/requirements.txt

# Set up PostgreSQL (required!)
# Option 1: Supabase (free) — https://supabase.com → Create project → Get connection string
# Option 2: Local PostgreSQL — install and create database
# Then set DATABASE_URL in backend/.env

# Run (single process, serves API + built frontend)
cd backend && python run.py
# → http://localhost:5000
```

### Dev mode (hot-reload, two terminals)

```bash
# Terminal 1 — API on :5000
cd backend && python run.py

# Terminal 2 — Vite dev server on :5173, proxies /api → :5000
cd frontend && npm run dev
```

## Architecture

- **Backend**: Flask + Flask-SQLAlchemy, blueprints registered in `backend/run.py` with function-level imports (avoids circular imports)
- **Frontend**: React 18 + Vite + Tailwind CSS + DaisyUI, built to `frontend/dist`
- **Database**: PostgreSQL (Supabase or local) — SQLAlchemy models in `backend/models.py`
- **API prefix**: all routes under `/api/` (e.g., `/api/books/`, `/api/collections/`)
- **Real-time**: Flask-SocketIO with eventlet for WebSocket support

## Key Conventions

- **No tests, no linter, no formatter configured** — don't look for these commands
- **No env vars required** — `SECRET_KEY` has a dev default in `config.py` (auto-generated & cached in `data/.secret_key`)
- **DaisyUI themes**: toggle via `data-theme` attribute on `<html>`, persisted in `localStorage` under `"theme"`
- **Book serialization**: `book_to_dict()` embeds reading progress fields (`reading_status`, `current_page`, `reading_percentage`) — don't duplicate these in API responses
- **Collection ordering**: `Collection.order_index` drives sort order; the `/api/collections/<id>/reorder` endpoint accepts `{book_ids: [...]}` array
- **PostgreSQL IDs**: All IDs are UUID strings — SQLAlchemy generates them via `generate_id()`

## External Services

| Service | Purpose | Auth |
|---|---|---|
| OpenLibrary (`openlibrary.py`) | ISBN lookup + search | None |
| Anna's Archive (`annas_archive.py`) | Ebook search (scraping) | None — fragile CSS selectors |
| Project Gutenberg (`gutenberg.py`) | Public domain ebooks | None |

Anna's Archive uses BeautifulSoup selectors (`div.iframe-list > div`) — will break silently if the site changes. All service functions return `[]` on failure.

## Ports

| Mode | URL |
|---|---|
| Production (Flask serves built frontend) | http://localhost:5000 |
| Dev (Vite hot-reload) | http://localhost:5173 |

## Database Tables

| Table | Purpose |
|---|---|
| `books` | Book metadata + reading progress + collection refs |
| `collections` | User collections with order_index |
| `collection_books` | Many-to-many join table for collections and books |
| `users` | User accounts, profiles, currently_reading ref |
| `friend_requests` | Pending/accepted friend requests |
| `conversations` | 1-on-1 and group chats |
| `conversation_participants` | Many-to-many join table for conversations and users |
| `messages` | Chat messages |
| `ebook_sources` | Ebook download sources for books |
