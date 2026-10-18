import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Cookies from 'js-cookie';
import { AlertCircle, ChevronRight, FolderGit2, Globe, Lock } from 'lucide-react';
import GithubButton from '../components/GithubButton';

const Dashboard = () => {
  const [data, setData] = useState({ name: "", email: "", github_username: null });
  const [repos, setRepos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const headers = { Authorization: `Bearer ${Cookies.get("token")}` };

    const fetchDashboard = async () => {
      try {
        const me = await axios.get(import.meta.env.VITE_API_URL + "/me", { headers });
        setData(me.data);
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
        setError(err.response?.data?.detail || "Couldn't load your dashboard. Please try again.");
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, [navigate]);

  const connected = Boolean(data.github_username);

  return (
    <div className="max-w-5xl mx-auto px-6 py-10 md:px-10">
      {error && (
        <div className="motion-safe:animate-[fadeInUp_0.4s_ease-out_both] mb-6 flex items-center gap-3 bg-red-50 border border-red-100 rounded-2xl px-5 py-4">
          <AlertCircle size={18} className="text-red-500 shrink-0" />
          <p className="text-sm font-semibold text-red-700">{error}</p>
        </div>
      )}

      <div className="motion-safe:animate-[fadeInUp_0.5s_ease-out_both] flex items-center justify-between mb-8">
        {loading ? (
          <div className="h-10 w-72 bg-slate-200/70 rounded-lg animate-pulse" />
        ) : (
          <div>
            <p className="text-[10px] font-bold text-indigo-500 tracking-[0.2em] uppercase mb-1">Dashboard</p>
            <h1 className="text-4xl font-bold text-slate-900 tracking-tight">
              Hello, <span className="text-indigo-600">{data.name?.split(" ")[0] || "there"}</span>
            </h1>
          </div>
        )}
        {loading ? (
          <div className="w-12 h-12 rounded-2xl bg-slate-200/70 animate-pulse shrink-0" />
        ) : (
          <div className="w-12 h-12 bg-indigo-600 rounded-2xl flex items-center justify-center text-white font-bold text-lg shrink-0">
            {data.name?.charAt(0)?.toUpperCase() || "?"}
          </div>
        )}
      </div>

      {!loading && (
        <>
          <div
            className="motion-safe:animate-[fadeInUp_0.5s_ease-out_both] bg-white border border-slate-100 rounded-3xl p-6 shadow-sm mb-8"
            style={{ animationDelay: '80ms' }}
          >
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-4">Profile</p>
            <div className="grid sm:grid-cols-3 gap-3">
              <InfoBox label="Name" value={data.name} />
              <InfoBox label="Email" value={data.email} />
              <InfoBox label="GitHub" value={connected ? `@${data.github_username}` : "Not connected"} />
            </div>
            {connected && (
              <div className="mt-5 pt-5 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3">
                <p className="text-xs text-slate-400">GitHub not working, or repos missing? Connect it again.</p>
                <GithubButton label="Reconnect GitHub" />
              </div>
            )}
          </div>

          <div className="motion-safe:animate-[fadeInUp_0.5s_ease-out_both]" style={{ animationDelay: '150ms' }}>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-4">Your Repositories</p>

            {!connected ? (
              <div className="flex flex-col items-center justify-center py-16 px-6 bg-white border border-slate-100 rounded-3xl text-center">
                <FolderGit2 size={48} className="text-slate-200 mb-4" strokeWidth={1.5} />
                <h3 className="text-lg font-bold text-slate-700">Connect GitHub</h3>
                <p className="text-slate-400 text-sm mt-1 mb-6">Connect your GitHub account to see your repositories, including private ones.</p>
                <GithubButton label="Connect GitHub" />
              </div>
            ) : repos.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 bg-white border border-slate-100 rounded-3xl">
                <FolderGit2 size={48} className="text-slate-200 mb-4" strokeWidth={1.5} />
                <h3 className="text-lg font-bold text-slate-700">No repositories found</h3>
              </div>
            ) : (
              <div className="space-y-3">
                {repos.map((r) => (
                  <button
                    key={r.id}
                    onClick={() => navigate(`/repo/${r.full_name}`)}
                    className="w-full flex items-center justify-between gap-4 p-5 bg-white border border-slate-100 rounded-3xl hover:border-indigo-200 hover:shadow-md transition-all duration-300 group text-left"
                  >
                    <div className="flex items-center gap-4 min-w-0">
                      <div className="p-3 bg-indigo-50 rounded-2xl group-hover:scale-110 transition-transform duration-300 shrink-0">
                        <FolderGit2 size={20} className="text-indigo-600" />
                      </div>
                      <div className="min-w-0">
                        <p className="font-bold text-slate-800 tracking-tight break-all">{r.full_name}</p>
                        {r.description && <p className="text-xs text-slate-400 mt-0.5 line-clamp-1">{r.description}</p>}
                      </div>
                    </div>
                    <div className="flex items-center gap-3 shrink-0">
                      {r.language && <span className="hidden sm:inline text-xs font-semibold text-slate-400">{r.language}</span>}
                      <span className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest ${r.private ? "bg-slate-100 text-slate-500" : "bg-indigo-50 text-indigo-600"}`}>
                        {r.private ? <Lock size={11} /> : <Globe size={11} />}
                        {r.private ? "Private" : "Public"}
                      </span>
                      <ChevronRight size={18} className="text-slate-300 group-hover:text-indigo-600 group-hover:translate-x-1 transition-all" />
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

const InfoBox = ({ label, value }) => (
  <div className="p-3 bg-slate-50 rounded-2xl min-w-0">
    <p className="text-[9px] font-bold text-slate-400 uppercase tracking-wider leading-none mb-1">{label}</p>
    <p className="text-sm font-bold text-slate-700 break-all">{value}</p>
  </div>
);

export default Dashboard;
