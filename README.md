# booKeeper

A self-hosted personal book manager. Scan ISBNs, organize collections, track reading progress, and find ebook downloads.

## Features

- **ISBN Scanning** — Look up books by ISBN via OpenLibrary (manual entry + camera support)
- **Library Management** — Grid/list views, search, sort, and filter
- **Collections** — Organize books with drag-and-drop collections
- **Reading Tracker** — Track pages, status (Want to Read / Reading / Finished), and progress percentage
- **Ebook Downloads** — Search Anna's Archive and Project Gutenberg for EPUB/PDF downloads
- **Statistics** — Dashboard with reading stats and library breakdown
- **Self-Hosted** — SQLite database, single Flask process, no Docker needed

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+

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

## Project Structure

```
booKeeper/
├── backend/
│   ├── run.py              # Entry point
│   ├── config.py           # Configuration
│   ├── models.py           # Database models
│   ├── routes/             # API endpoints
│   └── services/           # External API integrations
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page-level components
│   │   └── api/            # API client
│   └── ...
├── data/                   # SQLite database (auto-created)
└── README.md
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS, DaisyUI |
| Drag & Drop | @dnd-kit |
| Backend | Flask, Flask-SQLAlchemy |
| Database | SQLite |
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

## License

MIT
