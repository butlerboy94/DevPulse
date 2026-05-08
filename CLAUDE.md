# CLAUDE.md — DevPulse Project Memory

This file is the living memory of the DevPulse project. It is updated every session to reflect exactly where we are, what decisions were made, what was built, and what comes next. Any AI assistant reading this file should treat it as the single source of truth for the project.

---

## Project Identity

| Field | Value |
|---|---|
| **Project Name** | DevPulse |
| **Tagline** | Code performance analysis, powered by C++ and AI |
| **Owner** | Kaleb Butler |
| **Started** | 2026-05-07 |
| **Status** | Phase 1 — In Progress |
| **Live URL** | TBD (Vercel + Railway/Render) |
| **GitHub Repo** | TBD |

---

## What DevPulse Does

DevPulse is a web platform where developers paste or upload code and receive a full performance analysis report. It benchmarks execution speed, identifies bottlenecks, scores code quality, and uses AI to generate plain-English optimization recommendations.

Think of it as a **code doctor** — you bring it sick code, it tells you exactly what's wrong and how to fix it.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                      FRONTEND                           │
│         Next.js 14 + TypeScript + Tailwind CSS          │
│         Monaco Editor | Recharts | Zustand | Axios      │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP / REST
┌────────────────────────▼────────────────────────────────┐
│                    BACKEND (FastAPI)                     │
│         Python 3.13 | SQLAlchemy | Alembic | JWT        │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │  C++ Engine  │  │  AST Analysis│  │ Anthropic API │ │
│  │  via pybind11│  │  (ast module)│  │ (Claude AI)   │ │
│  └──────────────┘  └──────────────┘  └───────────────┘ │
└──────────┬─────────────────────────────────────────────-┘
           │
