// rows: [{ label, value, color }], color is a bg-* class
const BarList = ({ title, rows, children }) => {
  const max = Math.max(1, ...rows.map((row) => row.value));

  return (
    <div className="p-5 bg-surface border border-line rounded-2xl flex flex-col gap-4">
      <h2 className="font-display text-lg font-bold">{title}</h2>
      {rows.map((row) => (
        <div key={row.label} title={`${row.label}: ${row.value}`}>
          <div className="flex justify-between text-sm mb-1.5">
            <span className="flex items-center gap-2 font-semibold"><span className={`w-2 h-2 rounded-full ${row.color}`} />{row.label}</span>
            <span className="font-bold">{row.value}</span>
          </div>
          <div className="h-2 bg-surface-2 rounded-full">
            <div className={`h-2 rounded-full ${row.color}`} style={{ width: `${(row.value / max) * 100}%` }} />
          </div>
        </div>
      ))}
      {children && <div className="mt-auto">{children}</div>}
    </div>
  );
};

export default BarList;
