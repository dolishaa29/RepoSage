import { Link, Outlet, useNavigate } from 'react-router-dom';
import Cookies from 'js-cookie';

const UserLayout = () => {
  const navigate = useNavigate();

  const logout = () => {
    Cookies.remove("token");
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="bg-white border-b border-slate-100">
        <div className="max-w-4xl mx-auto h-16 px-6 flex items-center justify-between">
          <Link to="/dashboard" className="font-bold text-xl">git<span className="text-indigo-600">Audit</span></Link>
          <button onClick={logout} className="text-sm font-bold text-red-500">Sign Out</button>
        </div>
      </header>
      <Outlet />
    </div>
  );
};

export default UserLayout;
