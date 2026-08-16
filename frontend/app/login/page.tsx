// Login page ("/login") — email/password form that calls POST /auth/login
// and, on success, saves the session and redirects into /analyze.
"use client";

import { useState } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { loginUser } from "@/lib/api";
import { useAuthStore } from "@/lib/store";

export default function LoginPage() {
  const router = useRouter();
  const setSession = useAuthStore((s) => s.setSession);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const token = await loginUser(email, password);
      // The login endpoint only returns a token, not the user profile, so we
      // derive a display name locally rather than adding a /me round trip.
      setSession(token.access_token, { id: 0, email, username: email.split("@")[0], created_at: "" });
      router.push("/analyze");
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.data?.detail) {
        setError(String(err.response.data.detail));
      } else {
        setError("Login failed. Check your credentials and try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="max-w-sm mx-auto px-4 py-16">
      <h1 className="text-2xl font-bold text-white mb-6">Log in</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm text-zinc-400 mb-1">Email</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full bg-zinc-900 text-zinc-200 text-sm rounded-md px-3 py-2 border border-zinc-700 focus:outline-none focus:ring-1 focus:ring-sky-500"
          />
        </div>
        <div>
          <label className="block text-sm text-zinc-400 mb-1">Password</label>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full bg-zinc-900 text-zinc-200 text-sm rounded-md px-3 py-2 border border-zinc-700 focus:outline-none focus:ring-1 focus:ring-sky-500"
          />
        </div>
        {error && <p className="text-sm text-[#e66767]">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-sky-500 hover:bg-sky-400 disabled:bg-zinc-700 text-white font-semibold py-2 rounded-lg transition-colors"
        >
          {loading ? "Logging in…" : "Log in"}
        </button>
      </form>
      <p className="text-sm text-zinc-500 mt-4">
        Don&apos;t have an account?{" "}
        <Link href="/register" className="text-sky-400 hover:underline">
          Sign up
        </Link>
      </p>
    </main>
  );
}
