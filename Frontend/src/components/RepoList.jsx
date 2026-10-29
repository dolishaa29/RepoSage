import { useState } from 'react';
import { Link } from 'react-router-dom';

const RepoList = ({ repos, showAccount }) => {
  const [search, setSearch] = useState("");
  const shown = repos.filter((r) => r.full_name.toLowerCase().includes(search.toLowerCase()));

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <h2 className="font-bold text-slate-700">Your repositories ({repos.length})</h2>
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search repos..."
          className="w-full sm:w-64 py-2 px-4 text-sm bg-white border border-slate-200 rounded-xl outline-none focus:border-indigo-400"
        />
      </div>
      <div className="space-y-3">
        {shown.map((r) => (
          <Link
            key={r.id}
            to={`/repo/${r.full_name}`}
            className="flex items-center justify-between gap-4 p-5 bg-white border border-slate-100 rounded-2xl hover:border-indigo-300"
          >
            <div className="min-w-0">
              <p className="font-bold text-slate-800 break-all">{r.full_name}</p>
              {r.description && <p className="text-xs text-slate-400 truncate">{r.description}</p>}
            </div>
            <span className="shrink-0 text-right text-xs text-slate-400">
              {r.language} · {r.private ? "Private" : "Public"}
              {showAccount && <span className="block">via @{r.account}</span>}
            </span>
          </Link>
        ))}
        {shown.length === 0 && <p className="text-slate-400">No repositories found.</p>}
      </div>
    </div>
  );
};

export default RepoList;
