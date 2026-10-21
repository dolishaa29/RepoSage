import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Cookies from 'js-cookie';
import GithubButton from '../components/GithubButton';

const input = "w-full px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:border-indigo-400";

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
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-sm p-8 bg-white rounded-3xl border border-slate-100 shadow-sm">
        <h1 className="text-3xl font-black text-center mb-8">git<span className="text-indigo-600">Audit</span></h1>

        <form onSubmit={handleLogin} className="space-y-4">
          <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required className={input} />
          <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required className={input} />
          <button disabled={loading} className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl disabled:opacity-50">
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <p className="text-center text-xs text-slate-400 my-4">or</p>
        <GithubButton label="Continue with GitHub" className="w-full" />

        <p className="text-center text-sm text-slate-500 mt-6">
          No account? <Link to="/register" className="text-indigo-600 font-semibold">Register</Link>
        </p>
        {message && <p className="text-center text-sm mt-4 font-bold text-red-600">{message}</p>}
      </div>
    </div>
  );
};

export default Login;
