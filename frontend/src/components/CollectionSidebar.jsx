import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getCollections, createCollection, addToCollection } from "../api/client";

export default function CollectionSidebar({ onDragStart, onDragEnd }) {
  const [collections, setCollections] = useState([]);
  const [showNew, setShowNew] = useState(false);
  const [newName, setNewName] = useState("");

  const loadCollections = async () => {
    try {
      const { data } = await getCollections();
      setCollections(data);
    } catch (err) {
      console.error("Failed to load collections:", err);
    }
  };

  useEffect(() => {
    loadCollections();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newName.trim()) return;
    try {
      const { data } = await createCollection({ name: newName.trim() });
      setCollections([...collections, data]);
      setNewName("");
      setShowNew(false);
    } catch (err) {
      console.error("Failed to create collection:", err);
    }
  };

  const handleDropToCollection = async (e, collectionId) => {
    e.preventDefault();
    const bookId = e.dataTransfer.getData("text/plain");
    if (!bookId) return;
    try {
      await addToCollection(collectionId, parseInt(bookId));
      // Refresh collections to update book counts
      loadCollections();
      if (onDragEnd) onDragEnd();
    } catch (err) {
      console.error("Failed to add book to collection:", err);
    }
  };

  return (
    <div className="drawer lg:drawer-open">
      <input id="sidebar-toggle" type="checkbox" className="drawer-toggle" />
      <div className="drawer-content">
        <label htmlFor="sidebar-toggle" className="btn btn-primary lg:hidden fixed top-20 left-4 z-40">
          Collections
        </label>
      </div>
      <div className="drawer-side">
        <label htmlFor="sidebar-toggle" className="drawer-overlay"></label>
        <div className="menu p-4 w-72 min-h-full bg-base-100">
          <h2 className="text-lg font-bold mb-2">Collections</h2>

          <Link to="/" className="btn btn-ghost btn-block justify-start">
            All Books
          </Link>

          {collections.map((col) => (
            <div key={col.id} className="flex items-center gap-1">
              <Link
                to={`/collection/${col.id}`}
                className="btn btn-ghost btn-block justify-start flex-1"
              >
                <span className="truncate">{col.name}</span>
                <span className="badge badge-sm">{col.book_count}</span>
              </Link>
              <button
                className="btn btn-xs btn-ghost"
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => handleDropToCollection(e, col.id)}
                title="Drop book here"
              >
                +
              </button>
            </div>
          ))}

          {showNew ? (
            <form onSubmit={handleCreate} className="flex gap-1 mt-2">
              <input
                type="text"
                className="input input-xs flex-1"
                placeholder="Collection name"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                autoFocus
              />
              <button type="submit" className="btn btn-xs btn-primary">
                Add
              </button>
            </form>
          ) : (
            <button
              className="btn btn-xs btn-ghost mt-2"
              onClick={() => setShowNew(true)}
            >
              + New Collection
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
