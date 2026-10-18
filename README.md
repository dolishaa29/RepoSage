# RepoSage

A web app where you log in, connect your GitHub account, pick a pull request, and let AI (Google Gemini)
review the changed code for bugs and security problems.

**Status:** login, register, GitHub login/connect, repo list, PR list and AI review of a PR work.

---

## Tech stack

| Part | Tech |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy |
| Database | PostgreSQL on Neon (cloud) |
| Login | JWT tokens (python-jose), passwords hashed with argon2 |
| GitHub | GitHub OAuth App, `httpx` to call the GitHub API |
| AI | LangChain + `langchain-google-genai` → Google Gemini |
| Frontend | React + Vite |

---

## Folder structure

```
Backend/
├── .env                      secrets (never commit)
├── requirements.txt
└── app/
    ├── main.py               creates the app, CORS, tables, routers
    ├── core/
    │   ├── db.py             database connection, get_db
    │   ├── auth.py           create_token, auth (checks the JWT on protected routes)
    │   └── llm.py            the AI model: init_chat_model("google_genai:gemini-flash-latest")
    ├── models/
    │   ├── user.py           users table
    │   └── review.py         reviews table
    ├── schemas/              request bodies the frontend SENDS (…Dto) + responses the backend RETURNS
    ├── services/             the real logic
    │   ├── auth_service.py   register, login
    │   ├── github_service.py GitHub login, connect, repos, pull requests
    │   └── review_service.py AI review of a pull request
    └── routers/              URLs → call a service
        ├── auth.py           /register  /login  /me
        ├── github.py         /github/...
        └── review.py         /reviews

Frontend/src/
├── App.jsx                   all routes (react-router-dom)
├── index.css                 Tailwind + theme colours
├── components/
│   ├── UserLayout.jsx        top navbar + <Outlet /> for logged-in pages
│   ├── Userpri.jsx           private route: no token cookie → /login
│   └── GithubButton.jsx      sends the user to GitHub to log in / connect
└── pages/
    ├── GithubCallback.jsx    "/" : GitHub comes back here with ?code=, finishes login / connect
    ├── Login.jsx             /login
    ├── Register.jsx          /register
    ├── Dashboard.jsx         /dashboard : profile + repos
    └── RepoPage.jsx          /repo/:owner/:name : open PRs + AI review
```

Frontend stack: React + Vite, Tailwind CSS, lucide-react icons, react-router-dom, axios, js-cookie.
Every page calls the backend itself with `axios` (`import.meta.env.VITE_API_URL + "/..."`).
The JWT is kept in a cookie called `token` (1 day) and sent as `Authorization: Bearer <token>`.

A request always goes: **router → service → database / GitHub**.

---

## How it works

### 1. Email + password

```
Register page ──POST /register──▶ save user (password hashed with argon2)
Login page    ──POST /login─────▶ check password ──▶ return JWT token
                                                       │
Frontend saves the token in a cookie ("token") ◀───────┘
Every request after that sends:  Authorization: Bearer <token>
```

The token lasts 60 minutes. When it expires the frontend goes back to the login page.

### 2. GitHub (one button does both "login" and "connect")

```
1. User clicks the GitHub button
        │
        ▼
2. GitHub page: "Authorize reposage?" → user clicks Allow
        │
        ▼
3. GitHub sends the user back to  http://localhost:5174/?code=abc123
        │
        ▼
4. GithubCallback.jsx (route "/") reads the code:
        ├── not logged in → POST /github/login   {code} → backend returns a JWT
        └── logged in     → POST /github/connect {code} → GitHub gets linked to this user
        │
        ▼
5. Backend: code → GitHub access token → GitHub user info → save in users table
```

- **Client ID + Client Secret** identify the *app*. There is one pair for the whole app.
- **GitHub access token** belongs to *one user*. Each user gets their own, and it only sees their own repos.
- The token is saved in the `users` table and is never sent to the frontend.
  ⚠️ For now it is saved as plain text. **Encrypt it before production** (see Next steps).
