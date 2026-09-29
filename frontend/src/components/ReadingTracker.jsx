import { useState, useEffect } from "react";
import { getReadingProgress, updateReadingProgress } from "../api/client";

const STATUS_OPTIONS = [
  { value: "want_to_read", label: "Want to Read" },
  { value: "reading", label: "Reading" },
  { value: "finished", label: "Finished" },
];

export default function ReadingTracker({ bookId, pageCount, onUpdate }) {
  const [progress, setProgress] = useState({
    current_page: 0,
    total_pages: pageCount || null,
    status: "want_to_read",
    percentage: 0,
  });
  const [currentPage, setCurrentPage] = useState(0);
  const [status, setStatus] = useState("want_to_read");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadProgress();
  }, [bookId]);

  // Update total_pages when pageCount prop changes
  useEffect(() => {
    setProgress((prev) => ({
      ...prev,
      total_pages: pageCount || null,
    }));
  }, [pageCount]);

  const loadProgress = async () => {
    try {
      const { data } = await getReadingProgress(bookId);
      setProgress(data);
      setCurrentPage(data.current_page || 0);
      setStatus(data.status || "want_to_read");
    } catch (err) {
      console.error("Failed to load progress:", err);
    }
  };

  const handlePageChange = async (e) => {
    const page = Math.max(0, parseInt(e.target.value) || 0);
    setCurrentPage(page);

    setSaving(true);
    try {
      const { data } = await updateReadingProgress(bookId, {
        current_page: page,
        total_pages: progress.total_pages,
      });
      setProgress(data);
      onUpdate?.(data);
    } catch (err) {
      console.error("Failed to save progress:", err);
    } finally {
      setSaving(false);
    }
  };

  const handleStatusChange = async (e) => {
    const newStatus = e.target.value;
    setStatus(newStatus);

    setSaving(true);
    try {
      const { data } = await updateReadingProgress(bookId, {
        status: newStatus,
        current_page: currentPage,
        total_pages: progress.total_pages,
      });
      setProgress(data);
      onUpdate?.(data);
    } catch (err) {
      console.error("Failed to update status:", err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="card bg-base-100 shadow-md p-6">
      <h3 className="font-bold text-lg mb-4">Reading Progress</h3>

      <div className="space-y-4">
        <div>
          <label className="label">
            <span className="label-text">Status</span>
          </label>
          <select
            className="select select-bordered w-full"
            value={status}
            onChange={handleStatusChange}
          >
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="label">
            <span className="label-text">
              Page {currentPage}
              {progress.total_pages ? ` of ${progress.total_pages}` : ""}
            </span>
          </label>
          <input
            type="number"
            className="input input-bordered w-full"
            min={0}
            max={progress.total_pages || undefined}
            value={currentPage}
            onChange={handlePageChange}
            placeholder="Current page"
            aria-label="Current page number"
          />
        </div>

        {progress.percentage > 0 && (
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span>Progress</span>
              <span>{progress.percentage}%</span>
            </div>
            <div className="progress progress-primary h-3">
              <div
                className="progress-bar transition-all"
                style={{ width: `${progress.percentage}%` }}
              ></div>
            </div>
          </div>
        )}

        {saving && <p className="text-xs text-base-content/50">Saving...</p>}
      </div>
    </div>
  );
}
