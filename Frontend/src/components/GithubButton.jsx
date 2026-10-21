const GITHUB_CLIENT_ID = import.meta.env.VITE_GITHUB_CLIENT_ID;

const GithubButton = ({ label, className = '' }) => {
  const goToGithub = () => {
    const state = crypto.randomUUID();
    sessionStorage.setItem('github_state', state);
    window.location.href =
      `https://github.com/login/oauth/authorize?client_id=${GITHUB_CLIENT_ID}&scope=repo%20workflow%20user:email&state=${state}`;
  };

  return (
    <button type="button" onClick={goToGithub} className={`block py-3 px-5 bg-slate-900 hover:bg-slate-800 text-white text-sm font-bold rounded-xl ${className}`}>
      {label}
    </button>
  );
};

export default GithubButton;
