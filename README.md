<div align="center">

# gitAudit

**AI code review for GitHub pull requests: find the bugs, fix them, open the PR.**

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-4169E1?logo=postgresql&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-Gemini-1C3C3C?logo=langchain&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4-06B6D4?logo=tailwindcss&logoColor=white)

</div>

## What it does

1. **Review:** three AI agents review a pull request and report bugs, security problems and bad practices, each with severity, file, line and a suggested fix.
2. **Fix:** for any finding, the AI writes the fix plus a unit test in the repo's own language.
3. **Approve:** after you approve, gitAudit opens a new PR with the fix and the test.
4. **Test:** GitHub Actions runs the test. If it fails, the AI reads the error and tries again (max 3 times).

**Nothing is merged automatically.** A person always decides.

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

**Review: 3 LangChain agents**

```mermaid
flowchart LR
    D[PR diff] --> A[Structure agent<br/>bugs, logic]
    D --> B[Security agent<br/>injection, secrets, auth]
    A --> L[Lead agent<br/>merge, dedupe, summary]
    B --> L
```

The structure and security agents run in parallel (`RunnableParallel`). Every agent uses structured output, so the result is always typed JSON, never free text.

**Fix: on approve**, the fix branch `gitaudit/fix-pr<n>-<time>` gets three commits: the fixed file, the test, and `.github/workflows/gitaudit-tests.yml`. The workflow runs the AI's test command on `ubuntu-latest`, which already has Python, Node, Java, Go, Ruby, PHP, .NET and Rust, so it works for any language. Tests never run on the gitAudit server.

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy, Alembic |
| Database | PostgreSQL (Neon) |
| AI | LangChain + Google Gemini |
| Auth | JWT, Argon2 password hashing, Fernet-encrypted GitHub tokens |
| Frontend | React 19, Vite, Tailwind CSS 4, React Router, Axios |

## Project structure

```
Backend/
├── migrations/            Alembic migrations
└── app/
    ├── main.py            app + routers
    ├── core/              db, auth (JWT), llm (Gemini), crypto (token encryption)
    ├── models/            users, reviews, fixes
    ├── schemas/           request / response shapes
    ├── routers/           user, github, review, fix
    └── services/
        ├── user_service.py
        ├── github_service.py
        ├── review/        review_service + prompts (3 agents)
        └── fix/           fix_service, prompts, workflow, github_files

Frontend/src/
├── App.jsx                routes
├── components/            UserLayout (navbar), Userpri (private route), GithubButton
└── pages/                 Login, Register, GithubCallback, Dashboard, RepoPage
```

## Run locally

**1. GitHub OAuth App:** GitHub → Settings → Developer settings → OAuth Apps → New.
Set Homepage URL and Authorization callback URL to `http://localhost:5174`, and leave "Expire user access tokens" unticked.

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
FRONTEND_URL=http://localhost:5174
```

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
| `GET` | `/me` | current user |
| `POST` | `/github/login`, `/github/connect` | GitHub OAuth |
| `GET` | `/github/repos`, `/github/repos/{owner}/{name}/pulls` | repos and open PRs |
| `POST` / `GET` | `/reviews` | review a PR / saved reviews |
| `POST` / `GET` | `/fixes` | make a fix / saved fixes |
| `POST` | `/fixes/{id}/approve`, `/reject`, `/check` | open PR / reject / check CI and retry |

GitHub endpoints used, with docs links: [docs/GITHUB_API.md](docs/GITHUB_API.md).

## Security

- Passwords hashed with Argon2. GitHub tokens encrypted at rest with Fernet and never sent to the browser.
- The OAuth `state` parameter is checked (CSRF).
- AI fixes go to a new branch and a new PR, and are never merged automatically.

## Troubleshooting

| Problem | Fix |
|---|---|
| DB or AI calls take very long | Broken IPv6 on the machine. `db.py` already forces IPv4 for the database; make Windows prefer IPv4 for everything else. |
| `column ... does not exist` | `alembic upgrade head` |
| `--reload` misses changes (Windows) | set `WATCHFILES_FORCE_POLLING=true` before `uvicorn` |
| GitHub calls fail / Approve fails | Reconnect GitHub (the token needs the `repo` and `workflow` scopes) |
| Gemini `429` | free-tier quota used up: wait or enable billing |

## Status

- [x] Login (email + GitHub), repos, pull requests
- [x] Multi-agent AI review
- [x] Fix with AI → approve → PR
- [x] Unit tests in GitHub Actions + AI retry (any language)
- [x] Alembic migrations, encrypted GitHub tokens
- [ ] **Deployment**
