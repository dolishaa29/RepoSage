import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Cookies from 'js-cookie';

const GithubCallback = () => {
  const navigate = useNavigate();
  const [message, setMessage] = useState("");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    const token = Cookies.get("token");

    if (!code) {
      navigate(token ? "/dashboard" : "/login");
      return;
    }
    if (params.get("state") !== sessionStorage.getItem("github_state")) {
      setMessage("GitHub login failed, please try again");
      return;
    }
    sessionStorage.removeItem("github_state");

    const finish = async () => {
      try {
        if (token) {
          await axios.post(
            import.meta.env.VITE_API_URL + "/github/connect",
            { code },
            { headers: { Authorization: `Bearer ${token}` } }
          );
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
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 px-6 text-center">
      {message ? (
        <>
          <p className="text-sm font-bold text-red-600">{message}</p>
          <button onClick={() => navigate("/login")} className="mt-4 text-sm font-semibold text-violet-600 hover:underline">
            Back to login
          </button>
        </>
      ) : (
        <>
          <div className="w-10 h-10 border-4 border-indigo-100 border-t-indigo-600 rounded-full animate-spin" />
          <p className="mt-4 text-slate-400 text-sm font-medium">Signing in with GitHub...</p>
        </>
      )}
    </div>
  );
};

export default GithubCallback;
