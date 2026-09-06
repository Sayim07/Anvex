// ThreatSkeleton.jsx — Animated skeleton loader rows for Threat Feed table
export default function ThreatSkeleton({ rows = 4 }) {
  return (
    <>
      {Array.from({ length: rows }).map((_, idx) => (
        <tr key={`skeleton-${idx}`} className="border-b border-slate-800/60">
          {/* Time */}
          <td className="p-3">
            <div className="h-4 w-16 rounded skeleton-shimmer bg-slate-800/40" />
          </td>
          {/* Source -> Dest */}
          <td className="p-3">
            <div className="flex items-center gap-2">
              <div className="h-4 w-28 rounded skeleton-shimmer bg-slate-800/40" />
              <div className="h-3 w-3 rounded skeleton-shimmer bg-slate-800/40" />
              <div className="h-4 w-28 rounded skeleton-shimmer bg-slate-800/40" />
            </div>
          </td>
          {/* Threat Class */}
          <td className="p-3">
            <div className="h-5 w-24 rounded skeleton-shimmer bg-slate-800/40" />
          </td>
          {/* Severity */}
          <td className="p-3">
            <div className="h-5 w-16 rounded skeleton-shimmer bg-slate-800/40" />
          </td>
          {/* Confidence */}
          <td className="p-3">
            <div className="h-5 w-14 rounded skeleton-shimmer bg-slate-800/40" />
          </td>
          {/* Tx Hash */}
          <td className="p-3">
            <div className="h-5 w-28 rounded skeleton-shimmer bg-slate-800/40" />
          </td>
          {/* Verify Button */}
          <td className="p-3">
            <div className="h-6 w-16 rounded skeleton-shimmer bg-slate-800/40" />
          </td>
          {/* Expand Arrow */}
          <td className="p-3">
            <div className="h-4 w-4 rounded skeleton-shimmer bg-slate-800/40" />
          </td>
        </tr>
      ))}
    </>
  );
}
