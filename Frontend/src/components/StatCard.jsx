// dot: a bg-* class, for example "bg-accent"
const StatCard = ({ label, value, note, dot }) => {
  return (
    <div className="p-5 bg-surface border border-line rounded-2xl flex flex-col gap-1.5">
      <p className="flex items-center gap-2 text-xs font-semibold tracking-wider uppercase text-muted">
        <span className={`w-1.5 h-1.5 rounded-full ${dot}`} />{label}
      </p>
      <p className="font-display text-4xl font-bold tracking-tight">{value}</p>
      {note && <p className="text-sm text-ink-2">{note}</p>}
    </div>
  );
};

export default StatCard;
