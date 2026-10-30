import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import Cookies from 'js-cookie';
import { CheckIcon, FixIcon } from '../components/Icons';
import { waitForJob } from '../jobs';

const API = import.meta.env.VITE_API_URL;
const REFRESH_FIXES_EVERY = 30000;
const authHeaders = () => ({ headers: { Authorization: `Bearer ${Cookies.get("token")}` } });

const SEVERITY = {
  high: "bg-high-soft text-high-text",
  medium: "bg-med-soft text-med-text",
  low: "bg-surface-2 text-ink-2",
};

const CATEGORY = { bug: "Bug", security: "Security", bad_practice: "Bad practice" };

const CI_STATUS = {
  running: "Tests running",
  passed: "Tests passed",
  failed: "Tests failed",
  skipped: "No test for this file",
};

const button = "min-h-11 px-5 text-sm font-bold rounded-xl disabled:opacity-50";
const primary = `${button} bg-accent text-on-accent hover:opacity-90`;
const secondary = `${button} bg-surface border border-line text-ink hover:border-accent`;
const fixButton = `${button} border border-teal text-teal-text hover:bg-teal-soft`;

const RepoPage = () => {
  const { owner, name } = useParams();
  const repo = `${owner}/${name}`;
  const [pulls, setPulls] = useState(null);
  const [selected, setSelected] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [fixes, setFixes] = useState([]);
  const [reviewing, setReviewing] = useState(null);
  const [chunks, setChunks] = useState(0);
  const [indexing, setIndexing] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleError = (err, fallback) => {
    if (err.response?.status === 401) {
      Cookies.remove("token");
      navigate("/login");
      return;
    }
    setError(err.response?.data?.detail || fallback);
  };

  useEffect(() => {
    const load = async () => {
      try {
        const [p, r, f, i] = await Promise.all([
          axios.get(`${API}/github/repos/${repo}/pulls`, authHeaders()),
          axios.get(`${API}/reviews`, { ...authHeaders(), params: { repo } }),
          axios.get(`${API}/fixes`, { ...authHeaders(), params: { repo } }),
          axios.get(`${API}/github/repos/${repo}/index`, authHeaders()),
        ]);
        setPulls(p.data);
        setSelected(p.data[0]?.number ?? null);
        setReviews(r.data);
        setFixes(f.data);
        setChunks(i.data.chunks);
      } catch (err) {
        handleError(err, "Couldn't load pull requests.");
        setPulls([]);
      }
    };
    load();
  }, [repo]);

  // shows test results without a click, the server checks them by itself
  useEffect(() => {
    const refresh = async () => {
      try {
        const response = await axios.get(`${API}/fixes`, { ...authHeaders(), params: { repo } });
        setFixes(response.data);
      } catch {
        // the next refresh tries again
      }
    };
    const timer = setInterval(refresh, REFRESH_FIXES_EVERY);
    return () => clearInterval(timer);
  }, [repo]);

  const runReview = async (prNumber) => {
    setError("");
    setReviewing(prNumber);
    try {
      const response = await waitForJob(await axios.post(`${API}/reviews`, { repo, pr_number: prNumber }, authHeaders()));
      setReviews((current) => [response.data, ...current]);
    } catch (err) {
      handleError(err, "AI review failed.");
    } finally {
      setReviewing(null);
    }
  };

  const indexRepo = async () => {
    setError("");
    setIndexing(true);
    try {
      const response = await waitForJob(await axios.post(`${API}/github/repos/${repo}/index`, {}, authHeaders()));
      setChunks(response.data.chunks);
    } catch (err) {
      handleError(err, "Indexing failed.");
    } finally {
      setIndexing(false);
    }
  };

  const pr = pulls?.find((p) => p.number === selected);
  const review = reviews.find((r) => r.pr_number === selected);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-8 lg:px-12 py-8 flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <p className="text-sm text-muted">
          <Link to="/repos" className="font-semibold text-accent-text">Repositories</Link> / {owner}
        </p>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <h1 className="font-display text-3xl font-bold tracking-tight break-all">{name}</h1>
          <div className="flex flex-wrap items-center gap-2.5">
            {chunks ? (
              <span className="h-11 px-3.5 flex items-center gap-2 rounded-xl bg-ok-soft text-ok-text text-sm font-bold">
                <CheckIcon size={16} /> Code indexed · {chunks} chunks
              </span>
            ) : (
              <span className="text-sm text-muted">Not indexed, agents use exact search only</span>
            )}
            <button onClick={indexRepo} disabled={indexing} className={secondary}>
              {indexing ? "Indexing code…" : chunks ? "Re-index code" : "Index code for AI search"}
            </button>
          </div>
        </div>
      </header>

      {error && <p className="p-4 bg-high-soft text-high-text text-sm font-semibold rounded-2xl">{error}</p>}
      {pulls === null && <p className="text-muted">Loading pull requests...</p>}
      {pulls?.length === 0 && !error && <p className="text-muted">No open pull requests.</p>}

      {pr && (
        <div className="flex flex-wrap items-start gap-6">
          <section aria-label="Open pull requests" className="flex-[1_1_280px] min-w-0 flex flex-col gap-2.5">
            <h2 className="font-display text-lg font-bold">Open pull requests</h2>
            {pulls.map((p) => {
              const latest = reviews.find((r) => r.pr_number === p.number);
              const active = p.number === selected;
              return (
                <button
                  key={p.number}
                  onClick={() => setSelected(p.number)}
                  className={`text-left p-4 rounded-2xl bg-surface ${active ? "border-2 border-accent" : "border border-line hover:border-accent"}`}
                >
                  <span className="block text-sm font-bold">#{p.number} {p.title}</span>
                  <span className="block mt-1 text-xs text-muted">by {p.author} · {latest ? "reviewed" : "not reviewed"}{latest?.risk ? ` · ${latest.risk} risk` : ""}</span>
                </button>
              );
            })}
            <button onClick={() => runReview(pr.number)} disabled={reviewing !== null} className={primary}>
              {reviewing === pr.number ? "Reviewing… (can take a minute)" : review ? "Review again" : "Review this PR with AI"}
            </button>
          </section>

          <section aria-label="Review" className="flex-[999_1_520px] min-w-0 flex flex-col gap-4">
            {review ? (
              <Review review={review} pr={pr} repo={repo} fixes={fixes} setFixes={setFixes} />
            ) : (
              <div className="p-10 bg-surface border border-line rounded-2xl text-center text-ink-2">
                <a href={pr.html_url} target="_blank" rel="noreferrer" className="font-bold text-ink">#{pr.number} {pr.title} ↗</a>
                <p className="mt-2 text-sm">Not reviewed yet. Click “Review this PR with AI”.</p>
              </div>
            )}
          </section>
        </div>
      )}
    </div>
  );
};

