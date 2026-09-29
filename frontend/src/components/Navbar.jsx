import { Link, useLocation, useNavigate } from "react-router-dom";

export default function Navbar({ theme, toggleTheme }) {
  const location = useLocation();
  const navigate = useNavigate();
  const isLoggedIn = !!localStorage.getItem("token");

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/login");
  };

  return (
    <div className="navbar bg-base-100 shadow-lg sticky top-0 z-50">
      <div className="flex-1">
        <Link to="/" className="btn btn-ghost text-xl font-bold">
          booKeeper
        </Link>
      </div>

      <div className="flex-none gap-2">
        {isLoggedIn ? (
          <>
            <Link
              to="/"
              className={`btn btn-sm ${location.pathname === "/" ? "btn-primary" : "btn-ghost"}`}
            >
              Library
            </Link>
            <Link
              to="/friends"
              className={`btn btn-sm ${location.pathname === "/friends" ? "btn-primary" : "btn-ghost"}`}
            >
              Friends
            </Link>
            <Link
              to="/collections"
              className={`btn btn-sm ${location.pathname.startsWith("/collection") ? "btn-primary" : "btn-ghost"}`}
            >
              Collections
            </Link>
            <Link
              to="/chat"
              className={`btn btn-sm ${location.pathname.startsWith("/chat") ? "btn-primary" : "btn-ghost"}`}
            >
              Messages
            </Link>
            <Link
              to="/stats"
              className={`btn btn-sm ${location.pathname === "/stats" ? "btn-primary" : "btn-ghost"}`}
            >
              Stats
            </Link>

            <button
              className="btn btn-sm btn-ghost btn-circle"
              onClick={toggleTheme}
              title="Toggle theme"
            >
              {theme === "luxury" ? (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                </svg>
              )}
            </button>

            <button className="btn btn-sm btn-ghost" onClick={handleLogout}>
              Logout
            </button>
          </>
        ) : (
          <Link to="/login" className="btn btn-sm btn-primary">
            Login
          </Link>
        )}
      </div>
    </div>
  );
}