- **Reconnect GitHub** (dashboard, when already connected) runs the same flow again and saves a fresh token.
  Use it when GitHub calls start failing. To switch to a different GitHub account, log out of github.com first.

### 3. AI review of a pull request

```
Dashboard → click a repo → RepoPage shows its open pull requests
        │
        ▼  "Review with AI"
POST /reviews {repo, pr_number}
        │
        ▼
Backend:
  1. GitHub: PR title + changed files (the diff)
  2. Gemini: "find bugs and security problems in this diff"
     → answer comes back as a ReviewResult object (summary + findings), not free text
  3. save it in the reviews table
        │
        ▼
RepoPage shows: summary + each finding (severity, file:line, why, how to fix)
```

- The AI part is a LangChain chain: `chain = prompt | model.with_structured_output(ReviewResult)`.
  The model must answer in the `ReviewResult` shape (summary + findings), so we get an object back, not free text.
- Binary files (images etc.) are skipped.
- GitHub returns the first 30 changed files of a PR.

---

## API

| Method | URL | Login needed | What it does |
|---|---|---|---|
| POST | `/register` | no | create account `{name, email, password}` |
| POST | `/login` | no | returns `{access_token}` |
| GET | `/me` | yes | the logged-in user |
| POST | `/github/login` | no | `{code}` → log in / sign up with GitHub, returns `{access_token}` |
| GET | `/github/callback` | no | only forwards GitHub's `?code=` to the frontend, for an OAuth App whose callback is `localhost:8001/github/callback` |
| POST | `/github/connect` | yes | `{code}` → link GitHub to the logged-in user |
| GET | `/github/repos` | yes | the user's GitHub repos (30 most recently updated) |
| GET | `/github/repos/{owner}/{name}/pulls` | yes | open pull requests of a repo |
| POST | `/reviews` | yes | `{repo, pr_number}` → AI reviews the PR, saves and returns the result |
| GET | `/reviews?repo=owner/name` | yes | saved reviews of a repo, newest first |

Interactive docs: http://localhost:8001/docs

---

## Database

**users**

| Column | Notes |
|---|---|
| id | primary key |
| name | |
| email | unique |
| hashed_password | empty for users who signed up with GitHub |
| github_id | GitHub's user id, unique |
| github_username | e.g. `dolishaa29` |
| github_token | GitHub access token (plain text for now, encrypt before production) |

**reviews**

| Column | Notes |
|---|---|
| id | primary key |
| user_id | who asked for the review |
| repo | `owner/name` |
| pr_number, pr_title | which pull request |
| ai | which AI did the review (`gemini`) |
| summary | AI's short summary |
| findings | JSON list: file, line, severity (high/medium/low), category, title, explanation, suggestion |
| created_at | |

Tables are created automatically when the backend starts (`Base.metadata.create_all`).
It does **not** add new columns to an existing table. A new column must be added by hand (`ALTER TABLE`).

---

## Setup

### 1. GitHub OAuth App (one time)

GitHub → Settings → Developer settings → OAuth Apps → New OAuth App

| Field | Value |
|---|---|
| Homepage URL | `http://localhost:5174` |
| Authorization callback URL | `http://localhost:5174` |
| Expire user access tokens | unticked |

Copy the **Client ID**, then click **Generate a new client secret** and copy it.

### 2. Backend

```bash
cd Backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Create `Backend/.env`:

```
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
JWT=<long random string>
GITHUB_CLIENT_ID=<from step 1>
GITHUB_CLIENT_SECRET=<from step 1>

# Google Gemini (key from aistudio.google.com)
GOOGLE_API_KEY=<Gemini API key>
```

**Gemini setup (one time):** aistudio.google.com → **Get API key** → create key → `GOOGLE_API_KEY`.
The model name is set in `core/llm.py` (`gemini-flash-latest`; Pro models are quota-limited on the free tier).

Make the random values with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"                                  # JWT
```

