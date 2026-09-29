import { useState, useEffect } from "react";
import { getStats, getBooks } from "../api/client";

export default function StatsPage() {
  const [stats, setStats] = useState(null);
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsRes, booksRes] = await Promise.all([getStats(), getBooks()]);
      setStats(statsRes.data);
      setBooks(booksRes.data);
    } catch (err) {
      console.error("Failed to load stats:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      const [statsRes, booksRes] = await Promise.all([getStats(), getBooks()]);
      setStats(statsRes.data);
      setBooks(booksRes.data);
    } catch (err) {
      console.error("Failed to refresh stats:", err);
    } finally {
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    );
  }

  // Use backend-provided counts (authoritative)
  const statusCounts = {
    want_to_read: stats?.want_to_read || 0,
    reading: stats?.currently_reading || 0,
    finished: stats?.finished || 0,
  };

  const recentBooks = books.slice(0, 5);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Reading Stats</h1>
        <button className="btn btn-sm btn-ghost" onClick={handleRefresh} disabled={refreshing}>
          {refreshing ? <span className="loading loading-spinner loading-sm"></span> : "Refresh"}
        </button>
      </div>

      {/* Overview cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="card bg-base-100 shadow-md p-4 text-center">
          <p className="text-3xl font-bold text-primary">{stats?.total_books || 0}</p>
          <p className="text-sm text-base-content/60">Total Books</p>
        </div>
        <div className="card bg-base-100 shadow-md p-4 text-center">
          <p className="text-3xl font-bold text-secondary">{statusCounts.want_to_read}</p>
          <p className="text-sm text-base-content/60">Want to Read</p>
        </div>
        <div className="card bg-base-100 shadow-md p-4 text-center">
          <p className="text-3xl font-bold text-info">{statusCounts.reading}</p>
          <p className="text-sm text-base-content/60">Currently Reading</p>
        </div>
        <div className="card bg-base-100 shadow-md p-4 text-center">
          <p className="text-3xl font-bold text-success">{statusCounts.finished}</p>
          <p className="text-sm text-base-content/60">Finished</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Pages read */}
        <div className="card bg-base-100 shadow-md p-6">
          <h3 className="font-bold text-lg mb-2">Pages Read</h3>
          <p className="text-4xl font-bold text-primary">{stats?.total_pages_read?.toLocaleString() || 0}</p>
          <p className="text-sm text-base-content/60 mt-1">total pages tracked</p>
        </div>

        {/* Reading breakdown */}
        <div className="card bg-base-100 shadow-md p-6">
          <h3 className="font-bold text-lg mb-4">Library Breakdown</h3>
          <div className="space-y-3">
            {[
              { label: "Want to Read", count: statusCounts.want_to_read, color: "bg-secondary" },
              { label: "Reading", count: statusCounts.reading, color: "bg-info" },
              { label: "Finished", count: statusCounts.finished, color: "bg-success" },
            ].map((item) => (
              <div key={item.label}>
                <div className="flex justify-between text-sm mb-1">
                  <span>{item.label}</span>
                  <span>{item.count}</span>
                </div>
                <div className="progress h-2">
                  <div
                    className={`${item.color} h-full rounded`}
                    style={{
                      width: `${stats?.total_books ? (item.count / stats.total_books) * 100 : 0}%`,
                    }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent books */}
      {recentBooks.length > 0 && (
        <div className="mt-8">
          <h3 className="font-bold text-lg mb-4">Recently Added</h3>
          <div className="space-y-2">
            {recentBooks.map((book) => (
              <div key={book.id} className="card bg-base-100 shadow-sm p-3 flex items-center gap-3">
                {book.cover_url && (
                  <img src={book.cover_url} alt="" className="w-10 h-14 object-cover rounded" />
                )}
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{book.title}</p>
                  <p className="text-sm text-base-content/60 truncate">{book.author}</p>
                </div>
                <span className="badge badge-sm">{book.reading_status}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
