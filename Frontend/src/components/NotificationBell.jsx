import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import axios from 'axios';
import Cookies from 'js-cookie';
import { BellIcon } from './Icons';

const API = import.meta.env.VITE_API_URL;
const CHECK_EVERY = 30000;

const NotificationBell = () => {
  const [unread, setUnread] = useState(0);
  const { pathname } = useLocation();

  useEffect(() => {
    const load = async () => {
      try {
        const response = await axios.get(`${API}/notifications/unread`, { headers: { Authorization: `Bearer ${Cookies.get("token")}` } });
        setUnread(response.data.count);
      } catch {
      }
    };
    load();
    const timer = setInterval(load, CHECK_EVERY);
    return () => clearInterval(timer);
  }, [pathname]);

  const count = pathname === "/notifications" ? 0 : unread;

  return (
    <Link to="/notifications" aria-label={`Notifications, ${count} unread`} className="relative shrink-0 w-11 h-11 flex items-center justify-center rounded-xl border border-line text-ink-2 hover:bg-surface-2">
      <BellIcon />
      {count > 0 && (
        <span className="absolute -top-1.5 -right-1.5 min-w-5 h-5 px-1 flex items-center justify-center rounded-full bg-high text-on-accent text-[11px] font-bold">
          {count > 99 ? "99+" : count}
        </span>
      )}
    </Link>
  );
};

export default NotificationBell;
