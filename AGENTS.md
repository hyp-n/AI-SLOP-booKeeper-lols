# AGENTS.md

## Build & Run Order

The frontend MUST be built before Flask can serve it. Flask serves `frontend/dist` — if it doesn't exist, pages won't load.

```bash
# One-time setup
cd frontend && npm install && npm run build && cd ..
pip install -r backend/requirements.txt

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
- **Database**: SQLite at `data/books.db` — auto-created on startup via `db.create_all()`, no migrations
- **API prefix**: all routes under `/api/` (e.g., `/api/books/`, `/api/collections/`)

## Key Conventions

- **No tests, no linter, no formatter configured** — don't look for these commands
- **No env vars required** — `SECRET_KEY` has a dev default in `config.py`
- **DaisyUI themes**: toggle via `data-theme` attribute on `<html>`, persisted in `localStorage` under `"theme"`
- **Book serialization**: `Book.to_dict()` embeds reading progress fields (`reading_status`, `current_page`, `reading_percentage`) — don't duplicate these in API responses
- **Collection ordering**: `BookCollection.order_index` drives sort order; the `/api/collections/<id>/reorder` endpoint accepts `{book_ids: [...]}` array

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
