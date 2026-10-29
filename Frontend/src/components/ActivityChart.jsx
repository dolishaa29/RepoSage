// days: [{ day, reviews, fixes }]
const ActivityChart = ({ days }) => {
  const max = Math.max(1, ...days.map((d) => Math.max(d.reviews, d.fixes)));

  return (
    <div className="h-full p-5 bg-surface border border-line rounded-2xl flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="font-display text-lg font-bold">Last 14 days</h2>
        <div className="flex gap-4 text-sm text-ink-2">
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-sm bg-accent" /> Reviews</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-sm bg-teal" /> Fixes</span>
        </div>
      </div>

      <div className="flex-1 min-h-44 flex items-end gap-1.5 border-b border-line">
        {days.map((d) => (
          <div
            key={d.day}
            title={`${d.day}: ${d.reviews} reviews, ${d.fixes} fixes`}
            className="flex-1 h-full flex items-end justify-center gap-0.5 hover:bg-surface-2 rounded-t"
          >
            <div className="w-[38%] rounded-t bg-accent" style={{ height: `${(d.reviews / max) * 100}%` }} />
            <div className="w-[38%] rounded-t bg-teal" style={{ height: `${(d.fixes / max) * 100}%` }} />
          </div>
        ))}
      </div>

      <div className="flex justify-between text-xs text-muted">
        <span>{days[0]?.day.slice(5)}</span>
        <span>Today</span>
      </div>
    </div>
  );
};

export default ActivityChart;
