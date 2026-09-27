import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useState, useEffect, Component } from "react";
import Navbar from "./components/Navbar";
import LibraryPage from "./pages/LibraryPage";
import CollectionPage from "./pages/CollectionPage";
import BookDetailPage from "./pages/BookDetailPage";
import StatsPage from "./pages/StatsPage";
import LoginPage from "./pages/LoginPage";
import ProfilePage from "./pages/ProfilePage";
import FriendsPage from "./pages/FriendsPage";
import ChatPage from "./pages/ChatPage";

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("React error boundary caught:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-base-200 flex items-center justify-center">
          <div className="card bg-base-100 shadow-md p-8 max-w-md text-center">
            <h2 className="text-xl font-bold text-error mb-2">Something went wrong</h2>
            <p className="text-base-content/60 mb-4">
              {this.state.error?.message || "An unexpected error occurred"}
            </p>
            <button
              className="btn btn-primary"
              onClick={() => {
                this.setState({ hasError: false, error: null });
                window.location.reload();
              }}
            >
              Reload
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

function PrivateRoute({ children }) {
  const token = localStorage.getItem("token");
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default function App() {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem("theme") || "retro";
  });

  const toggleTheme = () => {
    setTheme((prev) => (prev === "retro" ? "luxury" : "retro"));
  };

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  return (
    <BrowserRouter>
      <ErrorBoundary>
        <div className="min-h-screen bg-base-200">
          <Navbar theme={theme} toggleTheme={toggleTheme} />
          <main className="container mx-auto px-4 py-6">
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/" element={<PrivateRoute><LibraryPage /></PrivateRoute>} />
              <Route path="/collection/:id" element={<PrivateRoute><CollectionPage /></PrivateRoute>} />
              <Route path="/book/:id" element={<PrivateRoute><BookDetailPage /></PrivateRoute>} />
              <Route path="/stats" element={<PrivateRoute><StatsPage /></PrivateRoute>} />
              <Route path="/profile/:userId" element={<PrivateRoute><ProfilePage /></PrivateRoute>} />
              <Route path="/friends" element={<PrivateRoute><FriendsPage /></PrivateRoute>} />
              <Route path="/chat/:convId" element={<PrivateRoute><ChatPage /></PrivateRoute>} />
              <Route path="/chat" element={<PrivateRoute><ChatPage /></PrivateRoute>} />
            </Routes>
          </main>
        </div>
      </ErrorBoundary>
    </BrowserRouter>
  );
}