Run:

```bash
uvicorn app.main:app --reload --reload-include .env --port 8001
```

If code changes are not picked up (happens on some Windows drives), use polling:

```bash
WATCHFILES_FORCE_POLLING=true uvicorn app.main:app --reload --reload-include .env --port 8001   # Git Bash
$env:WATCHFILES_FORCE_POLLING="true"; uvicorn app.main:app --reload --reload-include .env --port 8001   # PowerShell
```

### 3. Frontend

```bash
cd Frontend
npm install
```

Create `Frontend/.env`:

```
VITE_API_URL=http://localhost:8001
VITE_GITHUB_CLIENT_ID=<same Client ID as the backend>
```

The frontend calls `VITE_API_URL` directly (no Vite proxy), so the backend CORS origin in `main.py` must be `http://localhost:5174`.

Run:

```bash
npm run dev -- --port 5174
```

Open http://localhost:5174

Ports 8001 / 5174 are used because 8000 / 5173 are often busy with another project.
If you change them, also change the CORS origin in `Backend/app/main.py` and the URLs in the GitHub OAuth App.

---

## Troubleshooting

| Problem | Cause / fix |
|---|---|
| `500` with `column ... does not exist` | the table in Neon is older than the model → add the column with `ALTER TABLE` |
| `SSL connection has been closed unexpectedly` | Neon closes idle connections; `pool_pre_ping=True` in `db.py` handles it |
| Backend still shows old routes after a change | the file watcher missed it → start with `WATCHFILES_FORCE_POLLING=true` (see Setup), or stop and start again |
| Thrown back to the login page | the 60-minute token expired → log in again |
| Every request fails with a CORS / network error | `VITE_API_URL` in `Frontend/.env` is wrong, the backend is not running, or the CORS origin in `main.py` is not `http://localhost:5174` |
| GitHub button says "login failed" | the callback URL in the GitHub OAuth App must be `http://localhost:5174` |
| GitHub says "redirect_uri is not associated" | the URL GitHub sends users back to must be registered in the OAuth App: `http://localhost:5174` (or `http://localhost:8001/github/callback`, which forwards to it) |
| GitHub calls fail with 401 / "connect GitHub again" | the saved token expired or was revoked → Reconnect GitHub |
| Repos stop loading after some hours | "Expire user access tokens" is ticked in the GitHub OAuth App → untick it, then Reconnect GitHub |
| "AI is not set up" | add `GOOGLE_API_KEY` to `.env` |
| Gemini `429 RESOURCE_EXHAUSTED` | free-tier quota used up (Pro models have almost none) → use `gemini-flash-latest`, wait, or enable billing |

---

## Next steps

**Before production (must do):**
- [ ] Encrypt the GitHub token in the database again (Fernet with a `TOKEN_ENCRYPTION_KEY` in `.env`;
      the old `core/crypto.py` is in git history: `git log --all -- Backend/app/core/crypto.py`)
- [ ] Long random `JWT` secret, new GitHub client secret, new Gemini key (old ones were shared)

**Features:**

- [x] AI review of a pull request (LangChain + Gemini)
- [ ] Second AI as backup. Claude on AWS Bedrock is blocked on this AWS account (Marketplace agreement
      `NOT_AVAILABLE`). Bedrock models that worked in a test with our `ReviewResult` format:
      `qwen.qwen3-coder-next`, `deepseek.v3.2`, `mistral.devstral-2-123b`, `moonshotai.kimi-k2.5`, `zai.glm-5`
- [ ] Alembic migrations (instead of manual `ALTER TABLE`)
- [ ] AI writes a fix + unit tests, human approves / rejects, then a new branch + PR on GitHub
- [ ] LangGraph: split into 3 agents (structure, security, fix + tests)
- [ ] Webhook: review automatically when a PR is opened
- [ ] pgvector memory of past fixes
- [ ] Deploy (public URL + update the GitHub OAuth App URLs)
