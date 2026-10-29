import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Cookies from 'js-cookie';
import GithubButton from '../components/GithubButton';
import RepoList from '../components/RepoList';

const API = import.meta.env.VITE_API_URL;
const authHeaders = () => ({ headers: { Authorization: `Bearer ${Cookies.get("token")}` } });

const Repos = () => {
  const [user, setUser] = useState(null);
  const [repos, setRepos] = useState(null);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const load = async () => {
      try {
        const me = await axios.get(`${API}/me`, authHeaders());
        setUser(me.data);
        if (me.data.github_accounts.length > 0) {
          const response = await axios.get(`${API}/github/repos`, authHeaders());
          setRepos(response.data);
        }
      } catch (err) {
        if (err.response?.status === 401) {
          Cookies.remove("token");
          navigate("/login");
          return;
        }
        setError(err.response?.data?.detail || "Couldn't load your repositories.");
      }
    };
    load();
  }, [navigate]);

  if (!user) return <p className="p-10 text-center text-muted">{error || "Loading..."}</p>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-8 lg:px-12 py-8 flex flex-col gap-6">
      <div>
        <h1 className="font-display text-3xl font-bold tracking-tight">Repositories</h1>
        <p className="mt-1 text-sm text-ink-2">Pick a repo to review its open pull requests.</p>
      </div>

      {error && <p className="p-4 bg-high-soft text-high-text text-sm font-semibold rounded-2xl">{error}</p>}

      {user.github_accounts.length === 0 ? (
        <div className="p-10 bg-surface border border-line rounded-2xl flex flex-col items-center gap-5 text-center">
          <p className="text-ink-2">Connect GitHub to see your repositories.</p>
          <GithubButton label="Connect GitHub" />
        </div>
      ) : repos === null ? (
        <p className="text-muted">Loading repositories...</p>
      ) : (
        <RepoList repos={repos} showAccount={user.github_accounts.length > 1} />
      )}
    </div>
  );
};

export default Repos;
