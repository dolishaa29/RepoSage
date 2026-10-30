import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import AuthLayout from '../components/AuthLayout';

const input = "w-full min-h-12 px-4 bg-surface text-ink border border-line rounded-xl focus:outline-none focus:border-accent";
const label = "flex flex-col gap-1.5 text-sm font-semibold";

const ResetPassword = () => {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setLoading(true);
    try {
      await axios.post(import.meta.env.VITE_API_URL + "/reset-password", { token: params.get("token") || "", password });
      navigate("/login");
    } catch (err) {
      const detail = err.response?.data?.detail;
      setMessage(Array.isArray(detail) ? detail[0].msg : detail || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <div>
        <h2 className="font-display text-3xl font-bold tracking-tight">Set a new password</h2>
        <p className="mt-1 text-sm text-ink-2">Then sign in with it.</p>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <label className={label}>New password
          <input type="password" placeholder="At least 6 characters" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} className={input} />
        </label>
        <button disabled={loading} className="min-h-12 bg-accent text-on-accent hover:opacity-90 font-bold rounded-xl disabled:opacity-50">
          {loading ? "Please wait..." : "Save password"}
        </button>
      </form>

      {message && <p className="p-3 rounded-xl bg-high-soft text-high-text text-sm font-semibold">{message}</p>}
      <p className="text-center text-sm text-ink-2">
        <Link to="/forgot-password" className="text-accent-text font-bold">Ask for a new link</Link>
      </p>
    </AuthLayout>
  );
};

export default ResetPassword;
