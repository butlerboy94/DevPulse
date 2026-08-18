// Top nav bar shown on every page (mounted once in app/layout.tsx). Shows
// Analyze/History links plus either "Log in / Sign up" or the current
// username + "Log out", depending on auth state.
//
// Below the "sm" breakpoint (roughly phone-width screens, under 640px) the
// links don't fit in one row next to the logo, so they collapse behind a
// hamburger button instead — the same pattern as almost every mobile site:
// tap the three lines, a panel drops down with the same links stacked
// vertically. `sm:hidden` / `hidden sm:flex` is what does the swapping: two
// versions of the same links exist in the markup, and Tailwind's responsive
// prefixes show exactly one of them depending on screen width.
"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/store";

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const [menuOpen, setMenuOpen] = useState(false);

  // Highlights whichever nav link matches the current page.
  const linkClass = (href: string) =>
    `text-sm font-medium transition-colors ${
      pathname === href ? "text-white" : "text-zinc-400 hover:text-white"
    }`;

  const handleLogout = () => {
    logout();
    setMenuOpen(false);
    router.push("/");
  };

  // Auth links/buttons — rendered twice below (desktop row, mobile panel)
  // since they need different spacing/sizing in each layout.
  const authLinks = user ? (
    <>
      <span className="text-sm text-zinc-400">{user.username}</span>
      <button
        onClick={handleLogout}
        className="text-sm font-medium text-zinc-400 hover:text-white transition-colors"
      >
        Log out
      </button>
    </>
  ) : (
    <>
      <Link href="/login" className={linkClass("/login")} onClick={() => setMenuOpen(false)}>
        Log in
      </Link>
      <Link
        href="/register"
        onClick={() => setMenuOpen(false)}
        className="text-sm font-semibold bg-sky-500 hover:bg-sky-400 text-white px-3 py-1.5 rounded-md transition-colors text-center"
      >
        Sign up
      </Link>
    </>
  );

  return (
    <header className="border-b border-zinc-800 bg-zinc-950/80 backdrop-blur sticky top-0 z-10">
      <nav className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link href="/" className="font-bold text-white tracking-tight" onClick={() => setMenuOpen(false)}>
          Dev<span className="text-sky-400">Pulse</span>
        </Link>

        {/* Full link row — only shown at "sm" width and up */}
        <div className="hidden sm:flex items-center gap-6">
          <Link href="/analyze" className={linkClass("/analyze")}>
            Analyze
          </Link>
          <Link href="/history" className={linkClass("/history")}>
            History
          </Link>
          <div className="flex items-center gap-4">{authLinks}</div>
        </div>

        {/* Hamburger button — only shown below "sm" width */}
        <button
          type="button"
          onClick={() => setMenuOpen((open) => !open)}
          aria-label={menuOpen ? "Close menu" : "Open menu"}
          aria-expanded={menuOpen}
          className="sm:hidden p-2 -mr-2 text-zinc-400 hover:text-white transition-colors"
        >
          {/* Three lines when closed, an X when open — a single small SVG
              covers both so no icon library is needed for one glyph. */}
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            {menuOpen ? (
              <path strokeLinecap="round" d="M6 6l12 12M18 6L6 18" />
            ) : (
              <path strokeLinecap="round" d="M4 7h16M4 12h16M4 17h16" />
            )}
          </svg>
        </button>
      </nav>

      {/* Dropdown panel — only rendered (and only reachable below "sm"
          width) while the hamburger button is toggled open */}
      {menuOpen && (
        <div className="sm:hidden border-t border-zinc-800 px-4 py-3 flex flex-col gap-3">
          <Link href="/analyze" className={linkClass("/analyze")} onClick={() => setMenuOpen(false)}>
            Analyze
          </Link>
          <Link href="/history" className={linkClass("/history")} onClick={() => setMenuOpen(false)}>
            History
          </Link>
          <div className="flex flex-col gap-3 pt-2 border-t border-zinc-800/60">{authLinks}</div>
        </div>
      )}
    </header>
  );
}
