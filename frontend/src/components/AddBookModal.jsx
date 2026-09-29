import { useState, useEffect } from "react";
import { addBookByIsbn, searchBooks, addBook } from "../api/client";

export default function AddBookModal({ isOpen, onClose, onBookAdded }) {
  const [isbn, setIsbn] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [tab, setTab] = useState("isbn"); // isbn | search
  const [scanning, setScanning] = useState(false);

  useEffect(() => {
    if (!isOpen) {
      setIsbn("");
      setSearchQuery("");
      setSearchResults([]);
      setError("");
      setTab("isbn");
    }
  }, [isOpen]);

  const handleIsbnSubmit = async (e) => {
    e.preventDefault();
    if (!isbn.trim()) return;

    setLoading(true);
    setError("");
    try {
      const { data } = await addBookByIsbn(isbn.trim());
      onBookAdded(data);
      onClose();
    } catch (err) {
      setError(err.response?.data?.error || "Failed to add book");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError("");
    try {
      const { data } = await searchBooks(searchQuery.trim());
      setSearchResults(data);
    } catch (err) {
      setError("Search failed");
    } finally {
      setLoading(false);
    }
  };

  const handleAddFromSearch = async (book) => {
    setLoading(true);
    setError("");
    try {
      const { data } = await addBookByIsbn(book.isbn || "");
      onBookAdded(data);
      onClose();
    } catch (err) {
      // If ISBN add fails, try manual
      try {
        const { data } = await addBook({
          title: book.title,
          author: book.author,
          cover_url: book.cover_url,
          publisher: book.publisher,
          published_date: book.published_date,
          page_count: book.page_count,
          isbn: book.isbn,
        });
        onBookAdded(data);
        onClose();
      } catch (err2) {
        setError(err2.response?.data?.error || "Failed to add book");
      }
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal modal-open">
      <div className="modal-box max-w-2xl">
        <h3 className="font-bold text-lg mb-4">Add a Book</h3>

        <div className="tabs tabs-boxed mb-4">
          <button
            className={`tab ${tab === "isbn" ? "tab-active" : ""}`}
            onClick={() => setTab("isbn")}
          >
            Scan / Enter ISBN
          </button>
          <button
            className={`tab ${tab === "search" ? "tab-active" : ""}`}
            onClick={() => setTab("search")}
          >
            Search
          </button>
        </div>

        {tab === "isbn" && (
          <form onSubmit={handleIsbnSubmit} className="space-y-4">
            <div>
              <label className="label">
                <span className="label-text">ISBN</span>
              </label>
              <input
                type="text"
                className="input input-bordered w-full"
                placeholder="978-0-123456-78-9"
                value={isbn}
                onChange={(e) => setIsbn(e.target.value)}
                autoFocus
              />
            </div>

            <button
              type="button"
              className="btn btn-outline btn-block"
              onClick={() => setScanning(!scanning)}
            >
              {scanning ? "Stop Camera" : "Scan with Camera"}
            </button>

            {scanning && (
              <div className="rounded overflow-hidden border">
                <p className="text-sm text-center p-2">Camera scanner active</p>
              </div>
            )}
          </form>
        )}

        {tab === "search" && (
          <div className="space-y-4">
            <form onSubmit={handleSearch} className="flex gap-2">
              <input
                type="text"
                className="input input-bordered flex-1"
                placeholder="Search by title, author, or ISBN..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? <span className="loading loading-spinner loading-sm"></span> : "Search"}
              </button>
            </form>

            <div className="max-h-64 overflow-y-auto space-y-2">
              {searchResults.map((book, i) => (
                <div key={i} className="flex items-center gap-3 p-2 rounded bg-base-200">
                  {book.cover_url && (
                    <img src={book.cover_url} alt="" className="w-10 h-14 object-cover rounded" />
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{book.title}</p>
                    <p className="text-sm text-base-content/60 truncate">{book.author}</p>
                  </div>
                  <button
                    className="btn btn-sm btn-primary"
                    onClick={() => handleAddFromSearch(book)}
                    disabled={loading}
                  >
                    Add
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {error && (
          <div className="alert alert-error mt-4">
            <span>{error}</span>
          </div>
        )}

        <div className="modal-action">
          <button className="btn" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
