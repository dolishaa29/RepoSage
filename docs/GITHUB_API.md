# GitHub API used by gitAudit

All calls use the official [GitHub REST API](https://docs.github.com/en/rest) with the user's OAuth token
(`Authorization: Bearer <token>`). Code: `services/github_service.py` and `services/fix/github_files.py`.

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
| File content + `sha` | `GET /repos/{owner}/{repo}/contents/{path}?ref={branch}` | [Contents](https://docs.github.com/en/rest/repos/contents) |

## Writing a fix and checking CI

| Step | Endpoint | Docs |
|---|---|---|
| Create a branch | `POST /repos/{owner}/{repo}/git/refs` | [Git references](https://docs.github.com/en/rest/git/refs) |
| Commit a file | `PUT /repos/{owner}/{repo}/contents/{path}` | [Contents](https://docs.github.com/en/rest/repos/contents) |
| Open a PR | `POST /repos/{owner}/{repo}/pulls` | [Pull requests](https://docs.github.com/en/rest/pulls/pulls) |
| Latest commit of a branch | `GET /repos/{owner}/{repo}/branches/{branch}` | [Branches](https://docs.github.com/en/rest/branches/branches) |
| CI run of that commit | `GET /repos/{owner}/{repo}/actions/runs?branch=…&head_sha=…` | [Workflow runs](https://docs.github.com/en/rest/actions/workflow-runs) |
| Test log | `GET …/actions/runs/{id}/jobs`, then `GET …/actions/jobs/{job_id}/logs` | [Workflow jobs](https://docs.github.com/en/rest/actions/workflow-jobs) |

## Good to know

- **`sha` on update:** proves you are editing the latest version, so nobody's newer change is overwritten.
- **base64:** the Contents API sends and receives file content as base64.
- **Branch = reference:** creating a branch means creating `refs/heads/<name>` pointing at a commit.
- **Pagination:** list endpoints return 30 items by default ([pagination](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api)).
- **Rate limits:** [rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api).
