<div align="center">

# gitAudit

**AI code review for GitHub pull requests: find the bugs, fix them, open the PR.**

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-4169E1?logo=postgresql&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-Gemini-1C3C3C?logo=langchain&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-agents-1C3C3C?logo=langchain&logoColor=white)
![pgvector](https://img.shields.io/badge/pgvector-code_search-4169E1?logo=postgresql&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4-06B6D4?logo=tailwindcss&logoColor=white)

</div>

## What it does

1. **Review:** AI agents with tools review a pull request and report bugs, security problems and bad practices, each with severity, file, line and a suggested fix. Big PRs are split into parts and reviewed in parallel.
2. **Fix:** for any finding, an AI agent reads only the code it needs, edits it with small patches (also in other files that use the code) and writes a unit test in the repo's own language.
3. **Approve:** after you approve, gitAudit opens a new PR with the fix and the test.
4. **Test:** GitHub Actions runs the test. If it fails, the AI reads the error and tries again (max 3 times).

**Nothing is merged automatically.** A person always decides.

**Dashboard:** stat cards (PRs reviewed, findings, AI fixes, CI pass rate), a 14-day activity chart, findings by severity and type, fix status, top repos, recent activity and a searchable repo list.

**Design:** responsive layout (sidebar on desktop, top bar + bottom tabs on phone) with a **light and dark theme**. The toggle is saved in the browser; the first visit follows the system setting.

**Many GitHub accounts:** link more than one GitHub account (for example personal + work). Repos from all of them are shown together, and for every repo gitAudit uses the account that can open it.

## How it works

```mermaid
flowchart LR
    A[Login] --> B[Connect GitHub] --> C[Pick repo + PR] --> D[Review with AI]
    D --> E[Findings] --> F[Fix with AI] --> G{Approve?}
    G -- No --> E
    G -- Yes --> H[Branch + commit + PR] --> I[GitHub Actions runs test]
    I -- failed --> J[AI retries with the error] --> I
    I -- passed --> K[Done]
```

**Review: a LangGraph graph (map → reduce)**

```mermaid
flowchart LR
    D[PR diff] --> S[Split into parts<br/>max 30k chars each]
    S --> A1[Structure agent<br/>part 1] & B1[Security agent<br/>part 1]
    S --> A2[Structure agent<br/>part 2] & B2[Security agent<br/>part 2]
    A1 & B1 & A2 & B2 --> L[Lead<br/>merge, dedupe, summary]
```

- The diff is split per file (and big files per piece). Lock files, minified and generated files are skipped. Max 6 parts; files that were not reviewed are named in the summary.
- LangGraph `Send` starts one structure agent and one security agent per part, all in parallel. Their findings are added together in the graph state, then the lead merges them.
- The agents have **read-only tools**, so they can look outside the diff (the full function, a helper, its callers).

**Agent tools** (`services/agent/tools.py`)

| Tool | What it does | Used by |
|---|---|---|
| `read_file(path, start, end)` | reads only some lines (max 300), with line numbers. Works for huge files | review, fix |
| `list_files(folder)` | files in a folder | review, fix |
| `search_code(text)` | exact search with GitHub code search (default branch) | review, fix |
| `semantic_search(question)` | search by meaning in the pgvector index | review, fix |
| `edit_file(path, old, new)` | replaces one exact piece of text. Fails if it is not found or found twice | fix |
| `create_file(path, content)` | new file only (the unit test) | fix |

**Fix: a LangChain agent** (`create_agent`, runs on LangGraph). The agent never rewrites a whole file: it reads the lines it needs and changes them with `edit_file`, so a 10,000-line file is fine and nothing else in the file changes. One fix can change up to 6 files. Edits stay in memory until you approve, and the UI shows a diff per file.

**On approve**, the fix branch `gitaudit/fix-pr<n>-<time>` gets **one commit** (Git Trees API) with every changed file, the test and `.github/workflows/gitaudit-tests.yml`. The workflow runs the AI's test command on `ubuntu-latest`, which already has Python, Node, Java, Go, Ruby, PHP, .NET and Rust, so it works for any language. Tests never run on the gitAudit server. If they fail, the same agent gets the log, reads the branch again and pushes a new commit.

**Code index (pgvector):** "Index code for AI search" downloads the repo once (tarball), cuts code files into 60-line chunks, embeds them with `gemini-embedding-001` (768 numbers) and saves them in the `code_chunks` table. `semantic_search` embeds the question and returns the 5 closest chunks (cosine distance).

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy, Alembic |
| Database | PostgreSQL (Neon) |
| AI | LangChain + LangGraph + Google Gemini, pgvector for code search |
| Auth | JWT, Argon2 password hashing, Fernet-encrypted GitHub tokens |
| Frontend | React 19, Vite, Tailwind CSS 4, React Router, Axios |

## Project structure

```
Backend/
├── migrations/            Alembic migrations
└── app/
    ├── main.py            app + routers
    ├── core/              db, auth (JWT), llm (Gemini), crypto (token encryption)
    ├── models/            users, github_accounts, reviews, fixes, code_chunks
    ├── schemas/           request / response shapes
    ├── routers/           user, github, review, fix, stats
    └── services/
        ├── user_service.py
        ├── github_service.py   GitHub OAuth, accounts, get_token(user, repo)
        ├── stats_service.py    numbers for the dashboard
        ├── agent/         tools (read, search, edit), code_index (pgvector)
        ├── review/        review_service (split diff), graph (LangGraph), prompts (each agent next to its prompt)
        └── fix/           fix_service, prompts (fix agent), workflow, github_files

Frontend/src/
├── App.jsx                routes
├── index.css              theme colors (CSS variables for light and .dark)
├── components/            UserLayout (sidebar + phone tabs), AuthLayout, Userpri (private route), GithubButton,
│                          Logo, Icons, ThemeToggle,
│                          dashboard parts: StatCard, BarList, ActivityChart, RecentActivity, GithubAccounts, RepoList
└── pages/                 Login, Register, GithubCallback, Dashboard, Repos, RepoPage
```

## Run locally

**1. GitHub OAuth App:** GitHub → Settings → Developer settings → OAuth Apps → New.
Set Homepage URL and Authorization callback URL to `http://localhost:5174`, and leave "Expire user access tokens" unticked.

The database needs the `vector` extension (Neon has it; migration `0004` turns it on).

**2. Backend**

```bash
cd Backend
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8001
```

`Backend/.env`:

```env
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
JWT=<python -c "import secrets; print(secrets.token_hex(32))">
TOKEN_ENCRYPTION_KEY=<python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
GITHUB_CLIENT_ID=<client id>
GITHUB_CLIENT_SECRET=<client secret>
GOOGLE_API_KEY=<gemini api key>
GEMINI_MODEL=gemini-2.5-flash
FRONTEND_URL=http://localhost:5174
```

`FRONTEND_URL` is the only origin CORS allows, and the GitHub callback sends users back to it. Set it to the real frontend URL when you deploy.

**3. Frontend**

```bash
cd Frontend
npm install
npm run dev -- --port 5174
```

`Frontend/.env`:

```env
VITE_API_URL=http://localhost:8001
VITE_GITHUB_CLIENT_ID=<client id>
```

API docs: http://localhost:8001/docs

**Database changes:** edit a model → `alembic revision --autogenerate -m "what changed"` → `alembic upgrade head`.

## API

| Method | Endpoint | What it does |
|---|---|---|
| `POST` | `/register`, `/login` | account, returns a JWT |
| `GET` | `/me` | current user with linked GitHub accounts |
| `GET` | `/stats` | dashboard numbers |
| `POST` | `/github/login`, `/github/connect` | GitHub OAuth (connect adds another account) |
| `DELETE` | `/github/accounts/{id}` | remove a linked GitHub account |
| `GET` | `/github/repos`, `/github/repos/{owner}/{name}/pulls` | repos of all linked accounts and open PRs |
| `POST` / `GET` | `/github/repos/{owner}/{name}/index` | index the code in pgvector / chunk count |
| `POST` / `GET` | `/reviews` | review a PR / saved reviews |
| `POST` / `GET` | `/fixes` | make a fix / saved fixes |
| `POST` | `/fixes/{id}/approve`, `/reject`, `/check` | open PR / reject / check CI and retry |

GitHub endpoints used, with docs links: [docs/GITHUB_API.md](docs/GITHUB_API.md).

## Security

- Passwords hashed with Argon2. GitHub tokens encrypted at rest with Fernet and never sent to the browser.
- A login stays valid for 7 days (JWT and cookie).
- The OAuth `state` parameter is checked (CSRF).
- AI fixes go to a new branch and a new PR, and are never merged automatically.
- Agents treat repo code as untrusted. Their tools cannot read or change paths with `..`, `.` or empty parts, the edit tools cannot touch `.github/` and can change at most 6 files, and `search_code` stays inside the current repo.
- A fix cannot be approved if its files changed after it was made (`409`), because that would undo the newer commits. Reject it and make a new fix.

## Troubleshooting

| Problem | Fix |
|---|---|
| DB or AI calls take very long | Broken IPv6 on the machine. `db.py` already forces IPv4 for the database; make Windows prefer IPv4 for everything else. |
| `column ... does not exist` | `alembic upgrade head` |
| `--reload` misses changes (Windows) | set `WATCHFILES_FORCE_POLLING=true` before `uvicorn` |
| GitHub calls fail / Approve fails | Reconnect GitHub (the token needs the `repo` and `workflow` scopes) |
| "Add another account" links the same account again | GitHub shows an account picker; if the other account is not listed, sign in to it on github.com first |
| Gemini `429` | free tier allows ~5 calls per minute. Agents wait and retry 4 times; big PRs are slow on the free tier |
| Indexing takes many minutes | free tier allows 30,000 embedding tokens per minute. Indexing sends 25 chunks at a time and waits when the limit is hit; a big repo can take around 20 minutes, so keep the page open |
| AI call hangs with no error | `gemini-flash-latest` sometimes never answers. Set `GEMINI_MODEL=gemini-2.5-flash` |

## Status

- [x] Login (email + GitHub), repos, pull requests
- [x] Multi-agent AI review (LangGraph, tools, big PRs in parts)
- [x] Fix agent with patch edits and multi-file fixes → approve → PR
- [x] pgvector code index + semantic search
- [x] Unit tests in GitHub Actions + AI retry (any language)
- [x] Alembic migrations, encrypted GitHub tokens
- [x] Dashboard with stats and charts
- [x] Many GitHub accounts per user
- [x] New responsive design with light / dark theme
- [ ] **Deployment**
