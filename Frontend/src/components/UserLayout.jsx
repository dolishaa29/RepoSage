import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import Cookies from 'js-cookie';
import Logo from './Logo';
import NotificationBell from './NotificationBell';
import ThemeToggle from './ThemeToggle';
import { BookIcon, GridIcon, LogoutIcon } from './Icons';

const NAV = [
  { to: "/dashboard", label: "Dashboard", Icon: GridIcon },
  { to: "/repos", label: "Repositories", Icon: BookIcon },
];

const sideLink = ({ isActive }) =>
  `flex items-center gap-3 min-h-11 px-3 rounded-xl text-sm ${isActive ? "bg-accent-soft text-accent-text font-bold" : "text-ink-2 font-medium hover:bg-surface-2"}`;

const tabLink = ({ isActive }) =>
  `flex flex-col items-center justify-center gap-1 text-xs ${isActive ? "text-accent-text font-bold" : "text-ink-2 font-semibold"}`;

const UserLayout = () => {
  const navigate = useNavigate();

  const logout = () => {
    Cookies.remove("token");
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-bg text-ink lg:flex">
      {/* desktop: sidebar */}
      <aside className="hidden lg:flex w-64 shrink-0 sticky top-0 h-screen flex-col gap-7 px-4 py-6 bg-surface border-r border-line">
        <div className="px-2"><Logo /></div>
        <nav aria-label="Main" className="flex flex-col gap-1">
          {NAV.map(({ to, label, Icon }) => (
            <NavLink key={to} to={to} className={sideLink}><Icon />{label}</NavLink>
          ))}
        </nav>
        <div className="mt-auto flex flex-col gap-4">
          <div className="p-4 rounded-2xl bg-accent-soft">
            <p className="text-sm font-bold text-accent-text">Human in the loop</p>
            <p className="mt-1 text-xs leading-relaxed text-ink-2">Every AI fix opens a new PR. Nothing is merged without you.</p>
          </div>
          <div className="flex items-center gap-2">
            <NotificationBell />
            <ThemeToggle />
            <button onClick={logout} className="flex-1 min-h-11 flex items-center justify-center gap-2 rounded-xl border border-line text-sm font-semibold text-high-text hover:bg-high-soft">
              <LogoutIcon size={16} /> Sign out
            </button>
          </div>
        </div>
      </aside>

      {/* phone: top bar */}
      <header className="lg:hidden sticky top-0 z-20 h-16 px-4 flex items-center justify-between bg-surface border-b border-line">
        <Logo />
        <div className="flex items-center gap-2">
          <NotificationBell />
          <ThemeToggle />
          <button onClick={logout} aria-label="Sign out" className="w-11 h-11 flex items-center justify-center rounded-xl border border-line text-high-text">
            <LogoutIcon />
          </button>
        </div>
      </header>

      <main className="flex-1 min-w-0 pb-24 lg:pb-0">
        <Outlet />
      </main>

      {/* phone: bottom tabs */}
      <nav aria-label="Main" className="lg:hidden fixed bottom-0 inset-x-0 z-20 h-16 grid grid-cols-2 bg-surface border-t border-line">
        {NAV.map(({ to, label, Icon }) => (
          <NavLink key={to} to={to} className={tabLink}><Icon size={20} />{label}</NavLink>
        ))}
      </nav>
    </div>
  );
};

export default UserLayout;
