import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import GithubButton from '../components/GithubButton';

const Register = () => {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();
    setMessage("");
    setLoading(true);
    try {
      await axios.post(
        import.meta.env.VITE_API_URL + "/register",
        { name, email, password },
        { headers: { "Content-Type": "application/json" } }
      );
      navigate("/login");
    } catch (err) {
      const detail = err.response?.data?.detail;
      setMessage(Array.isArray(detail) ? detail.map((d) => d.msg).join(", ") : detail || "Register Failed! Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-slate-50 bg-[radial-gradient(ellipse_at_top,_#f4f6ec,_#fafaf9)] font-sans overflow-hidden py-10">

      <div className="motion-safe:animate-[floatSlow_9s_ease-in-out_infinite] absolute top-[-10%] left-[-5%] w-96 h-96 bg-violet-200/40 blur-[100px] rounded-full" />
      <div className="motion-safe:animate-[floatSlower_11s_ease-in-out_infinite] absolute bottom-[-10%] right-[-5%] w-96 h-96 bg-indigo-200/40 blur-[100px] rounded-full" />

      <div className="motion-safe:animate-[fadeInUp_0.6s_ease-out_both] relative z-10 w-full max-w-[420px] p-10 bg-white/80 backdrop-blur-xl rounded-[2.5rem] border border-white shadow-[0_30px_60px_-15px_rgba(147,51,234,0.1)] mx-4">

        <div className="text-center mb-10">
          <h1 className="text-3xl font-black tracking-tighter text-slate-900">
            git<span className="bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">Audit</span>
          </h1>
          <p className="text-slate-400 text-[11px] font-bold uppercase tracking-[0.2em] mt-2">Create a new account</p>
        </div>

        <form onSubmit={handleRegister} className="space-y-6">
          <div>
            <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-widest ml-1 mb-2">Name</label>
            <input
              placeholder="Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full px-5 py-4 bg-white border border-slate-200 rounded-2xl text-slate-800 placeholder:text-slate-300 focus:outline-none focus:ring-4 focus:ring-violet-500/10 focus:border-violet-400 transition-all shadow-sm"
            />
          </div>

          <div>
            <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-widest ml-1 mb-2">Email</label>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-5 py-4 bg-white border border-slate-200 rounded-2xl text-slate-800 placeholder:text-slate-300 focus:outline-none focus:ring-4 focus:ring-violet-500/10 focus:border-violet-400 transition-all shadow-sm"
            />
          </div>

          <div>
            <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-widest ml-1 mb-2">Password</label>
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              className="w-full px-5 py-4 bg-white border border-slate-200 rounded-2xl text-slate-800 placeholder:text-slate-300 focus:outline-none focus:ring-4 focus:ring-violet-500/10 focus:border-violet-400 transition-all shadow-sm"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-4 mt-4 bg-gradient-to-r from-violet-600 to-indigo-600 hover:opacity-90 text-white font-bold rounded-2xl shadow-xl shadow-violet-200 transform transition-all active:scale-[0.98] disabled:opacity-50"
          >
            {loading ? "Please wait..." : "Create Account"}
          </button>
        </form>

        <div className="flex items-center gap-3 my-6 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
          <span className="flex-1 border-t border-slate-200" /> or <span className="flex-1 border-t border-slate-200" />
        </div>
        <GithubButton label="Continue with GitHub" className="w-full" />

        <p className="text-center text-sm text-slate-500 mt-6">
          Already have an account?
          <button onClick={() => navigate('/login')} className="text-violet-600 hover:underline ml-1 font-semibold">Log in</button>
        </p>

        {message && (
          <p className="text-center text-xs mt-4 font-bold text-red-600">{message}</p>
        )}
      </div>
    </div>
  );
};

export default Register;
