import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import AuthLayout from '../components/AuthLayout';
import GithubButton from '../components/GithubButton';

const input = "w-full min-h-12 px-4 bg-surface text-ink border border-line rounded-xl focus:outline-none focus:border-accent";
const label = "flex flex-col gap-1.5 text-sm font-semibold";

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
      await axios.post(import.meta.env.VITE_API_URL + "/register", { name, email, password });
      navigate("/login");
    } catch (err) {
      const detail = err.response?.data?.detail;
      setMessage(Array.isArray(detail) ? detail[0].msg : detail || "Register failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <div>
        <h2 className="font-display text-3xl font-bold tracking-tight">Create your account</h2>
        <p className="mt-1 text-sm text-ink-2">Start reviewing pull requests with AI.</p>
      </div>

      <GithubButton label="Continue with GitHub" className="w-full" />
      <div className="flex items-center gap-3 text-xs text-muted"><span className="flex-1 h-px bg-line" />or with email<span className="flex-1 h-px bg-line" /></div>

      <form onSubmit={handleRegister} className="flex flex-col gap-4">
        <label className={label}>Name
          <input placeholder="Your name" value={name} onChange={(e) => setName(e.target.value)} required className={input} />
        </label>
        <label className={label}>Email
          <input type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required className={input} />
        </label>
        <label className={label}>Password
          <input type="password" placeholder="At least 6 characters" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} className={input} />
        </label>
        <button disabled={loading} className="min-h-12 bg-accent text-on-accent hover:opacity-90 font-bold rounded-xl disabled:opacity-50">
          {loading ? "Please wait..." : "Create account"}
        </button>
      </form>

      {message && <p className="p-3 rounded-xl bg-high-soft text-high-text text-sm font-semibold">{message}</p>}
      <p className="text-center text-sm text-ink-2">
        Have an account? <Link to="/login" className="text-accent-text font-bold">Sign in</Link>
      </p>
    </AuthLayout>
  );
};

export default Register;
