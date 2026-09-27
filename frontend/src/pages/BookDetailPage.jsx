import { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { getBook, deleteBook, updateBook } from "../api/client";
import ReadingTracker from "../components/ReadingTracker";
import EbookSearch from "../components/EbookSearch";

export default function BookDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [book, setBook] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState({});

  useEffect(() => {
    loadBook();
  }, [id]);

  const loadBook = async () => {
    setLoading(true);
    try {
      const { data } = await getBook(id);
      setBook(data);
      setEditForm({
        title: data.title,
        author: data.author || "",
        description: data.description || "",
        page_count: data.page_count || "",
      });
    } catch (err) {
      console.error("Failed to load book:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("Remove this book from your library?")) return;
    try {
      await deleteBook(id);
      navigate("/");
    } catch (err) {
      console.error("Failed to delete book:", err);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      const { data } = await updateBook(id, editForm);
      setBook(data);
      setEditing(false);
    } catch (err) {
      console.error("Failed to update book:", err);
    }
  };

  const handleReadingUpdate = (progress) => {
    setBook({ ...book, reading_status: progress.status, reading_percentage: progress.percentage });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    );
  }

  if (!book) {
    return (
      <div className="text-center py-16">
        <p className="text-lg">Book not found</p>
        <Link to="/" className="btn btn-primary mt-4">Back to Library</Link>
      </div>
    );
  }

  return (
    <div>
      <Link to="/" className="btn btn-sm btn-ghost mb-4">
        &larr; Back to Library
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left column: Cover + Actions */}
        <div className="lg:col-span-1">
          <div className="card bg-base-100 shadow-md">
            <figure className="p-4">
              {book.cover_url ? (
                <img src={book.cover_url} alt={book.title} className="w-full rounded shadow-lg" />
              ) : (
                <div className="w-full h-64 flex items-center justify-center bg-base-300 rounded">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-24 w-24 text-base-content/30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
              )}
            </figure>
          </div>

          <div className="flex gap-2 mt-4">
            <button className="btn btn-primary btn-sm flex-1" onClick={() => setEditing(true)}>
              Edit
            </button>
            <button className="btn btn-error btn-sm btn-outline flex-1" onClick={handleDelete}>
              Delete
            </button>
          </div>
        </div>

        {/* Right column: Details + Tools */}
        <div className="lg:col-span-2 space-y-6">
          {/* Book info */}
          <div className="card bg-base-100 shadow-md p-6">
            {editing ? (
              <form onSubmit={handleSave} className="space-y-4">
                <div>
                  <label className="label"><span className="label-text">Title</span></label>
                  <input
                    type="text"
                    className="input input-bordered w-full"
                    value={editForm.title}
                    onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                  />
                </div>
                <div>
                  <label className="label"><span className="label-text">Author</span></label>
                  <input
                    type="text"
                    className="input input-bordered w-full"
                    value={editForm.author}
                    onChange={(e) => setEditForm({ ...editForm, author: e.target.value })}
                  />
                </div>
                <div>
                  <label className="label"><span className="label-text">Description</span></label>
                  <textarea
                    className="textarea textarea-bordered w-full"
                    rows={3}
                    value={editForm.description}
                    onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                  />
                </div>
                <div>
                  <label className="label"><span className="label-text">Page Count</span></label>
                  <input
                    type="number"
                    className="input input-bordered w-full"
                    value={editForm.page_count}
                    onChange={(e) => setEditForm({ ...editForm, page_count: parseInt(e.target.value) || null })}
                  />
                </div>
                <div className="flex gap-2">
                  <button type="submit" className="btn btn-primary btn-sm">Save</button>
                  <button type="button" className="btn btn-ghost btn-sm" onClick={() => setEditing(false)}>
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              <>
                <h1 className="text-2xl font-bold mb-2">{book.title}</h1>
                <p className="text-lg text-base-content/70 mb-4">{book.author}</p>

                <div className="flex flex-wrap gap-4 text-sm text-base-content/60 mb-4">
                  {book.publisher && <span>{book.publisher}</span>}
                  {book.published_date && <span>{book.published_date}</span>}
                  {book.page_count && <span>{book.page_count} pages</span>}
                  {book.isbn && <span>ISBN: {book.isbn}</span>}
                  {book.language && <span>Language: {book.language}</span>}
                </div>

                {book.description && (
                  <div className="prose max-w-none">
                    <p className="text-sm whitespace-pre-wrap">{book.description}</p>
                  </div>
                )}
              </>
            )}
          </div>

          {/* Reading Tracker */}
          <ReadingTracker
            bookId={book.id}
            pageCount={book.page_count}
            onUpdate={handleReadingUpdate}
          />

          {/* Ebook Download */}
          <EbookSearch bookTitle={book.title} bookIsbn={book.isbn} />
        </div>
      </div>
    </div>
  );
}
