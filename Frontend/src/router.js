import { useEffect, useState } from 'react'

// tiny hash router: #/login , #/register , #/
export function useRoute() {
  const [hash, setHash] = useState(window.location.hash)
  useEffect(() => {
    const onChange = () => setHash(window.location.hash)
    window.addEventListener('hashchange', onChange)
    return () => window.removeEventListener('hashchange', onChange)
  }, [])
  if (hash.startsWith('#/register')) return 'register'
  if (hash.startsWith('#/login')) return 'login'
  return 'dashboard'
}

export const navigate = (path) => {
  window.location.hash = path
}
