// Registration page ("/register") — sign-up form that calls POST
// /auth/register, then immediately logs the new user in and redirects to
// /analyze so they land straight in the product.
"use client";

import { useState } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { registerUser, loginUser } from "@/lib/api";
import { useAuthStore } from "@/lib/store";

export default function RegisterPage() {
  const router = useRouter();
  const setSession = useAuthStore((s) => s.setSession);
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const user = await registerUser({ email, username, password });
      const token = await loginUser(email, password);
      setSession(token.access_token, user);
      router.push("/analyze");
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.data?.detail) {
        setError(String(err.response.data.detail));
      } else {
        setError("Registration failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="max-w-sm mx-auto px-4 py-16">
      <h1 className="text-2xl font-bold text-white mb-6">Create an account</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm text-zinc-400 mb-1">Username</label>
          <input
            type="text"
            required
            minLength={3}
            maxLength={50}
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full bg-zinc-900 text-zinc-200 text-sm rounded-md px-3 py-2 border border-zinc-700 focus:outline-none focus:ring-1 focus:ring-sky-500"
          />
        </div>
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
            minLength={8}
            maxLength={128}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full bg-zinc-900 text-zinc-200 text-sm rounded-md px-3 py-2 border border-zinc-700 focus:outline-none focus:ring-1 focus:ring-sky-500"
          />
          <p className="text-xs text-zinc-500 mt-1">At least 8 characters.</p>
        </div>
        {error && <p className="text-sm text-[#e66767]">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-sky-500 hover:bg-sky-400 disabled:bg-zinc-700 text-white font-semibold py-2 rounded-lg transition-colors"
        >
          {loading ? "Creating account…" : "Sign up"}
        </button>
      </form>
      <p className="text-sm text-zinc-500 mt-4">
        Already have an account?{" "}
        <Link href="/login" className="text-sky-400 hover:underline">
          Log in
        </Link>
      </p>
    </main>
  );
}
