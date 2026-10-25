import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import Cookies from 'js-cookie';

const API = import.meta.env.VITE_API_URL;
const authHeaders = () => ({ headers: { Authorization: `Bearer ${Cookies.get("token")}` } });

const SEVERITY = {
  high: "border-red-500 text-red-600",
  medium: "border-amber-500 text-amber-600",
  low: "border-blue-500 text-blue-600",
};

const CI_STATUS = {
  running: "Tests running",
  passed: "Tests passed ✅",
  failed: "Tests failed ❌",
  skipped: "No test for this file",
};

const button = "py-2 px-4 text-xs font-bold rounded-xl disabled:opacity-50";
const primary = `${button} bg-indigo-600 hover:bg-indigo-700 text-white`;
const secondary = `${button} bg-white border border-slate-200 hover:border-indigo-300 text-indigo-600`;

const RepoPage = () => {
  const { owner, name } = useParams();
  const repo = `${owner}/${name}`;
  const [pulls, setPulls] = useState(null);
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

  const runReview = async (prNumber) => {
    setError("");
    setReviewing(prNumber);
    try {
      const response = await axios.post(`${API}/reviews`, { repo, pr_number: prNumber }, authHeaders());
      setReviews([response.data, ...reviews]);
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
      const response = await axios.post(`${API}/github/repos/${repo}/index`, {}, authHeaders());
      setChunks(response.data.chunks);
    } catch (err) {
      handleError(err, "Indexing failed.");
    } finally {
      setIndexing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <Link to="/dashboard" className="text-xs font-bold text-slate-400 hover:text-indigo-600">← Back</Link>
      <h1 className="text-3xl font-bold mt-4 break-all">{repo}</h1>
      <div className="mt-3 mb-8 flex flex-wrap items-center gap-3">
        <button onClick={indexRepo} disabled={indexing} className={secondary}>
          {indexing ? "Indexing code…" : chunks ? "Index code again" : "Index code for AI search"}
        </button>
        <span className="text-xs text-slate-400">
          {chunks ? `${chunks} code chunks indexed, agents can search code by meaning` : "Not indexed, agents use exact search only"}
        </span>
      </div>

      {error && <p className="mb-6 p-4 bg-red-50 text-red-700 text-sm font-semibold rounded-2xl">{error}</p>}
      {pulls === null && <p className="text-slate-400">Loading pull requests...</p>}
      {pulls?.length === 0 && <p className="text-slate-400">No open pull requests.</p>}

      <div className="space-y-5">
        {pulls?.map((pr) => {
          const review = reviews.find((r) => r.pr_number === pr.number);
          return (
            <div key={pr.number} className="p-6 bg-white border border-slate-100 rounded-3xl">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <a href={pr.html_url} target="_blank" rel="noreferrer" className="font-bold hover:text-indigo-600">
                    #{pr.number} {pr.title} ↗
                  </a>
                  <p className="text-xs text-slate-400">by {pr.author}</p>
                </div>
                <button onClick={() => runReview(pr.number)} disabled={reviewing !== null} className={primary}>
                  {reviewing === pr.number ? "Reviewing… (can take a minute)" : review ? "Review again" : "Review with AI"}
                </button>
              </div>
              {review && <Review review={review} repo={repo} fixes={fixes} setFixes={setFixes} />}
            </div>
          );
        })}
      </div>
    </div>
  );
};

const Review = ({ review, repo, fixes, setFixes }) => (
  <div className="mt-6 pt-6 border-t border-slate-100">
    <p className="text-sm text-slate-600 mb-4">{review.summary}</p>
    {review.findings.length === 0 && <p className="text-sm font-bold text-emerald-600">No problems found.</p>}

    <div className="space-y-3">
      {review.findings.map((f, i) => (
        <div key={i} className={`p-4 bg-slate-50 rounded-2xl border-l-4 ${SEVERITY[f.severity]}`}>
          <p className="text-sm">
            <span className="font-bold uppercase text-xs">{f.severity}</span>{" "}
            <span className="font-bold text-slate-800">{f.title}</span>{" "}
            <span className="text-xs text-slate-400 font-mono">{f.file}{f.line ? `:${f.line}` : ""}</span>
          </p>
          <p className="text-sm text-slate-600 mt-1">{f.explanation}</p>
          <p className="text-sm text-slate-600 mt-1"><b>Fix:</b> {f.suggestion}</p>
          <FixBox repo={repo} prNumber={review.pr_number} finding={f} fixes={fixes} setFixes={setFixes} />
        </div>
      ))}
    </div>
  </div>
);

const FixBox = ({ repo, prNumber, finding, fixes, setFixes }) => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const fix = fixes.find((x) => x.pr_number === prNumber && x.file === finding.file && x.title === finding.title);

  const send = async (url, body) => {
    setMessage("");
    setLoading(true);
    try {
      const response = await axios.post(API + url, body, authHeaders());
      setFixes([response.data, ...fixes.filter((x) => x.id !== response.data.id)]);
    } catch (err) {
      setMessage(err.response?.data?.detail || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (!fix || fix.status === "rejected") {
    return (
      <div className="mt-4">
        <button onClick={() => send("/fixes", { repo, pr_number: prNumber, finding })} disabled={loading} className={secondary}>
          {loading ? "Writing fix… (can take a minute)" : fix ? "Try another fix" : "Fix with AI"}
        </button>
        {message && <p className="text-xs mt-2 font-bold text-red-600">{message}</p>}
      </div>
    );
  }

  if (fix.status === "approved") {
    return (
      <div className="mt-4 flex flex-wrap items-center gap-3 text-sm">
        <a href={fix.pr_url} target="_blank" rel="noreferrer" className="font-bold text-emerald-600 hover:underline">Fix PR created ↗</a>
        {fix.ci_status && <span className="text-xs text-slate-500">{CI_STATUS[fix.ci_status]} · attempt {fix.attempts}</span>}
        {fix.ci_status === "running" && (
          <button onClick={() => send(`/fixes/${fix.id}/check`, {})} disabled={loading} className={secondary}>
            {loading ? "Checking..." : "Check tests"}
          </button>
        )}
        {message && <p className="w-full text-xs font-bold text-red-600">{message}</p>}
      </div>
    );
  }

  return (
    <div className="mt-4 p-4 bg-white border border-slate-100 rounded-2xl space-y-3">
      <p className="text-sm text-slate-600">{fix.explanation}</p>
      {fix.changes.map((change) => (
        <Diff key={change.file} label={change.file === fix.test_file ? `Unit test · ${change.file}` : change.file} diff={change.diff} />
      ))}
      {fix.test_file && <Code label="CI will run" code={fix.test_command} />}
      <div className="flex gap-2">
        <button onClick={() => send(`/fixes/${fix.id}/approve`, {})} disabled={loading} className={primary}>
          {loading ? "Please wait..." : "Approve & create PR"}
        </button>
        <button onClick={() => send(`/fixes/${fix.id}/reject`, {})} disabled={loading} className={`${button} text-red-500 hover:bg-red-50`}>
          Reject
        </button>
      </div>
      {message && <p className="text-xs font-bold text-red-600">{message}</p>}
    </div>
  );
};

const diffColor = (line) => {
  if (line.startsWith("+")) return "text-emerald-400";
  if (line.startsWith("-")) return "text-red-400";
  if (line.startsWith("@@")) return "text-indigo-300";
  return "text-slate-300";
};

const Diff = ({ label, diff }) => (
  <div className="min-w-0">
    <p className="text-xs font-bold text-slate-400 mb-1">{label}</p>
    <pre className="max-h-96 overflow-auto bg-slate-900 text-xs rounded-xl p-3">
      {diff.split("\n").map((line, i) => (
        <div key={i} className={diffColor(line)}>{line || " "}</div>
      ))}
    </pre>
  </div>
);

const Code = ({ label, code }) => (
  <div className="min-w-0">
    <p className="text-xs font-bold text-slate-400 mb-1">{label}</p>
    <pre className="max-h-80 overflow-auto bg-slate-900 text-slate-100 text-xs rounded-xl p-3">{code}</pre>
  </div>
);

export default RepoPage;
