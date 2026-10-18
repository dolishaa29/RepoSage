import React from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import Cookies from 'js-cookie';
import { LayoutDashboard, LogOut } from 'lucide-react';

const UserLayout = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900">

      <header className="sticky top-0 z-30 bg-white/90 backdrop-blur border-b border-slate-100">
        <div className="max-w-5xl mx-auto h-16 px-6 md:px-10 flex items-center justify-between gap-4">
          <button onClick={() => navigate('/dashboard')} className="font-bold text-xl tracking-tight text-slate-900">
            git<span className="text-indigo-600">Audit</span>
          </button>

          <div className="flex items-center gap-2">
            <NavLink
              to="/dashboard"
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-4 py-2.5 rounded-xl transition-all duration-300 font-bold text-[13px]
                ${isActive ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-100' : 'text-slate-400 hover:bg-slate-50 hover:text-indigo-600'}`
              }
            >
              <LayoutDashboard size={16} />
              <span className="hidden sm:inline">Dashboard</span>
            </NavLink>
            <button
              onClick={() => { Cookies.remove("token"); navigate("/login"); }}
              className="flex items-center gap-2.5 px-4 py-2.5 text-red-500 hover:bg-red-50/50 rounded-xl transition-all duration-300 font-bold text-[13px]"
            >
              <LogOut size={16} />
              <span className="hidden sm:inline">Sign Out</span>
            </button>
          </div>
        </div>
      </header>

      <main>
        <Outlet />
      </main>
    </div>
  );
};

export default UserLayout;
