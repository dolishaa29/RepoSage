import Cookies from 'js-cookie';
import { GithubIcon } from './Icons';

const GITHUB_CLIENT_ID = import.meta.env.VITE_GITHUB_CLIENT_ID;

const GithubButton = ({ label, className = '' }) => {
  const goToGithub = () => {
    // the account picker is only needed when linking another account, not on every login
    const picker = Cookies.get("token") ? "&prompt=select_account" : "";
    const state = crypto.randomUUID();
    sessionStorage.setItem('github_state', state);
    window.location.href =
      `https://github.com/login/oauth/authorize?client_id=${GITHUB_CLIENT_ID}&scope=repo%20workflow%20user:email${picker}&state=${state}`;
  };

  return (
    <button type="button" onClick={goToGithub} className={`min-h-12 px-5 flex items-center justify-center gap-2.5 bg-invert text-on-invert hover:opacity-90 text-sm font-bold rounded-xl ${className}`}>
      <GithubIcon />
      {label}
    </button>
  );
};

export default GithubButton;
