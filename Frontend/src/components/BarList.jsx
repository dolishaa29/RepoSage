// rows: [{ label, value, color }]
const BarList = ({ title, rows }) => {
  const max = Math.max(1, ...rows.map((row) => row.value));

  return (
    <div className="p-5 bg-white border border-slate-100 rounded-2xl">
      <h2 className="mb-4 font-bold text-slate-700">{title}</h2>
      <div className="space-y-3">
        {rows.map((row) => (
          <div key={row.label} title={`${row.label}: ${row.value}`}>
            <div className="flex justify-between text-xs mb-1">
              <span className="font-semibold text-slate-600 break-all">{row.label}</span>
              <span className="font-bold text-slate-800">{row.value}</span>
            </div>
            <div className="h-2 bg-slate-100 rounded-full">
              <div className="h-2 rounded-full" style={{ width: `${(row.value / max) * 100}%`, background: row.color }} />
            </div>
          </div>
        ))}
        {rows.length === 0 && <p className="text-sm text-slate-400">Nothing yet.</p>}
      </div>
    </div>
  );
};

export default BarList;
