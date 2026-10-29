import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Cookies from 'js-cookie';
import ActivityChart from '../components/ActivityChart';
import BarList from '../components/BarList';
import GithubAccounts from '../components/GithubAccounts';
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

  if (!user || !stats) return <p className="p-10 text-center text-slate-400">{error || "Loading..."}</p>;

  const ciDone = stats.ci_passed + stats.ci_failed;
  const passRate = ciDone === 0 ? "–" : `${Math.round((stats.ci_passed / ciDone) * 100)}%`;

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-10">
      <h1 className="text-3xl font-bold mb-1">Hello, <span className="text-indigo-600">{user.name}</span></h1>
      <p className="text-sm text-slate-400 mb-8">{user.email}</p>

      {error && <p className="mb-6 p-4 bg-red-50 text-red-700 text-sm font-semibold rounded-2xl">{error}</p>}

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard label="PRs reviewed" value={stats.reviews} />
        <StatCard label="Findings" value={stats.findings} note={`${stats.severity.high} high severity`} />
        <StatCard label="AI fixes" value={stats.fixes} note={`${stats.prs_opened} fix PRs opened`} />
        <StatCard label="CI pass rate" value={passRate} note={`${stats.ci_passed} passed · ${stats.ci_failed} failed`} />
      </div>

      <div className="grid lg:grid-cols-3 gap-4 mb-6">
        <div className="lg:col-span-2">
          <ActivityChart days={stats.last_14_days} />
        </div>
        <BarList
          title="Findings by severity"
          rows={[
            { label: "High", value: stats.severity.high, color: "#dc2626" },
            { label: "Medium", value: stats.severity.medium, color: "#d97706" },
            { label: "Low", value: stats.severity.low, color: "#78716c" },
          ]}
        />
      </div>

      <div className="grid md:grid-cols-3 gap-4 mb-6">
        <BarList
          title="Findings by type"
          rows={[
            { label: "Security", value: stats.category.security, color: "#5f7f1f" },
            { label: "Bug", value: stats.category.bug, color: "#5f7f1f" },
            { label: "Bad practice", value: stats.category.bad_practice, color: "#5f7f1f" },
          ]}
        />
        <BarList
          title="Fix status"
          rows={[
            { label: "Approved", value: stats.fix_status.approved, color: "#3b6fd8" },
            { label: "Pending", value: stats.fix_status.pending, color: "#3b6fd8" },
            { label: "Rejected", value: stats.fix_status.rejected, color: "#3b6fd8" },
          ]}
        />
        <BarList
          title="Top repos by findings"
          rows={stats.top_repos.map((r) => ({ label: r.repo, value: r.findings, color: "#5f7f1f" }))}
        />
      </div>

      <div className="grid lg:grid-cols-3 gap-4 mb-10">
        <div className="lg:col-span-2">
          <RecentActivity items={stats.recent} />
        </div>
        <GithubAccounts accounts={user.github_accounts} onRemove={removeAccount} />
      </div>

      {user.github_accounts.length > 0 && <RepoList repos={repos} showAccount={user.github_accounts.length > 1} />}
    </div>
  );
};

export default Dashboard;
