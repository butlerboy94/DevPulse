// Top nav bar shown on every page (mounted once in app/layout.tsx). Shows
// Analyze/History links plus either "Log in / Sign up" or the current
// username + "Log out", depending on auth state.
"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/store";

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);

  // Highlights whichever nav link matches the current page.
  const linkClass = (href: string) =>
    `text-sm font-medium transition-colors ${
      pathname === href ? "text-white" : "text-zinc-400 hover:text-white"
    }`;

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  return (
    <header className="border-b border-zinc-800 bg-zinc-950/80 backdrop-blur sticky top-0 z-10">
      <nav className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link href="/" className="font-bold text-white tracking-tight">
          Dev<span className="text-sky-400">Pulse</span>
        </Link>
        <div className="flex items-center gap-6">
          <Link href="/analyze" className={linkClass("/analyze")}>
            Analyze
          </Link>
          <Link href="/history" className={linkClass("/history")}>
            History
          </Link>
          {user ? (
            <div className="flex items-center gap-3">
              <span className="text-sm text-zinc-400">{user.username}</span>
              <button
                onClick={handleLogout}
                className="text-sm font-medium text-zinc-400 hover:text-white transition-colors"
              >
                Log out
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-4">
              <Link href="/login" className={linkClass("/login")}>
                Log in
              </Link>
              <Link
                href="/register"
                className="text-sm font-semibold bg-sky-500 hover:bg-sky-400 text-white px-3 py-1.5 rounded-md transition-colors"
              >
                Sign up
              </Link>
            </div>
          )}
        </div>
      </nav>
    </header>
  );
}
