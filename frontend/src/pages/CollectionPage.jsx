import { useState, useEffect, useCallback } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import {
  getCollection,
  getBooks,
  addToCollection,
  removeFromCollection,
  reorderCollection,
  deleteCollection,
} from "../api/client";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  useSortable,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

function SortableBook({ book, onRemove }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: book.id,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="card bg-base-100 shadow-sm p-3 flex items-center gap-3"
    >
      <button className="btn btn-xs btn-ghost cursor-grab" {...attributes} {...listeners}>
        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path d="M7 2a2 2 0 1 0 .001 4.001A2 2 0 0 0 7 2zm0 6a2 2 0 1 0 .001 4.001A2 2 0 0 0 7 8zm0 6a2 2 0 1 0 .001 4.001A2 2 0 0 0 7 14zm6-8a2 2 0 1 0-.001-4.001A2 2 0 0 0 13 6zm0 2a2 2 0 1 0 .001 4.001A2 2 0 0 0 13 8zm0 6a2 2 0 1 0 .001 4.001A2 2 0 0 0 13 14z" />
        </svg>
      </button>
      {book.cover_url && (
        <img src={book.cover_url} alt="" className="w-10 h-14 object-cover rounded" />
      )}
      <div className="flex-1 min-w-0">
        <Link to={`/book/${book.id}`} className="font-medium text-sm truncate hover:text-primary">
          {book.title}
        </Link>
        <p className="text-xs text-base-content/60 truncate">{book.author}</p>
      </div>
      <button className="btn btn-xs btn-ghost" onClick={() => onRemove(book.id)} disabled={actionLoading}>
        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      </button>
    </div>
  );
}

export default function CollectionPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [collection, setCollection] = useState(null);
  const [allBooks, setAllBooks] = useState([]);
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [showAddBook, setShowAddBook] = useState(false);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const loadCollection = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await getCollection(id);
      setCollection(data);
      setBooks(data.books || []);
    } catch (err) {
      console.error("Failed to load collection:", err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  const loadAllBooks = async () => {
    try {
      const { data } = await getBooks();
      setAllBooks(data);
    } catch (err) {
      console.error("Failed to load books:", err);
    }
  };

  useEffect(() => {
    loadCollection();
    loadAllBooks();
  }, [loadCollection]);

  const handleDragEnd = async (event) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;

    const oldIndex = books.findIndex((b) => b.id === active.id);
    const newIndex = books.findIndex((b) => b.id === over.id);

    const newOrder = arrayMove(books, oldIndex, newIndex);
    setBooks(newOrder);

    // Persist new order
    try {
      await reorderCollection(id, newOrder.map((b) => b.id));
    } catch (err) {
      console.error("Failed to save order:", err);
    }
  };

  const handleAddBook = async (bookId) => {
    setActionLoading(true);
    try {
      await addToCollection(id, bookId);
      const book = allBooks.find((b) => b.id === bookId);
      if (book) setBooks([...books, book]);
      setShowAddBook(false);
    } catch (err) {
      console.error("Failed to add book:", err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleRemoveBook = async (bookId) => {
    setActionLoading(true);
    try {
      await removeFromCollection(id, bookId);
      setBooks(books.filter((b) => b.id !== bookId));
    } catch (err) {
      console.error("Failed to remove book:", err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteCollection = async () => {
    if (!confirm("Delete this collection? Books will stay in your library.")) return;
    setActionLoading(true);
    try {
      await deleteCollection(id);
      navigate("/");
    } catch (err) {
      console.error("Failed to delete collection:", err);
    } finally {
      setActionLoading(false);
    }
  };

  const availableBooks = allBooks.filter(
    (b) => !books.find((cb) => cb.id === b.id)
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    );
  }

  if (!collection) {
    return (
      <div className="text-center py-16">
        <p className="text-lg">Collection not found</p>
        <Link to="/" className="btn btn-primary mt-4">Back to Library</Link>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="flex flex-wrap items-center gap-4 mb-6">
        <div className="flex-1">
          <h1 className="text-2xl font-bold">{collection.name}</h1>
          {collection.description && (
            <p className="text-base-content/60">{collection.description}</p>
          )}
        </div>
        <button className="btn btn-sm btn-ghost text-error" onClick={handleDeleteCollection} disabled={actionLoading}>
          Delete Collection
        </button>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Books list */}
        <div className="flex-1">
          {books.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-base-content/50">No books in this collection yet</p>
              <button className="btn btn-primary btn-sm mt-4" onClick={() => setShowAddBook(true)}>
                Add Books
              </button>
            </div>
          ) : (
            <>
              <div className="flex justify-between items-center mb-4">
                <p className="text-sm text-base-content/50">
                  {books.length} book{books.length !== 1 ? "s" : ""}
                </p>
                <button className="btn btn-sm btn-primary" onClick={() => setShowAddBook(true)}>
                  + Add Books
                </button>
              </div>

              <DndContext
                sensors={sensors}
                collisionDetection={closestCenter}
                onDragEnd={handleDragEnd}
              >
                <SortableContext
                  items={books.map((b) => b.id)}
                  strategy={verticalListSortingStrategy}
                >
                  <div className="space-y-2">
                    {books.map((book) => (
                      <SortableBook key={book.id} book={book} onRemove={handleRemoveBook} />
                    ))}
                  </div>
                </SortableContext>
              </DndContext>
            </>
          )}
        </div>

        {/* Add book sidebar */}
        {showAddBook && (
          <div className="lg:w-80">
            <div className="card bg-base-100 shadow-md p-4 sticky top-20">
              <h3 className="font-bold mb-3">Add Books to Collection</h3>
              {availableBooks.length === 0 ? (
                <p className="text-sm text-base-content/50">All books are already in this collection</p>
              ) : (
                <div className="max-h-96 overflow-y-auto space-y-2">
                  {availableBooks.map((book) => (
                    <div key={book.id} className="flex items-center gap-2 p-2 rounded bg-base-200">
                      {book.cover_url && (
                        <img src={book.cover_url} alt="" className="w-8 h-10 object-cover rounded" />
                      )}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm truncate">{book.title}</p>
                      </div>
                      <button
                        className="btn btn-xs btn-primary"
                        onClick={() => handleAddBook(book.id)}
                        disabled={actionLoading}
                      >
                        Add
                      </button>
                    </div>
                  ))}
                </div>
              )}
              <button className="btn btn-ghost btn-sm mt-3" onClick={() => setShowAddBook(false)}>
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
