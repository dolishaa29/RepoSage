import { useEffect, useState } from 'react'
import { api } from '../api'
import { GithubButton, TopBar } from '../components'

export default function Dashboard({ user, onLogout, notice }) {
  const connected = Boolean(user.github_username)
  const [repos, setRepos] = useState([])
  const [loading, setLoading] = useState(connected)
  const [error, setError] = useState(notice || '')

  useEffect(() => {
    if (!connected) return
    api
      .githubRepos()
      .then(setRepos)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [connected])

  return (
    <div className="layout">
      <TopBar user={user} onLogout={onLogout} />
      <main className="content">
        {error && <div className="alert error">{error}</div>}

        <section className="card">
          <h2>Dashboard</h2>
          <dl className="profile">
            <dt>Name</dt>
            <dd>{user.name}</dd>
            <dt>Email</dt>
            <dd>{user.email}</dd>
            <dt>GitHub</dt>
            <dd>{connected ? `@${user.github_username}` : 'Not connected'}</dd>
          </dl>
          {connected && (
            <div className="reconnect">
              <p className="muted small-text">GitHub not working, or repos missing? Connect it again.</p>
              <GithubButton label="Reconnect GitHub" />
            </div>
          )}
        </section>

        <section className="card">
          <h2>Your repositories</h2>
          {!connected && (
            <>
              <p className="muted">Connect your GitHub account to see your repositories, including private ones.</p>
              <GithubButton label="Connect GitHub" />
            </>
          )}
          {connected && loading && <p className="muted">Loading repositories…</p>}
          {connected && !loading && !error && repos.length === 0 && <p className="muted">No repositories found.</p>}
          {repos.length > 0 && (
            <ul className="repos">
              {repos.map((r) => (
                <li key={r.id} className="repo">
                  <div>
                    <a className="repo-name" href={`#/repo/${r.full_name}`}>
                      {r.full_name}
                    </a>
                    {r.description && <p className="muted repo-desc">{r.description}</p>}
                  </div>
                  <div className="repo-meta">
                    {r.language && <span className="muted">{r.language}</span>}
                    <span className="tag">{r.private ? 'Private' : 'Public'}</span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>
    </div>
  )
}
