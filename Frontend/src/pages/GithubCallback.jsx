import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Cookies from 'js-cookie';

const GithubCallback = () => {
  const navigate = useNavigate();
  const [message, setMessage] = useState("Signing in with GitHub...");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    const token = Cookies.get("token");

    if (!code) {
      navigate(token ? "/dashboard" : "/login");
      return;
    }
    if (params.get("state") !== sessionStorage.getItem("github_state")) {
      navigate("/login");
      return;
    }
    sessionStorage.removeItem("github_state");

    const finish = async () => {
      try {
        if (token) {
          await axios.post(import.meta.env.VITE_API_URL + "/github/connect", { code }, { headers: { Authorization: `Bearer ${token}` } });
        } else {
          const response = await axios.post(import.meta.env.VITE_API_URL + "/github/login", { code });
          Cookies.set("token", response.data.access_token, { expires: 1 });
        }
        navigate("/dashboard");
      } catch (err) {
        setMessage(err.response?.data?.detail || "GitHub login failed, please try again");
      }
    };
    finish();
  }, [navigate]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-4 bg-bg text-ink text-sm">
      <p className="font-bold text-ink-2">{message}</p>
      <Link to="/login" className="text-accent-text font-semibold">Back to login</Link>
    </div>
  );
};

export default GithubCallback;
