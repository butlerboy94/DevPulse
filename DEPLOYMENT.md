# Deploying DevPulse

This is the step-by-step runbook for taking DevPulse from "runs on my
machine" to a real, public URL. It's written so this can be followed in a
single sitting without needing to remember anything from earlier sessions.

Nothing in this file can be done by an AI assistant on its own — every step
below needs your own Vercel and Railway accounts and your own login, so this
is a guide for *you* (optionally with an assistant sitting alongside you
following along) rather than something that runs unattended.

Rough order of operations, and why it's this order: the backend and its
database need to exist and be reachable on the internet *before* the
frontend is told where to find them, so backend-first avoids a chicken-and-
egg problem where the frontend has nothing to talk to yet.

---

## 0. Before you start

You'll need, free-tier is fine for all of these:
- A [Railway](https://railway.app) account (backend + Postgres + Redis)
- A [Vercel](https://vercel.com) account (frontend)
- An [Anthropic API key](https://console.anthropic.com) if you want AI
  recommendations live (optional — the app works without one, it just skips
  that section of the report)
- This repo pushed to GitHub (already done)

Generate a real production JWT secret now — this is the key that signs
every login token, so it needs to be long, random, and different from the
placeholder in `.env.example`. Run this once and save the output somewhere
safe (a password manager, not a text file in the repo):

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 1. Backend + database on Railway

1. **New Project → Deploy from GitHub repo**, pick this repository.
2. Railway will find `backend/Dockerfile` — point the service's **root
   directory** at `backend/` so it builds that Dockerfile specifically
   (not the whole monorepo).
3. **Add a Postgres database** (Railway's "+ New" → Database → PostgreSQL)
   to the same project. Railway automatically creates a `DATABASE_URL`
   variable — reference it in the backend service's variables as
   `${{Postgres.DATABASE_URL}}` rather than copy-pasting the value, so it
   stays correct if Railway ever rotates it.
4. **Add a Redis instance** the same way, if you want caching (optional
   today — the app runs fine without it, Redis isn't wired into the
   analysis pipeline yet).
5. Set the backend service's environment variables:
   | Variable | Value |
   |---|---|
   | `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` |
   | `JWT_SECRET_KEY` | the value you generated in step 0 |
   | `JWT_ALGORITHM` | `HS256` |
   | `ANTHROPIC_API_KEY` | your key, or leave unset to skip AI recommendations |
   | `ALLOWED_ORIGINS` | leave unset for now — you'll come back and set this in step 3, once you know the Vercel URL |
6. Deploy. Once it's up, Railway gives you a public URL like
   `https://devpulse-backend-production.up.railway.app`. Confirm it's alive
   by visiting `<that URL>/docs` — you should see the Swagger UI.
7. **Run the database migrations** against the new production database —
   the app's tables don't exist until this runs. From your own machine,
   with `DATABASE_URL` set to the same Postgres connection string Railway
   is using (copy it from the Postgres service's "Connect" tab):
   ```bash
   cd backend
   DATABASE_URL="<railway postgres url>" python -m alembic upgrade head
   ```

---

## 2. Frontend on Vercel

1. **Add New Project → Import** this GitHub repo.
2. Set the project's **root directory** to `frontend/` (same reasoning as
   the Railway root-directory step — this is a monorepo, so Vercel needs to
   be told which subfolder is the actual Next.js app).
3. Set one environment variable:
   | Variable | Value |
   |---|---|
   | `NEXT_PUBLIC_API_URL` | the Railway backend URL from step 1.6 |
4. Deploy. Vercel gives you a URL like `https://devpulse.vercel.app`.

---

## 3. Close the loop: tell the backend about the frontend

Browsers block a webpage from calling an API on a different domain unless
that API explicitly allows it (CORS). Go back to the Railway backend
service's variables and set:

| Variable | Value |
|---|---|
| `ALLOWED_ORIGINS` | the Vercel URL from step 2.4 (e.g. `https://devpulse.vercel.app`) |

Redeploy the backend for the new variable to take effect.

---

## 4. Smoke test

From the live Vercel URL:
1. Register an account, log in.
2. Submit the default Python snippet on `/analyze` — confirm you get a
   real benchmark result back (not a network error, which would mean
   `NEXT_PUBLIC_API_URL` or `ALLOWED_ORIGINS` is wrong).
3. Check `/history` shows the submission.
4. Open the result's `/results/<token>` link directly — confirms the
   public-token routing (see CLAUDE.md's security notes on why this isn't
   a plain sequential id) works end to end.

If step 2 fails with a CORS error in the browser console specifically, it's
almost always step 3 above — either the value doesn't match the Vercel URL
exactly (no trailing slash) or the backend hasn't redeployed since it was
set.

---

## Notes for next time

- The backend Dockerfile intentionally does **not** use uvicorn's
  `--reload` flag (that's dev-only — see the comment in
  `backend/Dockerfile`), so Railway is already running it the right way
  without any extra configuration.
- `docker-compose.yml` is for **local development only** — it's not used
  by either Railway or Vercel, both of which build straight from each
  service's own Dockerfile / `package.json`.
- If you rotate `JWT_SECRET_KEY` in production, every currently logged-in
  user is instantly logged out (their existing tokens no longer verify).
  That's expected, not a bug.
