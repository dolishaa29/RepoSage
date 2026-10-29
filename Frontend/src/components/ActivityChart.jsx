const REVIEW_COLOR = "#5f7f1f";
const FIX_COLOR = "#3b6fd8";

// days: [{ day, reviews, fixes }]
const ActivityChart = ({ days }) => {
  const max = Math.max(1, ...days.map((d) => Math.max(d.reviews, d.fixes)));

  return (
    <div className="p-5 bg-white border border-slate-100 rounded-2xl">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
        <h2 className="font-bold text-slate-700">Last 14 days</h2>
        <div className="flex gap-4 text-xs text-slate-500">
          <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-sm" style={{ background: REVIEW_COLOR }} /> Reviews</span>
          <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-sm" style={{ background: FIX_COLOR }} /> Fixes</span>
        </div>
      </div>

      <div className="flex items-end gap-1 h-36 border-b border-slate-200">
        {days.map((d) => (
          <div
            key={d.day}
            title={`${d.day}: ${d.reviews} reviews, ${d.fixes} fixes`}
            className="flex-1 h-full flex items-end justify-center gap-0.5 hover:bg-slate-50 rounded-t"
          >
            <div className="w-1/3 rounded-t" style={{ height: `${(d.reviews / max) * 100}%`, background: REVIEW_COLOR }} />
            <div className="w-1/3 rounded-t" style={{ height: `${(d.fixes / max) * 100}%`, background: FIX_COLOR }} />
          </div>
        ))}
      </div>

      <div className="flex justify-between mt-2 text-xs text-slate-400">
        <span>{days[0]?.day.slice(5)}</span>
        <span>Today</span>
      </div>
    </div>
  );
};

export default ActivityChart;
