import { useEffect, useState } from 'react'
import { api } from '../api'
import { TopBar } from '../components'

export default function RepoPage({ user, onLogout, repo }) {
  const [pulls, setPulls] = useState([])
  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(true)
  const [reviewing, setReviewing] = useState(null) // number of the PR being reviewed
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([api.githubPulls(repo), api.listReviews(repo)])
      .then(([p, r]) => {
        setPulls(p)
        setReviews(r)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [repo])

  const runReview = async (prNumber) => {
    setError('')
    setReviewing(prNumber)
    try {
      const review = await api.createReview(repo, prNumber)
      setReviews([review, ...reviews])
    } catch (err) {
      setError(err.message)
    } finally {
      setReviewing(null)
    }
  }

  // newest review of a PR (reviews come newest first)
  const latestReview = (prNumber) => reviews.find((r) => r.pr_number === prNumber)

  return (
    <div className="layout">
      <TopBar user={user} onLogout={onLogout} />
      <main className="content">
        <a href="#/" className="back">← Back to dashboard</a>
        {error && <div className="alert error">{error}</div>}

        <section className="card">
          <h2>{repo}</h2>
          <p className="muted">Open pull requests. Click "Review with AI" to check the changed code.</p>

          {loading && <p className="muted">Loading pull requests…</p>}
          {!loading && pulls.length === 0 && <p className="muted">No open pull requests.</p>}

          <ul className="pulls">
            {pulls.map((pr) => {
              const review = latestReview(pr.number)
              return (
                <li key={pr.number} className="pull">
                  <div className="pull-head">
                    <div>
                      <a className="pull-title" href={pr.html_url} target="_blank" rel="noreferrer">
                        #{pr.number} {pr.title}
                      </a>
                      <div className="muted small-text">by {pr.author}</div>
                    </div>
                    <button
                      className="btn primary"
                      onClick={() => runReview(pr.number)}
                      disabled={reviewing !== null}
                    >
                      {reviewing === pr.number ? 'Reviewing… (can take a minute)' : review ? 'Review again' : 'Review with AI'}
                    </button>
                  </div>
                  {review && <ReviewResult review={review} />}
                </li>
              )
            })}
          </ul>
        </section>
      </main>
    </div>
  )
}

function ReviewResult({ review }) {
  return (
    <div className="review">
      <p className="review-summary">{review.summary}</p>
      {review.findings.length === 0 && <p className="good">No problems found.</p>}
      <ul className="findings">
        {review.findings.map((f, i) => (
          <li key={i} className={`finding ${f.severity}`}>
            <div className="finding-head">
              <span className={`sev ${f.severity}`}>{f.severity}</span>
              <strong>{f.title}</strong>
              <span className="muted mono">
                {f.file}
                {f.line ? `:${f.line}` : ''}
              </span>
            </div>
            <p>{f.explanation}</p>
            <p>
              <strong>Fix:</strong> {f.suggestion}
            </p>
          </li>
        ))}
      </ul>
    </div>
  )
}
