import Logo from './Logo';
import ThemeToggle from './ThemeToggle';

// Login and Register: dark brand panel on the left, form on the right
const AuthLayout = ({ children }) => (
  <div className="min-h-screen flex flex-wrap bg-bg text-ink">
    <section className="dark flex-[1_1_420px] p-8 sm:p-14 bg-bg text-ink flex flex-col justify-between gap-12">
      <Logo to="/login" />
      <div className="max-w-md flex flex-col gap-5">
        <h1 className="font-display text-4xl sm:text-5xl font-bold leading-[1.05] tracking-tight">
          Find the bugs.<br />Fix them.<br /><span className="text-accent-text">Open the PR.</span>
        </h1>
        <p className="text-base leading-relaxed text-ink-2">
          AI agents review your pull requests, write the fix and a unit test, and open a new PR only after you approve.
        </p>
      </div>
      <pre className="font-mono text-[13px] leading-loose p-4 rounded-2xl bg-surface border border-line text-ink-2 overflow-x-auto">
        <span className="text-accent-text">review </span> → findings{"\n"}
        <span className="text-teal-text">fix    </span> → code + unit test{"\n"}
        <span className="text-accent-text">approve</span> → PR opened{"\n"}
        <span className="text-ok-text">ci     </span> → tests passed
      </pre>
    </section>

    <section className="flex-[1_1_420px] p-8 sm:p-14 flex flex-col gap-6">
      <div className="flex justify-end"><ThemeToggle /></div>
      <div className="flex-1 w-full max-w-sm mx-auto flex flex-col justify-center gap-5">
        {children}
      </div>
    </section>
  </div>
);

export default AuthLayout;
