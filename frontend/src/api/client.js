import axios from "axios";

// Use relative URL in production (served by Flask), or Vite proxy in dev
// For GitHub Pages: VITE_API_BASE_URL must be set to the backend URL
// For local dev: defaults to /api (proxied by Vite)
const baseURL = import.meta.env.VITE_API_BASE_URL || "/api";

const api = axios.create({
  baseURL,
  headers: { "Content-Type": "application/json" },
});

// Log API configuration in development
if (import.meta.env.DEV) {
  console.log("[API] Base URL:", baseURL);
}

// Auth token interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const register = (data) => api.post("/auth/register", data);
export const login = (data) => api.post("/auth/login", data);
export const getMe = () => api.get("/auth/me");
export const updateMe = (data) => api.put("/auth/me", data);

// Books
export const getBooks = (params = {}) => api.get("/books/", { params });
export const getBook = (id) => api.get(`/books/${id}`);
export const addBook = (data) => api.post("/books/", data);
export const addBookByIsbn = (isbn) => api.post(`/books/add-by-isbn/${isbn}`);
export const add_by_isbn = addBookByIsbn; // Alias for LoginPage
export const updateBook = (id, data) => api.put(`/books/${id}`, data);
export const deleteBook = (id) => api.delete(`/books/${id}`);
export const lookupIsbn = (isbn) => api.get(`/books/lookup/${isbn}`);
export const searchBooks = (q) => api.get("/books/search", { params: { q } });

// Collections
export const getCollections = () => api.get("/collections/");
export const getCollection = (id) => api.get(`/collections/${id}`);
export const createCollection = (data) => api.post("/collections/", data);
export const updateCollection = (id, data) => api.put(`/collections/${id}`, data);
export const deleteCollection = (id) => api.delete(`/collections/${id}`);
export const addToCollection = (collectionId, bookId) =>
  api.post(`/collections/${collectionId}/books`, { book_id: bookId });
export const removeFromCollection = (collectionId, bookId) =>
  api.delete(`/collections/${collectionId}/books/${bookId}`);
export const reorderCollection = (collectionId, bookIds) =>
  api.put(`/collections/${collectionId}/reorder`, { book_ids: bookIds });

// Ebooks
export const searchEbooks = (q) => api.get("/ebooks/search", { params: { q } });
export const getBookEbooks = (bookId) => api.get(`/ebooks/book/${bookId}`);
export const saveEbookSource = (bookId, data) => api.post(`/ebooks/book/${bookId}`, data);

// Reading
export const getReadingProgress = (bookId) => api.get(`/reading/${bookId}`);
export const updateReadingProgress = (bookId, data) => api.put(`/reading/${bookId}`, data);
export const getStats = () => api.get("/reading/stats");

// Social
export const getFriends = () => api.get("/social/friends");
export const getFriendRequests = () => api.get("/social/friends/requests");
export const sendFriendRequest = (email) => api.post("/social/friends/request", { email });
export const acceptFriendRequest = (requestId) => api.put(`/social/friends/accept/${requestId}`);
export const declineFriendRequest = (requestId) => api.put(`/social/friends/decline/${requestId}`);
export const removeFriend = (friendId) => api.delete(`/social/friends/${friendId}`);
export const searchUsers = (q) => api.get("/social/users/search", { params: { q } });
export const getUserProfile = (userId) => api.get(`/social/users/${userId}`);

// Messages
export const getConversations = () => api.get("/messages/conversations");
export const createConversation = (data) => api.post("/messages/conversations", data);
export const getMessages = (convId) => api.get(`/messages/conversations/${convId}/messages`);
export const sendMessage = (convId, content) =>
  api.post(`/messages/conversations/${convId}/messages`, { content });
export const addToGroup = (convId, userId) =>
  api.post(`/messages/conversations/${convId}/group/add`, { user_id: userId });
export const renameGroup = (convId, name) =>
  api.put(`/messages/conversations/${convId}/group/rename`, { name });
