import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Cookies from 'js-cookie';
import AuthLayout from '../components/AuthLayout';
import GithubButton from '../components/GithubButton';

const GithubCallback = () => {
  const navigate = useNavigate();
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const started = useRef(false);

  useEffect(() => {
    if (started.current) return;
    started.current = true;

    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    const token = Cookies.get("token");

    if (!code && !params.has("error")) return;

    const expectedState = sessionStorage.getItem("github_state");
    const intent = sessionStorage.getItem("github_intent");
    sessionStorage.removeItem("github_state");
    sessionStorage.removeItem("github_intent");
    if (!code || !expectedState || params.get("state") !== expectedState) {
      setMessage("GitHub authorization did not complete. Try again.");
      return;
    }

    if (intent === "connect" && !token) {
      setMessage("Your session expired. Continue with GitHub again.");
      return;
    }

    const finish = async () => {
      const api = import.meta.env.VITE_API_URL;
      setBusy(true);
      try {
        if (intent === "connect") {
          await axios.post(api + "/github/connect", { code }, { headers: { Authorization: `Bearer ${token}` } });
        } else {
          const { data } = await axios.post(api + "/github/login", { code });
          Cookies.set("token", data.access_token, {
            expires: 7,
            sameSite: 'lax',
            secure: window.location.protocol === 'https:',
          });
        }
        navigate("/dashboard", { replace: true });
      } catch (err) {
        if (err.response?.status === 401) {
          Cookies.remove("token");
          setMessage("Your session expired. Continue with GitHub again.");
        } else {
          setMessage(err.response?.data?.detail || "Could not connect to GitHub. Try again.");
        }
      } finally {
        setBusy(false);
      }
    };
    finish();
  }, [navigate]);

  return (
    <AuthLayout>
      <h2 className="font-display text-3xl font-bold tracking-tight">Connect GitHub</h2>
      {busy ? (
        <p role="status">Connecting to GitHub…</p>
      ) : (
        <>
          {message && <p role="alert" className="text-high-text">{message}</p>}
          <GithubButton label="Continue with GitHub" intent="signin" className="w-full" />
          {Cookies.get("token") && (
            <Link to="/dashboard" className="text-center text-accent-text font-semibold">Open dashboard</Link>
          )}
        </>
      )}
    </AuthLayout>
  );
};

export default GithubCallback;
