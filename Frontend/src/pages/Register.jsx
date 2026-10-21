import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import GithubButton from '../components/GithubButton';

const input = "w-full px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:border-indigo-400";

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
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-sm p-8 bg-white rounded-3xl border border-slate-100 shadow-sm">
        <h1 className="text-3xl font-black text-center mb-8">git<span className="text-indigo-600">Audit</span></h1>

        <form onSubmit={handleRegister} className="space-y-4">
          <input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} required className={input} />
          <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required className={input} />
          <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} className={input} />
          <button disabled={loading} className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl disabled:opacity-50">
            {loading ? "Please wait..." : "Create Account"}
          </button>
        </form>

        <p className="text-center text-xs text-slate-400 my-4">or</p>
        <GithubButton label="Continue with GitHub" className="w-full" />

        <p className="text-center text-sm text-slate-500 mt-6">
          Have an account? <Link to="/login" className="text-indigo-600 font-semibold">Log in</Link>
        </p>
        {message && <p className="text-center text-sm mt-4 font-bold text-red-600">{message}</p>}
      </div>
    </div>
  );
};

export default Register;
