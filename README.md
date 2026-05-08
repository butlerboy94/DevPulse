<div align="center">

# ⚡ DevPulse

### Code Performance Analysis, Powered by C++ and AI

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-Latest-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![C++](https://img.shields.io/badge/C++-C++17-00599C?style=for-the-badge&logo=cplusplus&logoColor=white)](https://isocpp.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Latest-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Anthropic](https://img.shields.io/badge/Anthropic-Claude_AI-D4A017?style=for-the-badge&logo=anthropic&logoColor=white)](https://anthropic.com)

<br/>

> **Paste your code. Get a diagnosis. Ship better software.**

DevPulse is a full-stack web platform that benchmarks your code's execution speed, identifies performance bottlenecks, scores code quality, and delivers AI-powered optimization recommendations — all in seconds.

<br/>

<!-- Replace with actual demo GIF once deployed -->
<!-- ![DevPulse Demo](./assets/demo.gif) -->

**[Live Demo](#)** · **[Report a Bug](#)** · **[Request a Feature](#)**

</div>

---

## What Is DevPulse?

Think of DevPulse as a **code doctor**. You bring it your code, and it tells you exactly what's wrong and how to fix it.

Under the hood, DevPulse does four things simultaneously:

| Step | What Happens |
|---|---|
| **1. Benchmark** | A C++ engine (built with `chrono` and exposed via `pybind11`) times your code's execution with nanosecond precision and tracks memory usage |
| **2. Profile** | The engine detects nested loop depth, identifies hotspot lines, and counts function calls |
| **3. Score** | Python's `ast` module parses your code into an Abstract Syntax Tree and scores it on cyclomatic complexity, function length, naming conventions, and unused variables |
| **4. Recommend** | The Anthropic API (Claude) reads the full analysis report and writes plain-English optimization suggestions tailored to your specific code |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│            Next.js 14 · TypeScript · Tailwind CSS            │
│         Monaco Editor · Recharts · Zustand · Axios           │
└────────────────────────────┬─────────────────────────────────┘
                             │  REST API
┌────────────────────────────▼─────────────────────────────────┐
│                   BACKEND  (FastAPI)                         │
│                                                              │
│   ┌─────────────────┐  ┌──────────────┐  ┌───────────────┐  │
│   │   C++ Engine    │  │ AST Analyzer │  │ Anthropic API │  │
│   │  (via pybind11) │  │ (ast module) │  │  (Claude AI)  │  │
│   └─────────────────┘  └──────────────┘  └───────────────┘  │
│                                                              │
│              SQLAlchemy · Alembic · JWT Auth                 │
└──────────────┬─────────────────────────────────┬────────────┘
               │                                 │
  ┌────────────▼──────────┐        ┌─────────────▼──────────┐
  │      PostgreSQL        │        │          Redis          │
  │   (primary database)   │        │   (analysis caching)   │
  └───────────────────────┘        └────────────────────────┘

              All services containerized via Docker Compose
              Deployed via GitHub Actions CI/CD pipeline
```

---

## Tech Stack

### Backend
| Technology | Role |
|---|---|
| **FastAPI** | Python web framework — async, fast, auto-generates Swagger UI |
| **pybind11** | Bridges the C++ benchmarking engine into Python |
| **CMake** | Build system for the C++ engine |
| **SQLAlchemy** | ORM — Python objects that map to PostgreSQL tables |
| **Alembic** | Database migration manager |
| **Python `ast`** | Parses code into an Abstract Syntax Tree for static analysis |
| **`subprocess`** | Runs user-submitted code in an isolated, sandboxed process |
| **JWT** | Stateless authentication tokens for user sessions |
| **Pytest** | Automated testing for all API endpoints |

### C++ Engine
| Technology | Role |
|---|---|
| **`chrono`** | High-precision execution timer (nanosecond accuracy) |
| **Standard Library** | Memory tracking and data structures |
| **pybind11 bindings** | Exposes C++ functions as callable Python functions |

### Frontend
| Technology | Role |
|---|---|
| **Next.js 14** | React framework with App Router, SSR, and file-based routing |
| **TypeScript** | Type-safe JavaScript — catches errors before they reach production |
| **Tailwind CSS** | Utility-first styling for fast, responsive UI development |
| **Monaco Editor** | The VS Code editor embedded as a React component |
| **Recharts** | Performance data visualization (charts, gauges, graphs) |
| **Axios** | HTTP client for all frontend-to-backend API calls |
| **Zustand** | Lightweight global state management |

### Infrastructure
| Technology | Role |
|---|---|
| **PostgreSQL** | Primary database for users, submissions, and results |
| **Redis** | Caches repeated analyses to avoid redundant computation |
| **Docker + Compose** | Containerizes every service for consistent local development |
| **GitHub Actions** | CI/CD — runs tests and deploys on every push to main |
| **Vercel** | Frontend deployment |
| **Railway / Render** | Backend deployment |

---

## Project Structure

```
DevPulse/
├── frontend/                   # Next.js 14 TypeScript application
│   ├── app/                    # App Router pages and layouts
│   ├── components/             # Reusable React components
│   └── public/                 # Static assets
│
├── backend/                    # FastAPI Python application
│   ├── app/
│   │   ├── api/                # Route handlers (analyze, results, auth)
│   │   ├── models/             # SQLAlchemy database models
│   │   ├── services/           # Business logic (analysis, AI, auth)
│   │   └── core/               # Config, security, dependencies
│   ├── alembic/                # Database migration files
│   └── tests/                  # Pytest test suite
│
├── engine/                     # C++ benchmarking engine
│   ├── src/                    # C++ source files
│   ├── include/                # C++ header files
│   ├── bindings/               # pybind11 Python binding definitions
│   └── CMakeLists.txt          # C++ build configuration
│
├── .github/
│   └── workflows/              # GitHub Actions CI/CD pipelines
│
├── docker-compose.yml          # Local multi-service orchestration
├── .gitignore                  # Keeps secrets and build artifacts out of git
├── README.md                   # You are here
└── CLAUDE.md                   # Living project memory and session log
```

---

## Getting Started

> **Prerequisites:** Docker Desktop, Git, Node.js 18+, Python 3.13, a C++ compiler (GCC or Clang)

### 1. Clone the repository
```bash
git clone https://github.com/your-username/DevPulse.git
cd DevPulse
```

### 2. Set up environment variables
```bash
# Copy the example env file (never commit the actual .env)
cp backend/.env.example backend/.env
```

Edit `backend/.env` and fill in your values:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/devpulse
REDIS_URL=redis://localhost:6379
ANTHROPIC_API_KEY=your_anthropic_api_key
JWT_SECRET_KEY=your_secret_key
```

### 3. Start all services with Docker
```bash
docker compose up --build
```

This starts:
- **Frontend** at `http://localhost:3000`
- **Backend API** at `http://localhost:8000`
- **Swagger UI** at `http://localhost:8000/docs`
- **PostgreSQL** on port `5432`
- **Redis** on port `6379`

### 4. Run the C++ engine build (first time only)
```bash
cd engine
cmake -B build && cmake --build build
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/analyze` | Submit code for full analysis |
| `GET` | `/results/{id}` | Retrieve a specific analysis result |
| `GET` | `/history` | Get all past analyses for current user |
| `POST` | `/auth/register` | Create a new user account |
| `POST` | `/auth/login` | Log in and receive a JWT token |

Full interactive API documentation available at `/docs` (Swagger UI) when running locally.

---

## Roadmap

- [x] Project setup and architecture
- [ ] **Phase 1** — Initialize monorepo, Docker, FastAPI and Next.js skeletons
- [ ] **Phase 2** — C++ benchmarking engine with pybind11 bindings
- [ ] **Phase 3** — Python backend, static analysis, AI integration, database
- [ ] **Phase 4** — Frontend: code editor, dashboard, auth, charts
- [ ] **Phase 5** — CI/CD pipeline, cloud deployment, live demo URL

---

## Why DevPulse?

DevPulse was built to demonstrate the full range of modern software engineering — from low-level C++ systems work all the way to a polished user interface, connected through a typed API and shipped with automated deployments.

It is directly relevant to performance-focused engineering teams at companies like **RunPod**, **NVIDIA**, **Amazon**, and **Microsoft** — anywhere that cares about what code actually does at runtime, not just whether it compiles.

---

<div align="center">

Built by **Kaleb Butler**

</div>
