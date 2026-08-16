import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // This project's agent instructions already live in the root CLAUDE.md —
  // disable Next.js 16's own generated AGENTS.md/CLAUDE.md so the two don't
  // conflict.
  agentRules: false,
};

export default nextConfig;
