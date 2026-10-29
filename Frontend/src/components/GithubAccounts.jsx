import GithubButton from './GithubButton';

// accounts: [{ id, username }]
const GithubAccounts = ({ accounts, onRemove }) => {
  return (
    <div className="p-5 bg-white border border-slate-100 rounded-2xl">
      <h2 className="mb-4 font-bold text-slate-700">GitHub accounts</h2>
      <div className="space-y-2 mb-4">
        {accounts.map((account) => (
          <div key={account.id} className="flex items-center justify-between gap-3 p-3 bg-slate-50 rounded-xl">
            <a href={`https://github.com/${account.username}`} target="_blank" rel="noreferrer" className="text-sm font-bold text-slate-800 break-all">
              @{account.username}
            </a>
            <button onClick={() => onRemove(account)} className="text-xs font-bold text-red-500">Remove</button>
          </div>
        ))}
        {accounts.length === 0 && <p className="text-sm text-slate-400">No account connected yet.</p>}
      </div>
      <GithubButton label={accounts.length === 0 ? "Connect GitHub" : "+ Add another account"} className="w-full" />
      {accounts.length > 0 && (
        <p className="mt-2 text-xs text-slate-400">GitHub will ask which account to use. To add a different one, pick it there or sign in to it on github.com first.</p>
      )}
    </div>
  );
};

export default GithubAccounts;
