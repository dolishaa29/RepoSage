import { Link } from 'react-router-dom';

// items: [{ kind, repo, pr_number, title, status, created_at }]
const RecentActivity = ({ items }) => {
  return (
    <div className="p-5 bg-white border border-slate-100 rounded-2xl">
      <h2 className="mb-4 font-bold text-slate-700">Recent activity</h2>
      <div className="space-y-2">
        {items.map((item, i) => (
          <Link
            key={i}
            to={`/repo/${item.repo}`}
            className="flex items-center justify-between gap-3 p-3 rounded-xl hover:bg-slate-50"
          >
            <div className="min-w-0">
              <p className="text-sm font-semibold text-slate-800 truncate">
                {item.kind === "review" ? "🔍 Review" : "🛠️ Fix"} · {item.title}
              </p>
              <p className="text-xs text-slate-400 break-all">
                {item.repo} #{item.pr_number} · {new Date(item.created_at).toLocaleDateString()}
              </p>
            </div>
            <span className="shrink-0 text-xs font-bold text-slate-500">{item.status}</span>
          </Link>
        ))}
        {items.length === 0 && <p className="text-sm text-slate-400">No reviews yet. Open a repo and review a pull request.</p>}
      </div>
    </div>
  );
};

export default RecentActivity;