const Review = ({ review, pr, repo, fixes, setFixes }) => {
  const count = (level) => review.findings.filter((f) => f.severity === level).length;

  return (
    <>
      <div className="p-5 bg-surface border border-line rounded-2xl flex flex-col gap-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <a href={pr.html_url} target="_blank" rel="noreferrer" className="font-display text-xl font-bold">
            AI review · #{pr.number} {pr.title} ↗
          </a>
          <span className="text-sm text-muted">{review.ai} · {new Date(review.created_at).toLocaleDateString()}</span>
        </div>
        <p className="text-sm leading-relaxed text-ink-2">{review.summary}</p>
        <div className="flex flex-wrap gap-2">
          {review.risk && <span className={`px-2.5 py-1.5 rounded-full text-xs font-bold capitalize border border-line ${SEVERITY[review.risk]}`}>{review.risk} risk</span>}
          <span className={`px-2.5 py-1.5 rounded-full text-xs font-bold ${SEVERITY.high}`}>{count("high")} High</span>
          <span className={`px-2.5 py-1.5 rounded-full text-xs font-bold ${SEVERITY.medium}`}>{count("medium")} Medium</span>
          <span className={`px-2.5 py-1.5 rounded-full text-xs font-bold ${SEVERITY.low}`}>{count("low")} Low</span>
        </div>
      </div>

      {review.pr_summary && <PrSummary key={review.id} review={review} />}

      {review.findings.length === 0 && <p className="p-4 rounded-2xl bg-ok-soft text-ok-text text-sm font-bold">No problems found.</p>}

      {review.findings.map((f, i) => (
        <article key={`${review.id}-${i}`} className="bg-surface border border-line rounded-2xl overflow-hidden">
          <div className="p-5 flex flex-col gap-2.5">
            <div className="flex flex-wrap items-center gap-2">
              <span className={`px-2.5 py-1 rounded-md text-xs font-bold capitalize ${SEVERITY[f.severity]}`}>{f.severity}</span>
              <span className="px-2.5 py-1 rounded-md bg-surface-2 text-xs font-semibold text-ink-2">{CATEGORY[f.category]}</span>
              <span className="text-sm text-ink-2 font-mono break-all">{f.file}{f.line ? `:${f.line}` : ""}</span>
            </div>
            <h3 className="font-bold">{f.title}</h3>
            <p className="text-sm leading-relaxed text-ink-2">{f.explanation}</p>
            <p className="text-sm leading-relaxed text-ink-2"><b className="text-ink">Suggestion:</b> {f.suggestion}</p>
          </div>
          <FixBox repo={repo} prNumber={review.pr_number} finding={f} fixes={fixes} setFixes={setFixes} />
        </article>
      ))}
    </>
  );
};

