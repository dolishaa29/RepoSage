import { useState } from 'react';
import { MoonIcon, SunIcon } from './Icons';

const ThemeToggle = () => {
  const [dark, setDark] = useState(document.documentElement.classList.contains("dark"));

  const toggle = () => {
    const next = !dark;
    document.documentElement.classList.toggle("dark", next);
    try {
      localStorage.setItem("theme", next ? "dark" : "light");
    } catch {
      // private mode: theme just won't be remembered
    }
    setDark(next);
  };

  return (
    <button
      onClick={toggle}
      aria-label={dark ? "Switch to light theme" : "Switch to dark theme"}
      className="w-11 h-11 shrink-0 flex items-center justify-center rounded-xl border border-line bg-surface text-ink hover:border-accent"
    >
      {dark ? <SunIcon /> : <MoonIcon />}
    </button>
  );
};

export default ThemeToggle;
