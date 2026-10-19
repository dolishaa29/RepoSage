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

---

## Overview

gitAudit connects to your GitHub account and reviews the code in your pull requests with AI (Google Gemini).
It reports bugs, security problems and bad practices, each with a severity, the exact file and line, an explanation and a suggested fix.
For any finding you can ask the AI to write the fix. Once you approve it, gitAudit opens a new pull request with the change.

**Nothing is merged automatically.** A person always reviews the fix PR on GitHub before it is merged.

## Features

| | Feature | Description |
|---|---|---|
| 🔐 | **Accounts** | Sign up with email and password, or with GitHub. JWT-based sessions. |
| 🐙 | **GitHub integration** | Connect your GitHub account through OAuth. Works with public and private repositories. |
| 🔍 | **AI pull request review** | Reviews the diff of a PR and returns a summary plus structured findings: severity (high / medium / low), category (bug / security / bad practice), file, line, explanation and fix. |
| 🛠️ | **Fix with AI** | Generates a fix for a single finding and shows the old and new code side by side. |
| ✅ | **Human approval** | On approval it creates a branch, commits the fix and opens a pull request into the original PR's branch. |
| 🗂️ | **Review history** | Every review is saved, so earlier results are still there when you come back to a repository. |

## How it works

```mermaid
flowchart LR
    A[Sign in] --> B[Connect GitHub]
    B --> C[Pick a repository]
    C --> D[Pick an open PR]
    D --> E[Review with AI]
    E --> F[Findings]
    F --> G[Fix with AI]
    G --> H{Approve?}
    H -- Yes --> I[New branch + commit + PR]
    H -- No --> F
```

### AI review

1. The backend fetches the pull request and its changed files from the GitHub API.
2. The patches are joined into one diff (binary files are skipped).
3. A LangChain chain sends the diff to Gemini with **structured output**, so the model must return a `ReviewResult` object (`summary` + `findings[]`) instead of free text.
4. The result is saved in PostgreSQL and returned to the frontend.

```python
chain = prompt | model.with_structured_output(ReviewResult)
```

### Fix with AI

1. The backend fetches the full file from the PR's branch.
2. Gemini is asked to fix **only** the selected problem and return the complete file.
3. The user compares the old and new code, then approves or rejects.
4. On approval: a branch `gitaudit/fix-pr<number>-<timestamp>` is created from the PR's branch, the fixed file is committed, and a pull request is opened into the PR's branch.

## Architecture

```mermaid
flowchart LR
    UI["React + Vite<br/>(localhost:5174)"] -- "REST + JWT" --> API["FastAPI<br/>(localhost:8001)"]
    API --> DB[("PostgreSQL<br/>Neon")]
    API --> GH["GitHub REST API"]
    API --> LLM["Google Gemini<br/>via LangChain"]
```

Every backend request follows the same layers: **router → service → database / GitHub / AI**.

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy, Pydantic |
| Database | PostgreSQL (Neon) |
| Auth | JWT (`python-jose`), password hashing with Argon2 |
| GitHub | GitHub OAuth App, `httpx` |
| AI | LangChain, `langchain-google-genai`, Google Gemini (`gemini-flash-latest`) |
| Frontend | React 19, Vite, Tailwind CSS 4, React Router, Axios, lucide-react |

## Project structure

```
gitAudit/
├── Backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py                 App, CORS, table creation, routers
│       ├── core/
│       │   ├── db.py               Database engine and session
│       │   ├── auth.py             JWT creation and the auth dependency
│       │   └── llm.py              Gemini model (LangChain)
│       ├── models/                 SQLAlchemy tables: users, reviews
│       ├── schemas/                Request bodies (…Dto) and responses
│       ├── services/
│       │   ├── auth_service.py     Register, login
│       │   ├── github_service.py   GitHub OAuth, repos, PRs, API helpers
│       │   ├── review_service.py   AI review of a pull request
│       │   └── fix_service.py      AI fix + branch / commit / PR
│       └── routers/                auth, github, review, fix
│
└── Frontend/
    └── src/
        ├── App.jsx                 Routes
        ├── components/
        │   ├── UserLayout.jsx      Navbar + page outlet
        │   ├── Userpri.jsx         Private route guard
        │   └── GithubButton.jsx    GitHub OAuth redirect
        └── pages/
            ├── GithubCallback.jsx  Finishes GitHub login / connect
            ├── Login.jsx
            ├── Register.jsx
            ├── Dashboard.jsx       Profile and repositories
            └── RepoPage.jsx        Pull requests, reviews and fixes
```

## Getting started

### Prerequisites

