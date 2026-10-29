import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Cookies from 'js-cookie';
import AuthLayout from '../components/AuthLayout';
import GithubButton from '../components/GithubButton';

const input = "w-full min-h-12 px-4 bg-surface text-ink border border-line rounded-xl focus:outline-none focus:border-accent";
const label = "flex flex-col gap-1.5 text-sm font-semibold";

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setMessage("");
    setLoading(true);
    try {
      const response = await axios.post(import.meta.env.VITE_API_URL + "/login", { email, password });
      Cookies.set("token", response.data.access_token, { expires: 1 });
      navigate("/dashboard");
    } catch (err) {
      setMessage(err.response?.data?.detail || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <div>
        <h2 className="font-display text-3xl font-bold tracking-tight">Welcome back</h2>
        <p className="mt-1 text-sm text-ink-2">Sign in to review your pull requests.</p>
      </div>

      <GithubButton label="Continue with GitHub" className="w-full" />
      <div className="flex items-center gap-3 text-xs text-muted"><span className="flex-1 h-px bg-line" />or with email<span className="flex-1 h-px bg-line" /></div>

      <form onSubmit={handleLogin} className="flex flex-col gap-4">
        <label className={label}>Email
          <input type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required className={input} />
        </label>
        <label className={label}>Password
          <input type="password" placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} required className={input} />
        </label>
        <button disabled={loading} className="min-h-12 bg-accent text-on-accent hover:opacity-90 font-bold rounded-xl disabled:opacity-50">
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </form>

      {message && <p className="p-3 rounded-xl bg-high-soft text-high-text text-sm font-semibold">{message}</p>}
      <p className="text-center text-sm text-ink-2">
        New here? <Link to="/register" className="text-accent-text font-bold">Create an account</Link>
      </p>
    </AuthLayout>
  );
};

export default Login;
