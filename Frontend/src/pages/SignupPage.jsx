import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { HeartPulseIcon } from "lucide-react";
import { signup } from "../api/auth";
import useStore from "../store";

export default function SignupPage() {
  const navigate = useNavigate();
  const setAuth = useStore((s) => s.setAuth);

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    displayName: "",
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const update = (key) => (e) =>
    setForm((f) => ({ ...f, [key]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (form.password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    setLoading(true);
    try {
      const data = await signup(form);
      setAuth({ token: data.access_token, user: data.user });
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message || "Signup failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-dvh items-center justify-center bg-zinc-950 px-4 py-8">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-12 h-12 rounded-2xl bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center mb-4">
            <HeartPulseIcon size={22} className="text-indigo-400" />
          </div>
          <h1 className="text-zinc-100 text-xl font-semibold tracking-tight">
            MindfulChat
          </h1>
          <p className="text-zinc-500 text-sm mt-1">Create your account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-zinc-400 text-xs mb-1.5">
              Username
            </label>
            <input
              type="text"
              required
              minLength={3}
              maxLength={50}
              pattern="^[a-zA-Z0-9_]+$"
              value={form.username}
              onChange={update("username")}
              placeholder="your_username"
              className="w-full bg-zinc-900 border border-zinc-700 rounded-xl px-3.5 py-2.5 text-zinc-100 placeholder-zinc-600 text-sm outline-none focus:border-indigo-500/70 transition-colors"
            />
            <p className="text-zinc-600 text-xs mt-1">
              Letters, numbers, and underscores only.
            </p>
          </div>

          <div>
            <label className="block text-zinc-400 text-xs mb-1.5">Email</label>
            <input
              type="email"
              required
              value={form.email}
              onChange={update("email")}
              placeholder="you@example.com"
              className="w-full bg-zinc-900 border border-zinc-700 rounded-xl px-3.5 py-2.5 text-zinc-100 placeholder-zinc-600 text-sm outline-none focus:border-indigo-500/70 transition-colors"
            />
          </div>

          <div>
            <label className="block text-zinc-400 text-xs mb-1.5">
              Password
            </label>
            <input
              type="password"
              required
              minLength={8}
              value={form.password}
              onChange={update("password")}
              placeholder="Min. 8 characters"
              className="w-full bg-zinc-900 border border-zinc-700 rounded-xl px-3.5 py-2.5 text-zinc-100 placeholder-zinc-600 text-sm outline-none focus:border-indigo-500/70 transition-colors"
            />
          </div>

          <div>
            <label className="block text-zinc-400 text-xs mb-1.5">
              Display Name <span className="text-zinc-600">(optional)</span>
            </label>
            <input
              type="text"
              maxLength={255}
              value={form.displayName}
              onChange={update("displayName")}
              placeholder="How should we call you?"
              className="w-full bg-zinc-900 border border-zinc-700 rounded-xl px-3.5 py-2.5 text-zinc-100 placeholder-zinc-600 text-sm outline-none focus:border-indigo-500/70 transition-colors"
            />
          </div>

          {error && (
            <p className="text-red-400 text-xs bg-red-950/30 border border-red-800/40 rounded-lg px-3 py-2">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-zinc-700 disabled:text-zinc-500 text-white text-sm font-semibold rounded-xl transition-all"
          >
            {loading ? "Creating account…" : "Create Account"}
          </button>
        </form>

        <p className="text-center text-zinc-600 text-xs mt-6">
          Already have an account?{" "}
          <Link
            to="/login"
            className="text-indigo-400 hover:text-indigo-300 transition-colors"
          >
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
