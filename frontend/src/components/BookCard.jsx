import { Link } from "react-router-dom";

const statusColors = {
  want_to_read: "badge-secondary",
  reading: "badge-primary",
  finished: "badge-success",
};

const statusLabels = {
  want_to_read: "Want to Read",
  reading: "Reading",
  finished: "Finished",
};

export default function BookCard({ book, draggable, onDragStart, onDragEnd }) {
  return (
    <div
      className="card bg-base-100 shadow-md hover:shadow-xl transition-shadow"
      draggable={draggable}
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
    >
      <Link to={`/book/${book.id}`}>
        <figure className="h-56 overflow-hidden bg-base-300">
          {book.cover_url ? (
            <img src={book.cover_url} alt={book.title} className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-base-content/40">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
          )}
        </figure>
      </Link>
      <div className="card-body p-4">
        <Link to={`/book/${book.id}`}>
          <h2 className="card-title text-base line-clamp-2 hover:text-primary transition-colors">
            {book.title}
          </h2>
        </Link>
        <p className="text-sm text-base-content/70">{book.author}</p>
        {book.page_count && (
          <p className="text-xs text-base-content/50">{book.page_count} pages</p>
        )}
        <div className="flex gap-1 mt-2 flex-wrap">
          <span className={`badge badge-sm ${statusColors[book.reading_status] || "badge-secondary"}`}>
            {statusLabels[book.reading_status] || "Want to Read"}
          </span>
        </div>
        {book.reading_percentage > 0 && (
          <div className="flex items-center gap-2 mt-2">
            <div className="progress progress-primary h-1.5 flex-1">
              <div className="progress-bar" style={{ width: `${book.reading_percentage}%` }}></div>
            </div>
            <span className="text-xs text-base-content/50">{book.reading_percentage}%</span>
          </div>
        )}
      </div>
    </div>
  );
}