const PrSummary = ({ review }) => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const publish = async () => {
    setMessage("");
    setLoading(true);
    try {
      await axios.post(`${API}/reviews/${review.id}/publish-summary`, {}, authHeaders());
      setMessage("Added to the PR description on GitHub.");
    } catch (err) {
      if (err.response?.status === 401) {
        Cookies.remove("token");
        navigate("/login");
        return;
      }
      setMessage(err.response?.data?.detail || "Couldn't update the PR description.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-5 bg-surface border border-line rounded-2xl flex flex-col gap-3">
      <h3 className="font-bold">PR summary</h3>
      <div className="text-sm leading-relaxed text-ink-2 wrap-break-word">
        {review.pr_summary.split("\n").map((line, i) => (
          line.startsWith("### ")
            ? <p key={i} className="mt-2 first:mt-0 font-semibold text-ink">{line.slice(4)}</p>
            : <p key={i}>{line}</p>
        ))}
      </div>
      <div className="flex flex-wrap items-center gap-3">
        <button onClick={publish} disabled={loading} className={secondary}>
          {loading ? "Please wait..." : "Add to PR description"}
        </button>
        {message && <span className="text-sm font-semibold text-ink-2">{message}</span>}
      </div>
    </div>
  );
};

const FixBox = ({ repo, prNumber, finding, fixes, setFixes }) => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const fix = fixes.find((x) => x.pr_number === prNumber && x.file === finding.file && x.title === finding.title);

  const send = async (url, body) => {
    setMessage("");
    setLoading(true);
    try {
      const first = await axios.post(API + url, body, authHeaders());
      const response = first.data.job_id ? await waitForJob(first) : first;
      setFixes((current) => [response.data, ...current.filter((x) => x.id !== response.data.id)]);
    } catch (err) {
      if (err.response?.status === 401) {
        Cookies.remove("token");
        navigate("/login");
        return;
      }
      setMessage(err.response?.data?.detail || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const error = message && <p className="w-full text-sm font-semibold text-high-text">{message}</p>;

  if (!fix || fix.status === "rejected") {
    return (
      <div className="px-5 pb-5 flex flex-col items-start gap-2">
        <button onClick={() => send("/fixes", { repo, pr_number: prNumber, finding })} disabled={loading} className={fixButton}>
          {loading ? "Writing fix… (can take a minute)" : fix ? "Try another fix" : "Fix with AI"}
        </button>
        {error}
      </div>
    );
  }

  if (fix.status === "approved") {
    const passed = fix.ci_status === "passed";
    return (
      <div className="px-5 pb-5 flex flex-wrap items-center gap-3">
        <a href={fix.pr_url} target="_blank" rel="noreferrer" className={`min-h-11 px-4 flex items-center rounded-xl text-sm font-bold ${passed ? "bg-ok-soft text-ok-text" : "bg-accent-soft text-accent-text"}`}>
          Fix PR created ↗
        </a>
        {fix.ci_status && (
          <span className={`text-sm font-semibold ${fix.ci_status === "failed" ? "text-high-text" : "text-ink-2"}`}>
            {CI_STATUS[fix.ci_status]} · attempt {fix.attempts}
          </span>
        )}
        {fix.ci_status === "running" && (
          <button onClick={() => send(`/fixes/${fix.id}/check`, {})} disabled={loading} className={secondary}>
            {loading ? "Checking..." : "Check tests"}
          </button>
        )}
        {error}
      </div>
    );
  }

  return (
    <div className="border-t border-line bg-surface-2 p-5 flex flex-col gap-3.5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h4 className="flex items-center gap-2 text-sm font-bold text-teal-text">
          <FixIcon size={16} /> AI fix · {fix.changes.length} {fix.changes.length === 1 ? "file" : "files"} changed
        </h4>
        <span className="text-sm text-ink-2">{fix.explanation}</span>
      </div>
      {fix.changes.map((change) => (
        <Diff key={change.file} label={change.file} isTest={change.file === fix.test_file} diff={change.diff} />
      ))}
      {fix.test_file && (
        <div className="border border-line rounded-xl overflow-hidden bg-code">
          <p className="px-3.5 py-2.5 border-b border-line text-sm font-semibold">CI will run</p>
          <pre className="px-3.5 py-2.5 overflow-x-auto font-mono text-[13px] text-ink-2">$ {fix.test_command}</pre>
        </div>
      )}
      <div className="flex flex-wrap gap-2.5">
        <button onClick={() => send(`/fixes/${fix.id}/approve`, {})} disabled={loading} className={primary}>
          {loading ? "Please wait..." : "Approve & open PR"}
        </button>
        <button onClick={() => send(`/fixes/${fix.id}/reject`, {})} disabled={loading} className={`${button} bg-surface border border-line text-high-text hover:bg-high-soft`}>
          Reject
        </button>
      </div>
      {error}
    </div>
  );
};

const diffStyle = (line) => {
  if (line.startsWith("+++") || line.startsWith("---")) return "text-muted";
  if (line.startsWith("+")) return "bg-ok-soft text-ok-text";
  if (line.startsWith("-")) return "bg-high-soft text-high-text";
  if (line.startsWith("@@")) return "text-accent-text";
  return "text-ink-2";
};

const Diff = ({ label, isTest, diff }) => (
  <div className="min-w-0 border border-line rounded-xl overflow-hidden bg-code">
    <p className="px-3.5 py-2.5 border-b border-line flex flex-wrap justify-between gap-2 text-sm font-semibold font-mono">
      <span className="break-all">{label}</span>
      {isTest && <span className="text-teal-text">new test</span>}
    </p>
    <pre className="max-h-96 overflow-auto font-mono text-[13px] leading-relaxed py-1">
      {diff.split("\n").map((line, i) => (
        <div key={i} className={`px-3.5 ${diffStyle(line)}`}>{line || " "}</div>
      ))}
    </pre>
  </div>
);

export default RepoPage;
