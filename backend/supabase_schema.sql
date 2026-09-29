-- Supabase PostgreSQL Schema for booKeeper
-- This file is for reference. Tables are auto-created by SQLAlchemy's db.create_all()
-- You can also run this SQL manually in the Supabase SQL editor if needed.

CREATE TABLE IF NOT EXISTS books (
    id VARCHAR(36) PRIMARY KEY,
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
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS collection_books (
    id SERIAL PRIMARY KEY,
    collection_id VARCHAR(36) NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
    book_id VARCHAR(36) NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    order_index INTEGER DEFAULT 0,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    name VARCHAR(200),
    avatar_url TEXT,
    bio TEXT,
    currently_reading VARCHAR(36),
    oauth_provider VARCHAR(50),
    oauth_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS friend_requests (
    id VARCHAR(36) PRIMARY KEY,
    sender_id VARCHAR(36) NOT NULL REFERENCES users(id),
    receiver_id VARCHAR(36) NOT NULL REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS conversations (
    id VARCHAR(36) PRIMARY KEY,
    is_group BOOLEAN DEFAULT FALSE,
    group_name VARCHAR(200),
    group_admin VARCHAR(36),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_message_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS conversation_participants (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(36) NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS messages (
    id VARCHAR(36) PRIMARY KEY,
    sender_id VARCHAR(36) NOT NULL REFERENCES users(id),
    conversation_id VARCHAR(36) NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_by JSONB DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS ebook_sources (
    id SERIAL PRIMARY KEY,
    book_id VARCHAR(36) NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    source_name VARCHAR(200),
    format VARCHAR(50),
    external_url TEXT,
    file_size VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_books_isbn ON books(isbn);
CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
CREATE INDEX IF NOT EXISTS idx_collection_books_collection_id ON collection_books(collection_id);
CREATE INDEX IF NOT EXISTS idx_collection_books_book_id ON collection_books(book_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversation_participants_conversation_id ON conversation_participants(conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversation_participants_user_id ON conversation_participants(user_id);
CREATE INDEX IF NOT EXISTS idx_friend_requests_sender_id ON friend_requests(sender_id);
CREATE INDEX IF NOT EXISTS idx_friend_requests_receiver_id ON friend_requests(receiver_id);
CREATE INDEX IF NOT EXISTS idx_ebook_sources_book_id ON ebook_sources(book_id);
CREATE INDEX IF NOT EXISTS idx_messages_sender_id ON messages(sender_id);
