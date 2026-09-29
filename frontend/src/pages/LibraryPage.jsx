import { useState, useEffect } from "react";
import { getBooks, deleteBook } from "../api/client";
import BookCard from "../components/BookCard";
import AddBookModal from "../components/AddBookModal";

export default function LibraryPage() {
  const [books, setBooks] = useState([]);
  const [filteredBooks, setFilteredBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState("created_at");
  const [viewMode, setViewMode] = useState("grid"); // grid | list
  const [showAddModal, setShowAddModal] = useState(false);
  const [statusFilter, setStatusFilter] = useState("");

  useEffect(() => {
    loadBooks();
  }, []);

  useEffect(() => {
    filterBooks();
  }, [books, searchQuery, sortBy, statusFilter]);

  const loadBooks = async () => {
    setLoading(true);
    try {
      const { data } = await getBooks();
      setBooks(data);
    } catch (err) {
      console.error("Failed to load books:", err);
    } finally {
      setLoading(false);
    }
  };

  const filterBooks = () => {
    let result = [...books];

    // Search filter
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (b) =>
          b.title.toLowerCase().includes(q) ||
          (b.author && b.author.toLowerCase().includes(q)) ||
          (b.isbn && b.isbn.toLowerCase().includes(q))
      );
    }

    // Status filter
    if (statusFilter) {
      result = result.filter((b) => b.reading_status === statusFilter);
    }

    // Sort
    if (sortBy === "title") {
      result.sort((a, b) => a.title.localeCompare(b.title));
    } else if (sortBy === "author") {
      result.sort((a, b) => (a.author || "").localeCompare(b.author || ""));
    } else if (sortBy === "created_at") {
      result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    }

    setFilteredBooks(result);
  };

  const handleDelete = async (bookId) => {
    if (!confirm("Remove this book from your library?")) return;
    setActionLoading(true);
    try {
      await deleteBook(bookId);
      setBooks(books.filter((b) => b.id !== bookId));
    } catch (err) {
      console.error("Failed to delete book:", err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleBookAdded = (book) => {
    setBooks([book, ...books]);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    );
  }

  return (
    <div>
      {/* Toolbar */}
      <div className="flex flex-wrap gap-2 mb-6 items-center">
        <input
          type="text"
          className="input input-bordered flex-1 min-w-[200px]"
          placeholder="Search books..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />

        <select
          className="select select-bordered"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">All Status</option>
          <option value="want_to_read">Want to Read</option>
          <option value="reading">Reading</option>
          <option value="finished">Finished</option>
        </select>

        <select
          className="select select-bordered"
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
        >
          <option value="created_at">Date Added</option>
          <option value="title">Title</option>
          <option value="author">Author</option>
        </select>

        <div className="btn-group">
          <button
            className={`btn btn-sm ${viewMode === "grid" ? "btn-active" : ""}`}
            onClick={() => setViewMode("grid")}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
          </button>
          <button
            className={`btn btn-sm ${viewMode === "list" ? "btn-active" : ""}`}
            onClick={() => setViewMode("list")}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
            </svg>
          </button>
        </div>

        <button className="btn btn-primary" onClick={() => setShowAddModal(true)} disabled={actionLoading}>
          + Add Book
        </button>
      </div>

      {/* Results count */}
      <p className="text-sm text-base-content/50 mb-4">
        {filteredBooks.length} book{filteredBooks.length !== 1 ? "s" : ""}
      </p>

      {/* Books display */}
      {filteredBooks.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-lg text-base-content/50">No books found</p>
          <p className="text-sm text-base-content/40 mt-2">
            Add your first book by ISBN or search
          </p>
        </div>
      ) : viewMode === "grid" ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          {filteredBooks.map((book) => (
            <BookCard key={book.id} book={book} />
          ))}
        </div>
      ) : (
        <div className="space-y-2">
          {filteredBooks.map((book) => (
            <div key={book.id} className="card bg-base-100 shadow-sm p-4 flex gap-4 items-center">
              {book.cover_url && (
                <img src={book.cover_url} alt="" className="w-12 h-16 object-cover rounded" />
              )}
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate">{book.title}</p>
                <p className="text-sm text-base-content/60 truncate">{book.author}</p>
              </div>
              <span className="badge">{book.reading_status.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())}</span>
              {book.page_count && <span className="text-sm text-base-content/50">{book.page_count}p</span>}
            </div>
          ))}
        </div>
      )}

      <AddBookModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onBookAdded={handleBookAdded}
      />
    </div>
  );
}
