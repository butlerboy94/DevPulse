// ESLint's configuration file — the rulebook `npm run lint` (and the CI
// pipeline's Lint step) checks every file against. `eslint-config-next`
// ships Next.js's own recommended rules (React hooks correctness,
// accessibility checks, etc.) as a ready-made flat config array; this file
// just hands that straight to ESLint.
//
// Why this file exists at all: `next lint` (the command `npm run lint` was
// already calling before this session) has always needed a config file like
// this one to actually do anything, but no one had ever generated it — Next
// used to offer an interactive first-run wizard to create it, which never
// got run here. Without it, `next lint` failed immediately with an unrelated-
// looking "Invalid project directory" error instead of a helpful message.
import nextConfig from "eslint-config-next";

const eslintConfig = [...nextConfig];

export default eslintConfig;