┌──────────▼──────────────┐     ┌──────────────────────┐
│     PostgreSQL           │     │        Redis          │
│  (primary database)      │     │  (analysis caching)   │
└─────────────────────────┘     └──────────────────────┘
```

All services run inside Docker containers, orchestrated with Docker Compose locally and deployed via CI/CD on GitHub Actions.

---

## Full Tech Stack

### Languages
| Language | Version | Role |
|---|---|---|
| Python | 3.13 | Backend, API, AI integration, static analysis |
| C++ | C++17 | High-precision benchmarking engine |
| TypeScript | Latest | Frontend, type-safe React components |
| SQL | PostgreSQL dialect | Database queries and schema |

### Backend
| Tool | Purpose |
|---|---|
| FastAPI | Python web framework — fast, async, auto-generates Swagger docs |
| pybind11 | Bridge between C++ benchmarking engine and Python backend |
| CMake | Build system for C++ code |
| SQLAlchemy | ORM — lets Python talk to PostgreSQL without raw SQL |
| Alembic | Handles database schema migrations (version control for the DB) |
| Python `ast` module | Parses code into an Abstract Syntax Tree for static analysis |
| `subprocess` module | Runs submitted code in an isolated sandbox safely |
| JWT | JSON Web Tokens — handles user authentication |
| Pytest | Automated testing framework for all API endpoints |

### C++ Engine
| Tool | Purpose |
|---|---|
| `chrono` library | High-precision execution timing (nanosecond accuracy) |
| Standard Library | Memory tracking, data structures |
| pybind11 bindings | Exposes C++ functions to Python as if they were Python functions |

### Frontend
| Tool | Purpose |
|---|---|
| Next.js 14 (App Router) | React framework — handles routing, SSR, and project structure |
| TypeScript | Adds type safety to JavaScript — catches bugs before runtime |
| Tailwind CSS | Utility-first CSS framework for fast, consistent styling |
| Monaco Editor | The exact editor that powers VS Code, embedded as a React component |
| Recharts | Charting library for visualizing performance data |
| Axios | HTTP client for making API calls to the FastAPI backend |
| Zustand | Lightweight global state management (simpler than Redux) |

### Database & Caching
| Tool | Purpose |
|---|---|
| PostgreSQL | Primary relational database — stores users, submissions, results |
| Redis | Optional caching layer — avoids re-analyzing identical code |

### DevOps
| Tool | Purpose |
|---|---|
| Docker | Containerizes each service so it runs identically everywhere |
| Docker Compose | Orchestrates all containers locally with one command |
| GitHub Actions | CI/CD — runs tests and deploys automatically on push |
| Railway / Render | Cloud hosting for the FastAPI backend |
| Vercel | Hosting for the Next.js frontend |
| AWS S3 | Optional — stores uploaded code files |

### AI
| Tool | Purpose |
|---|---|
| Anthropic API | Powers the AI recommendation engine using Claude |
| Prompt Engineering | Structured prompts that return consistent JSON optimization reports |

---

## Full Phase Roadmap

### Phase 1 — Project Setup and Architecture (Week 1)
- [ ] Initialize monorepo structure (`frontend/`, `backend/`, `engine/`)
- [ ] Set up Git repository with README
- [ ] Configure Docker and Docker Compose for local development
- [ ] Set up FastAPI project skeleton with health check endpoint
- [ ] Set up Next.js/TypeScript project skeleton
- [ ] Define database schema and set up PostgreSQL
- [ ] Write initial `CMakeLists.txt` for C++ engine
- [ ] Set up Python virtual environment and `requirements.txt`

### Phase 2 — C++ Benchmarking Engine (Week 2)
- [ ] Build C++ execution timer using `chrono` (high-precision clock)
- [ ] Implement execution counter and memory usage tracker
- [ ] Build loop complexity detector (nested loop depth analysis)
- [ ] Implement line-by-line execution profiling
- [ ] Write pybind11 bindings to expose all C++ functions to Python
- [ ] Write Python wrapper class for clean interface
- [ ] Test with sample code snippets
- [ ] Document the engine API

### Phase 3 — Python Backend and API (Week 3)
- [ ] Build code submission endpoint (`POST /analyze`)
- [ ] Build code execution sandbox (safe isolated execution via `subprocess`)
- [ ] Wire C++ engine into analysis pipeline via pybind11
- [ ] Implement static analysis layer using Python `ast` module:
  - [ ] Cyclomatic complexity scoring
  - [ ] Function length analysis
  - [ ] Naming convention checks
  - [ ] Unused variable detection
- [ ] Build Anthropic API integration for AI recommendations
- [ ] Design prompt engineering for structured JSON optimization output
- [ ] Store analysis results in PostgreSQL
- [ ] Build results retrieval endpoint (`GET /results/{id}`)
- [ ] Build history endpoint (`GET /history`)
- [ ] Add JWT authentication for user accounts
- [ ] Write automated tests for all endpoints (Pytest)

### Phase 4 — Frontend (Week 4)
- [ ] Build code editor interface using Monaco Editor
- [ ] Build language selector (Python, C++, JavaScript)
- [ ] Build analysis results dashboard:
  - [ ] Execution time display
  - [ ] Memory usage chart
  - [ ] Complexity score gauge
  - [ ] Line-by-line hotspot highlighter
  - [ ] AI recommendations panel
- [ ] Build analysis history page
- [ ] Build user auth pages (login, register)
- [ ] Wire all frontend components to the FastAPI backend
- [ ] Mobile responsive layout with Tailwind CSS

### Phase 5 — DevOps and Deployment (Week 5)
- [ ] Write GitHub Actions CI/CD pipeline (test → build → deploy)
- [ ] Containerize full stack with Docker Compose
- [ ] Deploy backend to Railway or Render
- [ ] Deploy frontend to Vercel
- [ ] Set up environment variables and secrets management
- [ ] Configure PostgreSQL production database
- [ ] Write architecture diagram, add demo GIF to README

---

## Environment Variables Required

These must NEVER be committed to git. They live in `.env` files only.

```
# Backend
DATABASE_URL=postgresql://user:password@localhost:5432/devpulse
REDIS_URL=redis://localhost:6379
ANTHROPIC_API_KEY=your_key_here
JWT_SECRET_KEY=your_secret_here
JWT_ALGORITHM=HS256

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Monorepo Folder Structure

