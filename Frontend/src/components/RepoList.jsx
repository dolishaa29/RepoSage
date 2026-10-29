import { useState } from 'react';
import { Link } from 'react-router-dom';
import { SearchIcon } from './Icons';

const FILTERS = ["All", "Private", "Public"];

// limit: show only the first N repos (dashboard), with a link to all of them
const RepoList = ({ repos, showAccount, limit }) => {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("All");

  const matching = repos.filter((r) => {
    if (filter === "Private" && !r.private) return false;
    if (filter === "Public" && r.private) return false;
    return r.full_name.toLowerCase().includes(search.toLowerCase());
  });
  const shown = limit ? matching.slice(0, limit) : matching;

  return (
    <section className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="font-display text-lg font-bold">Your repositories ({repos.length})</h2>
        <div className="flex flex-wrap items-center gap-2">
          {FILTERS.map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`min-h-9 px-3.5 rounded-full text-sm font-semibold ${filter === f ? "bg-invert text-on-invert" : "bg-surface border border-line text-ink-2"}`}
            >
              {f}
            </button>
          ))}
          <label className="w-full sm:w-60 h-11 flex items-center gap-2 px-3.5 bg-surface border border-line rounded-xl text-muted focus-within:border-accent">
            <SearchIcon size={16} />
            <span className="sr-only">Search repositories</span>
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search repos…"
              className="flex-1 min-w-0 bg-transparent text-sm text-ink outline-none"
            />
          </label>
        </div>
      </div>

      <div className="grid grid-cols-[repeat(auto-fill,minmax(280px,1fr))] gap-3">
        {shown.map((r) => (
          <Link key={r.id} to={`/repo/${r.full_name}`} className="p-5 bg-surface border border-line rounded-2xl hover:border-accent flex flex-col gap-2.5">
            <span className="flex items-start justify-between gap-2">
              <span className="font-bold break-all">{r.full_name}</span>
              <span className="shrink-0 px-2 py-0.5 rounded-md border border-line text-[11px] font-semibold text-ink-2">{r.private ? "Private" : "Public"}</span>
            </span>
            {r.description && <span className="text-sm leading-relaxed text-ink-2 line-clamp-2">{r.description}</span>}
            <span className="mt-auto flex flex-wrap gap-3.5 text-xs text-muted">
              {r.language && <span>{r.language}</span>}
              {showAccount && <span>via @{r.account}</span>}
            </span>
          </Link>
        ))}
      </div>
      {shown.length === 0 && <p className="text-muted">No repositories found.</p>}
      {limit && matching.length > limit && (
        <Link to="/repos" className="self-start text-sm font-bold text-accent-text">See all {matching.length} repositories →</Link>
      )}
    </section>
  );
};

export default RepoList;
