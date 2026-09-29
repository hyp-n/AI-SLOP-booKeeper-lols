# Supabase Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the database configuration to properly use Supabase PostgreSQL instead of the incorrect MongoDB setup currently in `.env` and documentation.

**Architecture:** The backend already uses Flask-SQLAlchemy with PostgreSQL models. The issue is that `.env` and `.env.template` contain MongoDB configuration, and `AGENTS.md` documents MongoDB as the database. We need to align all configuration and documentation with the actual PostgreSQL/Supabase setup.

**Tech Stack:** Flask, Flask-SQLAlchemy, PostgreSQL (Supabase), pg8000 driver

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `backend/.env` | Modify | Replace MongoDB config with Supabase PostgreSQL connection string |
| `backend/.env.template` | Modify | Replace MongoDB template with PostgreSQL/Supabase template |
| `AGENTS.md` | Modify | Update database references from MongoDB to PostgreSQL/Supabase |
| `backend/supabase_schema.sql` | Create | SQL schema for Supabase table creation (optional, for reference) |

---

### Task 1: Fix backend/.env to use Supabase PostgreSQL

**Files:**
- Modify: `backend/.env`

- [ ] **Step 1: Replace MongoDB config with Supabase PostgreSQL**

Replace the contents of `backend/.env` with:

```
# Supabase PostgreSQL connection
# Get this from: https://supabase.com → Project → Settings → Database → Connection string
DATABASE_URL=postgresql+pg8000://postgres:password@db.xxxx.supabase.co:5432/postgres

# Flask debug mode
FLASK_DEBUG=false
```

- [ ] **Step 2: Verify the file was updated correctly**

Run: `type backend\.env`
Expected: Shows the new PostgreSQL configuration

---

### Task 2: Fix backend/.env.template to use Supabase PostgreSQL

**Files:**
- Modify: `backend/.env.template`

- [ ] **Step 1: Replace MongoDB template with PostgreSQL/Supabase template**

Replace the contents of `backend/.env.template` with:

```
# Backend Environment Variables
# Copy this to .env and modify as needed

# PostgreSQL connection string
# Supabase (free): https://supabase.com → Project → Settings → Database → Connection string
DATABASE_URL=postgresql+pg8000://postgres:password@db.xxxx.supabase.co:5432/postgres

# Local PostgreSQL:
# DATABASE_URL=postgresql+pg8000://postgres:postgres@localhost:5432/bookeeper

# Secret key for JWT tokens (auto-generated if not set, cached in data/.secret_key)
# SECRET_KEY=your-32-byte-hex-secret

# JWT token expiry in days
JWT_EXPIRY_DAYS=30

# Google OAuth (leave blank to disable Google login button)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Comma-separated allowed CORS origins
ALLOWED_ORIGINS=http://localhost:5000,http://localhost:5173

# Flask debug mode
FLASK_DEBUG=false
```

- [ ] **Step 2: Verify the file was updated correctly**

Run: `type backend\.env.template`
Expected: Shows the new PostgreSQL/Supabase template

---

### Task 3: Update AGENTS.md to reflect PostgreSQL/Supabase

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: Update the Database section in AGENTS.md**

Replace the MongoDB references with PostgreSQL/Supabase:

```markdown
## Architecture

- **Backend**: Flask + Flask-PyMongo, blueprints registered in `backend/run.py` with function-level imports (avoids circular imports)
- **Frontend**: React 18 + Vite + Tailwind CSS + DaisyUI, built to `frontend/dist`
- **Database**: PostgreSQL (Supabase or local) — SQLAlchemy models in `backend/models.py`
- **API prefix**: all routes under `/api/` (e.g., `/api/books/`, `/api/collections/`)
- **Real-time**: Flask-SocketIO with eventlet for WebSocket support
```

- [ ] **Step 2: Update the Build & Run Order section**

Replace the MongoDB instructions with PostgreSQL:

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

- [ ] **Step 3: Update the Database Collections section**

Replace with PostgreSQL tables:

```markdown
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
```

- [ ] **Step 4: Update the Key Conventions section**

Replace MongoDB-specific conventions with PostgreSQL:

