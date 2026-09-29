import { useState, useEffect } from "react";
import { useNavigate, Link, useSearchParams } from "react-router-dom";
import { login, register, addBookByIsbn } from "../api/client";
import CameraScanner from "../components/CameraScanner";

export default function LoginPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showCameraScanner, setShowCameraScanner] = useState(false);

  // Handle OAuth token redirect from backend
  useEffect(() => {
    const token = searchParams.get("token");
    if (token) {
      localStorage.setItem("token", token);
      // Fetch user info
      fetch("/api/auth/me", {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => res.json())
        .then((user) => {
          localStorage.setItem("user", JSON.stringify(user));
          navigate("/");
        })
        .catch(() => {
          localStorage.removeItem("token");
          setError("Failed to complete Google sign-in");
        });
    }
  }, [searchParams, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const { data } = isLogin
        ? await login({ email, password })
        : await register({ email, password, name });

      localStorage.setItem("token", data.token);
      localStorage.setItem("user", JSON.stringify(data.user));
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.error || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const handleCameraScan = async () => {
    setError("");
    setShowCameraScanner(true);
  };

  const handleScanComplete = async (isbn) => {
    setShowCameraScanner(false);
    setError("");

    try {
      setLoading(true);
      const { data } = await addBookByIsbn(isbn);
      navigate("/"); // Redirect to library with the new book
    } catch (err) {
      setError(err.response?.data?.error || "Failed to add book from ISBN");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-base-200">
      <div className="card bg-base-100 shadow-xl w-full max-w-md">
        <div className="card-body">
          <h1 className="text-3xl font-bold text-center mb-2">booKeeper</h1>
          <p className="text-center text-base-content/60 mb-6">
            {isLogin ? "Welcome back" : "Create your account"}
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <div>
                <label className="label">
                  <span className="label-text">Name</span>
                </label>
                <input
                  type="text"
                  className="input input-bordered w-full"
                  placeholder="Your name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>
            )}

            <div>
              <label className="label">
                <span className="label-text">Email</span>
              </label>
              <input
                type="email"
                className="input input-bordered w-full"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="label">
                <span className="label-text">Password</span>
              </label>
              <input
                type="password"
                className="input input-bordered w-full"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
              />
            </div>

            {error && (
              <div className="alert alert-error">
                <span>{error}</span>
              </div>
            )}

            <button type="submit" className="btn btn-primary w-full" disabled={loading}>
              {loading ? <span className="loading loading-spinner loading-sm"></span> : null}
              {isLogin ? "Login" : "Register"}
            </button>

            <div className="divider text-xs text-base-content/50">OR</div>

            <a
              href="/api/auth/google/login"
              className="btn btn-outline w-full"
            >
              <svg className="h-5 w-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
              </svg>
              Sign in with Google
            </a>

            <div className="divider text-xs text-base-content/50">OR</div>

            <button
              type="button"
              onClick={handleCameraScan}
              className="btn btn-outline w-full"
              disabled={loading}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.464.59l.775 4.58a2 2 0 01-.684 2.175L9.79 20.21A2.194 2.194 0 0012 21v-7h6.79a2 2 0 011.464-.59l.775-4.58a2 2 0 00-.684-2.175L15.07 5.59A2 2 0 0016.93 3H9a2 2 0 00-1.464.59L3 9z" />
              </svg>
              {loading ? "Scanning..." : "Scan ISBN with Camera"}
            </button>
          </form>

          <div className="text-center mt-4">
            <button
              className="link link-hover text-sm"
              onClick={() => setIsLogin(!isLogin)}
            >
              {isLogin ? "Need an account? Register" : "Have an account? Login"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
