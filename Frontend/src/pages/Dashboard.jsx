import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Cookies from 'js-cookie';
import ActivityChart from '../components/ActivityChart';
import BarList from '../components/BarList';
import GithubAccounts from '../components/GithubAccounts';
import { PlusIcon } from '../components/Icons';
import RecentActivity from '../components/RecentActivity';
import RepoList from '../components/RepoList';
import StatCard from '../components/StatCard';

const API = import.meta.env.VITE_API_URL;
const authHeaders = () => ({ headers: { Authorization: `Bearer ${Cookies.get("token")}` } });

const Dashboard = () => {
  const [user, setUser] = useState(null);
  const [stats, setStats] = useState(null);
  const [repos, setRepos] = useState([]);
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

  const loadRepos = async (accounts) => {
    if (accounts.length === 0) {
      setRepos([]);
      return;
    }
    const response = await axios.get(`${API}/github/repos`, authHeaders());
    setRepos(response.data);
  };

  useEffect(() => {
    const load = async () => {
      try {
        const [me, s] = await Promise.all([
          axios.get(`${API}/me`, authHeaders()),
          axios.get(`${API}/stats`, authHeaders()),
        ]);
        setUser(me.data);
        setStats(s.data);
        await loadRepos(me.data.github_accounts);
      } catch (err) {
        handleError(err, "Couldn't load your dashboard.");
      }
    };
    load();
  }, []);

  const removeAccount = async (account) => {
    if (!confirm(`Remove @${account.username} from gitAudit?`)) return;
    try {
      const response = await axios.delete(`${API}/github/accounts/${account.id}`, authHeaders());
      setUser(response.data);
      await loadRepos(response.data.github_accounts);
    } catch (err) {
      handleError(err, "Couldn't remove the account.");
    }
  };

  if (!user || !stats) return <p className="p-10 text-center text-muted">{error || "Loading..."}</p>;

  const ciDone = stats.ci_passed + stats.ci_failed;
  const passRate = ciDone === 0 ? "–" : `${Math.round((stats.ci_passed / ciDone) * 100)}%`;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-8 lg:px-12 py-8 flex flex-col gap-6">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl font-bold tracking-tight">Hello, {user.name}</h1>
          <p className="mt-1 text-sm text-ink-2">Here is what the AI found and fixed in your pull requests.</p>
        </div>
        <Link to="/repos" className="h-11 px-5 flex items-center gap-2 rounded-xl bg-accent text-on-accent text-sm font-bold hover:opacity-90">
          <PlusIcon size={16} /> Review a PR
        </Link>
      </header>

      {error && <p className="p-4 bg-high-soft text-high-text text-sm font-semibold rounded-2xl">{error}</p>}

      <section aria-label="Totals" className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="PRs reviewed" value={stats.reviews} note={`across ${stats.repos} repos`} dot="bg-accent" />
        <StatCard label="Findings" value={stats.findings} note={`${stats.severity.high} high severity`} dot="bg-high" />
        <StatCard label="AI fixes" value={stats.fixes} note={`${stats.prs_opened} fix PRs opened`} dot="bg-teal" />
        <StatCard label="CI pass rate" value={passRate} note={`${stats.ci_passed} passed · ${stats.ci_failed} failed`} dot="bg-ok-text" />
      </section>

      <section className="grid lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 min-w-0">
          <ActivityChart days={stats.last_14_days} />
        </div>
        <BarList
          title="Findings by severity"
          rows={[
            { label: "High", value: stats.severity.high, color: "bg-high" },
            { label: "Medium", value: stats.severity.medium, color: "bg-med" },
            { label: "Low", value: stats.severity.low, color: "bg-low" },
          ]}
        >
          <div className="flex flex-wrap gap-2">
            <span className="px-2.5 py-1.5 rounded-full bg-surface-2 text-xs font-semibold text-ink-2">Security {stats.category.security}</span>
            <span className="px-2.5 py-1.5 rounded-full bg-surface-2 text-xs font-semibold text-ink-2">Bug {stats.category.bug}</span>
            <span className="px-2.5 py-1.5 rounded-full bg-surface-2 text-xs font-semibold text-ink-2">Bad practice {stats.category.bad_practice}</span>
          </div>
        </BarList>
      </section>

      <section className="grid lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 min-w-0">
          <RecentActivity items={stats.recent} />
        </div>
        <GithubAccounts accounts={user.github_accounts} onRemove={removeAccount} />
      </section>

      {user.github_accounts.length > 0 && <RepoList repos={repos} showAccount={user.github_accounts.length > 1} limit={6} />}
    </div>
  );
};

export default Dashboard;
