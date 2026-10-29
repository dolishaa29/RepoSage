import GithubButton from './GithubButton';

const AVATAR = ["bg-accent", "bg-teal"];

// accounts: [{ id, username }]
const GithubAccounts = ({ accounts, onRemove }) => {
  return (
    <div className="h-full p-5 bg-surface border border-line rounded-2xl flex flex-col gap-3">
      <h2 className="font-display text-lg font-bold">GitHub accounts</h2>
      {accounts.map((account, i) => (
        <div key={account.id} className="flex items-center gap-3 px-3 py-2 rounded-xl bg-surface-2">
          <span className={`shrink-0 w-9 h-9 rounded-full flex items-center justify-center font-bold text-on-accent ${AVATAR[i % 2]}`}>
            {account.username[0].toUpperCase()}
          </span>
          <a href={`https://github.com/${account.username}`} target="_blank" rel="noreferrer" className="flex-1 min-w-0 text-sm font-semibold break-all">
            @{account.username}
          </a>
          <button onClick={() => onRemove(account)} className="min-h-11 px-2 text-sm font-semibold text-high-text">Remove</button>
        </div>
      ))}
      {accounts.length === 0 && <p className="text-sm text-muted">No account connected yet.</p>}
      <GithubButton label={accounts.length === 0 ? "Connect GitHub" : "Add another account"} className="w-full" />
      <p className="text-xs leading-relaxed text-muted">GitHub asks which account to link. Repos from every account show in one list.</p>
    </div>
  );
};

export default GithubAccounts;
