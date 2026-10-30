import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Cookies from 'js-cookie';

const API = import.meta.env.VITE_API_URL;
const authHeaders = () => ({ headers: { Authorization: `Bearer ${Cookies.get("token")}` } });

const Notifications = () => {
  const [notifications, setNotifications] = useState(null);
  const [error, setError] = useState("");
  const started = useRef(false);
  const navigate = useNavigate();

  useEffect(() => {
    // StrictMode runs this twice, and the second run would see everything as already read
    if (started.current) return;
    started.current = true;

    const load = async () => {
      try {
        const response = await axios.get(`${API}/notifications`, authHeaders());
        setNotifications(response.data);
        await axios.post(`${API}/notifications/read`, {}, authHeaders());
      } catch (err) {
        if (err.response?.status === 401) {
          Cookies.remove("token");
          navigate("/login");
          return;
        }
        setError(err.response?.data?.detail || "Couldn't load your notifications.");
      }
    };
    load();
  }, [navigate]);

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-8 py-8 flex flex-col gap-6">
      <div>
        <h1 className="font-display text-3xl font-bold tracking-tight">Notifications</h1>
        <p className="mt-1 text-sm text-ink-2">Your latest reviews, fixes and test results.</p>
      </div>

      {error && <p className="p-4 bg-high-soft text-high-text text-sm font-semibold rounded-2xl">{error}</p>}
      {notifications === null && !error && <p className="text-muted">Loading...</p>}
      {notifications?.length === 0 && <p className="text-muted">No notifications yet.</p>}

      {notifications?.length > 0 && (
        <div className="flex flex-col gap-2.5">
          {notifications.map((n) => (
            <Link key={n.id} to={n.link} className={`p-4 rounded-2xl border hover:border-accent ${n.is_read ? "bg-surface border-line" : "bg-accent-soft border-accent"}`}>
              <span className="block text-sm font-semibold break-words">{n.message}</span>
              <span className="block mt-1 text-xs text-muted">{new Date(n.created_at).toLocaleString()}</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default Notifications;