```
DevPulse/
├── frontend/           # Next.js 14 TypeScript app
├── backend/            # FastAPI Python app
│   ├── app/
│   │   ├── api/        # Route handlers
│   │   ├── models/     # SQLAlchemy DB models
│   │   ├── services/   # Business logic (analysis, AI, auth)
│   │   └── core/       # Config, security, dependencies
│   ├── alembic/        # DB migration files
│   └── tests/          # Pytest test files
├── engine/             # C++ benchmarking engine
│   ├── src/            # C++ source files
│   ├── include/        # C++ header files
│   ├── bindings/       # pybind11 binding definitions
│   └── CMakeLists.txt  # C++ build configuration
├── docker-compose.yml  # Local multi-service orchestration
├── .github/
│   └── workflows/      # GitHub Actions CI/CD pipelines
├── .gitignore
├── README.md
└── CLAUDE.md           # This file
```

---

## Key Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Backend framework | FastAPI over Django | Industry standard for AI/ML APIs; faster; auto-generates Swagger docs; adds new framework to resume |
| C++ integration | pybind11 | Lets us write real C++ performance code and call it from Python with zero overhead |
| Code execution | subprocess sandbox | Security — user-submitted code runs isolated, can't touch the server |
| State management | Zustand over Redux | Simpler API, less boilerplate, sufficient for this project's complexity |
| Auth | JWT | Stateless, works across frontend and backend naturally |

---

## Concepts Being Learned and Demonstrated

| Concept | Where It Appears |
|---|---|
| High-precision C++ benchmarking | C++ engine using `chrono` |
| Cross-language systems programming | pybind11 bridging C++ to Python |
| Abstract Syntax Tree (AST) analysis | Python `ast` module in static analyzer |
| Sandboxed code execution | `subprocess` isolation in backend |
| Prompt engineering for structured AI output | Anthropic API integration |
| Full-stack API design and integration | FastAPI ↔ Next.js |
| Real-time data visualization | Recharts dashboard |
| CI/CD pipeline automation | GitHub Actions |
| Containerized multi-service architecture | Docker Compose |
| JWT authentication across frontend and backend | Auth system |
| Database design for analytical data | PostgreSQL schema |

---

## Interview Pitch

> "I built DevPulse, a full-stack code performance analysis platform. It takes code submissions, runs them through a C++ benchmarking engine I built using pybind11 for high-precision execution timing, performs static analysis using Python's AST module for complexity scoring, and uses the Anthropic API to generate plain-English optimization recommendations. The whole thing is containerized with Docker, deployed via CI/CD on GitHub Actions, and live at this URL. Want me to run your code through it right now?"

Target companies: **RunPod, NVIDIA, Amazon, Microsoft**, and any performance-focused engineering team.

---

## Session Log

### Session 1 — 2026-05-07
**What was done:**
- Initialized git repository at `C:\Users\kaleb\Desktop\DevPulse`
- Created comprehensive `.gitignore` covering secrets, environment files, C++ build artifacts, Python artifacts, Node/Next.js artifacts, Docker volumes, OS files, and IDE files
- Updated `.gitignore` with project-specific additions for the full tech stack
- Created this `CLAUDE.md` living project memory file
- Created polished `README.md`

**Decisions made:**
- FastAPI chosen over Django (speed, AI/ML industry standard, Swagger docs)
- Monorepo structure: `frontend/`, `backend/`, `engine/` at root
- Security-first approach: `.gitignore` committed before any code

**Next session goals:**
- Begin Phase 1: Initialize monorepo folder structure
- Set up FastAPI skeleton with health check
- Set up Next.js skeleton
- Write `docker-compose.yml`

---

## Mistakes & Lessons Learned

_Nothing logged yet. Mistakes will be recorded here as they happen, along with the fix and what was learned._

---

## Deployment Targets

| Service | Platform | Status |
|---|---|---|
| Frontend | Vercel | Not deployed yet |
| Backend | Railway or Render | Not deployed yet |
| Database | Railway (PostgreSQL add-on) | Not deployed yet |
| Cache | Railway (Redis add-on) | Not deployed yet |

---

_Last updated: 2026-05-07 — Session 1_
