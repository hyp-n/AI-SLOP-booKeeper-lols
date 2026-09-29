import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { login, register, addBookByIsbn } from "../api/client";
import CameraScanner from "../components/CameraScanner";

export default function LoginPage() {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showCameraScanner, setShowCameraScanner] = useState(false);

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
