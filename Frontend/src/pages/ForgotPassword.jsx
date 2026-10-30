import { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import AuthLayout from '../components/AuthLayout';

const input = "w-full min-h-12 px-4 bg-surface text-ink border border-line rounded-xl focus:outline-none focus:border-accent";
const label = "flex flex-col gap-1.5 text-sm font-semibold";

const ForgotPassword = () => {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setLoading(true);
    try {
      await axios.post(import.meta.env.VITE_API_URL + "/forgot-password", { email });
      setSent(true);
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
        <h2 className="font-display text-3xl font-bold tracking-tight">Forgot your password?</h2>
        <p className="mt-1 text-sm text-ink-2">We will email you a link to set a new one.</p>
      </div>

      {sent ? (
        <p className="p-3 rounded-xl bg-ok-soft text-ok-text text-sm font-semibold">If this email has an account, a reset link is on its way. The link works for 30 minutes.</p>
      ) : (
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <label className={label}>Email
            <input type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required className={input} />
          </label>
          <button disabled={loading} className="min-h-12 bg-accent text-on-accent hover:opacity-90 font-bold rounded-xl disabled:opacity-50">
            {loading ? "Please wait..." : "Send reset link"}
          </button>
        </form>
      )}

      {message && <p className="p-3 rounded-xl bg-high-soft text-high-text text-sm font-semibold">{message}</p>}
      <p className="text-center text-sm text-ink-2">
        <Link to="/login" className="text-accent-text font-bold">Back to sign in</Link>
      </p>
    </AuthLayout>
  );
};

export default ForgotPassword;
