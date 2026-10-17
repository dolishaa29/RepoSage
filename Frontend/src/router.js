import { useEffect, useState } from 'react'

// tiny hash router: #/login , #/register , #/repo/owner/name , #/
export function useRoute() {
  const [hash, setHash] = useState(window.location.hash)
  useEffect(() => {
    const onChange = () => setHash(window.location.hash)
    window.addEventListener('hashchange', onChange)
    return () => window.removeEventListener('hashchange', onChange)
  }, [])
  if (hash.startsWith('#/register')) return { page: 'register' }
  if (hash.startsWith('#/login')) return { page: 'login' }
  if (hash.startsWith('#/repo/')) return { page: 'repo', repo: hash.slice('#/repo/'.length) }
  return { page: 'dashboard' }
}

export const navigate = (path) => {
  window.location.hash = path
}
