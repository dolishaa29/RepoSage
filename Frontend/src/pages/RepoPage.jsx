import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import Cookies from 'js-cookie';
import { AlertCircle, ArrowLeft, CheckCircle2, ExternalLink, GitPullRequest, Sparkles, Wrench } from 'lucide-react';

const SEVERITY = {
  high: { card: 'border-l-red-500', badge: 'bg-red-50 text-red-600' },
  medium: { card: 'border-l-amber-500', badge: 'bg-amber-50 text-amber-600' },
  low: { card: 'border-l-blue-500', badge: 'bg-blue-50 text-blue-600' },
};

const CI_STATUS = {
  running: { label: 'Tests running', badge: 'bg-amber-50 text-amber-600' },
  passed: { label: 'Tests passed', badge: 'bg-emerald-50 text-emerald-600' },
  failed: { label: 'Tests failed', badge: 'bg-red-50 text-red-600' },
  skipped: { label: 'No test for this file', badge: 'bg-slate-100 text-slate-500' },
};

const RepoPage = () => {
  const { owner, name } = useParams();
  const repo = `${owner}/${name}`;
  const [pulls, setPulls] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [fixes, setFixes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [reviewing, setReviewing] = useState(null);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const headers = { Authorization: `Bearer ${Cookies.get("token")}` };

  const handleError = (err, fallback) => {
    if (err.response?.status === 401) {
      Cookies.remove("token");
      navigate("/login");
      return;
    }
    setError(err.response?.data?.detail || fallback);
  };

  useEffect(() => {
    const fetchRepo = async () => {
      try {
        const [p, r, f] = await Promise.all([
          axios.get(import.meta.env.VITE_API_URL + `/github/repos/${repo}/pulls`, { headers }),
          axios.get(import.meta.env.VITE_API_URL + "/reviews", { headers, params: { repo } }),
          axios.get(import.meta.env.VITE_API_URL + "/fixes", { headers, params: { repo } }),
        ]);
        setPulls(p.data);
        setReviews(r.data);
        setFixes(f.data);
      } catch (err) {
        handleError(err, "Couldn't load pull requests. Please try again.");
      } finally {
        setLoading(false);
      }
    };
    fetchRepo();
  }, [repo]);

  const runReview = async (prNumber) => {
    setError("");
    setReviewing(prNumber);
    try {
      const response = await axios.post(
        import.meta.env.VITE_API_URL + "/reviews",
        { repo, pr_number: prNumber },
        { headers }
      );
      setReviews([response.data, ...reviews]);
    } catch (err) {
      handleError(err, "AI review failed. Please try again.");
    } finally {
      setReviewing(null);
    }
  };

  const latestReview = (prNumber) => reviews.find((r) => r.pr_number === prNumber);

  return (
    <div className="max-w-5xl mx-auto px-6 py-10 md:px-10">
      <button
        onClick={() => navigate('/dashboard')}
        className="flex items-center gap-1.5 text-xs font-bold text-slate-400 hover:text-indigo-600 transition-colors mb-6"
      >
        <ArrowLeft size={14} /> Back to dashboard
      </button>

      {error && (
        <div className="motion-safe:animate-[fadeInUp_0.4s_ease-out_both] mb-6 flex items-center gap-3 bg-red-50 border border-red-100 rounded-2xl px-5 py-4">
          <AlertCircle size={18} className="text-red-500 shrink-0" />
          <p className="text-sm font-semibold text-red-700">{error}</p>
        </div>
      )}

      <div className="motion-safe:animate-[fadeInUp_0.4s_ease-out_both] mb-10">
        <p className="text-[10px] font-bold text-indigo-500 tracking-[0.2em] uppercase mb-1">{owner}</p>
        <h1 className="text-3xl md:text-4xl font-bold text-slate-900 tracking-tight break-all">{name}</h1>
        <p className="text-sm text-slate-400 mt-2">Open pull requests. Click "Review with AI" to check the changed code.</p>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-40">
          <div className="w-10 h-10 border-4 border-indigo-100 border-t-indigo-600 rounded-full animate-spin" />
          <p className="mt-4 text-slate-400 text-sm font-medium">Loading pull requests...</p>
        </div>
      ) : pulls.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-32 bg-white border border-slate-100 rounded-3xl">
          <GitPullRequest size={48} className="text-slate-200 mb-4" strokeWidth={1.5} />
          <h3 className="text-lg font-bold text-slate-700">No open pull requests</h3>
        </div>
      ) : (
        <div className="space-y-5">
          {pulls.map((pr, i) => {
            const review = latestReview(pr.number);
            return (
              <div
                key={pr.number}
                style={{ animationDelay: `${Math.min(i, 8) * 60}ms` }}
                className="motion-safe:animate-[fadeInUp_0.45s_ease-out_both] bg-white border border-slate-100 rounded-3xl p-6 shadow-sm"
              >
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div className="flex items-center gap-4 min-w-0">
                    <div className="p-3 bg-indigo-50 rounded-2xl shrink-0">
                      <GitPullRequest size={20} className="text-indigo-600" />
                    </div>
                    <div className="min-w-0">
                      <a
                        href={pr.html_url}
                        target="_blank"
                        rel="noreferrer"
                        className="flex items-center gap-1.5 font-bold text-slate-800 tracking-tight hover:text-indigo-600 transition-colors"
                      >
                        #{pr.number} {pr.title} <ExternalLink size={13} className="shrink-0" />
                      </a>
                      <p className="text-xs text-slate-400 mt-0.5">by {pr.author}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => runReview(pr.number)}
                    disabled={reviewing !== null}
                    className="flex items-center gap-2 py-3 px-5 bg-gradient-to-r from-violet-600 to-indigo-600 hover:opacity-90 text-white text-sm font-bold rounded-2xl shadow-lg shadow-indigo-100 transition-all active:scale-[0.98] disabled:opacity-50"
                  >
                    <Sparkles size={15} />
                    {reviewing === pr.number ? "Reviewing… (can take a minute)" : review ? "Review again" : "Review with AI"}
                  </button>
                </div>
                {review && <ReviewResult review={review} repo={repo} fixes={fixes} setFixes={setFixes} />}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

const ReviewResult = ({ review, repo, fixes, setFixes }) => (
  <div className="mt-6 pt-6 border-t border-slate-100">
    {review.ai && (
      <p className="text-[10px] font-bold text-indigo-500 uppercase tracking-widest mb-2">Reviewed by {review.ai}</p>
    )}
    <p className="text-sm text-slate-600 leading-relaxed mb-5">{review.summary}</p>

    {review.findings.length === 0 && (
      <p className="flex items-center gap-2 text-sm font-bold text-emerald-600">
        <CheckCircle2 size={16} /> No problems found.
      </p>
    )}

    <div className="space-y-3">
      {review.findings.map((f, i) => (
        <div key={i} className={`p-4 bg-slate-50 rounded-2xl border-l-4 ${SEVERITY[f.severity]?.card}`}>
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-widest ${SEVERITY[f.severity]?.badge}`}>
              {f.severity}
            </span>
            <span className="font-bold text-slate-800 text-sm">{f.title}</span>
            <span className="text-xs text-slate-400 font-mono">
              {f.file}
              {f.line ? `:${f.line}` : ""}
            </span>
          </div>
          <p className="text-sm text-slate-600">{f.explanation}</p>
          <p className="text-sm text-slate-600 mt-1.5">
            <span className="font-bold text-slate-800">Fix:</span> {f.suggestion}
          </p>
          <FixBox repo={repo} prNumber={review.pr_number} finding={f} fixes={fixes} setFixes={setFixes} />
        </div>
      ))}
    </div>
  </div>
);

const FixBox = ({ repo, prNumber, finding, fixes, setFixes }) => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const headers = { Authorization: `Bearer ${Cookies.get("token")}` };

  const fix = fixes.find((x) => x.pr_number === prNumber && x.file === finding.file && x.title === finding.title);

  const saveFix = (updated) => setFixes([updated, ...fixes.filter((x) => x.id !== updated.id)]);

  const send = async (url, body, fallback) => {
    setMessage("");
    setLoading(true);
    try {
      const response = await axios.post(import.meta.env.VITE_API_URL + url, body, { headers });
      saveFix(response.data);
    } catch (err) {
      setMessage(err.response?.data?.detail || fallback);
    } finally {
      setLoading(false);
    }
  };

  const makeFix = () => send("/fixes", { repo, pr_number: prNumber, finding }, "AI fix failed. Please try again.");
  const approve = () => send(`/fixes/${fix.id}/approve`, {}, "Could not create the pull request. Please try again.");
  const reject = () => send(`/fixes/${fix.id}/reject`, {}, "Could not reject the fix. Please try again.");
  const checkTests = () => send(`/fixes/${fix.id}/check`, {}, "Could not check the tests. Please try again.");

  if (fix?.status === "approved") {
    return (
      <div className="mt-4 flex flex-wrap items-center gap-3">
        <a
          href={fix.pr_url}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-2 text-sm font-bold text-emerald-600 hover:underline"
        >
          <CheckCircle2 size={16} /> Fix pull request created. Open it <ExternalLink size={13} />
        </a>
        {fix.ci_status && (
          <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest ${CI_STATUS[fix.ci_status]?.badge}`}>
            {CI_STATUS[fix.ci_status]?.label} · attempt {fix.attempts}
          </span>
        )}
        {fix.ci_status === "running" && (
          <button
            onClick={checkTests}
            disabled={loading}
            className="py-2 px-4 bg-white border border-slate-200 hover:border-indigo-300 text-indigo-600 text-xs font-bold rounded-xl transition-all disabled:opacity-50"
          >
            {loading ? "Checking..." : "Check tests"}
          </button>
        )}
        {message && <p className="w-full text-xs font-bold text-red-600">{message}</p>}
      </div>
    );
  }

  return (
    <div className="mt-4">
      {(!fix || fix.status === "rejected") && (
        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={makeFix}
            disabled={loading}
            className="flex items-center gap-2 py-2 px-4 bg-white border border-slate-200 hover:border-indigo-300 text-indigo-600 text-xs font-bold rounded-xl transition-all disabled:opacity-50"
          >
            <Wrench size={13} /> {loading ? "Writing fix… (can take a minute)" : fix ? "Try another fix" : "Fix with AI"}
          </button>
          {fix && <span className="text-xs font-bold text-slate-400">Last fix was rejected</span>}
        </div>
      )}

      {fix?.status === "pending" && (
        <div className="bg-white border border-slate-100 rounded-2xl p-4">
          <p className="text-sm text-slate-600 mb-3">{fix.explanation}</p>
          <div className="grid md:grid-cols-2 gap-3">
            <CodeBlock label="Old code" code={fix.old_code} />
            <CodeBlock label="New code" code={fix.new_code} />
          </div>
          {fix.test_file && (
            <div className="mt-3">
              <CodeBlock label={`Unit test · ${fix.test_file}`} code={fix.test_code} />
              <div className="mt-3">
                <CodeBlock label="CI will run" code={fix.test_command} />
              </div>
            </div>
          )}
          <div className="flex flex-wrap gap-2 mt-4">
            <button
              onClick={approve}
              disabled={loading}
              className="py-2.5 px-5 bg-gradient-to-r from-violet-600 to-indigo-600 hover:opacity-90 text-white text-xs font-bold rounded-xl transition-all disabled:opacity-50"
            >
              {loading ? "Please wait..." : "Approve & create PR"}
            </button>
            <button
              onClick={reject}
              disabled={loading}
              className="py-2.5 px-5 text-red-500 hover:bg-red-50 text-xs font-bold rounded-xl transition-all disabled:opacity-50"
            >
              Reject
            </button>
          </div>
        </div>
      )}

      {message && <p className="text-xs mt-3 font-bold text-red-600">{message}</p>}
    </div>
  );
};

const CodeBlock = ({ label, code }) => (
  <div className="min-w-0">
    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">{label}</p>
    <pre className="max-h-80 overflow-auto bg-slate-900 text-slate-100 text-xs rounded-xl p-3 font-mono">{code}</pre>
  </div>
);

export default RepoPage;
