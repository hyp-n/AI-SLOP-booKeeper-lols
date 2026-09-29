import { useState } from "react";
import { searchEbooks } from "../api/client";

export default function EbookSearch({ bookTitle, bookIsbn }) {
  const [query, setQuery] = useState(bookTitle || "");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError("");
    setSearched(true);

    try {
      const { data } = await searchEbooks(query.trim());
      setResults(data);
    } catch (err) {
      setError("Search failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleSearchByIsbn = async () => {
    if (!bookIsbn || loading) return;
    setQuery(bookIsbn);
    setLoading(true);
    setError("");
    setSearched(true);

    try {
      const { data } = await searchEbooks(bookIsbn);
      setResults(data);
    } catch (err) {
      setError("Search failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card bg-base-100 shadow-md p-6">
      <h3 className="font-bold text-lg mb-4">Download Ebook</h3>

      <form onSubmit={handleSearch} className="flex gap-2 mb-4">
        <input
          type="text"
          className="input input-bordered flex-1"
          placeholder="Search by title or ISBN..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? <span className="loading loading-spinner loading-sm"></span> : "Search"}
        </button>
        {bookIsbn && (
          <button
            type="button"
            className="btn btn-outline"
            onClick={handleSearchByIsbn}
            disabled={loading}
            title="Search by ISBN"
          >
            {loading ? <span className="loading loading-spinner loading-sm"></span> : "ISBN"}
          </button>
        )}
      </form>

      {error && (
        <div className="alert alert-error">
          <span>{error}</span>
        </div>
      )}

      {searched && results.length === 0 && !loading && (
        <div className="text-center py-4 text-base-content/50">
          No ebooks found for "{query}"
        </div>
      )}

      <div className="space-y-2">
        {results.map((result, i) => (
          <div key={i} className="flex items-center gap-3 p-3 rounded bg-base-200">
            <div className="flex-1 min-w-0">
              <p className="font-medium">{result.source_name}</p>
              <p className="text-sm text-base-content/60">
                {result.format.toUpperCase()}
                {result.file_size && ` - ${result.file_size}`}
              </p>
            </div>
            <a
              href={result.external_url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-sm btn-primary"
            >
              Download
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}
