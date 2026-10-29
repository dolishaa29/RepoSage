import { GithubIcon } from './Icons';

const GITHUB_CLIENT_ID = import.meta.env.VITE_GITHUB_CLIENT_ID;

const GithubButton = ({ label, className = '' }) => {
  const goToGithub = () => {
    const state = crypto.randomUUID();
    sessionStorage.setItem('github_state', state);
    window.location.href =
      `https://github.com/login/oauth/authorize?client_id=${GITHUB_CLIENT_ID}&scope=repo%20workflow%20user:email&prompt=select_account&state=${state}`;
  };

  return (
    <button type="button" onClick={goToGithub} className={`min-h-12 px-5 flex items-center justify-center gap-2.5 bg-invert text-on-invert hover:opacity-90 text-sm font-bold rounded-xl ${className}`}>
      <GithubIcon />
      {label}
    </button>
  );
};

export default GithubButton;
