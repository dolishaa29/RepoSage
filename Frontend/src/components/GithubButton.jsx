import { GithubIcon } from './Icons';
import { goToGithub } from '../githubOAuth';

const GithubButton = ({ label, intent, className = '' }) => {
  return (
    <button type="button" onClick={() => goToGithub(intent)} className={`min-h-12 px-5 flex items-center justify-center gap-2.5 bg-invert text-on-invert hover:opacity-90 text-sm font-bold rounded-xl ${className}`}>
      <GithubIcon />
      {label}
    </button>
  );
};

export default GithubButton;
