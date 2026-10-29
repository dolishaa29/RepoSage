import { Link } from 'react-router-dom';
import { FixIcon, SearchIcon } from './Icons';

const pill = (status) => (status === "passed" ? "bg-ok-soft text-ok-text" : status === "failed" ? "bg-high-soft text-high-text" : "bg-surface-2 text-ink-2");

// items: [{ kind, repo, pr_number, title, status, created_at }]
const RecentActivity = ({ items }) => {
  return (
    <div className="h-full p-5 bg-surface border border-line rounded-2xl flex flex-col gap-1.5">
      <h2 className="mb-2 font-display text-lg font-bold">Recent activity</h2>
      {items.map((item, i) => (
        <Link key={i} to={`/repo/${item.repo}`} className="flex items-center gap-3.5 min-h-14 px-3 py-2 rounded-xl hover:bg-surface-2">
          {item.kind === "review" ? (
            <span className="shrink-0 w-10 h-10 rounded-xl flex items-center justify-center bg-accent-soft text-accent-text"><SearchIcon /></span>
          ) : (
            <span className="shrink-0 w-10 h-10 rounded-xl flex items-center justify-center bg-teal-soft text-teal-text"><FixIcon /></span>
          )}
          <span className="flex-1 min-w-0">
            <span className="block text-sm font-semibold truncate">{item.kind === "review" ? "Review" : "Fix"} · {item.title}</span>
            <span className="block text-xs text-muted font-mono truncate">
              {item.repo} #{item.pr_number} · {new Date(item.created_at).toLocaleDateString()}
            </span>
          </span>
          <span className={`shrink-0 px-2.5 py-1 rounded-full text-xs font-bold ${pill(item.status)}`}>{item.status}</span>
        </Link>
      ))}
      {items.length === 0 && <p className="text-sm text-muted">No reviews yet. Open a repo and review a pull request.</p>}
    </div>
  );
};

export default RecentActivity;
