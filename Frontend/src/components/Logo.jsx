import { Link } from 'react-router-dom';
import { LogoIcon } from './Icons';

const Logo = ({ to = "/dashboard" }) => (
  <Link to={to} className="flex items-center gap-2.5 font-display text-xl font-bold">
    <span className="w-9 h-9 rounded-xl bg-accent text-on-accent flex items-center justify-center"><LogoIcon /></span>
    <span>git<span className="text-accent-text">Audit</span></span>
  </Link>
);

export default Logo;