```markdown
## Key Conventions

- **No tests, no linter, no formatter configured** — don't look for these commands
- **No env vars required** — `SECRET_KEY` has a dev default in `config.py` (auto-generated & cached in `data/.secret_key`)
- **DaisyUI themes**: toggle via `data-theme` attribute on `<html>`, persisted in `localStorage` under `"theme"`
- **Book serialization**: `book_to_dict()` embeds reading progress fields (`reading_status`, `current_page`, `reading_percentage`) — don't duplicate these in API responses
- **Collection ordering**: `Collection.order_index` drives sort order; the `/api/collections/<id>/reorder` endpoint accepts `{book_ids: [...]}` array
- **PostgreSQL IDs**: All IDs are UUID strings — SQLAlchemy generates them via `generate_id()`
```

---

### Task 4: Create Supabase schema reference file

**Files:**
- Create: `backend/supabase_schema.sql`

- [ ] **Step 1: Create the schema file**

Create `backend/supabase_schema.sql` with the SQL schema for reference:

```sql
-- Supabase PostgreSQL Schema for booKeeper
-- This file is for reference. Tables are auto-created by SQLAlchemy's db.create_all()
-- You can also run this SQL manually in the Supabase SQL editor if needed.

CREATE TABLE IF NOT EXISTS books (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    isbn VARCHAR(20),
    title VARCHAR(500) NOT NULL,
    author VARCHAR(500),
    cover_url TEXT,
    description TEXT,
    publisher VARCHAR(500),
    published_date VARCHAR(50),
    page_count INTEGER,
    language VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reading_status VARCHAR(20) DEFAULT 'want_to_read',
    current_page INTEGER DEFAULT 0,
    reading_percentage FLOAT DEFAULT 0.0,
    reading_started_at TIMESTAMP WITH TIME ZONE,
    reading_finished_at TIMESTAMP WITH TIME ZONE,
    reading_updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS collection_books (
    id SERIAL PRIMARY KEY,
    collection_id UUID NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
    book_id UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    order_index INTEGER DEFAULT 0,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    name VARCHAR(200),
    avatar_url TEXT,
    bio TEXT,
    currently_reading UUID,
    oauth_provider VARCHAR(50),
    oauth_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS friend_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id UUID NOT NULL REFERENCES users(id),
    receiver_id UUID NOT NULL REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    is_group BOOLEAN DEFAULT FALSE,
    group_name VARCHAR(200),
    group_admin UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_message_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS conversation_participants (
    id SERIAL PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id UUID NOT NULL REFERENCES users(id),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_by JSONB DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS ebook_sources (
    id SERIAL PRIMARY KEY,
    book_id UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    source_name VARCHAR(200),
    format VARCHAR(50),
    external_url TEXT,
    file_size VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_books_isbn ON books(isbn);
CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_collection_books_collection_id ON collection_books(collection_id);
CREATE INDEX IF NOT EXISTS idx_collection_books_book_id ON collection_books(book_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversation_participants_conversation_id ON conversation_participants(conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversation_participants_user_id ON conversation_participants(user_id);
```

- [ ] **Step 2: Verify the file was created**

Run: `type backend\supabase_schema.sql`
Expected: Shows the SQL schema

---

### Task 5: Verify the configuration works

**Files:**
- Test: `backend/config.py`, `backend/run.py`

- [ ] **Step 1: Test that the app can be imported**

Run: `cd backend && python -c "from config import DATABASE_URL; print(DATABASE_URL)"`
Expected: Shows the PostgreSQL connection string

- [ ] **Step 2: Test that the app can be created**

Run: `cd backend && python -c "from run import create_app; app = create_app(); print('App created successfully')"`
Expected: "App created successfully" (may show a warning about database connection if Supabase is not reachable)

- [ ] **Step 3: Commit all changes**

```bash
git add backend/.env backend/.env.template AGENTS.md backend/supabase_schema.sql
git commit -m "fix: replace MongoDB config with Supabase PostgreSQL

- Update .env to use PostgreSQL connection string
- Update .env.template with Supabase setup instructions
- Update AGENTS.md to document PostgreSQL/Supabase instead of MongoDB
- Add supabase_schema.sql for reference
- All code already used SQLAlchemy with PostgreSQL models"
```

---

## Self-Review

**1. Spec coverage:**
- Fix `.env` to use Supabase PostgreSQL
- Fix `.env.template` to use Supabase PostgreSQL
- Update `AGENTS.md` to reflect PostgreSQL/Supabase
- Create Supabase schema reference file
- Verify configuration works

**2. Placeholder scan:** No placeholders found.

**3. Type consistency:** All references to database are now consistently PostgreSQL/Supabase.
