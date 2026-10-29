const StatCard = ({ label, value, note }) => {
  return (
    <div className="p-5 bg-white border border-slate-100 rounded-2xl">
      <p className="text-xs font-bold text-slate-400 uppercase">{label}</p>
      <p className="mt-1 text-3xl font-bold text-slate-800">{value}</p>
      {note && <p className="mt-1 text-xs text-slate-400">{note}</p>}
    </div>
  );
};

export default StatCard;
