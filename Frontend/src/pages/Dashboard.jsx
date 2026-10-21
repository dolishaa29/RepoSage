import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Cookies from 'js-cookie';
import GithubButton from '../components/GithubButton';

const Dashboard = () => {
  const [user, setUser] = useState(null);
  const [repos, setRepos] = useState([]);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const headers = { Authorization: `Bearer ${Cookies.get("token")}` };

    const load = async () => {
      try {
        const me = await axios.get(import.meta.env.VITE_API_URL + "/me", { headers });
        setUser(me.data);
        if (me.data.github_username) {
          const response = await axios.get(import.meta.env.VITE_API_URL + "/github/repos", { headers });
          setRepos(response.data);
        }
      } catch (err) {
        if (err.response?.status === 401) {
          Cookies.remove("token");
          navigate("/login");
          return;
        }
        setError(err.response?.data?.detail || "Couldn't load your dashboard.");
      }
    };
    load();
  }, [navigate]);

  if (!user) return <p className="p-10 text-center text-slate-400">{error || "Loading..."}</p>;

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <h1 className="text-3xl font-bold mb-1">Hello, <span className="text-indigo-600">{user.name}</span></h1>
      <p className="text-sm text-slate-400 mb-8">
        {user.email} · GitHub: {user.github_username ? `@${user.github_username}` : "not connected"}
      </p>

      {error && <p className="mb-6 p-4 bg-red-50 text-red-700 text-sm font-semibold rounded-2xl">{error}</p>}

      {!user.github_username ? (
        <div className="p-10 bg-white border border-slate-100 rounded-3xl text-center">
          <p className="text-slate-500 mb-6">Connect GitHub to see your repositories.</p>
          <GithubButton label="Connect GitHub" className="mx-auto" />
        </div>
      ) : (
        <>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-bold text-slate-700">Your repositories</h2>
            <GithubButton label="Reconnect GitHub" />
          </div>
          <div className="space-y-3">
            {repos.map((r) => (
              <Link
                key={r.id}
                to={`/repo/${r.full_name}`}
                className="flex items-center justify-between gap-4 p-5 bg-white border border-slate-100 rounded-2xl hover:border-indigo-300"
              >
                <div className="min-w-0">
                  <p className="font-bold text-slate-800 break-all">{r.full_name}</p>
                  {r.description && <p className="text-xs text-slate-400 truncate">{r.description}</p>}
                </div>
                <span className="shrink-0 text-xs text-slate-400">{r.language} · {r.private ? "Private" : "Public"}</span>
              </Link>
            ))}
            {repos.length === 0 && <p className="text-slate-400">No repositories found.</p>}
          </div>
        </>
      )}
    </div>
  );
};

export default Dashboard;
