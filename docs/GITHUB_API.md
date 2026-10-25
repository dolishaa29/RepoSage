# GitHub API used by gitAudit

All calls use the official [GitHub REST API](https://docs.github.com/en/rest) with the user's OAuth token
(`Authorization: Bearer <token>`). Code: `services/github_service.py`, `services/fix/github_files.py` and the agent tools in `services/agent/tools.py`.

## Authentication (OAuth App)

| Step | Call | Docs |
|---|---|---|
| Send the user to GitHub | `GET https://github.com/login/oauth/authorize?client_id=…&scope=repo workflow user:email&state=…` | [Authorizing OAuth apps](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps) |
| Exchange `code` for a token | `POST https://github.com/login/oauth/access_token` | same page |
| Permissions | `repo`, `workflow`, `user:email` | [Scopes for OAuth apps](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps) |

## Reading

| Used for | Endpoint | Docs |
|---|---|---|
| Current user | `GET /user` | [Users](https://docs.github.com/en/rest/users/users#get-the-authenticated-user) |
| Primary email | `GET /user/emails` | [Emails](https://docs.github.com/en/rest/users/emails) |
| Repositories | `GET /user/repos?sort=updated` | [Repos](https://docs.github.com/en/rest/repos/repos#list-repositories-for-the-authenticated-user) |
| Pull requests, one PR, changed files | `GET /repos/{owner}/{repo}/pulls`, `…/pulls/{n}`, `…/pulls/{n}/files` | [Pull requests](https://docs.github.com/en/rest/pulls/pulls) |
| Raw file text (agent `read_file`) | `GET /repos/{owner}/{repo}/contents/{path}?ref={sha}` with `Accept: application/vnd.github.raw` (files up to 100 MB) | [Contents](https://docs.github.com/en/rest/repos/contents) |
| All file paths (agent `list_files`) | `GET /repos/{owner}/{repo}/git/trees/{sha}?recursive=1` | [Git trees](https://docs.github.com/en/rest/git/trees) |
| Exact code search (agent `search_code`) | `GET /search/code?q=<text>+repo:{owner}/{repo}` with `Accept: application/vnd.github.text-match+json` | [Search code](https://docs.github.com/en/rest/search/search#search-code) |
| Whole repo for the pgvector index | `GET /repos/{owner}/{repo}/tarball` (redirects to a `.tar.gz`) | [Download a tarball](https://docs.github.com/en/rest/repos/contents#download-a-repository-archive-tar) |

## Writing a fix and checking CI

| Step | Endpoint | Docs |
|---|---|---|
| Create a branch | `POST /repos/{owner}/{repo}/git/refs` | [Git references](https://docs.github.com/en/rest/git/refs) |
| Delete a branch (when approve fails halfway) | `DELETE /repos/{owner}/{repo}/git/refs/heads/{branch}` | [Git references](https://docs.github.com/en/rest/git/refs) |
| Commit many files at once | `GET …/git/commits/{head}` → `POST …/git/trees` (with `base_tree`) → `POST …/git/commits` → `PATCH …/git/refs/heads/{branch}` | [Git database](https://docs.github.com/en/rest/guides/using-the-rest-api-to-interact-with-your-git-database) |
| Open a PR | `POST /repos/{owner}/{repo}/pulls` | [Pull requests](https://docs.github.com/en/rest/pulls/pulls) |
| Latest commit of a branch | `GET /repos/{owner}/{repo}/branches/{branch}` | [Branches](https://docs.github.com/en/rest/branches/branches) |
| CI run of that commit | `GET /repos/{owner}/{repo}/actions/runs?branch=…&head_sha=…` | [Workflow runs](https://docs.github.com/en/rest/actions/workflow-runs) |
| Test log | `GET …/actions/runs/{id}/jobs`, then `GET …/actions/jobs/{job_id}/logs` | [Workflow jobs](https://docs.github.com/en/rest/actions/workflow-jobs) |

## Good to know

- **One commit for many files:** a tree lists the new files on top of `base_tree` (the old tree), a commit points at that tree with the old head as parent, and moving the branch ref to the new commit publishes it.
- **Code search** only looks at the default branch and allows about 10 searches per minute.
- **Branch = reference:** creating a branch means creating `refs/heads/<name>` pointing at a commit.
- **Pagination:** list endpoints return 30 items by default ([pagination](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api)).
- **Rate limits:** [rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api).