- Python 3.12+
- Node.js 20+
- A PostgreSQL database (for example a free [Neon](https://neon.tech) project)
- A GitHub OAuth App
- A Google Gemini API key from [Google AI Studio](https://aistudio.google.com)

### 1. Create a GitHub OAuth App

GitHub → **Settings → Developer settings → OAuth Apps → New OAuth App**

| Field | Value |
|---|---|
| Homepage URL | `http://localhost:5174` |
| Authorization callback URL | `http://localhost:5174` |
| Expire user access tokens | unticked |

Copy the **Client ID**, then generate and copy a **Client secret**.

### 2. Backend

```bash
cd Backend
python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
```

Create `Backend/.env`:

```env
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
JWT=<long random string>
GITHUB_CLIENT_ID=<client id>
GITHUB_CLIENT_SECRET=<client secret>
GOOGLE_API_KEY=<gemini api key>
```

Generate a JWT secret with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Start the API:

```bash
uvicorn app.main:app --reload --port 8001
```

Tables are created automatically on startup. Interactive API docs are at **http://localhost:8001/docs**.

### 3. Frontend

```bash
cd Frontend
npm install
```

Create `Frontend/.env`:

```env
VITE_API_URL=http://localhost:8001
VITE_GITHUB_CLIENT_ID=<same client id as the backend>
```

Start the app:

```bash
npm run dev -- --port 5174
```

Open **http://localhost:5174**.

> The frontend calls the API directly, so the CORS origin in `Backend/app/main.py` must match the frontend URL.
> If you change a port, also update the URLs in the GitHub OAuth App.

## Environment variables

| Variable | Where | Description |
|---|---|---|
| `DATABASE_URL` | Backend | PostgreSQL connection string |
| `JWT` | Backend | Secret used to sign login tokens |
| `GITHUB_CLIENT_ID` | Backend | GitHub OAuth App client ID |
| `GITHUB_CLIENT_SECRET` | Backend | GitHub OAuth App client secret |
| `GOOGLE_API_KEY` | Backend | Google Gemini API key |
| `FRONTEND_URL` | Backend (optional) | Where `/github/callback` forwards to (default `http://localhost:5174`) |
| `VITE_API_URL` | Frontend | Backend base URL |
| `VITE_GITHUB_CLIENT_ID` | Frontend | GitHub OAuth App client ID |

## API reference

All endpoints except register, login and GitHub login require `Authorization: Bearer <token>`.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/register` | Create an account `{name, email, password}` |
| `POST` | `/login` | Log in, returns `{access_token}` |
| `GET` | `/me` | Current user |
| `POST` | `/github/login` | Log in or sign up with a GitHub OAuth `code` |
| `POST` | `/github/connect` | Link GitHub to the current user |
| `GET` | `/github/callback` | Forwards GitHub's `?code=` to the frontend |
| `GET` | `/github/repos` | The user's repositories (30 most recently updated) |
| `GET` | `/github/repos/{owner}/{name}/pulls` | Open pull requests of a repository |
| `POST` | `/reviews` | Review a PR with AI `{repo, pr_number}` |
| `GET` | `/reviews?repo=owner/name` | Saved reviews of a repository, newest first |
| `POST` | `/fixes` | Generate a fix for one finding `{repo, pr_number, finding}` |
| `POST` | `/fixes/apply` | Create branch, commit and PR `{repo, pr_number, file, new_code, title}` |

### Example finding

```json
{
  "file": "Backend/order_utils.py",
  "line": 11,
  "severity": "high",
  "category": "security",
  "title": "SQL injection",
  "explanation": "User input is concatenated directly into the SQL query.",
  "suggestion": "Use a parameterized query."
}
```

## GitHub API integration

All GitHub access goes through the official [GitHub REST API](https://docs.github.com/en/rest) with the user's OAuth token
(`Authorization: Bearer <token>`). The calls live in `github_service.py` and `fix_service.py`.

### Authentication (OAuth App)

| Step | Call | Docs |
|---|---|---|
| Send the user to GitHub | `GET https://github.com/login/oauth/authorize?client_id=…&scope=repo user:email&state=…` | [Authorizing OAuth apps](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps) |
| Exchange `code` for a token | `POST https://github.com/login/oauth/access_token` | same page |
| Permissions requested | `repo`, `user:email` | [Scopes for OAuth apps](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps) |

### Reading data

| Used for | Endpoint | Docs |
|---|---|---|
| Current GitHub user | `GET /user` | [Get the authenticated user](https://docs.github.com/en/rest/users/users#get-the-authenticated-user) |
| Primary email | `GET /user/emails` | [Emails](https://docs.github.com/en/rest/users/emails) |
| Repository list | `GET /user/repos?sort=updated` | [List repositories for the authenticated user](https://docs.github.com/en/rest/repos/repos#list-repositories-for-the-authenticated-user) |
| Open pull requests | `GET /repos/{owner}/{repo}/pulls` | [Pull requests](https://docs.github.com/en/rest/pulls/pulls) |
| One pull request | `GET /repos/{owner}/{repo}/pulls/{number}` | [Pull requests](https://docs.github.com/en/rest/pulls/pulls) |
| Changed files + patches | `GET /repos/{owner}/{repo}/pulls/{number}/files` | [Pull requests](https://docs.github.com/en/rest/pulls/pulls) |
| A file's content and `sha` | `GET /repos/{owner}/{repo}/contents/{path}?ref={branch}` | [Repository contents](https://docs.github.com/en/rest/repos/contents) |

### Writing a fix

| Step | Endpoint | Docs |
|---|---|---|
| 1. Create a branch from the PR's head commit | `POST /repos/{owner}/{repo}/git/refs` | [Git references](https://docs.github.com/en/rest/git/refs) |
| 2. Commit the fixed file to that branch | `PUT /repos/{owner}/{repo}/contents/{path}` | [Repository contents](https://docs.github.com/en/rest/repos/contents) |
| 3. Open a pull request into the PR's branch | `POST /repos/{owner}/{repo}/pulls` | [Pull requests](https://docs.github.com/en/rest/pulls/pulls) |

### Things worth knowing

- **Why the file `sha` is sent on update.** GitHub uses it to check that you are changing the latest version of the file. If someone changed the file in between, the request fails instead of silently overwriting their work.
- **Why base64.** The Contents API sends and receives file content as base64, so the code decodes it when reading and encodes it when writing.
- **A branch is a reference.** Creating a branch means creating `refs/heads/<name>` that points at a commit `sha`.
- **Pagination.** List endpoints return 30 items by default ([pagination](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api)).
- **Rate limits.** Authenticated requests are limited per hour ([rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)).

### Other references

| Topic | Docs |
|---|---|
| HTTP client used by the backend | [httpx](https://www.python-httpx.org) |
| Typed AI output (`with_structured_output`) | [LangChain structured output](https://python.langchain.com/docs/how_to/structured_output/) |
| API framework | [FastAPI](https://fastapi.tiangolo.com) |

Interview notes on how this was built: [docs/INTERVIEW_PREP.md](docs/INTERVIEW_PREP.md).

## Data model

**users**: `id`, `name`, `email` (unique), `hashed_password` (empty for GitHub-only accounts), `github_id`, `github_username`, `github_token`

**reviews**: `id`, `user_id`, `repo`, `pr_number`, `pr_title`, `ai`, `summary`, `findings` (JSON), `created_at`

> `create_all` only creates missing tables. It does not add new columns to existing tables, so schema changes need an `ALTER TABLE` until migrations are added.

## Security notes

- Passwords are hashed with Argon2. Raw passwords are never stored.
- The user's GitHub access token stays on the server and is never sent to the browser.
- The OAuth `state` parameter is checked to protect the GitHub login from CSRF.
- AI fixes never touch the default branch and are never merged automatically.
- ⚠️ **Before production:** encrypt GitHub tokens at rest, and use strong, freshly rotated secrets for `JWT`, the GitHub client secret, the Gemini key and the database password.

## Troubleshooting

| Problem | Solution |
|---|---|
| Backend is very slow to start, or database calls hang | Usually broken IPv6 on the machine: each IPv6 address of the database times out before IPv4 is tried. `connect_timeout` in `db.py` limits the wait. A database region closer to you also helps a lot. |
| `column ... does not exist` | The table is older than the model. Add the column with `ALTER TABLE`. |
| CORS or network errors in the browser | Check `VITE_API_URL`, that the backend is running, and the CORS origin in `main.py`. |
| GitHub: "redirect_uri is not associated" | The OAuth App callback URL must be `http://localhost:5174`. |
| GitHub calls fail or repositories disappear | The token expired or was revoked. Use **Reconnect GitHub**. Make sure "Expire user access tokens" is unticked. |
| Gemini `429 RESOURCE_EXHAUSTED` | Free-tier quota used up. Use `gemini-flash-latest`, wait, or enable billing. |
| Sent back to the login page | The session token expired after 60 minutes. Log in again. |

## Roadmap

- [x] Email / password and GitHub authentication
- [x] AI review of pull requests with structured findings
- [x] Fix with AI → human approval → pull request
- [ ] Unit tests generated with each fix, with automatic retry on failure
- [ ] Store fixes and their status (pending / approved / rejected)
- [ ] Automatic review when a PR is opened (GitHub webhook)
- [ ] Multi-agent review with LangGraph (structure, security, fix + tests)
- [ ] Alembic migrations
- [ ] Encrypt GitHub tokens at rest
- [ ] Deployment
