import Cookies from 'js-cookie';

const GITHUB_CLIENT_ID = import.meta.env.VITE_GITHUB_CLIENT_ID;

export const goToGithub = (intent = 'connect') => {
  const state = crypto.randomUUID();
  const params = new URLSearchParams({
    client_id: GITHUB_CLIENT_ID,
    redirect_uri: window.location.origin === 'http://localhost:5174'
      ? new URL('/github/callback', import.meta.env.VITE_API_URL).href
      : new URL('/', window.location.origin).href,
    scope: 'repo workflow user:email',
    state,
  });
  if (Cookies.get('token')) params.set('prompt', 'select_account');
  sessionStorage.setItem('github_state', state);
  sessionStorage.setItem('github_intent', intent);
  window.location.href = `https://github.com/login/oauth/authorize?${params}`;
};
