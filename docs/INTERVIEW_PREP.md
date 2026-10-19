# Interview prep: gitAudit

## "How did you integrate GitHub?"

> I integrated GitHub using an **OAuth App**. The user authorizes on GitHub, GitHub redirects back with a one-time `code`, and my backend exchanges it for an access token. The token stays on the server, never in the browser. I also verify the OAuth `state` parameter to prevent CSRF.
>
> After that I call the **GitHub REST API** with that token. For reviews I fetch the PR and its changed files. Each file has a `patch`, which I join into one diff and send to Gemini through LangChain with **structured output**, so I get typed findings back instead of free text.
>
> For auto-fix I follow the normal Git flow through the API: read the file with the Contents API to get its content and `sha`, create a branch with the Git Refs API, commit the fixed file with a PUT to the Contents API, and open a pull request. **Nothing is merged automatically.** A human reviews the PR.

## "How did you learn it?"

> I used the official GitHub REST API docs for each endpoint, tested the calls with curl, and used AI tools to speed up writing code. But I understand every call and why it's needed, for example why the file update needs the `sha`.

## Be ready to explain in your own words

- **Why the `sha` on file update:** GitHub checks that you are changing the latest version of the file, so nobody's work gets overwritten by mistake.
- **Why base64:** the Contents API sends and receives file content as base64.
- **Branch = reference:** creating a branch means creating `refs/heads/<name>` that points at a commit `sha`.
- **Why the token stays on the server:** if it reached the browser, any XSS bug could steal access to the user's repos.
- **Why structured output:** the model must return a `ReviewResult` object (summary + findings), so the code never has to parse free text.
- **Why a human approves fixes:** AI can be wrong, so the fix is opened as a PR on a new branch and is never merged automatically.

The endpoint-by-endpoint list with doc links is in the README, under **GitHub API integration**.
